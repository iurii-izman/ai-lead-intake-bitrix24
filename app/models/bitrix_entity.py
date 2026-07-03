"""Bitrix24 entity sync results for an intake request."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, new_uuid, utc_now_iso


class BitrixEntityRecord(Base):
    __tablename__ = "bitrix_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    intake_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("intake_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    bitrix_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bitrix_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utc_now_iso)

    intake_request = relationship("IntakeRequestRecord", back_populates="bitrix_entities")
