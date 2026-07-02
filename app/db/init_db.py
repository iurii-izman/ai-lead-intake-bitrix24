"""Database initialization helpers."""

from sqlalchemy import Engine

from app.models.ai_classification import AIClassificationRecord
from app.models.base import Base
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.models.routing_decision import RoutingDecisionRecord


def create_all(engine: Engine) -> None:
    """Create all MVP tables without migrations."""

    Base.metadata.create_all(
        bind=engine,
        tables=[
            IntakeRequestRecord.__table__,
            AIClassificationRecord.__table__,
            RoutingDecisionRecord.__table__,
            BitrixEntityRecord.__table__,
            ProcessingLogRecord.__table__,
        ],
    )


def drop_all(engine: Engine) -> None:
    """Drop all MVP tables."""

    Base.metadata.drop_all(
        bind=engine,
        tables=[
            ProcessingLogRecord.__table__,
            BitrixEntityRecord.__table__,
            RoutingDecisionRecord.__table__,
            AIClassificationRecord.__table__,
            IntakeRequestRecord.__table__,
        ],
    )
