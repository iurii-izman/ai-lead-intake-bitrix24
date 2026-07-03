from __future__ import annotations

from pathlib import Path

import pytest

from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
)
from app.schemas.classification import AIClassification, ExtractedContact
from app.services.routing_engine import RoutingEngine


def build_classification(
    *,
    category: AIClassificationCategory,
    priority: AIClassificationPriority,
    confidence: float = 0.91,
    intent: str = "Client wants help with the request.",
    needs_human_review: bool = False,
) -> AIClassification:
    return AIClassification(
        category=category,
        priority=priority,
        confidence=confidence,
        intent=intent,
        summary="Summary",
        contact=ExtractedContact(),
        product_interest=None,
        suggested_tone=AIClassificationTone.formal,
        draft_reply="Thanks for the request.",
        reasoning="Reasoning",
        needs_human_review=needs_human_review,
    )


def test_routing_critical_complaint_rule_wins_before_fallback():
    engine = RoutingEngine.from_file()
    classification = build_classification(
        category=AIClassificationCategory.complaint,
        priority=AIClassificationPriority.critical,
        intent="Urgent complaint about failed delivery",
    )

    decision = engine.route(classification)

    assert decision.rule_id == "critical_complaint"
    assert decision.action == "route"
    assert decision.responsible_id == 1
    assert decision.create_task is True
    assert decision.task_deadline_hours == 1
    assert decision.task_title == "⚠️ Срочная жалоба: Urgent complaint about failed delivery"


def test_routing_fallback_handles_unknown_category():
    engine = RoutingEngine.from_file()
    classification = build_classification(
        category=AIClassificationCategory.other,
        priority=AIClassificationPriority.low,
        intent="Need an initial consultation",
    )

    decision = engine.route(classification)

    assert decision.rule_id == "fallback"
    assert decision.action == "route"
    assert decision.responsible_id == 1
    assert decision.create_task is True
    assert decision.task_deadline_hours == 24
    assert decision.task_title == "Новая заявка: Need an initial consultation"


def test_routing_spam_category_is_dropped():
    engine = RoutingEngine.from_file()
    classification = build_classification(
        category=AIClassificationCategory.spam,
        priority=AIClassificationPriority.low,
        intent="Buy followers now",
    )

    decision = engine.route(classification)

    assert decision.rule_id == "spam"
    assert decision.action == "drop"
    assert decision.responsible_id is None
    assert decision.create_task is False
    assert decision.task_title is None


def test_routing_low_confidence_goes_to_review():
    engine = RoutingEngine.from_file()
    classification = build_classification(
        category=AIClassificationCategory.crm_implementation,
        priority=AIClassificationPriority.high,
        confidence=0.42,
        intent="Need CRM setup but details are unclear",
    )

    decision = engine.route(classification)

    assert decision.rule_id == "human_review_gate"
    assert decision.action == "review"
    assert decision.responsible_id == 1
    assert decision.create_task is True
    assert decision.task_deadline_hours == 24
    assert decision.task_title == "Ручная проверка: Need CRM setup but details are unclear"


def test_routing_needs_human_review_goes_to_review():
    engine = RoutingEngine.from_file()
    classification = build_classification(
        category=AIClassificationCategory.support,
        priority=AIClassificationPriority.medium,
        confidence=0.91,
        needs_human_review=True,
        intent="Please review this request manually",
    )

    decision = engine.route(classification)

    assert decision.rule_id == "human_review_gate"
    assert decision.action == "review"


def test_routing_engine_rejects_invalid_config(tmp_path: Path):
    config_path = tmp_path / "routing.yaml"
    config_path.write_text(
        """
defaults:
  confidence_threshold: 0.75
rules:
  - id: broken
    conditions:
      category: support
      unknown_field: true
    action:
      responsible_id: 1
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid routing config"):
        RoutingEngine.from_file(config_path)
