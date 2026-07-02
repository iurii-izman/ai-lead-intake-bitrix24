"""Service layer for Bitrix24 synchronization."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.integrations.bitrix24_client import (
    Bitrix24Client,
    BitrixCallResult,
    BitrixClientError,
    BitrixConfigurationError,
    BitrixRequestError,
    BitrixRetryableError,
    build_bitrix24_client,
)
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.enums import AIClassificationPriority, RequestStatus
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.schemas.bitrix import BitrixEntityResult
from app.schemas.classification import AIClassification
from app.schemas.routing import RoutingDecision

DEFAULT_FIELD_MAPPING_PATH = Path(__file__).resolve().parents[2] / "config" / "field_mapping.yaml"


class BitrixMappingError(ValueError):
    """Raised when the YAML field mapping cannot be loaded."""


class BitrixServiceError(RuntimeError):
    """Raised when Bitrix24 synchronization fails in a predictable way."""


class BitrixModeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_type_id: int | None = None
    fields: dict[str, str] = Field(default_factory=dict)


class FieldMappingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    universal: BitrixModeConfig
    legacy: BitrixModeConfig


@dataclass(slots=True, frozen=True)
class BitrixFieldMapping:
    universal: BitrixModeConfig
    legacy: BitrixModeConfig

    @classmethod
    def from_file(cls, path: Path | str = DEFAULT_FIELD_MAPPING_PATH) -> "BitrixFieldMapping":
        config_path = Path(path)
        if not config_path.exists():
            raise BitrixMappingError(f"Bitrix field mapping not found: {config_path}")

        try:
            raw_config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            mapping = FieldMappingConfig.model_validate(raw_config["bitrix"])
        except (OSError, KeyError, TypeError, ValidationError, yaml.YAMLError) as exc:
            raise BitrixMappingError(f"Invalid Bitrix field mapping: {config_path}") from exc

        return cls(universal=mapping.universal, legacy=mapping.legacy)


@dataclass(slots=True)
class BitrixService:
    settings: Settings
    client: Bitrix24Client
    field_mapping: BitrixFieldMapping

    def __init__(
        self,
        settings: Settings | None = None,
        client: Bitrix24Client | None = None,
        field_mapping: BitrixFieldMapping | None = None,
        field_mapping_path: Path | str = DEFAULT_FIELD_MAPPING_PATH,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client or build_bitrix24_client(self.settings)
        self.field_mapping = field_mapping or BitrixFieldMapping.from_file(field_mapping_path)

    async def sync_approved_outcome(
        self,
        session: Session,
        intake_request: IntakeRequestRecord,
        classification: AIClassification,
        routing_decision: RoutingDecision,
        *,
        allow_human_override: bool = False,
    ) -> list[BitrixEntityResult]:
        if routing_decision.action != "route":
            raise BitrixServiceError(
                f"Cannot sync Bitrix entities for action={routing_decision.action}"
            )

        if not allow_human_override and (
            classification.needs_human_review
            or classification.confidence < self.settings.confidence_threshold
        ):
            raise BitrixServiceError("Cannot sync a request that still requires human review")

        results: list[BitrixEntityResult] = []
        crm_mode = self.settings.bitrix_crm_mode.lower()
        if crm_mode not in {"universal", "legacy"}:
            raise BitrixServiceError(
                f"Unsupported Bitrix CRM mode: {self.settings.bitrix_crm_mode}"
            )

        crm_entity_type = "crm.item" if crm_mode == "universal" else "crm.lead"
        crm_existing = self._existing_successful_entity(session, intake_request.id, crm_entity_type)
        if crm_existing is not None:
            results.append(self._record_to_result(crm_existing))
        else:
            self._log(
                session,
                intake_request.id,
                event="bitrix_syncing",
                status=RequestStatus.bitrix_syncing,
                details={
                    "entity_type": crm_entity_type,
                    "mode": crm_mode,
                },
            )
            crm_payload = self._build_crm_payload(intake_request, classification, routing_decision)
            try:
                crm_result = await self._create_crm_entity(crm_payload)
            except BitrixConfigurationError:
                self._log(
                    session,
                    intake_request.id,
                    event="bitrix_failed",
                    status=RequestStatus.failed,
                    details={
                        "entity_type": crm_entity_type,
                        "mode": crm_mode,
                        "error": "configuration",
                    },
                )
                session.commit()
                raise
            except BitrixRequestError:
                self._log(
                    session,
                    intake_request.id,
                    event="bitrix_failed",
                    status=RequestStatus.failed,
                    details={
                        "entity_type": crm_entity_type,
                        "mode": crm_mode,
                        "error": "request",
                    },
                )
                session.commit()
                raise
            except (BitrixRetryableError, BitrixClientError):
                self._log(
                    session,
                    intake_request.id,
                    event="bitrix_failed",
                    status=RequestStatus.failed_retryable,
                    details={
                        "entity_type": crm_entity_type,
                        "mode": crm_mode,
                    },
                )
                session.commit()
                raise

            crm_record = self._persist_entity(
                session,
                intake_request.id,
                entity_type=crm_entity_type,
                result=crm_result,
            )
            self._log(
                session,
                intake_request.id,
                event="bitrix_lead_created",
                status=RequestStatus.bitrix_syncing,
                details={
                    "entity_type": crm_entity_type,
                    "bitrix_id": crm_record.bitrix_id,
                },
            )
            session.commit()
            results.append(self._record_to_result(crm_record))

        if not routing_decision.create_task:
            return results

        task_existing = self._existing_successful_entity(session, intake_request.id, "task")
        if task_existing is not None:
            results.append(self._record_to_result(task_existing))
            return results

        task_payload = self._build_task_payload(
            intake_request,
            classification,
            routing_decision,
            crm_bitrix_id=results[0].bitrix_id,
        )
        try:
            task_result = await self.client.create_task(task_payload)
        except BitrixConfigurationError:
            self._log(
                session,
                intake_request.id,
                event="bitrix_failed",
                status=RequestStatus.failed,
                details={
                    "entity_type": "task",
                    "error": "configuration",
                },
            )
            session.commit()
            raise
        except BitrixRequestError:
            self._log(
                session,
                intake_request.id,
                event="bitrix_failed",
                status=RequestStatus.failed,
                details={
                    "entity_type": "task",
                    "error": "request",
                },
            )
            session.commit()
            raise
        except (BitrixRetryableError, BitrixClientError):
            self._log(
                session,
                intake_request.id,
                event="bitrix_failed",
                status=RequestStatus.failed_retryable,
                details={
                    "entity_type": "task",
                },
            )
            session.commit()
            raise

        task_record = self._persist_entity(
            session,
            intake_request.id,
            entity_type="task",
            result=task_result,
        )
        self._log(
            session,
            intake_request.id,
            event="bitrix_task_created",
            status=RequestStatus.bitrix_syncing,
            details={
                "entity_type": "task",
                "bitrix_id": task_record.bitrix_id,
            },
        )
        session.commit()
        results.append(self._record_to_result(task_record))
        return results

    async def _create_crm_entity(self, payload: dict[str, Any]) -> BitrixCallResult:
        crm_mode = self.settings.bitrix_crm_mode.lower()
        if crm_mode == "universal":
            return await self.client.create_crm_item(payload)
        if crm_mode == "legacy":
            return await self.client.create_lead(payload)
        raise BitrixServiceError(f"Unsupported Bitrix CRM mode: {self.settings.bitrix_crm_mode}")

    def _build_crm_payload(
        self,
        intake_request: IntakeRequestRecord,
        classification: AIClassification,
        routing_decision: RoutingDecision,
    ) -> dict[str, Any]:
        mapping = self._mapping_for_mode()
        comments = _build_comments(intake_request, classification)
        title = f"[AI Intake] {classification.intent}"
        source_id = "WEB"
        responsible_id = routing_decision.responsible_id or 1

        if self.settings.bitrix_crm_mode.lower() == "universal":
            return {
                "entityTypeId": mapping.entity_type_id or 1,
                "fields": {
                    mapping.fields["title"]: title,
                    mapping.fields["name"]: classification.contact.name or "",
                    mapping.fields["company"]: classification.contact.company or "",
                    mapping.fields["source_id"]: source_id,
                    mapping.fields["source_description"]: "AI Lead Intake",
                    mapping.fields["assigned_by_id"]: responsible_id,
                    mapping.fields["comments"]: comments,
                    mapping.fields["ai_category"]: classification.category,
                    mapping.fields["ai_confidence"]: str(classification.confidence),
                    mapping.fields["intake_id"]: intake_request.id,
                },
            }

        fields = {
            mapping.fields["title"]: title,
            mapping.fields["name"]: classification.contact.name or "",
            mapping.fields["company"]: classification.contact.company or "",
            mapping.fields["source_id"]: source_id,
            mapping.fields["assigned_by_id"]: responsible_id,
            mapping.fields["comments"]: comments,
            mapping.fields["ai_category"]: classification.category,
            mapping.fields["ai_confidence"]: str(classification.confidence),
            mapping.fields["intake_id"]: intake_request.id,
        }
        if classification.contact.phone:
            fields[mapping.fields["phone"]] = [
                {"VALUE": classification.contact.phone, "VALUE_TYPE": "WORK"}
            ]
        if classification.contact.email:
            fields[mapping.fields["email"]] = [
                {"VALUE": classification.contact.email, "VALUE_TYPE": "WORK"}
            ]
        return {"fields": fields}

    def _build_task_payload(
        self,
        intake_request: IntakeRequestRecord,
        classification: AIClassification,
        routing_decision: RoutingDecision,
        *,
        crm_bitrix_id: int,
    ) -> dict[str, Any]:
        deadline_hours = routing_decision.task_deadline_hours or 24
        deadline = datetime.now(UTC) + timedelta(hours=deadline_hours)
        priority = (
            "2"
            if classification.priority
            in {AIClassificationPriority.high, AIClassificationPriority.critical}
            else "1"
        )
        return {
            "fields": {
                "TITLE": routing_decision.task_title or f"Новая заявка: {classification.intent}",
                "RESPONSIBLE_ID": routing_decision.responsible_id or 1,
                "DEADLINE": deadline.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "DESCRIPTION": _build_task_description(intake_request, classification),
                "UF_CRM_TASK": [f"L_{crm_bitrix_id}"],
                "PRIORITY": priority,
            }
        }

    def _persist_entity(
        self,
        session: Session,
        intake_id: str,
        *,
        entity_type: str,
        result: BitrixCallResult,
    ) -> BitrixEntityRecord:
        record = BitrixEntityRecord(
            intake_id=intake_id,
            entity_type=entity_type,
            bitrix_id=result.bitrix_id,
            bitrix_url=result.bitrix_url,
            status="created",
            error_message=None,
        )
        session.add(record)
        session.flush()
        return record

    def _existing_successful_entity(
        self,
        session: Session,
        intake_id: str,
        entity_type: str,
    ) -> BitrixEntityRecord | None:
        return session.scalar(
            select(BitrixEntityRecord).where(
                BitrixEntityRecord.intake_id == intake_id,
                BitrixEntityRecord.entity_type == entity_type,
                BitrixEntityRecord.status == "created",
                BitrixEntityRecord.bitrix_id.is_not(None),
            )
        )

    def _record_to_result(self, record: BitrixEntityRecord) -> BitrixEntityResult:
        return BitrixEntityResult(
            entity_type=record.entity_type,
            bitrix_id=record.bitrix_id,
            bitrix_url=record.bitrix_url,
            status=record.status,
            error_message=record.error_message,
        )

    def _mapping_for_mode(self) -> BitrixModeConfig:
        crm_mode = self.settings.bitrix_crm_mode.lower()
        if crm_mode == "universal":
            return self.field_mapping.universal
        if crm_mode == "legacy":
            return self.field_mapping.legacy
        raise BitrixServiceError(f"Unsupported Bitrix CRM mode: {self.settings.bitrix_crm_mode}")

    @staticmethod
    def _log(
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


def _build_comments(intake_request: IntakeRequestRecord, classification: AIClassification) -> str:
    return "\n".join(
        [
            f"Категория: {classification.category}",
            f"Приоритет: {classification.priority}",
            f"Confidence: {classification.confidence:.2f}",
            "",
            "Summary:",
            classification.summary,
            "",
            "AI Draft Reply:",
            classification.draft_reply,
            "",
            f"Intake ID: {intake_request.id}",
        ]
    )


def _build_task_description(
    intake_request: IntakeRequestRecord, classification: AIClassification
) -> str:
    return "\n".join(
        [
            "AI Lead Intake создал задачу по новой заявке.",
            "",
            f"Категория: {classification.category}",
            f"Приоритет: {classification.priority}",
            f"Intent: {classification.intent}",
            "",
            "Черновик ответа:",
            classification.draft_reply,
            "",
            f"Intake ID: {intake_request.id}",
        ]
    )
