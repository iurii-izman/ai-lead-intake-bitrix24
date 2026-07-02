from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings
from app.db.session import create_session_factory
from app.main import create_app
from app.models.ai_classification import AIClassificationRecord
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.models.routing_decision import RoutingDecisionRecord


def build_test_client(tmp_path: Path) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'test.sqlite3'}"
    settings = Settings(
        database_url=database_url,
        intake_webhook_secret="test-secret",
        debug=False,
        database_echo=False,
    )
    app = create_app(settings=settings)
    return TestClient(app)


def get_session(client: TestClient):
    session_factory = create_session_factory(client.app.state.engine)
    return session_factory()


def test_intake_accepts_valid_payload_and_creates_log(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        response = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0001",
                "source": "web_form",
                "name": "Ivan Petrov",
                "email": "ivan.petrov@example.com",
                "phone": "+37360000000",
                "company": "OOO Romashka",
                "message": "Need Bitrix24 integration",
            },
        )

        assert response.status_code == 202
        body = response.json()
        assert body["idempotency_key"] == "site-form-20260703-0001"
        assert body["status"] == "received"
        assert body["raw_text"] == "Need Bitrix24 integration"
        assert "ivan.petrov@example.com" not in body["raw_payload_masked"]

        with get_session(client) as session:
            stored_request = session.scalar(select(IntakeRequestRecord))
            stored_log = session.scalar(select(ProcessingLogRecord))

            assert stored_request is not None
            assert stored_request.status.value == "received"
            assert stored_log is not None
            assert stored_log.event == "intake_received"
            assert session.scalars(select(AIClassificationRecord)).all() == []
            assert session.scalars(select(RoutingDecisionRecord)).all() == []
            assert session.scalars(select(BitrixEntityRecord)).all() == []


def test_intake_replays_duplicate_idempotency_key(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        first = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0002",
                "source": "web_form",
                "message": "Need Bitrix24 integration",
            },
        )
        second = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0002",
                "source": "web_form",
                "message": "Need Bitrix24 integration",
            },
        )

        assert first.status_code == 202
        assert second.status_code == 200
        assert first.json()["request_id"] == second.json()["request_id"]

        with get_session(client) as session:
            requests = session.scalars(select(IntakeRequestRecord)).all()
            logs = session.scalars(select(ProcessingLogRecord)).all()

            assert len(requests) == 1
            assert len(logs) == 1


def test_intake_rejects_invalid_secret(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        response = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "wrong-secret"},
            json={
                "idempotency_key": "site-form-20260703-0003",
                "source": "web_form",
                "message": "Need Bitrix24 integration",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid webhook secret"

        with get_session(client) as session:
            assert session.scalars(select(IntakeRequestRecord)).all() == []


def test_intake_rejects_invalid_payload(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        response = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0004",
                "source": "web_form",
                "email": "not-an-email",
                "message": "Need Bitrix24 integration",
            },
        )

        assert response.status_code == 422

        with get_session(client) as session:
            assert session.scalars(select(IntakeRequestRecord)).all() == []


def test_intake_rejects_blank_message(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        response = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0005",
                "source": "web_form",
                "message": "   ",
            },
        )

        assert response.status_code == 422

