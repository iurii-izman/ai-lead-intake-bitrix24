"""Database models and lifecycle primitives for AI Lead Intake for Bitrix24."""

from app.models.ai_classification import AIClassificationRecord
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.enums import (
    AIClassificationCategory,
    AIClassificationPriority,
    AIClassificationTone,
    RequestStatus,
)
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.models.routing_decision import RoutingDecisionRecord
from app.models.state_machine import (
    REQUEST_LIFECYCLE_STATE_MACHINE,
    InvalidStateTransitionError,
    RequestLifecycleStateMachine,
)

__all__ = [
    "AIClassificationCategory",
    "AIClassificationPriority",
    "AIClassificationTone",
    "AIClassificationRecord",
    "BitrixEntityRecord",
    "IntakeRequestRecord",
    "InvalidStateTransitionError",
    "ProcessingLogRecord",
    "REQUEST_LIFECYCLE_STATE_MACHINE",
    "RequestLifecycleStateMachine",
    "RequestStatus",
    "RoutingDecisionRecord",
]
