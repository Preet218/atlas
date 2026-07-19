from __future__ import annotations

import pytest

from atlas.application.enums import ApplicationStatus
from atlas.application.transitions import (
    allowed_next_statuses,
    is_terminal,
    is_valid_transition,
)


@pytest.mark.parametrize(
    "current,new,expected",
    [
        (ApplicationStatus.DRAFT, ApplicationStatus.APPLIED, True),
        (ApplicationStatus.DRAFT, ApplicationStatus.WITHDRAWN, True),
        (ApplicationStatus.DRAFT, ApplicationStatus.OFFER, False),
        (ApplicationStatus.APPLIED, ApplicationStatus.UNDER_REVIEW, True),
        (ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEWING, True),
        (ApplicationStatus.APPLIED, ApplicationStatus.DRAFT, False),
        (ApplicationStatus.UNDER_REVIEW, ApplicationStatus.INTERVIEWING, True),
        (ApplicationStatus.UNDER_REVIEW, ApplicationStatus.APPLIED, False),
        (ApplicationStatus.INTERVIEWING, ApplicationStatus.OFFER, True),
        (ApplicationStatus.INTERVIEWING, ApplicationStatus.REJECTED, True),
        (ApplicationStatus.OFFER, ApplicationStatus.ACCEPTED, True),
        (ApplicationStatus.OFFER, ApplicationStatus.WITHDRAWN, True),
        (ApplicationStatus.ACCEPTED, ApplicationStatus.OFFER, False),
        (ApplicationStatus.REJECTED, ApplicationStatus.APPLIED, False),
        (ApplicationStatus.WITHDRAWN, ApplicationStatus.APPLIED, False),
    ],
)
def test_is_valid_transition(current, new, expected):
    assert is_valid_transition(current, new) is expected


def test_same_status_transition_allowed_when_not_terminal():
    assert is_valid_transition(
        ApplicationStatus.INTERVIEWING, ApplicationStatus.INTERVIEWING
    )


@pytest.mark.parametrize(
    "status",
    [
        ApplicationStatus.ACCEPTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    ],
)
def test_same_status_transition_disallowed_when_terminal(status):
    assert not is_valid_transition(status, status)


@pytest.mark.parametrize(
    "status,expected",
    [
        (ApplicationStatus.DRAFT, False),
        (ApplicationStatus.APPLIED, False),
        (ApplicationStatus.OFFER, False),
        (ApplicationStatus.ACCEPTED, True),
        (ApplicationStatus.REJECTED, True),
        (ApplicationStatus.WITHDRAWN, True),
    ],
)
def test_is_terminal(status, expected):
    assert is_terminal(status) is expected


def test_allowed_next_statuses_from_draft():
    assert allowed_next_statuses(ApplicationStatus.DRAFT) == {
        ApplicationStatus.APPLIED,
        ApplicationStatus.WITHDRAWN,
    }


def test_allowed_next_statuses_from_terminal_is_empty():
    assert allowed_next_statuses(ApplicationStatus.ACCEPTED) == set()


def test_allowed_next_statuses_returns_a_copy():
    """Mutating the result should not corrupt the internal graph."""

    result = allowed_next_statuses(ApplicationStatus.DRAFT)
    result.add(ApplicationStatus.OFFER)

    assert ApplicationStatus.OFFER not in allowed_next_statuses(
        ApplicationStatus.DRAFT
    )
