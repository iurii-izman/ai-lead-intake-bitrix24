"""AI classifier service with provider abstraction and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.config import Settings, get_settings
from app.integrations.llm_client import LLMClient, build_llm_client
from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
)
from app.schemas.classification import AIClassification, ExtractedContact
from app.schemas.intake import IntakeRequestCreate


@dataclass(slots=True)
class AIClassificationResult:
    classification: AIClassification
    provider_name: str
    raw_response: str


class AIClassifier:
    def __init__(
        self,
        settings: Settings | None = None,
        client: LLMClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client or build_llm_client(self.settings)
        self.response_schema = AIClassification.model_json_schema()

    def classify(self, intake_request: IntakeRequestCreate) -> AIClassification:
        return self._classify_or_fallback(intake_request).classification

    def classify_with_metadata(self, intake_request: IntakeRequestCreate) -> AIClassificationResult:
        return self._classify_or_fallback(intake_request)

    def _classify_or_fallback(self, intake_request: IntakeRequestCreate) -> AIClassificationResult:
        try:
            raw_response = self.client.classify(intake_request, response_schema=self.response_schema)
            classification = self._validate_raw_output(raw_response)
            classification = self._apply_review_gate(classification)
        except Exception as exc:  # noqa: BLE001
            fallback = self._fallback_classification(
                intake_request,
                reason=f"AI response fallback: {exc.__class__.__name__}",
            )
            raw_response = fallback.model_dump_json()
            classification = fallback

        return AIClassificationResult(
            classification=classification,
            provider_name=self.client.provider_name,
            raw_response=raw_response,
        )

    def _validate_raw_output(self, raw_response: str) -> AIClassification:
        parsed = json.loads(raw_response)
        return AIClassification.model_validate(parsed)

    def _apply_review_gate(self, classification: AIClassification) -> AIClassification:
        if classification.confidence < self.settings.confidence_threshold:
            return classification.model_copy(update={"needs_human_review": True})
        if classification.needs_human_review:
            return classification
        return classification

    def _fallback_classification(
        self,
        intake_request: IntakeRequestCreate,
        *,
        reason: str,
    ) -> AIClassification:
        mock_payload = _fallback_payload(intake_request, reason=reason)
        return AIClassification.model_validate(mock_payload)


def _fallback_payload(intake_request: IntakeRequestCreate, *, reason: str) -> dict[str, Any]:
    normalized = " ".join(
        part
        for part in (
            intake_request.idempotency_key,
            intake_request.source,
            intake_request.name or "",
            intake_request.email or "",
            intake_request.phone or "",
            intake_request.company or "",
            intake_request.message,
        )
        if part
    ).lower()

    category = _detect_category(normalized)
    priority = _detect_priority(normalized, category)
    contact = ExtractedContact(
        name=intake_request.name,
        email=intake_request.email,
        phone=intake_request.phone,
        company=intake_request.company,
    )
    tone = _detect_tone(category, priority)

    return {
        "category": category.value,
        "priority": priority.value,
        "confidence": 0.0,
        "intent": _build_intent(category),
        "summary": _build_summary(category),
        "contact": contact.model_dump(mode="json"),
        "product_interest": _detect_product_interest(normalized),
        "suggested_tone": tone.value,
        "draft_reply": _build_draft_reply(category, tone),
        "reasoning": reason,
        "needs_human_review": True,
    }


def _detect_category(text: str) -> AIClassificationCategory:
    if any(keyword in text for keyword in ("spam", "спам", "unsubscribe", "casino")):
        return AIClassificationCategory.spam
    if any(keyword in text for keyword in ("1c", "1с", "битрикс24 и 1с", "bitrix24 + 1c")):
        return AIClassificationCategory.integration_1c
    if any(keyword in text for keyword in ("crm", "битрикс24", "bitrix24")):
        return AIClassificationCategory.crm_implementation
    if any(keyword in text for keyword in ("process", "процесс", "workflow", "автоматизац")):
        return AIClassificationCategory.business_process_automation
    if any(keyword in text for keyword in ("ai", "gpt", "llm", "нейросет")):
        return AIClassificationCategory.ai_automation
    if any(keyword in text for keyword in ("complaint", "жалоб", "problem", "недоволен")):
        return AIClassificationCategory.complaint
    if any(keyword in text for keyword in ("partner", "partnership", "сотруднич", "reseller")):
        return AIClassificationCategory.partnership
    if any(keyword in text for keyword in ("support", "поддержк", "help")):
        return AIClassificationCategory.support
    return AIClassificationCategory.other


def _detect_priority(text: str, category: AIClassificationCategory) -> AIClassificationPriority:
    if any(keyword in text for keyword in ("urgent", "срочно", "asap", "critical")):
        return AIClassificationPriority.critical
    if category in {
        AIClassificationCategory.complaint,
        AIClassificationCategory.crm_implementation,
        AIClassificationCategory.integration_1c,
        AIClassificationCategory.ai_automation,
    }:
        return AIClassificationPriority.high
    if category == AIClassificationCategory.business_process_automation:
        return AIClassificationPriority.medium
    return AIClassificationPriority.low


def _detect_tone(category: AIClassificationCategory, priority: AIClassificationPriority) -> AIClassificationTone:
    if priority == AIClassificationPriority.critical or category == AIClassificationCategory.complaint:
        return AIClassificationTone.urgent
    if category == AIClassificationCategory.partnership:
        return AIClassificationTone.friendly
    return AIClassificationTone.formal


def _detect_product_interest(text: str) -> str | None:
    if "1c" in text or "1с" in text:
        return "Bitrix24 + 1C"
    if "bitrix24" in text or "битрикс24" in text:
        return "Bitrix24 CRM"
    if "ai" in text or "gpt" in text or "нейросет" in text:
        return "AI automation"
    return None


def _build_intent(category: AIClassificationCategory) -> str:
    mapping = {
        AIClassificationCategory.crm_implementation: "Client wants Bitrix24 CRM implementation support.",
        AIClassificationCategory.integration_1c: "Client wants a Bitrix24 and 1C integration estimate.",
        AIClassificationCategory.business_process_automation: "Client wants business process automation.",
        AIClassificationCategory.ai_automation: "Client wants AI automation for CRM intake.",
        AIClassificationCategory.support: "Client needs support for an existing request.",
        AIClassificationCategory.partnership: "Client is asking about a partnership or cooperation.",
        AIClassificationCategory.complaint: "Client is raising a complaint or issue.",
        AIClassificationCategory.spam: "Message appears to be spam or irrelevant.",
        AIClassificationCategory.other: "Client is making a general inquiry.",
    }
    return mapping[category]


def _build_summary(category: AIClassificationCategory) -> str:
    mapping = {
        AIClassificationCategory.crm_implementation: "The client is asking about Bitrix24 CRM implementation.",
        AIClassificationCategory.integration_1c: "The client is interested in Bitrix24 and 1C integration.",
        AIClassificationCategory.business_process_automation: "The client wants to automate a business process.",
        AIClassificationCategory.ai_automation: "The client is asking about AI-driven automation.",
        AIClassificationCategory.support: "The client needs support with a request or setup.",
        AIClassificationCategory.partnership: "The client is interested in a partnership or cooperation.",
        AIClassificationCategory.complaint: "The client is reporting a complaint or issue.",
        AIClassificationCategory.spam: "The message appears to be spam or irrelevant.",
        AIClassificationCategory.other: "The request is general and needs human review.",
    }
    return mapping[category]


def _build_draft_reply(category: AIClassificationCategory, tone: AIClassificationTone) -> str:
    greeting = "Hello" if tone != AIClassificationTone.formal else "Good day"
    if category == AIClassificationCategory.spam:
        return "Thank you for your message. We will not proceed with this request."
    return (
        f"{greeting}. Thank you for your message. We will review the request and get back "
        "with the next steps."
    )
