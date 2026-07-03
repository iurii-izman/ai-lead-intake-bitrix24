"""Provider clients for AI classification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request

from app.config import Settings
from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
)
from app.schemas.intake import IntakeRequestCreate


class LLMClientError(RuntimeError):
    """Raised when an AI provider cannot return a valid response."""


class LLMClient(Protocol):
    provider_name: str

    def classify(
        self,
        intake_request: IntakeRequestCreate,
        *,
        response_schema: dict[str, Any],
    ) -> str:
        """Return the raw provider response as JSON text."""


def build_llm_client(settings: Settings) -> LLMClient:
    provider = settings.ai_provider.lower()
    if provider == "mock":
        return MockLLMClient()
    if provider == "openai":
        return OpenAILLMClient(settings=settings)
    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")


@dataclass(slots=True)
class MockLLMClient:
    provider_name: str = "mock"

    def classify(
        self,
        intake_request: IntakeRequestCreate,
        *,
        response_schema: dict[str, Any],
    ) -> str:
        payload = self._build_classification(intake_request)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    def _build_classification(self, intake_request: IntakeRequestCreate) -> dict[str, Any]:
        text = _normalized_text(intake_request)
        category = _detect_category(text)
        priority = _detect_priority(text, category)
        confidence = _detect_confidence(text, category)
        contact = _extract_contact(intake_request)
        tone = _detect_tone(category, priority, text)
        intent = _build_intent(category, text)
        summary = _build_summary(category, text)
        draft_reply = _build_draft_reply(category, tone, intake_request)
        reasoning = _build_reasoning(category, priority, confidence)

        return {
            "category": category.value,
            "priority": priority.value,
            "confidence": confidence,
            "intent": intent,
            "summary": summary,
            "contact": contact,
            "product_interest": _detect_product_interest(text),
            "suggested_tone": tone.value,
            "draft_reply": draft_reply,
            "reasoning": reasoning,
            "needs_human_review": confidence < 0.75,
        }


@dataclass(slots=True)
class OpenAILLMClient:
    settings: Settings
    provider_name: str = "openai"

    def classify(
        self,
        intake_request: IntakeRequestCreate,
        *,
        response_schema: dict[str, Any],
    ) -> str:
        if not self.settings.openai_api_key:
            raise LLMClientError("OPENAI_API_KEY is not configured")

        payload = {
            "model": self.settings.openai_model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": _system_prompt(),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": _user_prompt(intake_request),
                        }
                    ],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "ai_classification",
                    "schema": response_schema,
                    "strict": True,
                }
            },
        }
        raw_response = self._post_json("/responses", payload)
        return _extract_json_text(raw_response)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.openai_base_url.rstrip('/')}{path}"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(
                http_request,
                timeout=self.settings.openai_timeout_seconds,
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise LLMClientError(f"OpenAI request failed with HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise LLMClientError(f"OpenAI request failed: {exc.reason}") from exc


def _system_prompt() -> str:
    return (
        "You classify incoming CRM requests into a strict JSON object that matches the schema. "
        "Extract only the information that is present in the request."
    )


def _user_prompt(intake_request: IntakeRequestCreate) -> str:
    contact_bits = [
        f"idempotency_key: {intake_request.idempotency_key}",
        f"source: {intake_request.source}",
        f"name: {intake_request.name or ''}",
        f"email: {intake_request.email or ''}",
        f"phone: {intake_request.phone or ''}",
        f"company: {intake_request.company or ''}",
        f"message: {intake_request.message}",
    ]
    return "\n".join(contact_bits)


def _extract_json_text(raw_response: dict[str, Any]) -> str:
    if isinstance(raw_response.get("output_text"), str) and raw_response["output_text"].strip():
        return raw_response["output_text"]

    output = raw_response.get("output", [])
    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if isinstance(text, str) and text.strip():
                    return text
            if content.get("type") == "text":
                text = content.get("text", "")
                if isinstance(text, str) and text.strip():
                    return text

    choices = raw_response.get("choices", [])
    for choice in choices:
        message = choice.get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content

    raise LLMClientError("OpenAI response did not contain JSON text")


def _normalized_text(intake_request: IntakeRequestCreate) -> str:
    parts = [
        intake_request.idempotency_key,
        intake_request.source,
        intake_request.name or "",
        intake_request.email or "",
        intake_request.phone or "",
        intake_request.company or "",
        intake_request.message,
    ]
    return " ".join(part.strip() for part in parts if part).lower()


def _detect_category(text: str) -> AIClassificationCategory:
    if any(keyword in text for keyword in ("спам", "spam", "unsubscribe", "buy now", "casino")):
        return AIClassificationCategory.spam
    if any(keyword in text for keyword in ("1c", "1с", "bitrix24 + 1c", "битрикс24 и 1с")):
        return AIClassificationCategory.integration_1c
    if any(
        keyword in text
        for keyword in ("crm", "внедрен", "внедрить crm", "bitrix24", "битрикс24")
    ):
        return AIClassificationCategory.crm_implementation
    if any(keyword in text for keyword in ("процесс", "workflow", "автоматизац", "бизнес-процесс")):
        return AIClassificationCategory.business_process_automation
    if any(keyword in text for keyword in ("ai", "llm", "gpt", "нейросет", "модель")):
        return AIClassificationCategory.ai_automation
    if any(keyword in text for keyword in ("партнер", "partner", "collaboration", "reseller")):
        return AIClassificationCategory.partnership
    if any(keyword in text for keyword in ("жалоб", "complaint", "недоволен", "problem")):
        return AIClassificationCategory.complaint
    if any(keyword in text for keyword in ("поддержк", "support", "help", "issue")):
        return AIClassificationCategory.support
    return AIClassificationCategory.other


def _detect_priority(text: str, category: AIClassificationCategory) -> AIClassificationPriority:
    if any(keyword in text for keyword in ("срочно", "urgent", "asap", "critical", "немедленно")):
        return AIClassificationPriority.critical
    if category in {AIClassificationCategory.complaint, AIClassificationCategory.spam}:
        return AIClassificationPriority.high
    if category in {
        AIClassificationCategory.crm_implementation,
        AIClassificationCategory.integration_1c,
        AIClassificationCategory.ai_automation,
    }:
        return AIClassificationPriority.high
    if category == AIClassificationCategory.business_process_automation:
        return AIClassificationPriority.medium
    return AIClassificationPriority.low


def _detect_confidence(text: str, category: AIClassificationCategory) -> float:
    if category == AIClassificationCategory.spam:
        return 0.98
    if category in {
        AIClassificationCategory.crm_implementation,
        AIClassificationCategory.integration_1c,
        AIClassificationCategory.ai_automation,
    }:
        if any(
            keyword in text
            for keyword in ("интеграц", "integration", "внедрен", "автоматизац")
        ):
            return 0.93
        return 0.82
    if category == AIClassificationCategory.business_process_automation:
        return 0.8
    if category in {
        AIClassificationCategory.complaint,
        AIClassificationCategory.support,
        AIClassificationCategory.partnership,
    }:
        return 0.77
    return 0.6


def _detect_product_interest(text: str) -> str | None:
    if "1c" in text or "1с" in text:
        return "Bitrix24 + 1C"
    if "bitrix24" in text or "битрикс24" in text:
        return "Bitrix24 CRM"
    if "ai" in text or "gpt" in text or "нейросет" in text:
        return "AI automation"
    return None


def _detect_tone(
    category: AIClassificationCategory,
    priority: AIClassificationPriority,
    text: str,
) -> AIClassificationTone:
    if (
        priority == AIClassificationPriority.critical
        or category == AIClassificationCategory.complaint
    ):
        return AIClassificationTone.urgent
    if any(keyword in text for keyword in ("спасибо", "thanks", "сотруднич", "partner")):
        return AIClassificationTone.friendly
    return AIClassificationTone.formal


def _extract_contact(intake_request: IntakeRequestCreate) -> dict[str, Any]:
    return {
        "name": intake_request.name,
        "email": intake_request.email,
        "phone": intake_request.phone,
        "company": intake_request.company,
    }


def _build_intent(category: AIClassificationCategory, text: str) -> str:
    if category == AIClassificationCategory.integration_1c:
        return "Client wants a Bitrix24 and 1C integration estimate."
    if category == AIClassificationCategory.crm_implementation:
        return "Client wants help with Bitrix24 CRM implementation."
    if category == AIClassificationCategory.business_process_automation:
        return "Client wants to automate a business process."
    if category == AIClassificationCategory.ai_automation:
        return "Client wants an AI automation solution for CRM intake."
    if category == AIClassificationCategory.complaint:
        return "Client is raising a complaint or service issue."
    if category == AIClassificationCategory.partnership:
        return "Client is asking about partnership or cooperation."
    if category == AIClassificationCategory.spam:
        return "Message appears to be spam or irrelevant."
    if category == AIClassificationCategory.support:
        return "Client needs support with an existing request."
    return "Client is making a general inquiry."


def _build_summary(category: AIClassificationCategory, text: str) -> str:
    if category == AIClassificationCategory.spam:
        return "Message looks like spam or irrelevant outreach."
    if category == AIClassificationCategory.integration_1c:
        return "The client is interested in a Bitrix24 and 1C integration."
    if category == AIClassificationCategory.crm_implementation:
        return "The client is asking about Bitrix24 CRM implementation."
    if category == AIClassificationCategory.business_process_automation:
        return "The client wants to automate a business process."
    if category == AIClassificationCategory.ai_automation:
        return "The client is asking about AI-driven automation for intake or CRM."
    return "The client is requesting follow-up on an incoming inquiry."


def _build_draft_reply(
    category: AIClassificationCategory,
    tone: AIClassificationTone,
    intake_request: IntakeRequestCreate,
) -> str:
    greeting = "Hello" if tone != AIClassificationTone.formal else "Good day"
    if category == AIClassificationCategory.spam:
        return "Thank you for reaching out. We will not proceed with this message."
    if category == AIClassificationCategory.integration_1c:
        return (
            f"{greeting}. Thank you for your request about Bitrix24 and 1C. "
            "We will review the details and get back with the next steps."
        )
    if category == AIClassificationCategory.crm_implementation:
        return (
            f"{greeting}. Thank you for your request. We will review your Bitrix24 CRM needs "
            "and follow up with the next steps."
        )
    if category == AIClassificationCategory.ai_automation:
        return (
            f"{greeting}. Thank you for the inquiry about AI automation. "
            "We will review the request and reply with an appropriate next step."
        )
    return (
        f"{greeting}. Thank you for your message. We will review the request and come back "
        "with a short update."
    )


def _build_reasoning(
    category: AIClassificationCategory,
    priority: AIClassificationPriority,
    confidence: float,
) -> str:
    return (
        f"Matched {category.value} with {priority.value} priority "
        f"at confidence {confidence:.2f}."
    )
