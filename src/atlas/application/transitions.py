"""Valid status transitions for applications.

Kept separate from ApplicationService so the business rule (what
transitions are legal) is independently testable and has exactly one
owner, per contributing.md's "no duplicated logic."
"""

from __future__ import annotations

from atlas.application.enums import ApplicationStatus

# Terminal statuses have no outgoing transitions.
_ALLOWED_TRANSITIONS: dict[ApplicationStatus, set[ApplicationStatus]] = {
    ApplicationStatus.DRAFT: {
        ApplicationStatus.APPLIED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.APPLIED: {
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.INTERVIEWING,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.UNDER_REVIEW: {
        ApplicationStatus.INTERVIEWING,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.INTERVIEWING: {
        ApplicationStatus.OFFER,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.OFFER: {
        ApplicationStatus.ACCEPTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.ACCEPTED: set(),
    ApplicationStatus.REJECTED: set(),
    ApplicationStatus.WITHDRAWN: set(),
}


def allowed_next_statuses(status: ApplicationStatus) -> set[ApplicationStatus]:
    """Return the set of statuses reachable from the given status."""
    return set(_ALLOWED_TRANSITIONS[status])


def is_terminal(status: ApplicationStatus) -> bool:
    """Return True if no further transitions are possible from this status."""
    return not _ALLOWED_TRANSITIONS[status]


def is_valid_transition(
    current: ApplicationStatus,
    new: ApplicationStatus,
) -> bool:
    """Return True if moving from `current` to `new` is a legal transition.

    Re-logging the same status (e.g. recording notes on another
    interview round while remaining INTERVIEWING) is always allowed,
    provided the status isn't terminal — there's nothing further to log
    once an application has reached a terminal state.
    """

    if current == new:
        return not is_terminal(current)

    return new in _ALLOWED_TRANSITIONS[current]
