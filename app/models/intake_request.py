"""Queue record for an incoming lead intake request."""

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, new_uuid, utc_now_iso
from app.models.enums import RequestStatus


class IntakeRequestRecord(Base):
    __tablename__ = "intake_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_payload_masked: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus, native_enum=False, validate_strings=True, length=32),
        nullable=False,
        default=RequestStatus.received,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=utc_now_iso,
        onupdate=utc_now_iso,
    )

    ai_classifications = relationship(
        "AIClassificationRecord",
        back_populates="intake_request",
        cascade="all, delete-orphan",
    )
    routing_decisions = relationship(
        "RoutingDecisionRecord",
        back_populates="intake_request",
        cascade="all, delete-orphan",
    )
    bitrix_entities = relationship(
        "BitrixEntityRecord",
        back_populates="intake_request",
        cascade="all, delete-orphan",
    )
    processing_logs = relationship(
        "ProcessingLogRecord",
        back_populates="intake_request",
        cascade="all, delete-orphan",
    )
