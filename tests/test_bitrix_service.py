from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.init_db import create_all
from app.integrations.bitrix24_client import (
    BitrixConfigurationError,
    MockBitrix24Client,
    RealBitrix24Client,
)
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
    RequestStatus,
)
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.schemas.classification import AIClassification, ExtractedContact
from app.schemas.routing import RoutingDecision
from app.services.bitrix_service import BitrixService


def build_classification() -> AIClassification:
    return AIClassification(
        category=AIClassificationCategory.crm_implementation,
        priority=AIClassificationPriority.high,
        confidence=0.91,
        intent="Client wants Bitrix24 CRM implementation support.",
        summary="The client is asking about Bitrix24 CRM implementation.",
        contact=ExtractedContact(
            name="Ivan Petrov",
            email="ivan.petrov@example.com",
            phone="+37360000000",
            company="OOO Romashka",
        ),
        product_interest="Bitrix24 CRM",
        suggested_tone=AIClassificationTone.formal,
        draft_reply=(
            "Good day. Thank you for your message. We will review the request and get back "
            "with the next steps."
        ),
        reasoning="High confidence CRM implementation request.",
        needs_human_review=False,
    )


def build_routing_decision() -> RoutingDecision:
    return RoutingDecision(
        rule_id="crm_implementation",
        responsible_id=3,
        action="route",
        create_task=True,
        task_deadline_hours=8,
        task_title="Внедрение CRM: Client wants Bitrix24 CRM implementation support.",
    )


def build_session(tmp_path: Path) -> Session:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'bitrix.sqlite3'}")
    create_all(engine)
    return Session(engine)


def create_intake_request(session: Session) -> IntakeRequestRecord:
    intake = IntakeRequestRecord(
        idempotency_key="site-form-20260703-1001",
        source="web_form",
        raw_payload_masked='{"message":"masked"}',
        raw_text="Need Bitrix24 CRM implementation support.",
        status=RequestStatus.routed,
    )
    session.add(intake)
    session.commit()
    session.refresh(intake)
    return intake


def test_mock_bitrix_mode_creates_crm_entity_and_task_idempotently(tmp_path: Path) -> None:
    session = build_session(tmp_path)
    intake = create_intake_request(session)
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'bitrix.sqlite3'}",
        bitrix_mode="mock",
        bitrix_crm_mode="universal",
    )
    service = BitrixService(settings=settings, client=MockBitrix24Client(settings=settings))

    first = asyncio.run(
        service.sync_approved_outcome(
            session,
            intake,
            build_classification(),
            build_routing_decision(),
        )
    )
    second = asyncio.run(
        service.sync_approved_outcome(
            session,
            intake,
            build_classification(),
            build_routing_decision(),
        )
    )

    assert [item.entity_type for item in first] == ["crm.item", "task"]
    assert [item.bitrix_id for item in first] == [item.bitrix_id for item in second]

    entities = session.scalars(
        select(BitrixEntityRecord).order_by(BitrixEntityRecord.created_at)
    ).all()
    logs = session.scalars(
        select(ProcessingLogRecord).order_by(ProcessingLogRecord.created_at)
    ).all()

    assert len(entities) == 2
    assert len(logs) == 3
    assert [log.event for log in logs] == [
        "bitrix_syncing",
        "bitrix_lead_created",
        "bitrix_task_created",
    ]


def test_real_bitrix_mode_uses_expected_payload_contract(tmp_path: Path) -> None:
    session = build_session(tmp_path)
    intake = create_intake_request(session)
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'bitrix.sqlite3'}",
        bitrix_mode="real",
        bitrix_crm_mode="universal",
        bitrix24_webhook_url="https://portal.example.com/rest/1/webhook-token",
        bitrix24_base_url="https://portal.example.com",
    )

    calls: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        calls.append(
            {
                "path": request.url.path,
                "payload": payload,
            }
        )
        if request.url.path.endswith("/crm.item.add.json"):
            assert payload["entityTypeId"] == 1
            assert payload["fields"]["title"].startswith("[AI Intake]")
            assert payload["fields"]["assignedById"] == 3
            return httpx.Response(200, json={"result": {"item": {"id": 321}}})

        assert request.url.path.endswith("/tasks.task.add.json")
        assert payload["fields"]["RESPONSIBLE_ID"] == 3
        assert payload["fields"]["UF_CRM_TASK"] == ["L_321"]
        return httpx.Response(200, json={"result": {"task": {"id": 654}}})

    transport = httpx.MockTransport(handler)
    service = BitrixService(
        settings=settings,
        client=RealBitrix24Client(settings=settings, transport=transport),
    )

    results = asyncio.run(
        service.sync_approved_outcome(
            session,
            intake,
            build_classification(),
            build_routing_decision(),
        )
    )

    assert [item.entity_type for item in results] == ["crm.item", "task"]
    assert [item.bitrix_id for item in results] == [321, 654]
    assert calls[0]["path"].endswith("/crm.item.add.json")
    assert calls[1]["path"].endswith("/tasks.task.add.json")


def test_real_bitrix_mode_retries_429_before_succeeding(tmp_path: Path) -> None:
    session = build_session(tmp_path)
    intake = create_intake_request(session)
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'bitrix.sqlite3'}",
        bitrix_mode="real",
        bitrix_crm_mode="universal",
        bitrix24_webhook_url="https://portal.example.com/rest/1/webhook-token",
        bitrix24_base_url="https://portal.example.com",
    )

    attempts = {"crm": 0, "task": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/crm.item.add.json"):
            attempts["crm"] += 1
            if attempts["crm"] == 1:
                return httpx.Response(429, json={"error": "RATE_LIMIT"})
            return httpx.Response(200, json={"result": {"item": {"id": 777}}})

        attempts["task"] += 1
        return httpx.Response(200, json={"result": {"task": {"id": 888}}})

    transport = httpx.MockTransport(handler)
    service = BitrixService(
        settings=settings,
        client=RealBitrix24Client(settings=settings, transport=transport),
    )

    results = asyncio.run(
        service.sync_approved_outcome(
            session,
            intake,
            build_classification(),
            build_routing_decision(),
        )
    )

    assert [item.bitrix_id for item in results] == [777, 888]
    assert attempts["crm"] == 2
    assert attempts["task"] == 1


def test_real_bitrix_mode_raises_configuration_error_without_retry(tmp_path: Path) -> None:
    session = build_session(tmp_path)
    intake = create_intake_request(session)
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'bitrix.sqlite3'}",
        bitrix_mode="real",
        bitrix_crm_mode="universal",
        bitrix24_webhook_url="https://portal.example.com/rest/1/webhook-token",
        bitrix24_base_url="https://portal.example.com",
    )

    attempts = {"crm": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["crm"] += 1
        return httpx.Response(401, json={"error": "INVALID_AUTH"})

    transport = httpx.MockTransport(handler)
    service = BitrixService(
        settings=settings,
        client=RealBitrix24Client(settings=settings, transport=transport),
    )

    with pytest.raises(BitrixConfigurationError):
        asyncio.run(
            service.sync_approved_outcome(
                session,
                intake,
                build_classification(),
                build_routing_decision(),
            )
        )

    assert attempts["crm"] == 1
