"""Operational admin dashboard routes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_app_settings, get_db_session
from app.models.enums import RequestStatus
from app.security.admin_auth import require_admin_auth
from app.services.admin_dashboard import AdminDashboardService, _mask_free_text, _status_label

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin_auth)])

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters["pretty_json"] = lambda value: _pretty_json(value)
templates.env.filters["status_badge_class"] = lambda value: _status_badge_class(value)
templates.env.filters["status_label"] = lambda value: _status_label(RequestStatus(value))
templates.env.filters["mask_text"] = lambda value: _mask_free_text(value)


@router.get("/", response_class=HTMLResponse, name="admin_dashboard")
def dashboard(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> HTMLResponse:
    service = AdminDashboardService(settings=settings)
    summary_cards = service.dashboard_summary(db)
    requests = service.list_requests(db, limit=25)
    return templates.TemplateResponse(
        request,
        "requests.html",
        {
            "page_title": "Admin dashboard",
            "active_page": "dashboard",
            "summary_cards": summary_cards,
            "requests": requests,
            "filters": {"status": "", "source": ""},
            "page_heading": "Queue dashboard",
            "page_description": "Operational view of the intake pipeline.",
        },
    )


@router.get("/admin/requests", response_class=HTMLResponse, name="admin_requests")
def list_requests(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    source: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    service = AdminDashboardService(settings=settings)
    status_value = _parse_status_filter(status_filter)
    summary_cards = service.dashboard_summary(db)
    requests = service.list_requests(db, status=status_value, source=source, limit=50)
    return templates.TemplateResponse(
        request,
        "requests.html",
        {
            "page_title": "Admin requests",
            "active_page": "requests",
            "summary_cards": summary_cards,
            "requests": requests,
            "filters": {
                "status": status_filter or "",
                "source": source or "",
            },
            "page_heading": "All requests",
            "page_description": "Search and inspect intake records.",
        },
    )


@router.get("/admin/review", response_class=HTMLResponse, name="admin_review_queue")
def review_queue(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> HTMLResponse:
    service = AdminDashboardService(settings=settings)
    summary_cards = service.dashboard_summary(db)
    requests = service.list_requests(db, status=RequestStatus.review_needed, limit=50)
    return templates.TemplateResponse(
        request,
        "requests.html",
        {
            "page_title": "Review queue",
            "active_page": "review",
            "summary_cards": summary_cards,
            "requests": requests,
            "filters": {"status": RequestStatus.review_needed.value, "source": ""},
            "page_heading": "Review queue",
            "page_description": "Requests requiring manual review before sync.",
        },
    )


@router.get(
    "/admin/requests/{request_id}", response_class=HTMLResponse, name="admin_request_detail"
)
def request_detail(
    request: Request,
    request_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> HTMLResponse:
    service = AdminDashboardService(settings=settings)
    detail = service.get_request_detail(db, request_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    return templates.TemplateResponse(
        request,
        "request_detail.html",
        {
            "page_title": f"Request {detail.request_id}",
            "active_page": "requests",
            "detail": detail,
        },
    )


@router.post("/admin/requests/{request_id}/approve", name="admin_request_approve")
def approve_request(
    request_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> RedirectResponse:
    service = AdminDashboardService(settings=settings)
    try:
        service.approve_request(db, request_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(
        url=f"/admin/requests/{request_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/requests/{request_id}/retry", name="admin_request_retry")
def retry_request(
    request_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> RedirectResponse:
    service = AdminDashboardService(settings=settings)
    try:
        service.retry_request(db, request_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(
        url=f"/admin/requests/{request_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/requests/{request_id}/drop", name="admin_request_drop")
def drop_request(
    request_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> RedirectResponse:
    service = AdminDashboardService(settings=settings)
    try:
        service.drop_request(db, request_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(
        url=f"/admin/requests/{request_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/requests/{request_id}/reprocess-ai", name="admin_request_reprocess_ai")
def reprocess_ai_request(
    request_id: str,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> RedirectResponse:
    service = AdminDashboardService(settings=settings)
    try:
        service.reprocess_ai_request(db, request_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedirectResponse(
        url=f"/admin/requests/{request_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/admin/settings", response_class=HTMLResponse, name="admin_settings")
def settings_page(
    request: Request,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> HTMLResponse:
    service = AdminDashboardService(settings=settings)
    snapshot = service.get_settings_snapshot()
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "page_title": "Admin settings",
            "active_page": "settings",
            "snapshot": snapshot,
        },
    )


def _parse_status_filter(status_filter: str | None) -> RequestStatus | None:
    if not status_filter:
        return None
    try:
        return RequestStatus(status_filter)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
        ) from exc


def _pretty_json(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return text
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _status_badge_class(value: object) -> str:
    status_value = value.value if hasattr(value, "value") else str(value)
    mapping = {
        "completed": "bg-emerald-500/15 text-emerald-200 ring-emerald-400/30",
        "review_needed": "bg-amber-500/15 text-amber-200 ring-amber-400/30",
        "failed": "bg-rose-500/15 text-rose-200 ring-rose-400/30",
        "failed_retryable": "bg-orange-500/15 text-orange-200 ring-orange-400/30",
        "processing": "bg-sky-500/15 text-sky-200 ring-sky-400/30",
        "dropped": "bg-slate-500/15 text-slate-200 ring-slate-400/30",
        "duplicate": "bg-slate-500/15 text-slate-200 ring-slate-400/30",
        "received": "bg-indigo-500/15 text-indigo-200 ring-indigo-400/30",
        "classified": "bg-cyan-500/15 text-cyan-200 ring-cyan-400/30",
        "routed": "bg-violet-500/15 text-violet-200 ring-violet-400/30",
        "bitrix_syncing": "bg-blue-500/15 text-blue-200 ring-blue-400/30",
    }
    return mapping.get(status_value, "bg-slate-500/15 text-slate-200 ring-slate-400/30")
