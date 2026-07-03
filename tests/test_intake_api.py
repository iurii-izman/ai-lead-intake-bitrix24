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


def build_rate_limited_test_client(
    tmp_path: Path,
    *,
    max_requests: int,
    window_seconds: int = 60,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'rate-limit.sqlite3'}"
    settings = Settings(
        database_url=database_url,
        intake_webhook_secret="test-secret",
        debug=False,
        database_echo=False,
        intake_rate_limit_max_requests=max_requests,
        intake_rate_limit_window_seconds=window_seconds,
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


def test_intake_get_returns_existing_request(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        created = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0002-get",
                "source": "web_form",
                "message": "Need Bitrix24 integration",
            },
        )

        request_id = created.json()["request_id"]
        fetched = client.get(
            f"/api/v1/intake/{request_id}",
            headers={"X-Webhook-Secret": "test-secret"},
        )

        assert created.status_code == 202
        assert fetched.status_code == 200
        assert fetched.json()["request_id"] == request_id
        assert fetched.json()["status"] == "received"


def test_intake_get_requires_valid_secret(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        created = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={
                "idempotency_key": "site-form-20260703-0002-get-auth",
                "source": "web_form",
                "message": "Need Bitrix24 integration",
            },
        )

        request_id = created.json()["request_id"]
        fetched = client.get(
            f"/api/v1/intake/{request_id}",
            headers={"X-Webhook-Secret": "wrong-secret"},
        )

        assert fetched.status_code == 401
        assert fetched.json()["detail"] == "Invalid webhook secret"


def test_intake_get_returns_404_for_unknown_request(tmp_path):
    client = build_test_client(tmp_path)

    with client:
        response = client.get(
            "/api/v1/intake/unknown-request-id",
            headers={"X-Webhook-Secret": "test-secret"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Request not found"


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


def test_intake_rate_limit_returns_429(tmp_path):
    client = build_rate_limited_test_client(tmp_path, max_requests=2)

    with client:
        payload = {
            "source": "web_form",
            "message": "Need Bitrix24 integration",
        }

        first = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={**payload, "idempotency_key": "site-form-20260703-rl-1"},
        )
        second = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={**payload, "idempotency_key": "site-form-20260703-rl-2"},
        )
        third = client.post(
            "/api/v1/intake",
            headers={"X-Webhook-Secret": "test-secret"},
            json={**payload, "idempotency_key": "site-form-20260703-rl-3"},
        )

        assert first.status_code == 202
        assert second.status_code == 202
        assert third.status_code == 429
        assert third.json()["detail"] == "Rate limit exceeded"
        assert 1 <= int(third.headers["retry-after"]) <= 60

        with get_session(client) as session:
            requests = session.scalars(select(IntakeRequestRecord)).all()
            logs = session.scalars(select(ProcessingLogRecord)).all()

            assert len(requests) == 2
            assert len(logs) == 2

