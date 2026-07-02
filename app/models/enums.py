"""Explicit enums for request lifecycle and AI output."""

from enum import Enum


class StrEnum(str, Enum):
    """String-valued enum base for portable DB storage and JSON serialization."""


class RequestStatus(StrEnum):
    received = "received"
    processing = "processing"
    classified = "classified"
    review_needed = "review_needed"
    routed = "routed"
    bitrix_syncing = "bitrix_syncing"
    completed = "completed"
    failed = "failed"
    failed_retryable = "failed_retryable"
    dropped = "dropped"
    duplicate = "duplicate"


class AIClassificationCategory(StrEnum):
    crm_implementation = "crm_implementation"
    integration_1c = "integration_1c"
    business_process_automation = "business_process_automation"
    ai_automation = "ai_automation"
    support = "support"
    partnership = "partnership"
    complaint = "complaint"
    spam = "spam"
    other = "other"


class AIClassificationPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AIClassificationTone(StrEnum):
    formal = "formal"
    friendly = "friendly"
    urgent = "urgent"
