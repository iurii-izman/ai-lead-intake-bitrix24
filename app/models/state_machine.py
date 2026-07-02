"""Explicit request lifecycle state machine."""

from dataclasses import dataclass, field

from app.models.enums import RequestStatus


class InvalidStateTransitionError(ValueError):
    """Raised when a lifecycle transition is not allowed."""


@dataclass(frozen=True)
class RequestLifecycleStateMachine:
    """Deterministic transitions for intake request records."""

    transitions: dict[RequestStatus | None, frozenset[RequestStatus]] = field(
        default_factory=lambda: {
            None: frozenset({RequestStatus.received}),
            RequestStatus.received: frozenset({RequestStatus.processing, RequestStatus.duplicate}),
            RequestStatus.processing: frozenset(
                {RequestStatus.classified, RequestStatus.review_needed}
            ),
            RequestStatus.classified: frozenset(
                {RequestStatus.review_needed, RequestStatus.routed, RequestStatus.dropped}
            ),
            RequestStatus.review_needed: frozenset({RequestStatus.routed, RequestStatus.dropped}),
            RequestStatus.routed: frozenset({RequestStatus.bitrix_syncing, RequestStatus.dropped}),
            RequestStatus.bitrix_syncing: frozenset(
                {
                    RequestStatus.completed,
                    RequestStatus.failed_retryable,
                    RequestStatus.failed,
                }
            ),
            RequestStatus.failed_retryable: frozenset(
                {RequestStatus.processing, RequestStatus.failed}
            ),
            RequestStatus.completed: frozenset(),
            RequestStatus.failed: frozenset(),
            RequestStatus.dropped: frozenset(),
            RequestStatus.duplicate: frozenset(),
        }
    )
    terminal_states: frozenset[RequestStatus] = frozenset(
        {
            RequestStatus.completed,
            RequestStatus.failed,
            RequestStatus.dropped,
            RequestStatus.duplicate,
        }
    )

    def can_transition(
        self,
        from_status: RequestStatus | None,
        to_status: RequestStatus,
    ) -> bool:
        return to_status in self.transitions.get(from_status, frozenset())

    def validate_transition(
        self,
        from_status: RequestStatus | None,
        to_status: RequestStatus,
    ) -> None:
        if not self.can_transition(from_status, to_status):
            raise InvalidStateTransitionError(
                f"Transition from {from_status!r} to {to_status!r} is not allowed."
            )

    def is_terminal(self, status: RequestStatus) -> bool:
        return status in self.terminal_states


REQUEST_LIFECYCLE_STATE_MACHINE = RequestLifecycleStateMachine()
