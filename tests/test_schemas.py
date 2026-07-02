from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
    RequestStatus,
)
from app.schemas.bitrix import BitrixEntityResult
from app.schemas.classification import AIClassification, ExtractedContact
from app.schemas.intake import IntakeRequestCreate, IntakeRequestResponse
from app.schemas.routing import RoutingDecision


def test_intake_request_create_validates_and_normalizes_message():
    schema = IntakeRequestCreate(
        idempotency_key="site-form-20260702-0001",
        source="web_form",
        message="  Need Bitrix24 integration  ",
    )

    assert schema.message == "Need Bitrix24 integration"


def test_intake_request_create_requires_message():
    with pytest.raises(ValidationError):
        IntakeRequestCreate(idempotency_key="k-1", source="web_form", message="   ")


def test_intake_request_create_validates_email():
    with pytest.raises(ValidationError):
        IntakeRequestCreate(
            idempotency_key="k-1",
            source="web_form",
            email="not-an-email",
            message="Hello",
        )


def test_ai_classification_schema_supports_nested_contact():
    payload = AIClassification(
        category=AIClassificationCategory.integration_1c,
        priority=AIClassificationPriority.high,
        confidence=0.91,
        intent="Client wants Bitrix24 and 1C integration",
        summary="The client needs an initial estimate for integration.",
        contact=ExtractedContact(
            name="Ivan Petrov",
            email="ivan.petrov@example.com",
            phone="+37360000000",
            company="OOO Romashka",
        ),
        product_interest="Bitrix24 + 1C",
        suggested_tone=AIClassificationTone.formal,
        draft_reply="Thank you for your request.",
        reasoning="Clear integration request with high confidence.",
        needs_human_review=False,
    )

    assert payload.contact.email == "ivan.petrov@example.com"
    assert payload.model_dump()["category"] == "integration_1c"


def test_routing_and_bitrix_schemas_are_structured():
    routing = RoutingDecision(
        rule_id="fallback",
        responsible_id=1,
        action="route",
        create_task=True,
        task_deadline_hours=24,
        task_title="New request: Integration",
    )
    bitrix = BitrixEntityResult(
        entity_type="crm.lead",
        bitrix_id=123,
        bitrix_url="https://example.bitrix24.com/crm/lead/details/123/",
        status="created",
    )

    assert routing.create_task is True
    assert bitrix.bitrix_id == 123


def test_intake_request_response_serializes_request_state():
    response = IntakeRequestResponse(
        request_id="req-1",
        idempotency_key="site-form-20260702-0001",
        source="web_form",
        status=RequestStatus.received,
        raw_payload_masked='{"message":"masked"}',
        raw_text="Need help",
        error_message=None,
        retry_count=0,
        created_at=datetime(2026, 7, 2, 18, 30, tzinfo=timezone.utc).isoformat(),
        updated_at=datetime(2026, 7, 2, 18, 30, tzinfo=timezone.utc).isoformat(),
    )

    assert response.status == RequestStatus.received
