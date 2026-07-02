"""Timeline log entry for request processing."""

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, new_uuid, utc_now_iso
from app.models.enums import RequestStatus


class ProcessingLogRecord(Base):
    __tablename__ = "processing_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    intake_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("intake_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus, native_enum=False, validate_strings=True, length=32),
        nullable=False,
        index=True,
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utc_now_iso)

    intake_request = relationship("IntakeRequestRecord", back_populates="processing_logs")
