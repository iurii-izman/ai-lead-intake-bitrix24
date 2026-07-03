"""Deterministic routing rules for AI classification output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.models.enums import AIClassificationCategory, AIClassificationPriority
from app.schemas.classification import AIClassification
from app.schemas.routing import RoutingDecision

DEFAULT_ROUTING_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "routing.yaml"


class RoutingConfigError(ValueError):
    """Raised when routing configuration cannot be loaded or validated."""


class RoutingRuleConditions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: AIClassificationCategory | None = None
    priority: list[AIClassificationPriority] | None = None

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        raise ValueError("priority must be a string or a list of strings")


class RoutingRuleAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    responsible_id: int | None = None
    create_task: bool = True
    task_deadline_hours: int | None = None
    task_title: str | None = None
    drop: bool = False


class RoutingRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    conditions: RoutingRuleConditions = Field(default_factory=RoutingRuleConditions)
    action: RoutingRuleAction


class RoutingDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    default_responsible_id: int = 1
    review_responsible_id: int = 1
    task_deadline_hours: int = Field(default=24, ge=1)


class RoutingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    defaults: RoutingDefaults = Field(default_factory=RoutingDefaults)
    rules: list[RoutingRule] = Field(default_factory=list)


@dataclass(slots=True, frozen=True)
class RoutingEngine:
    """Evaluate routing rules in a deterministic top-down order."""

    config: RoutingConfig

    @classmethod
    def from_file(cls, config_path: Path | str = DEFAULT_ROUTING_CONFIG_PATH) -> RoutingEngine:
        path = Path(config_path)
        if not path.exists():
            raise RoutingConfigError(f"Routing config not found: {path}")

        try:
            raw_config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            config = RoutingConfig.model_validate(raw_config)
        except (OSError, yaml.YAMLError, ValidationError) as exc:
            raise RoutingConfigError(f"Invalid routing config: {path}") from exc

        return cls(config=config)

    def route(self, classification: AIClassification) -> RoutingDecision:
        if self._needs_human_review(classification):
            return RoutingDecision(
                rule_id="human_review_gate",
                responsible_id=self.config.defaults.review_responsible_id,
                action="review",
                create_task=True,
                task_deadline_hours=self.config.defaults.task_deadline_hours,
                task_title=self._format_template(
                    "Ручная проверка: {intent}",
                    classification.intent,
                ),
            )

        for rule in self.config.rules:
            if self._matches(rule.conditions, classification):
                return self._decision_from_rule(rule, classification)

        return self._fallback_decision(classification)

    def _decision_from_rule(
        self,
        rule: RoutingRule,
        classification: AIClassification,
    ) -> RoutingDecision:
        action = rule.action
        if action.drop:
            return RoutingDecision(
                rule_id=rule.id,
                responsible_id=None,
                action="drop",
                create_task=False,
                task_deadline_hours=None,
                task_title=None,
            )

        return RoutingDecision(
            rule_id=rule.id,
            responsible_id=(
                action.responsible_id
                if action.responsible_id is not None
                else self.config.defaults.default_responsible_id
            ),
            action="route",
            create_task=action.create_task,
            task_deadline_hours=action.task_deadline_hours
            or self.config.defaults.task_deadline_hours,
            task_title=self._format_template(action.task_title, classification.intent)
            if action.task_title
            else None,
        )

    def _fallback_decision(self, classification: AIClassification) -> RoutingDecision:
        fallback_rule = next(
            (
                rule
                for rule in self.config.rules
                if rule.conditions.category is None and not rule.conditions.priority
            ),
            None,
        )
        if fallback_rule is not None:
            return self._decision_from_rule(fallback_rule, classification)

        return RoutingDecision(
            rule_id="fallback",
            responsible_id=self.config.defaults.default_responsible_id,
            action="route",
            create_task=True,
            task_deadline_hours=self.config.defaults.task_deadline_hours,
            task_title=self._format_template("Новая заявка: {intent}", classification.intent),
        )

    def _matches(self, conditions: RoutingRuleConditions, classification: AIClassification) -> bool:
        if conditions.category is not None and conditions.category != classification.category:
            return False

        if conditions.priority and classification.priority not in conditions.priority:
            return False

        return True

    def _needs_human_review(self, classification: AIClassification) -> bool:
        return bool(
            classification.needs_human_review
            or classification.confidence < self.config.defaults.confidence_threshold
        )

    @staticmethod
    def _format_template(template: str | None, intent: str) -> str | None:
        if template is None:
            return None

        safe_intent = intent or ""
        return template.format(intent=safe_intent)


def load_default_routing_engine() -> RoutingEngine:
    """Load routing rules from the repository config directory."""

    return RoutingEngine.from_file(DEFAULT_ROUTING_CONFIG_PATH)
