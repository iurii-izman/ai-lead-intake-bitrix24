"""Intake request schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import RequestStatus


class IntakeRequestCreate(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=255)
    source: str = Field(min_length=1, max_length=100)
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    company: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=1, max_length=10_000)
    utm_source: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must not be blank")
        return cleaned


class IntakeRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: str
    idempotency_key: str
    source: str
    status: RequestStatus
    raw_payload_masked: str
    raw_text: str
    error_message: str | None = None
    retry_count: int = 0
    created_at: str
    updated_at: str
