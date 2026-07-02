"""AI classification schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
)


class ExtractedContact(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None


class AIClassification(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    category: AIClassificationCategory
    priority: AIClassificationPriority
    confidence: float = Field(ge=0.0, le=1.0)
    intent: str = Field(description="Краткое описание намерения клиента")
    summary: str = Field(description="Суть обращения в 1-2 предложениях")
    contact: ExtractedContact
    product_interest: str | None = None
    suggested_tone: AIClassificationTone
    draft_reply: str = Field(
        description="Черновик первого ответа клиенту. Не отправляется автоматически."
    )
    reasoning: str = Field(description="Краткое объяснение категории, приоритета и confidence")
    needs_human_review: bool
