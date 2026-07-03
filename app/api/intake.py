"""Protected intake API for incoming lead requests."""

from __future__ import annotations

import json
import logging
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_app_settings, get_db_session
from app.models.enums import RequestStatus
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.schemas.intake import IntakeRequestCreate, IntakeRequestResponse

router = APIRouter(prefix="/api/v1/intake", tags=["intake"])
logger = logging.getLogger(__name__)

SENSITIVE_FIELDS = {"email", "phone", "name", "company", "message"}


def is_valid_webhook_secret(provided: str | None, expected: str) -> bool:
    if not provided or not expected:
        return False
    return secrets.compare_digest(provided, expected)


def mask_payload_for_storage(payload: IntakeRequestCreate) -> str:
    data = payload.model_dump(mode="json")
    masked = {
        key: ("[masked]" if key in SENSITIVE_FIELDS and value is not None else value)
        for key, value in data.items()
    }
    return json.dumps(masked, ensure_ascii=False, separators=(",", ":"))


def build_request_response(record: IntakeRequestRecord) -> IntakeRequestResponse:
    return IntakeRequestResponse(
        request_id=record.id,
        idempotency_key=record.idempotency_key,
        source=record.source,
        status=record.status,
        raw_payload_masked=record.raw_payload_masked,
        raw_text=record.raw_text,
        error_message=record.error_message,
        retry_count=record.retry_count,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("", response_model=IntakeRequestResponse, status_code=status.HTTP_202_ACCEPTED)
def create_intake_request(
    payload: IntakeRequestCreate,
    response: Response,
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
    x_webhook_secret: Annotated[str | None, Header(alias="X-Webhook-Secret")] = None,
) -> IntakeRequestResponse:
    if not is_valid_webhook_secret(x_webhook_secret, settings.intake_webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )

    existing = db.scalar(
        select(IntakeRequestRecord).where(
            IntakeRequestRecord.idempotency_key == payload.idempotency_key
        )
    )
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        logger.info(
            "Duplicate intake request replayed",
            extra={
                "request_id": existing.id,
                "idempotency_key": existing.idempotency_key,
                "source": existing.source,
            },
        )
        return build_request_response(existing)

    record = IntakeRequestRecord(
        idempotency_key=payload.idempotency_key,
        source=payload.source,
        raw_payload_masked=mask_payload_for_storage(payload),
        raw_text=payload.message.strip(),
    )
    db.add(record)

    try:
        db.flush()
        db.add(
            ProcessingLogRecord(
                intake_id=record.id,
                event="intake_received",
                status=RequestStatus.received,
                details=json.dumps(
                    {"source": payload.source, "idempotency_key": payload.idempotency_key},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(IntakeRequestRecord).where(
                IntakeRequestRecord.idempotency_key == payload.idempotency_key
            )
        )
        if existing is None:
            raise
        response.status_code = status.HTTP_200_OK
        return build_request_response(existing)

    db.refresh(record)
    logger.info(
        "Intake request accepted",
        extra={
            "request_id": record.id,
            "idempotency_key": record.idempotency_key,
            "source": record.source,
        },
    )
    return build_request_response(record)
