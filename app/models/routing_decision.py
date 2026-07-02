"""Deterministic routing decisions for an intake request."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, new_uuid, utc_now_iso


class RoutingDecisionRecord(Base):
    __tablename__ = "routing_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    intake_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("intake_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    responsible_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    create_task: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    task_deadline_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    task_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utc_now_iso)

    intake_request = relationship("IntakeRequestRecord", back_populates="routing_decisions")
