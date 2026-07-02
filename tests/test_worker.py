from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.db.init_db import create_all
from app.integrations.bitrix24_client import (
    BitrixCallResult,
    BitrixRetryableError,
    MockBitrix24Client,
)
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
from app.schemas.classification import AIClassification, ExtractedContact
from app.services.ai_classifier import AIClassifier
from app.services.bitrix_service import BitrixService
from app.services.routing_engine import RoutingEngine
from app.services.worker import InProcessWorker, IntakePipelineService


def build_settings(tmp_path: Path, **overrides) -> Settings:
    return Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'worker.sqlite3'}",
        intake_webhook_secret="test-secret",
        ai_provider="mock",
        bitrix_mode="mock",
        bitrix_crm_mode="universal",
        worker_autostart=False,
        **overrides,
    )


def build_session_factory(tmp_path: Path) -> sessionmaker[Session]:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'worker.sqlite3'}")
    create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def create_request(
    session: Session, *, message: str, status: RequestStatus = RequestStatus.received
) -> IntakeRequestRecord:
    record = IntakeRequestRecord(
        idempotency_key=f"site-form-{message[:8].replace(' ', '-') or 'demo'}",
        source="web_form",
        raw_payload_masked=json.dumps(
            {
                "idempotency_key": "masked",
                "source": "web_form",
                "name": "[masked]",
                "email": "[masked]",
                "phone": "[masked]",
                "company": "[masked]",
                "message": "[masked]",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        raw_text=message,
        status=status,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def build_ai_classifier(payload: dict[str, object]) -> AIClassifier:
    return AIClassifier(
        settings=Settings(ai_provider="mock", confidence_threshold=0.75),
        client=StaticLLMClient(payload),
    )


def build_classification_payload(
    *,
    category: AIClassificationCategory,
    priority: AIClassificationPriority,
    confidence: float,
    needs_human_review: bool = False,
) -> dict[str, object]:
    classification = AIClassification(
        category=category,
        priority=priority,
        confidence=confidence,
        intent="Client wants follow-up on the request.",
        summary="The client submitted an incoming request.",
        contact=ExtractedContact(),
        product_interest=None,
        suggested_tone=AIClassificationTone.formal,
        draft_reply="Good day. Thank you for your message.",
        reasoning="Deterministic test payload.",
        needs_human_review=needs_human_review,
    )
    return classification.model_dump(mode="json")


def load_session(session_factory: sessionmaker[Session]) -> Session:
    return session_factory()


def test_worker_processes_happy_path_to_completion(tmp_path: Path) -> None:
    session_factory = build_session_factory(tmp_path)
    settings = build_settings(tmp_path)
    classifier = build_ai_classifier(
        build_classification_payload(
            category=AIClassificationCategory.crm_implementation,
            priority=AIClassificationPriority.high,
            confidence=0.93,
        )
    )
    pipeline = IntakePipelineService(
        settings=settings,
        classifier=classifier,
        routing_engine=RoutingEngine.from_file(),
        bitrix_service=BitrixService(
            settings=settings,
            client=MockBitrix24Client(settings=settings),
        ),
    )
    worker = InProcessWorker(session_factory, settings, pipeline=pipeline)

    with load_session(session_factory) as session:
        request = create_request(session, message="Need Bitrix24 CRM implementation support.")

    processed = worker.process_once()
    assert processed == 1

    with load_session(session_factory) as session:
        stored_request = session.get(IntakeRequestRecord, request.id)
        ai_records = session.scalars(select(AIClassificationRecord)).all()
        routing_records = session.scalars(select(RoutingDecisionRecord)).all()
        bitrix_records = session.scalars(select(BitrixEntityRecord)).all()
        logs = session.scalars(select(ProcessingLogRecord)).all()

    assert stored_request is not None
    assert stored_request.status == RequestStatus.completed
    assert stored_request.retry_count == 0
    assert len(ai_records) == 1
    assert len(routing_records) == 1
    assert len(bitrix_records) == 2
    assert {log.event for log in logs} >= {
        "worker_picked",
        "ai_started",
        "ai_classified",
        "routed",
        "bitrix_sync_started",
        "bitrix_syncing",
        "bitrix_lead_created",
        "bitrix_task_created",
        "completed",
    }


def test_worker_routes_low_confidence_request_to_review(tmp_path: Path) -> None:
    session_factory = build_session_factory(tmp_path)
    settings = build_settings(tmp_path)
    classifier = build_ai_classifier(
        build_classification_payload(
            category=AIClassificationCategory.crm_implementation,
            priority=AIClassificationPriority.high,
            confidence=0.41,
        )
    )
    pipeline = IntakePipelineService(
        settings=settings,
        classifier=classifier,
        routing_engine=RoutingEngine.from_file(),
        bitrix_service=BitrixService(
            settings=settings,
            client=MockBitrix24Client(settings=settings),
        ),
    )
    worker = InProcessWorker(session_factory, settings, pipeline=pipeline)

    with load_session(session_factory) as session:
        request = create_request(session, message="Need CRM help but details are unclear.")

    processed = worker.process_once()
    assert processed == 1

    with load_session(session_factory) as session:
        stored_request = session.get(IntakeRequestRecord, request.id)
        bitrix_records = session.scalars(select(BitrixEntityRecord)).all()
        logs = session.scalars(select(ProcessingLogRecord)).all()

    assert stored_request is not None
    assert stored_request.status == RequestStatus.review_needed
    assert len(bitrix_records) == 0
    assert {log.event for log in logs} >= {
        "worker_picked",
        "ai_started",
        "ai_classified",
        "review_needed",
    }
    assert not {log.event for log in logs} & {
        "bitrix_sync_started",
        "bitrix_syncing",
        "bitrix_lead_created",
        "bitrix_task_created",
    }


def test_worker_drops_spam_requests_without_bitrix_sync(tmp_path: Path) -> None:
    session_factory = build_session_factory(tmp_path)
    settings = build_settings(tmp_path)
    classifier = build_ai_classifier(
        build_classification_payload(
            category=AIClassificationCategory.spam,
            priority=AIClassificationPriority.low,
            confidence=0.98,
        )
    )
    pipeline = IntakePipelineService(
        settings=settings,
        classifier=classifier,
        routing_engine=RoutingEngine.from_file(),
        bitrix_service=BitrixService(
            settings=settings,
            client=MockBitrix24Client(settings=settings),
        ),
    )
    worker = InProcessWorker(session_factory, settings, pipeline=pipeline)

    with load_session(session_factory) as session:
        request = create_request(session, message="Buy followers now and unsubscribe.")

    processed = worker.process_once()
    assert processed == 1

    with load_session(session_factory) as session:
        stored_request = session.get(IntakeRequestRecord, request.id)
        bitrix_records = session.scalars(select(BitrixEntityRecord)).all()
        logs = session.scalars(select(ProcessingLogRecord)).all()

    assert stored_request is not None
    assert stored_request.status == RequestStatus.dropped
    assert len(bitrix_records) == 0
    assert {log.event for log in logs} >= {
        "worker_picked",
        "ai_started",
        "ai_classified",
        "dropped",
    }


def test_worker_retries_then_completes_after_transient_bitrix_failure(tmp_path: Path) -> None:
    session_factory = build_session_factory(tmp_path)
    settings = build_settings(tmp_path, worker_max_retry_attempts=3)
    classifier = build_ai_classifier(
        build_classification_payload(
            category=AIClassificationCategory.crm_implementation,
            priority=AIClassificationPriority.high,
            confidence=0.92,
        )
    )
    bitrix_client = RetryOnceBitrixClient()
    pipeline = IntakePipelineService(
        settings=settings,
        classifier=classifier,
        routing_engine=RoutingEngine.from_file(),
        bitrix_service=BitrixService(settings=settings, client=bitrix_client),
    )
    worker = InProcessWorker(session_factory, settings, pipeline=pipeline)

    with load_session(session_factory) as session:
        request = create_request(session, message="Need Bitrix24 CRM implementation support.")

    first_pass = worker.process_once()
    assert first_pass == 1

    with load_session(session_factory) as session:
        interim = session.get(IntakeRequestRecord, request.id)
        interim_logs = session.scalars(select(ProcessingLogRecord)).all()

    assert interim is not None
    assert interim.status == RequestStatus.failed_retryable
    assert interim.retry_count == 1
    assert {log.event for log in interim_logs} >= {
        "worker_picked",
        "ai_started",
        "ai_classified",
        "routed",
        "bitrix_sync_started",
        "bitrix_failed",
        "pipeline_failed_retryable",
    }

    second_pass = worker.process_once()
    assert second_pass == 1

    with load_session(session_factory) as session:
        final_request = session.get(IntakeRequestRecord, request.id)
        bitrix_records = session.scalars(select(BitrixEntityRecord)).all()
        final_logs = session.scalars(select(ProcessingLogRecord)).all()

    assert final_request is not None
    assert final_request.status == RequestStatus.completed
    assert final_request.retry_count == 1
    assert len(bitrix_records) == 2
    assert {log.event for log in final_logs} >= {
        "worker_picked",
        "ai_started",
        "ai_classified",
        "routed",
        "bitrix_sync_started",
        "bitrix_failed",
        "pipeline_failed_retryable",
        "completed",
    }


@dataclass(slots=True)
class StaticLLMClient:
    payload: dict[str, object]
    provider_name: str = "static"

    def classify(self, intake_request, *, response_schema: dict[str, object]) -> str:
        return json.dumps(self.payload, ensure_ascii=False, separators=(",", ":"))


@dataclass(slots=True)
class RetryOnceBitrixClient:
    provider_name: str = "retry-once"
    crm_attempts: int = 0

    async def create_crm_item(self, payload: dict[str, object]) -> BitrixCallResult:
        self.crm_attempts += 1
        if self.crm_attempts == 1:
            raise BitrixRetryableError("temporary Bitrix outage")
        return self._result("crm.item.add", "crm.item", 501, payload)

    async def create_lead(self, payload: dict[str, object]) -> BitrixCallResult:
        return self._result("crm.lead.add", "crm.lead", 501, payload)

    async def create_task(self, payload: dict[str, object]) -> BitrixCallResult:
        return self._result("tasks.task.add", "task", 777, payload)

    @staticmethod
    def _result(
        method: str,
        entity_type: str,
        bitrix_id: int,
        payload: dict[str, object],
    ) -> BitrixCallResult:
        return BitrixCallResult(
            method=method,
            entity_type=entity_type,
            bitrix_id=bitrix_id,
            bitrix_url=f"https://mock.bitrix24.local/{entity_type.replace('.', '/')}/{bitrix_id}/",
            payload=payload,
            raw_response={"result": {"id": bitrix_id}},
        )
