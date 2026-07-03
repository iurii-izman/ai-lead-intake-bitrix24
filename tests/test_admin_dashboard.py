from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.main import create_app
from app.models.ai_classification import AIClassificationRecord
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
    RequestStatus,
)
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.models.routing_decision import RoutingDecisionRecord


def build_test_client(tmp_path: Path) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'admin.sqlite3'}"
    settings = Settings(
        database_url=database_url,
        intake_webhook_secret="test-secret",
        admin_username="admin",
        admin_password="change-me",
        ai_provider="mock",
        bitrix_mode="mock",
        bitrix_crm_mode="universal",
        worker_autostart=False,
    )
    return TestClient(create_app(settings=settings))


def get_session(client: TestClient) -> Session:
    return Session(client.app.state.engine)


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Basic YWRtaW46Y2hhbmdlLW1l"}


def create_reviewable_request(session: Session) -> IntakeRequestRecord:
    request = IntakeRequestRecord(
        idempotency_key="site-form-admin-0001",
        source="web_form",
        raw_payload_masked=(
            '{"idempotency_key":"site-form-admin-0001","source":"web_form","name":"[masked]",'
            '"email":"[masked]","phone":"[masked]","company":"[masked]","message":"[masked]"}'
        ),
        raw_text="Please contact Ivan Petrov at ivan.petrov@example.com or +37360000000.",
        status=RequestStatus.review_needed,
        retry_count=0,
    )
    session.add(request)
    session.flush()

    session.add(
        AIClassificationRecord(
            intake_id=request.id,
            category=AIClassificationCategory.crm_implementation,
            priority=AIClassificationPriority.high,
            confidence=0.42,
            intent="Client wants Bitrix24 CRM implementation support.",
            summary="The client is asking about Bitrix24 CRM implementation.",
            contact_name="Ivan Petrov",
            contact_email_masked="ivan.petrov@example.com",
            contact_phone_masked="+37360000000",
            company="OOO Romashka",
            product_interest="Bitrix24 CRM",
            suggested_tone=AIClassificationTone.formal,
            needs_human_review=True,
            draft_reply="Good day. Thank you for your message.",
            reasoning="Low confidence.",
            model_used="mock",
            raw_ai_response='{"mock":"response"}',
        )
    )
    session.add(
        RoutingDecisionRecord(
            intake_id=request.id,
            rule_id="human_review_gate",
            responsible_id=3,
            action="review",
            create_task=True,
            task_deadline_hours=24,
            task_title="Review incoming request",
        )
    )
    session.add(
        ProcessingLogRecord(
            intake_id=request.id,
            event="intake_received",
            status=RequestStatus.received,
            details='{"source":"web_form"}',
        )
    )
    session.commit()
    session.refresh(request)
    return request


def create_approved_request(session: Session) -> IntakeRequestRecord:
    request = IntakeRequestRecord(
        idempotency_key="site-form-admin-0002",
        source="web_form",
        raw_payload_masked='{"message":"masked"}',
        raw_text="Need Bitrix24 CRM implementation support.",
        status=RequestStatus.review_needed,
    )
    session.add(request)
    session.flush()

    session.add(
        AIClassificationRecord(
            intake_id=request.id,
            category=AIClassificationCategory.crm_implementation,
            priority=AIClassificationPriority.high,
            confidence=0.41,
            intent="Client wants Bitrix24 CRM implementation support.",
            summary="The client is asking about Bitrix24 CRM implementation.",
            contact_name="Ivan Petrov",
            contact_email_masked="ivan.petrov@example.com",
            contact_phone_masked="+37360000000",
            company="OOO Romashka",
            product_interest="Bitrix24 CRM",
            suggested_tone=AIClassificationTone.formal,
            needs_human_review=True,
            draft_reply="Good day. Thank you for your message.",
            reasoning="Low confidence.",
            model_used="mock",
            raw_ai_response='{"mock":"response"}',
        )
    )
    session.add(
        RoutingDecisionRecord(
            intake_id=request.id,
            rule_id="crm_implementation",
            responsible_id=3,
            action="route",
            create_task=True,
            task_deadline_hours=8,
            task_title="CRM implementation: Client wants Bitrix24 CRM implementation support.",
        )
    )
    session.commit()
    session.refresh(request)
    return request


def create_dropped_request(session: Session) -> IntakeRequestRecord:
    request = IntakeRequestRecord(
        idempotency_key="site-form-admin-0003",
        source="web_form",
        raw_payload_masked='{"message":"masked"}',
        raw_text="Need Bitrix24 CRM implementation support after drop.",
        status=RequestStatus.dropped,
    )
    session.add(request)
    session.flush()

    session.add(
        AIClassificationRecord(
            intake_id=request.id,
            category=AIClassificationCategory.crm_implementation,
            priority=AIClassificationPriority.high,
            confidence=0.88,
            intent="Client wants Bitrix24 CRM implementation support.",
            summary="The client is asking about Bitrix24 CRM implementation.",
            contact_name="Ivan Petrov",
            contact_email_masked="ivan.petrov@example.com",
            contact_phone_masked="+37360000000",
            company="OOO Romashka",
            product_interest="Bitrix24 CRM",
            suggested_tone=AIClassificationTone.formal,
            needs_human_review=False,
            draft_reply="Good day. Thank you for your message.",
            reasoning="Dropped manually but classification is reusable.",
            model_used="mock",
            raw_ai_response='{"mock":"response"}',
        )
    )
    session.add(
        RoutingDecisionRecord(
            intake_id=request.id,
            rule_id="spam",
            responsible_id=None,
            action="drop",
            create_task=False,
            task_deadline_hours=None,
            task_title=None,
        )
    )
    session.commit()
    session.refresh(request)
    return request


def test_admin_dashboard_requires_basic_auth(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)

    with client:
        response = client.get("/")

        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Basic"


def test_admin_detail_masks_sensitive_data(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)

    with client:
        with get_session(client) as session:
            request = create_reviewable_request(session)

        response = client.get(f"/admin/requests/{request.id}", headers=auth_headers())

        assert response.status_code == 200
        html = response.text
        assert "ivan.petrov@example.com" not in html
        assert "+37360000000" not in html
        assert "[masked]" in html
        assert "Raw request" in html
        assert "AI classification" in html


def test_admin_approve_review_creates_bitrix_entities(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)

    with client:
        with get_session(client) as session:
            request = create_approved_request(session)

        response = client.post(
            f"/admin/requests/{request.id}/approve",
            headers=auth_headers(),
            follow_redirects=False,
        )

        assert response.status_code == 303

        with get_session(client) as session:
            stored_request = session.get(IntakeRequestRecord, request.id)
            bitrix_entities = session.scalars(
                select(BitrixEntityRecord).where(BitrixEntityRecord.intake_id == request.id)
            ).all()
            logs = session.scalars(
                select(ProcessingLogRecord).where(ProcessingLogRecord.intake_id == request.id)
            ).all()

        assert stored_request is not None
        assert stored_request.status == RequestStatus.completed
        assert len(bitrix_entities) == 2
        assert {log.event for log in logs} >= {
            "admin_approved",
            "bitrix_sync_started",
            "bitrix_lead_created",
            "bitrix_task_created",
            "completed",
        }


def test_admin_reprocess_dropped_request_completes_pipeline(tmp_path: Path) -> None:
    client = build_test_client(tmp_path)

    with client:
        with get_session(client) as session:
            request = create_dropped_request(session)

        response = client.post(
            f"/admin/requests/{request.id}/reprocess-ai",
            headers=auth_headers(),
            follow_redirects=False,
        )

        assert response.status_code == 303

        with get_session(client) as session:
            stored_request = session.get(IntakeRequestRecord, request.id)
            bitrix_entities = session.scalars(
                select(BitrixEntityRecord).where(BitrixEntityRecord.intake_id == request.id)
            ).all()
            logs = session.scalars(
                select(ProcessingLogRecord).where(ProcessingLogRecord.intake_id == request.id)
            ).all()

        assert stored_request is not None
        assert stored_request.status == RequestStatus.completed
        assert len(bitrix_entities) == 2
        assert {log.event for log in logs} >= {
            "admin_reprocess_started",
            "ai_reprocessed",
            "routed",
            "bitrix_sync_started",
            "bitrix_lead_created",
            "bitrix_task_created",
            "completed",
        }
