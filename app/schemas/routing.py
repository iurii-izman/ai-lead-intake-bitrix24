"""Routing decision schemas."""

from pydantic import BaseModel, ConfigDict


class RoutingDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: str | None = None
    responsible_id: int | None = None
    action: str | None = None
    create_task: bool | None = None
    task_deadline_hours: int | None = None
    task_title: str | None = None
