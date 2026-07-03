"""Operational admin dashboard service layer."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.integrations.bitrix24_client import (
    BitrixClientError,
    BitrixConfigurationError,
    BitrixRequestError,
    BitrixRetryableError,
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
from app.models.state_machine import REQUEST_LIFECYCLE_STATE_MACHINE
from app.schemas.classification import AIClassification, ExtractedContact
from app.schemas.intake import IntakeRequestCreate
from app.schemas.routing import RoutingDecision
from app.services.ai_classifier import AIClassifier
from app.services.bitrix_service import BitrixService
from app.services.routing_engine import RoutingEngine, load_default_routing_engine

DEFAULT_ROUTING_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "routing.yaml"
DEFAULT_FIELD_MAPPING_PATH = Path(__file__).resolve().parents[2] / "config" / "field_mapping.yaml"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{6,}\d)(?!\d)")


@dataclass(slots=True)
class AdminSummaryCard:
    label: str
    value: str
    tone: str


@dataclass(slots=True)
class AdminRequestSummary:
    request_id: str
    idempotency_key: str
    source: str
    status: str
    status_label: str
    created_at: str
    updated_at: str
    retry_count: int
    category: str | None
    priority: str | None
    confidence: float | None
    responsible_id: int | None
    action: str | None
    bitrix_summary: str


@dataclass(slots=True)
class AdminClassificationView:
    category: str | None
    priority: str | None
    confidence: float | None
    intent: str | None
    summary: str | None
    contact_name: str | None
    contact_email: str | None
    contact_phone: str | None
    company: str | None
    product_interest: str | None
    suggested_tone: str | None
    needs_human_review: bool | None
    draft_reply: str | None
    reasoning: str | None
    model_used: str | None
    raw_ai_response: str | None
    created_at: str | None


@dataclass(slots=True)
class AdminRoutingView:
    rule_id: str | None
    responsible_id: int | None
    action: str | None
    create_task: bool | None
    task_deadline_hours: int | None
    task_title: str | None
    created_at: str | None


@dataclass(slots=True)
class AdminBitrixEntityView:
    entity_type: str
    bitrix_id: int | None
    bitrix_url: str | None
    status: str
    error_message: str | None
    created_at: str


@dataclass(slots=True)
class AdminLogView:
    event: str
    status: str
    details: str
    created_at: str


@dataclass(slots=True)
class AdminRequestDetail:
    request_id: str
    idempotency_key: str
    source: str
    status: str
    status_label: str
    raw_payload_masked: str
    raw_text_masked: str
    error_message: str | None
    retry_count: int
    created_at: str
    updated_at: str
    ai_classification: AdminClassificationView | None
    routing_decision: AdminRoutingView | None
    bitrix_entities: list[AdminBitrixEntityView]
    processing_logs: list[AdminLogView]
    available_actions: list[str]
    classification_count: int
    routing_count: int
    bitrix_count: int


@dataclass(slots=True)
class AdminSettingsSnapshot:
    runtime: list[tuple[str, str]]
    routing_yaml: str
    field_mapping_yaml: str


class AdminDashboardService:
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

    def dashboard_summary(self, session: Session) -> list[AdminSummaryCard]:
        counts = {status.value: 0 for status in RequestStatus}
        for status_value, count in session.execute(
            select(IntakeRequestRecord.status, func.count(IntakeRequestRecord.id)).group_by(
                IntakeRequestRecord.status
            )
        ):
            counts[status_value.value] = count

        return [
            AdminSummaryCard(
                "Queued", str(counts["received"] + counts["failed_retryable"]), "blue"
            ),
            AdminSummaryCard("In review", str(counts["review_needed"]), "amber"),
            AdminSummaryCard("Completed", str(counts["completed"]), "green"),
            AdminSummaryCard("Dropped", str(counts["dropped"]), "slate"),
            AdminSummaryCard("Failed", str(counts["failed"]), "red"),
            AdminSummaryCard("Duplicates", str(counts["duplicate"]), "slate"),
        ]

    def list_requests(
        self,
        session: Session,
        *,
        status: RequestStatus | None = None,
        source: str | None = None,
        limit: int = 50,
    ) -> list[AdminRequestSummary]:
        query = (
            select(IntakeRequestRecord)
            .options(
                selectinload(IntakeRequestRecord.ai_classifications),
                selectinload(IntakeRequestRecord.routing_decisions),
                selectinload(IntakeRequestRecord.bitrix_entities),
            )
            .order_by(IntakeRequestRecord.created_at.desc(), IntakeRequestRecord.id.desc())
            .limit(limit)
        )
        if status is not None:
            query = query.where(IntakeRequestRecord.status == status)
        if source:
            query = query.where(IntakeRequestRecord.source == source)

        records = session.scalars(query).all()
        return [self._build_summary(record) for record in records]

    def get_request_detail(self, session: Session, request_id: str) -> AdminRequestDetail | None:
        record = session.scalar(
            select(IntakeRequestRecord)
            .where(IntakeRequestRecord.id == request_id)
            .options(
                selectinload(IntakeRequestRecord.ai_classifications),
                selectinload(IntakeRequestRecord.routing_decisions),
                selectinload(IntakeRequestRecord.bitrix_entities),
                selectinload(IntakeRequestRecord.processing_logs),
            )
        )
        if record is None:
            return None

        ai_records = sorted(
            record.ai_classifications,
            key=lambda item: (item.created_at, item.id),
        )
        routing_records = sorted(
            record.routing_decisions,
            key=lambda item: (item.created_at, item.id),
        )
        bitrix_records = sorted(
            record.bitrix_entities,
            key=lambda item: (item.created_at, item.id),
        )
        log_records = sorted(
            record.processing_logs,
            key=lambda item: (item.created_at, item.id),
        )
        latest_ai = ai_records[-1] if ai_records else None
        latest_routing = routing_records[-1] if routing_records else None

        return AdminRequestDetail(
            request_id=record.id,
            idempotency_key=record.idempotency_key,
            source=record.source,
            status=record.status.value,
            status_label=_status_label(record.status),
            raw_payload_masked=record.raw_payload_masked,
            raw_text_masked=_mask_free_text(record.raw_text),
            error_message=record.error_message,
            retry_count=record.retry_count,
            created_at=record.created_at,
            updated_at=record.updated_at,
            ai_classification=self._build_classification_view(latest_ai),
            routing_decision=self._build_routing_view(latest_routing),
            bitrix_entities=[self._build_bitrix_view(entity) for entity in bitrix_records],
            processing_logs=[self._build_log_view(log) for log in log_records],
            available_actions=self._available_actions(record.status),
            classification_count=len(ai_records),
            routing_count=len(routing_records),
            bitrix_count=len(bitrix_records),
        )

    def _build_approved_routing_decision(
        self,
        session: Session,
        record: IntakeRequestRecord,
        classification: AIClassification,
        routing_record: RoutingDecisionRecord,
    ) -> RoutingDecision:
        if routing_record.action == "route":
            return RoutingDecision(
                rule_id=routing_record.rule_id,
                responsible_id=routing_record.responsible_id,
                action=routing_record.action,
                create_task=routing_record.create_task,
                task_deadline_hours=routing_record.task_deadline_hours,
                task_title=routing_record.task_title,
            )

        approved_record = RoutingDecisionRecord(
            intake_id=record.id,
            rule_id="admin_approved",
            responsible_id=(
                routing_record.responsible_id
                or self.routing_engine.config.defaults.review_responsible_id
            ),
            action="route",
            create_task=True,
            task_deadline_hours=(
                routing_record.task_deadline_hours
                or self.routing_engine.config.defaults.task_deadline_hours
            ),
            task_title=routing_record.task_title or f"Approved request: {classification.intent}",
        )
        session.add(approved_record)
        return RoutingDecision(
            rule_id=approved_record.rule_id,
            responsible_id=approved_record.responsible_id,
            action=approved_record.action,
            create_task=approved_record.create_task,
            task_deadline_hours=approved_record.task_deadline_hours,
            task_title=approved_record.task_title,
        )

    @staticmethod
    def _build_classification_model(record: AIClassificationRecord) -> AIClassification:
        return AIClassification(
            category=record.category or AIClassificationCategory.other,
            priority=record.priority or AIClassificationPriority.low,
            confidence=record.confidence or 0.0,
            intent=record.intent or "",
            summary=record.summary or "",
            contact=ExtractedContact(
                name=record.contact_name,
                email=record.contact_email_masked,
                phone=record.contact_phone_masked,
                company=record.company,
            ),
            product_interest=record.product_interest,
            suggested_tone=record.suggested_tone or AIClassificationTone.formal,
            draft_reply=record.draft_reply or "",
            reasoning=record.reasoning or "",
            needs_human_review=bool(record.needs_human_review),
        )

    def get_settings_snapshot(self) -> AdminSettingsSnapshot:
        runtime_pairs = [
            ("app_name", self.settings.app_name),
            ("environment", self.settings.environment),
            ("debug", str(self.settings.debug).lower()),
            ("database_url", self._mask_setting("database_url", self.settings.database_url)),
            (
                "intake_webhook_secret",
                self._mask_setting("intake_webhook_secret", self.settings.intake_webhook_secret),
            ),
            ("admin_username", self.settings.admin_username),
            ("admin_password", self._mask_setting("admin_password", self.settings.admin_password)),
            ("ai_provider", self.settings.ai_provider),
            ("openai_api_key", self._mask_setting("openai_api_key", self.settings.openai_api_key)),
            ("openai_model", self.settings.openai_model),
            ("bitrix_mode", self.settings.bitrix_mode),
            ("bitrix_crm_mode", self.settings.bitrix_crm_mode),
        ]
        return AdminSettingsSnapshot(
            runtime=runtime_pairs,
            routing_yaml=self._read_text(DEFAULT_ROUTING_CONFIG_PATH),
            field_mapping_yaml=self._read_text(DEFAULT_FIELD_MAPPING_PATH),
        )

    def approve_request(self, session: Session, request_id: str) -> AdminRequestDetail:
        record = self._get_request_or_raise(session, request_id)
        if record.status != RequestStatus.review_needed:
            raise ValueError("Approve action is only available for review-needed requests")

        classification_record = self._latest_classification(record)
        routing_decision = self._latest_routing(record)
        if classification_record is None or routing_decision is None:
            raise ValueError("Cannot approve a request without AI and routing results")

        classification = self._build_classification_model(classification_record)

        approved_routing = self._build_approved_routing_decision(
            session,
            record,
            classification,
            routing_decision,
        )

        self._transition(
            session,
            record,
            RequestStatus.routed,
            event="admin_approved",
            details={"source": "admin", "request_id": record.id},
        )
        self._transition(
            session,
            record,
            RequestStatus.bitrix_syncing,
            event="bitrix_sync_started",
            details={"source": "admin", "request_id": record.id},
        )
        try:
            self._sync_bitrix(session, record, classification, approved_routing)
        except BitrixRetryableError as exc:
            self._mark_retryable_failure(session, record, exc)
        except (
            BitrixConfigurationError,
            BitrixRequestError,
            BitrixClientError,
            RuntimeError,
        ) as exc:
            self._mark_failed(session, record, exc)
        else:
            record.error_message = None
            self._transition(
                session,
                record,
                RequestStatus.completed,
                event="completed",
                details={"source": "admin", "request_id": record.id},
            )
        session.commit()
        return self.get_request_detail(session, request_id)  # type: ignore[return-value]

    def retry_request(self, session: Session, request_id: str) -> AdminRequestDetail:
        record = self._get_request_or_raise(session, request_id)
        if record.status != RequestStatus.failed_retryable:
            raise ValueError("Retry action is only available for retryable failures")

        classification_record = self._latest_classification(record)
        routing_decision = self._latest_routing(record)
        if classification_record is None or routing_decision is None:
            raise ValueError("Cannot retry a request without AI and routing results")

        classification = self._build_classification_model(classification_record)

        self._transition(
            session,
            record,
            RequestStatus.processing,
            event="admin_retry_started",
            details={"source": "admin", "request_id": record.id},
        )
        self._transition(
            session,
            record,
            RequestStatus.classified,
            event="ai_reused",
            details={"source": "admin", "request_id": record.id},
        )
        self._transition(
            session,
            record,
            RequestStatus.routed,
            event="routing_reused",
            details={"source": "admin", "request_id": record.id},
        )
        self._transition(
            session,
            record,
            RequestStatus.bitrix_syncing,
            event="bitrix_sync_started",
            details={"source": "admin", "request_id": record.id},
        )
        try:
            self._sync_bitrix(session, record, classification, routing_decision)
        except BitrixRetryableError as exc:
            self._mark_retryable_failure(session, record, exc)
        except (
            BitrixConfigurationError,
            BitrixRequestError,
            BitrixClientError,
            RuntimeError,
        ) as exc:
            self._mark_failed(session, record, exc)
        else:
            record.error_message = None
            self._transition(
                session,
                record,
                RequestStatus.completed,
                event="completed",
                details={"source": "admin", "request_id": record.id},
            )
        session.commit()
        return self.get_request_detail(session, request_id)  # type: ignore[return-value]

    def drop_request(self, session: Session, request_id: str) -> AdminRequestDetail:
        record = self._get_request_or_raise(session, request_id)
        self._transition(
            session,
            record,
            RequestStatus.dropped,
            event="admin_dropped",
            details={"source": "admin", "request_id": record.id},
            validate=False,
        )
        session.commit()
        return self.get_request_detail(session, request_id)  # type: ignore[return-value]

    def reprocess_ai_request(self, session: Session, request_id: str) -> AdminRequestDetail:
        record = self._get_request_or_raise(session, request_id)
        if record.status == RequestStatus.completed:
            raise ValueError("Completed requests cannot be reprocessed")
        if record.status not in {RequestStatus.review_needed, RequestStatus.failed_retryable}:
            raise ValueError(
                "Reprocess AI is only available for review-needed or retryable requests"
            )

        if record.status == RequestStatus.review_needed:
            self._transition(
                session,
                record,
                RequestStatus.processing,
                event="admin_reprocess_started",
                details={"source": "admin", "request_id": record.id},
                validate=False,
            )
        else:
            self._transition(
                session,
                record,
                RequestStatus.processing,
                event="admin_reprocess_started",
                details={"source": "admin", "request_id": record.id},
            )

        ai_input = self._build_classifier_input(record)
        ai_result = self.classifier.classify_with_metadata(ai_input)
        self._persist_ai_result(session, record.id, ai_result)
        self._transition(
            session,
            record,
            RequestStatus.classified,
            event="ai_reprocessed",
            details={
                "provider": ai_result.provider_name,
                "confidence": ai_result.classification.confidence,
                "fallback_used": ai_result.fallback_used,
            },
        )

        routing_decision = self.routing_engine.route(ai_result.classification)
        self._persist_routing_result(session, record.id, routing_decision)

        if routing_decision.action == "review":
            self._transition(
                session,
                record,
                RequestStatus.review_needed,
                event="review_needed",
                details={"rule_id": routing_decision.rule_id, "source": "admin"},
            )
            session.commit()
            return self.get_request_detail(session, request_id)  # type: ignore[return-value]

        if routing_decision.action == "drop":
            self._transition(
                session,
                record,
                RequestStatus.dropped,
                event="dropped",
                details={"rule_id": routing_decision.rule_id, "source": "admin"},
            )
            session.commit()
            return self.get_request_detail(session, request_id)  # type: ignore[return-value]

        self._transition(
            session,
            record,
            RequestStatus.routed,
            event="routed",
            details={"rule_id": routing_decision.rule_id, "source": "admin"},
        )
        self._transition(
            session,
            record,
            RequestStatus.bitrix_syncing,
            event="bitrix_sync_started",
            details={"rule_id": routing_decision.rule_id, "source": "admin"},
        )
        try:
            self._sync_bitrix(session, record, ai_result.classification, routing_decision)
        except BitrixRetryableError as exc:
            self._mark_retryable_failure(session, record, exc)
        except (
            BitrixConfigurationError,
            BitrixRequestError,
            BitrixClientError,
            RuntimeError,
        ) as exc:
            self._mark_failed(session, record, exc)
        else:
            record.error_message = None
            self._transition(
                session,
                record,
                RequestStatus.completed,
                event="completed",
                details={"source": "admin", "request_id": record.id},
            )
        session.commit()
        return self.get_request_detail(session, request_id)  # type: ignore[return-value]

    def _sync_bitrix(
        self,
        session: Session,
        record: IntakeRequestRecord,
        classification: AIClassification,
        routing_decision: RoutingDecision,
    ) -> None:
        import asyncio

        asyncio.run(
            self.bitrix_service.sync_approved_outcome(
                session,
                record,
                classification,
                routing_decision,
                allow_human_override=True,
            )
        )

    def _build_classifier_input(self, record: IntakeRequestRecord) -> IntakeRequestCreate:
        return IntakeRequestCreate(
            idempotency_key=record.idempotency_key,
            source=record.source,
            message=record.raw_text,
        )

    def _build_summary(self, record: IntakeRequestRecord) -> AdminRequestSummary:
        ai = self._latest_classification(record)
        routing = self._latest_routing(record)
        bitrix_summary = ", ".join(
            f"{entity.entity_type}#{entity.bitrix_id}"
            for entity in sorted(
                record.bitrix_entities, key=lambda item: (item.created_at, item.id)
            )
            if entity.bitrix_id is not None
        )
        return AdminRequestSummary(
            request_id=record.id,
            idempotency_key=record.idempotency_key,
            source=record.source,
            status=record.status.value,
            status_label=_status_label(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            retry_count=record.retry_count,
            category=_enum_value(ai.category) if ai and ai.category else None,
            priority=_enum_value(ai.priority) if ai and ai.priority else None,
            confidence=ai.confidence if ai else None,
            responsible_id=routing.responsible_id if routing else None,
            action=routing.action if routing else None,
            bitrix_summary=bitrix_summary or "-",
        )

    def _persist_ai_result(
        self,
        session: Session,
        intake_id: str,
        result,
    ) -> AIClassificationRecord:
        record = AIClassificationRecord(
            intake_id=intake_id,
            category=result.classification.category,
            priority=result.classification.priority,
            confidence=result.classification.confidence,
            intent=result.classification.intent,
            summary=result.classification.summary,
            contact_name=result.classification.contact.name,
            contact_email_masked=result.classification.contact.email,
            contact_phone_masked=result.classification.contact.phone,
            company=result.classification.contact.company,
            product_interest=result.classification.product_interest,
            suggested_tone=result.classification.suggested_tone,
            needs_human_review=result.classification.needs_human_review,
            draft_reply=result.classification.draft_reply,
            reasoning=result.classification.reasoning,
            model_used=result.provider_name,
            raw_ai_response=result.raw_response,
        )
        session.add(record)
        self._add_log(
            session,
            intake_id,
            event="ai_started",
            status=RequestStatus.processing,
            details={"provider": result.provider_name},
        )
        self._add_log(
            session,
            intake_id,
            event="ai_classified",
            status=RequestStatus.classified,
            details={
                "confidence": result.classification.confidence,
                "fallback_used": result.fallback_used,
            },
        )
        return record

    def _persist_routing_result(
        self,
        session: Session,
        intake_id: str,
        decision: RoutingDecision,
    ) -> RoutingDecisionRecord:
        record = RoutingDecisionRecord(
            intake_id=intake_id,
            rule_id=decision.rule_id,
            responsible_id=decision.responsible_id,
            action=decision.action,
            create_task=decision.create_task,
            task_deadline_hours=decision.task_deadline_hours,
            task_title=decision.task_title,
        )
        session.add(record)
        return record

    def _mark_retryable_failure(
        self, session: Session, record: IntakeRequestRecord, exc: Exception
    ) -> None:
        record.retry_count += 1
        if record.retry_count >= self.settings.worker_max_retry_attempts:
            self._transition(
                session,
                record,
                RequestStatus.failed,
                event="pipeline_failed",
                details={"error": exc.__class__.__name__, "source": "admin"},
            )
            record.error_message = str(exc)
            return

        self._transition(
            session,
            record,
            RequestStatus.failed_retryable,
            event="pipeline_failed_retryable",
            details={"error": exc.__class__.__name__, "source": "admin"},
        )
        record.error_message = str(exc)

    def _mark_failed(self, session: Session, record: IntakeRequestRecord, exc: Exception) -> None:
        self._transition(
            session,
            record,
            RequestStatus.failed,
            event="pipeline_failed",
            details={"error": exc.__class__.__name__, "source": "admin"},
        )
        record.error_message = str(exc)

    def _transition(
        self,
        session: Session,
        record: IntakeRequestRecord,
        to_status: RequestStatus,
        *,
        event: str,
        details: dict[str, Any],
        validate: bool = True,
    ) -> None:
        if validate:
            REQUEST_LIFECYCLE_STATE_MACHINE.validate_transition(record.status, to_status)
        record.status = to_status
        self._add_log(session, record.id, event=event, status=to_status, details=details)

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

    @staticmethod
    def _build_classification_view(
        record: AIClassificationRecord | None,
    ) -> AdminClassificationView | None:
        if record is None:
            return None
        return AdminClassificationView(
            category=_enum_value(record.category) if record.category else None,
            priority=_enum_value(record.priority) if record.priority else None,
            confidence=record.confidence,
            intent=record.intent,
            summary=record.summary,
            contact_name=_mask_free_text(record.contact_name) if record.contact_name else None,
            contact_email=_mask_contact_value(record.contact_email_masked),
            contact_phone=_mask_contact_value(record.contact_phone_masked),
            company=_mask_free_text(record.company) if record.company else None,
            product_interest=record.product_interest,
            suggested_tone=_enum_value(record.suggested_tone) if record.suggested_tone else None,
            needs_human_review=record.needs_human_review,
            draft_reply=record.draft_reply,
            reasoning=record.reasoning,
            model_used=record.model_used,
            raw_ai_response=record.raw_ai_response,
            created_at=record.created_at,
        )

    @staticmethod
    def _build_routing_view(record: RoutingDecisionRecord | None) -> AdminRoutingView | None:
        if record is None:
            return None
        return AdminRoutingView(
            rule_id=record.rule_id,
            responsible_id=record.responsible_id,
            action=record.action,
            create_task=record.create_task,
            task_deadline_hours=record.task_deadline_hours,
            task_title=record.task_title,
            created_at=record.created_at,
        )

    @staticmethod
    def _build_bitrix_view(record: BitrixEntityRecord) -> AdminBitrixEntityView:
        return AdminBitrixEntityView(
            entity_type=record.entity_type,
            bitrix_id=record.bitrix_id,
            bitrix_url=record.bitrix_url,
            status=record.status,
            error_message=record.error_message,
            created_at=record.created_at,
        )

    @staticmethod
    def _build_log_view(record: ProcessingLogRecord) -> AdminLogView:
        return AdminLogView(
            event=record.event,
            status=_enum_value(record.status),
            details=record.details or "{}",
            created_at=record.created_at,
        )

    @staticmethod
    def _get_request_or_raise(session: Session, request_id: str) -> IntakeRequestRecord:
        record = session.scalar(
            select(IntakeRequestRecord)
            .where(IntakeRequestRecord.id == request_id)
            .options(
                selectinload(IntakeRequestRecord.ai_classifications),
                selectinload(IntakeRequestRecord.routing_decisions),
                selectinload(IntakeRequestRecord.bitrix_entities),
                selectinload(IntakeRequestRecord.processing_logs),
            )
        )
        if record is None:
            raise ValueError(f"Request not found: {request_id}")
        return record

    @staticmethod
    def _latest_classification(record: IntakeRequestRecord) -> AIClassificationRecord | None:
        if not record.ai_classifications:
            return None
        return sorted(record.ai_classifications, key=lambda item: (item.created_at, item.id))[-1]

    @staticmethod
    def _latest_routing(record: IntakeRequestRecord) -> RoutingDecisionRecord | None:
        if not record.routing_decisions:
            return None
        return sorted(record.routing_decisions, key=lambda item: (item.created_at, item.id))[-1]

    @staticmethod
    def _available_actions(status: RequestStatus) -> list[str]:
        actions: list[str] = []
        if status == RequestStatus.review_needed:
            actions.extend(["approve", "reprocess_ai", "drop"])
        elif status == RequestStatus.failed_retryable:
            actions.extend(["retry", "reprocess_ai", "drop"])
        elif status == RequestStatus.dropped:
            actions.append("reprocess_ai")
        else:
            actions.append("drop")
        return actions

    @staticmethod
    def _mask_setting(key: str, value: str) -> str:
        if not value:
            return ""
        if any(token in key.lower() for token in ("secret", "password", "key", "token")):
            return "[masked]"
        return value

    @staticmethod
    def _read_text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _mask_contact_value(value: str | None) -> str | None:
    if not value:
        return None
    return "[masked]"


def _mask_free_text(text: str | None) -> str:
    if not text:
        return ""
    masked = EMAIL_RE.sub("[masked email]", text)
    masked = PHONE_RE.sub("[masked phone]", masked)
    return masked


def _status_label(status: RequestStatus) -> str:
    mapping = {
        RequestStatus.received: "Received",
        RequestStatus.processing: "Processing",
        RequestStatus.classified: "Classified",
        RequestStatus.review_needed: "Review needed",
        RequestStatus.routed: "Routed",
        RequestStatus.bitrix_syncing: "Bitrix syncing",
        RequestStatus.completed: "Completed",
        RequestStatus.failed: "Failed",
        RequestStatus.failed_retryable: "Retryable failure",
        RequestStatus.dropped: "Dropped",
        RequestStatus.duplicate: "Duplicate",
    }
    return mapping[status]
