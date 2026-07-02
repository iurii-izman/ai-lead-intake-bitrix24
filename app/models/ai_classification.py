"""AI classification results for an intake request."""

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, new_uuid, utc_now_iso
from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
)


class AIClassificationRecord(Base):
    __tablename__ = "ai_classifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    intake_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("intake_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[AIClassificationCategory | None] = mapped_column(
        SAEnum(AIClassificationCategory, native_enum=False, validate_strings=True, length=64),
        nullable=True,
    )
    priority: Mapped[AIClassificationPriority | None] = mapped_column(
        SAEnum(AIClassificationPriority, native_enum=False, validate_strings=True, length=32),
        nullable=True,
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    intent: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email_masked: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone_masked: Mapped[str | None] = mapped_column(String(64), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_interest: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suggested_tone: Mapped[AIClassificationTone | None] = mapped_column(
        SAEnum(AIClassificationTone, native_enum=False, validate_strings=True, length=32),
        nullable=True,
    )
    needs_human_review: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    draft_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utc_now_iso)

    intake_request = relationship("IntakeRequestRecord", back_populates="ai_classifications")
