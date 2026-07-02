"""In-process worker and intake pipeline orchestration."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.integrations.bitrix24_client import (
    BitrixClientError,
    BitrixConfigurationError,
    BitrixRequestError,
    BitrixRetryableError,
)
from app.models.enums import RequestStatus
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.models.state_machine import REQUEST_LIFECYCLE_STATE_MACHINE
from app.schemas.intake import IntakeRequestCreate
from app.services.ai_classifier import AIClassificationResult, AIClassifier
from app.services.bitrix_service import BitrixService
from app.services.routing_engine import RoutingEngine, load_default_routing_engine

logger = logging.getLogger(__name__)

PENDING_STATUSES = (RequestStatus.received, RequestStatus.failed_retryable)


@dataclass(slots=True)
class IntakePipelineResult:
    """Result of processing a single intake request."""

    request_id: str
    status: RequestStatus
    processed: bool
    retry_count: int


class IntakePipelineService:
    """Coordinate AI classification, routing, and Bitrix24 sync."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        classifier: AIClassifier | None = None,
        routing_engine: RoutingEngine | None = None,
        bitrix_service: BitrixService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.classifier = classifier or AIClassifier(settings=self.settings)
        self.routing_engine = routing_engine or load_default_routing_engine()
        self.bitrix_service = bitrix_service or BitrixService(settings=self.settings)

    def process_pending_requests(
        self,
        session: Session,
        *,
        limit: int | None = None,
    ) -> int:
        """Process up to ``limit`` queued requests in a single session."""

        batch_size = limit or self.settings.worker_batch_size
        request_ids = session.scalars(
            select(IntakeRequestRecord.id)
            .where(IntakeRequestRecord.status.in_(PENDING_STATUSES))
            .order_by(IntakeRequestRecord.created_at.asc(), IntakeRequestRecord.id.asc())
            .limit(batch_size)
        ).all()

        processed = 0
        for request_id in request_ids:
            if self.process_request(session, request_id):
                processed += 1
        return processed

    def process_request(self, session: Session, request_id: str) -> bool:
        """Process a single request by primary key."""

        intake_request = session.get(IntakeRequestRecord, request_id)
        if intake_request is None:
            return False

        if intake_request.status not in PENDING_STATUSES:
            return False

        self._transition(
            session,
            intake_request,
            RequestStatus.processing,
            event="worker_picked",
            details={"retry_count": intake_request.retry_count},
        )

        ai_input = self._build_classifier_input(intake_request)
        ai_result = self.classifier.classify_with_metadata(ai_input)
        self._persist_ai_result(session, intake_request.id, ai_result)
        self._transition(
            session,
            intake_request,
            RequestStatus.classified,
            event="ai_failed" if ai_result.fallback_used else "ai_classified",
            details={
                "provider": ai_result.provider_name,
                "confidence": ai_result.classification.confidence,
                "fallback_used": ai_result.fallback_used,
                "error_message": ai_result.error_message,
            },
        )

        routing_decision = self.routing_engine.route(ai_result.classification)
        self._persist_routing_result(session, intake_request.id, routing_decision)

        if routing_decision.action == "review":
            self._transition(
                session,
                intake_request,
                RequestStatus.review_needed,
                event="review_needed",
                details={
                    "rule_id": routing_decision.rule_id,
                    "responsible_id": routing_decision.responsible_id,
                },
            )
            session.commit()
            return True

        if routing_decision.action == "drop":
            self._transition(
                session,
                intake_request,
                RequestStatus.dropped,
                event="dropped",
                details={"rule_id": routing_decision.rule_id},
            )
            session.commit()
            return True

        self._transition(
            session,
            intake_request,
            RequestStatus.routed,
            event="routed",
            details={
                "rule_id": routing_decision.rule_id,
                "responsible_id": routing_decision.responsible_id,
            },
        )
        self._transition(
            session,
            intake_request,
            RequestStatus.bitrix_syncing,
            event="bitrix_sync_started",
            details={"rule_id": routing_decision.rule_id},
        )

        try:
            self._sync_bitrix(session, intake_request, ai_result.classification, routing_decision)
        except BitrixRetryableError as exc:
            self._mark_retryable_failure(session, intake_request, exc)
            session.commit()
            return True
        except (
            BitrixConfigurationError,
            BitrixRequestError,
            BitrixClientError,
            RuntimeError,
        ) as exc:
            self._mark_failed(session, intake_request, exc)
            session.commit()
            return True

        self._transition(
            session,
            intake_request,
            RequestStatus.completed,
            event="completed",
            details={"retry_count": intake_request.retry_count},
        )
        session.commit()
        return True

    def _sync_bitrix(
        self,
        session: Session,
        intake_request: IntakeRequestRecord,
        classification,
        routing_decision,
    ) -> None:
        asyncio.run(
            self.bitrix_service.sync_approved_outcome(
                session,
                intake_request,
                classification,
                routing_decision,
            )
        )

    def _build_classifier_input(self, intake_request: IntakeRequestRecord) -> IntakeRequestCreate:
        return IntakeRequestCreate(
            idempotency_key=intake_request.idempotency_key,
            source=intake_request.source,
            message=intake_request.raw_text,
        )

    def _persist_ai_result(
        self,
        session: Session,
        intake_id: str,
        result: AIClassificationResult,
    ) -> None:
        session.add(
            _build_ai_record(
                intake_id=intake_id,
                classification=result.classification,
                provider_name=result.provider_name,
                raw_response=result.raw_response,
            )
        )
        self._add_log(
            session,
            intake_id,
            event="ai_started",
            status=RequestStatus.processing,
            details={"provider": result.provider_name},
        )

    def _persist_routing_result(
        self,
        session: Session,
        intake_id: str,
        routing_decision,
    ) -> None:
        session.add(
            _build_routing_record(
                intake_id=intake_id,
                routing_decision=routing_decision,
            )
        )

    def _mark_retryable_failure(
        self,
        session: Session,
        intake_request: IntakeRequestRecord,
        exc: Exception,
    ) -> None:
        intake_request.retry_count += 1
        retry_count = intake_request.retry_count
        if retry_count >= self.settings.worker_max_retry_attempts:
            self._transition(
                session,
                intake_request,
                RequestStatus.failed,
                event="pipeline_failed",
                details={
                    "error": exc.__class__.__name__,
                    "retry_count": retry_count,
                },
            )
            intake_request.error_message = str(exc)
            return

        self._transition(
            session,
            intake_request,
            RequestStatus.failed_retryable,
            event="pipeline_failed_retryable",
            details={
                "error": exc.__class__.__name__,
                "retry_count": retry_count,
            },
        )
        intake_request.error_message = str(exc)

    def _mark_failed(
        self,
        session: Session,
        intake_request: IntakeRequestRecord,
        exc: Exception,
    ) -> None:
        self._transition(
            session,
            intake_request,
            RequestStatus.failed,
            event="pipeline_failed",
            details={
                "error": exc.__class__.__name__,
                "retry_count": intake_request.retry_count,
            },
        )
        intake_request.error_message = str(exc)

    def _transition(
        self,
        session: Session,
        intake_request: IntakeRequestRecord,
        to_status: RequestStatus,
        *,
        event: str,
        details: dict[str, Any],
    ) -> None:
        REQUEST_LIFECYCLE_STATE_MACHINE.validate_transition(intake_request.status, to_status)
        intake_request.status = to_status
        self._add_log(session, intake_request.id, event=event, status=to_status, details=details)

    @staticmethod
    def _add_log(
        session: Session,
        intake_id: str,
        *,
        event: str,
        status: RequestStatus,
        details: dict[str, Any],
    ) -> None:
        session.add(
            ProcessingLogRecord(
                intake_id=intake_id,
                event=event,
                status=status,
                details=json.dumps(details, ensure_ascii=False, separators=(",", ":")),
            )
        )


class InProcessWorker:
    """Bounded in-process worker loop for demo and local development."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        settings: Settings | None = None,
        *,
        pipeline: IntakePipelineService | None = None,
        poll_interval_seconds: float | None = None,
        batch_size: int | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.session_factory = session_factory
        self.pipeline = pipeline or IntakePipelineService(settings=self.settings)
        self.poll_interval_seconds = (
            poll_interval_seconds or self.settings.worker_poll_interval_seconds
        )
        self.batch_size = batch_size or self.settings.worker_batch_size
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self.run_forever,
            name="ai-lead-intake-worker",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float | None = 5.0) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

    def run_forever(self) -> None:
        while not self._stop_event.is_set():
            self.process_once()
            if self._stop_event.wait(self.poll_interval_seconds):
                break

    def process_once(self) -> int:
        with self.session_factory() as session:
            processed = self.pipeline.process_pending_requests(session, limit=self.batch_size)
            if processed:
                logger.info("Processed %s queued intake request(s)", processed)
            return processed


def _build_ai_record(
    *,
    intake_id: str,
    classification,
    provider_name: str,
    raw_response: str,
):
    from app.models.ai_classification import AIClassificationRecord

    return AIClassificationRecord(
        intake_id=intake_id,
        category=classification.category,
        priority=classification.priority,
        confidence=classification.confidence,
        intent=classification.intent,
        summary=classification.summary,
        contact_name=classification.contact.name,
        contact_email_masked=classification.contact.email,
        contact_phone_masked=classification.contact.phone,
        company=classification.contact.company,
        product_interest=classification.product_interest,
        suggested_tone=classification.suggested_tone,
        needs_human_review=classification.needs_human_review,
        draft_reply=classification.draft_reply,
        reasoning=classification.reasoning,
        model_used=provider_name,
        raw_ai_response=raw_response,
    )


def _build_routing_record(*, intake_id: str, routing_decision):
    from app.models.routing_decision import RoutingDecisionRecord

    return RoutingDecisionRecord(
        intake_id=intake_id,
        rule_id=routing_decision.rule_id,
        responsible_id=routing_decision.responsible_id,
        action=routing_decision.action,
        create_task=routing_decision.create_task,
        task_deadline_hours=routing_decision.task_deadline_hours,
        task_title=routing_decision.task_title,
    )
