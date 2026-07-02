from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.config import Settings
from app.integrations.llm_client import MockLLMClient
from app.models.enums import AIClassificationCategory, AIClassificationPriority
from app.schemas.intake import IntakeRequestCreate
from app.services.ai_classifier import AIClassifier


def build_request(message: str) -> IntakeRequestCreate:
    return IntakeRequestCreate(
        idempotency_key="site-form-20260703-0101",
        source="web_form",
        name="Ivan Petrov",
        email="ivan.petrov@example.com",
        phone="+37360000000",
        company="OOO Romashka",
        message=message,
    )


def test_mock_classifier_is_deterministic():
    classifier = AIClassifier(
        settings=Settings(ai_provider="mock", confidence_threshold=0.75),
        client=MockLLMClient(),
    )
    request = build_request("Need Bitrix24 and 1C integration for our team")

    first = classifier.classify(request)
    second = classifier.classify(request)

    assert first == second
    assert first.category == AIClassificationCategory.integration_1c.value
    assert first.priority == AIClassificationPriority.high.value
    assert first.needs_human_review is False
    assert first.confidence >= 0.75


def test_invalid_output_falls_back_to_review():
    classifier = AIClassifier(
        settings=Settings(ai_provider="mock", confidence_threshold=0.75),
        client=InvalidJsonClient(),
    )
    request = build_request("Need Bitrix24 and 1C integration for our team")

    result = classifier.classify(request)

    assert result.needs_human_review is True
    assert result.confidence == 0.0
    assert result.category == AIClassificationCategory.integration_1c.value
    assert result.priority == AIClassificationPriority.high.value
    assert result.reasoning.startswith("AI response fallback")


def test_low_confidence_valid_output_is_routed_to_review():
    classifier = AIClassifier(
        settings=Settings(ai_provider="mock", confidence_threshold=0.75),
        client=LowConfidenceClient(),
    )
    request = build_request("We need something, maybe automation, maybe CRM, not sure")

    result = classifier.classify(request)

    assert result.category == AIClassificationCategory.other.value
    assert result.needs_human_review is True
    assert result.confidence == pytest.approx(0.42)


def test_valid_provider_output_is_accepted():
    classifier = AIClassifier(
        settings=Settings(ai_provider="mock", confidence_threshold=0.75),
        client=ValidJsonClient(),
    )
    request = build_request("Need general CRM help")

    result = classifier.classify(request)

    assert result.category == AIClassificationCategory.crm_implementation.value
    assert result.confidence == pytest.approx(0.91)
    assert result.needs_human_review is False


@dataclass(slots=True)
class InvalidJsonClient:
    provider_name: str = "invalid-json"

    def classify(self, intake_request: IntakeRequestCreate, *, response_schema: dict) -> str:
        return "{not-json"


@dataclass(slots=True)
class LowConfidenceClient:
    provider_name: str = "low-confidence"

    def classify(self, intake_request: IntakeRequestCreate, *, response_schema: dict) -> str:
        return (
            '{"category":"other","priority":"low","confidence":0.42,'
            '"intent":"Unclear request","summary":"The request is unclear.",'
            '"contact":{"name":null,"email":null,"phone":null,"company":null},'
            '"product_interest":null,"suggested_tone":"formal",'
            '"draft_reply":"Thanks for your message.","reasoning":"Ambiguous request",'
            '"needs_human_review":false}'
        )


@dataclass(slots=True)
class ValidJsonClient:
    provider_name: str = "valid-json"

    def classify(self, intake_request: IntakeRequestCreate, *, response_schema: dict) -> str:
        return (
            '{"category":"crm_implementation","priority":"high","confidence":0.91,'
            '"intent":"Client wants Bitrix24 CRM implementation support.",'
            '"summary":"The client is asking about Bitrix24 CRM implementation.",'
            '"contact":{"name":"Ivan Petrov","email":"ivan.petrov@example.com",'
            '"phone":"+37360000000","company":"OOO Romashka"},'
            '"product_interest":"Bitrix24 CRM","suggested_tone":"formal",'
            '"draft_reply":"Good day. Thank you for your message. We will review the request and get back with the next steps.",'
            '"reasoning":"High confidence CRM implementation request.","needs_human_review":false}'
        )
