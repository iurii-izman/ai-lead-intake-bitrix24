"""Pydantic schemas for the AI Lead Intake domain."""

from app.schemas.bitrix import BitrixEntityResult
from app.schemas.classification import AIClassification, ExtractedContact
from app.schemas.intake import IntakeRequestCreate, IntakeRequestResponse
from app.schemas.routing import RoutingDecision

__all__ = [
    "AIClassification",
    "BitrixEntityResult",
    "ExtractedContact",
    "IntakeRequestCreate",
    "IntakeRequestResponse",
    "RoutingDecision",
]
