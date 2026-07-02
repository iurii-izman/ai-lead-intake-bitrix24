import pytest

from app.models.enums import RequestStatus
from app.models.state_machine import (
    REQUEST_LIFECYCLE_STATE_MACHINE,
    InvalidStateTransitionError,
)


@pytest.mark.parametrize(
    ("from_status", "to_status"),
    [
        (None, RequestStatus.received),
        (RequestStatus.received, RequestStatus.processing),
        (RequestStatus.processing, RequestStatus.classified),
        (RequestStatus.processing, RequestStatus.review_needed),
        (RequestStatus.classified, RequestStatus.routed),
        (RequestStatus.review_needed, RequestStatus.dropped),
        (RequestStatus.routed, RequestStatus.bitrix_syncing),
        (RequestStatus.bitrix_syncing, RequestStatus.completed),
        (RequestStatus.bitrix_syncing, RequestStatus.failed_retryable),
        (RequestStatus.failed_retryable, RequestStatus.processing),
        (RequestStatus.received, RequestStatus.duplicate),
    ],
)
def test_allowed_transitions(from_status, to_status):
    assert REQUEST_LIFECYCLE_STATE_MACHINE.can_transition(from_status, to_status)


@pytest.mark.parametrize(
    ("from_status", "to_status"),
    [
        (RequestStatus.completed, RequestStatus.processing),
        (RequestStatus.failed, RequestStatus.routed),
        (RequestStatus.dropped, RequestStatus.completed),
        (RequestStatus.processing, RequestStatus.completed),
    ],
)
def test_disallowed_transitions(from_status, to_status):
    assert not REQUEST_LIFECYCLE_STATE_MACHINE.can_transition(from_status, to_status)
    with pytest.raises(InvalidStateTransitionError):
        REQUEST_LIFECYCLE_STATE_MACHINE.validate_transition(from_status, to_status)


def test_terminal_states_are_explicit():
    assert REQUEST_LIFECYCLE_STATE_MACHINE.is_terminal(RequestStatus.completed)
    assert REQUEST_LIFECYCLE_STATE_MACHINE.is_terminal(RequestStatus.failed)
    assert REQUEST_LIFECYCLE_STATE_MACHINE.is_terminal(RequestStatus.dropped)
    assert REQUEST_LIFECYCLE_STATE_MACHINE.is_terminal(RequestStatus.duplicate)
