"""Bitrix24 sync result schemas."""

from pydantic import BaseModel, ConfigDict


class BitrixEntityResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_type: str
    bitrix_id: int | None = None
    bitrix_url: str | None = None
    status: str
    error_message: str | None = None
