from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from atlas.application.enums import ApplicationStatus
from atlas.application.exceptions import (
    FollowUpNotFoundError,
    InvalidStatusTransitionError,
)
from atlas.application.models import RecruiterContact
from atlas.application.service import ApplicationService
from atlas.application.storage import ApplicationStorage
from tests.fixtures.factories.job import create_job

FIXED_NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def make_service(tmp_path) -> ApplicationService:
    return ApplicationService(storage=ApplicationStorage(root=tmp_path))


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------


def test_create_starts_in_draft_with_history(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    assert application.status == ApplicationStatus.DRAFT
    assert len(application.status_history) == 1
    assert application.status_history[0].status == ApplicationStatus.DRAFT
    assert application.applied_at is None


def test_create_persists_the_application(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    assert service.get(application.id) == application


def test_create_stores_resume_and_cover_letter_references(tmp_path):
    service = make_service(tmp_path)

    application = service.create(
        create_job(),
        resume_reference="resumes/senior-ds-v3.pdf",
        cover_letter="Dear Hiring Manager, ...",
    )

    assert application.resume_reference == "resumes/senior-ds-v3.pdf"
    assert application.cover_letter == "Dear Hiring Manager, ..."


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------


def test_update_status_valid_transition(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    updated = service.update_status(
        application, ApplicationStatus.APPLIED, now=FIXED_NOW
    )

    assert updated.status == ApplicationStatus.APPLIED
    assert len(updated.status_history) == 2
    assert updated.applied_at == FIXED_NOW


def test_update_status_invalid_transition_raises(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    with pytest.raises(InvalidStatusTransitionError):
        service.update_status(application, ApplicationStatus.OFFER, now=FIXED_NOW)


def test_update_status_does_not_overwrite_applied_at(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    applied = service.update_status(
        application, ApplicationStatus.APPLIED, now=FIXED_NOW
    )
    later = FIXED_NOW + timedelta(days=3)

    under_review = service.update_status(
        applied, ApplicationStatus.UNDER_REVIEW, now=later
    )

    assert under_review.applied_at == FIXED_NOW  # unchanged
    assert under_review.updated_at == later


def test_update_status_records_note(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    updated = service.update_status(
        application,
        ApplicationStatus.APPLIED,
        note="Applied via referral",
        now=FIXED_NOW,
    )

    assert updated.status_history[-1].note == "Applied via referral"


def test_update_status_persists_changes(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())
    updated = service.update_status(
        application, ApplicationStatus.APPLIED, now=FIXED_NOW
    )

    assert service.get(application.id).status == ApplicationStatus.APPLIED
    assert service.get(application.id) == updated


def test_terminal_status_cannot_transition_further(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())
    application = service.update_status(application, ApplicationStatus.WITHDRAWN)

    with pytest.raises(InvalidStatusTransitionError):
        service.update_status(application, ApplicationStatus.APPLIED)


# ---------------------------------------------------------------------------
# Recruiter contacts
# ---------------------------------------------------------------------------


def test_add_recruiter_contact(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    contact = RecruiterContact(name="Alex Kim", role="Recruiter", email="alex@openai.com")

    updated = service.add_recruiter_contact(application, contact)

    assert len(updated.recruiter_contacts) == 1
    assert updated.recruiter_contacts[0].name == "Alex Kim"


def test_add_multiple_recruiter_contacts(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    application = service.add_recruiter_contact(
        application, RecruiterContact(name="Alex Kim", role="Recruiter")
    )
    application = service.add_recruiter_contact(
        application, RecruiterContact(name="Sam Lee", role="Hiring Manager")
    )

    assert [c.name for c in application.recruiter_contacts] == ["Alex Kim", "Sam Lee"]


# ---------------------------------------------------------------------------
# Follow-ups
# ---------------------------------------------------------------------------


def test_schedule_follow_up(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    updated = service.schedule_follow_up(
        application, due_date=date(2026, 7, 26), reason="Check in after one week"
    )

    assert len(updated.follow_ups) == 1
    assert updated.follow_ups[0].reason == "Check in after one week"
    assert not updated.follow_ups[0].completed


def test_due_follow_ups_excludes_future_reminders(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())
    application = service.schedule_follow_up(
        application, due_date=date(2026, 7, 26), reason="Follow up"
    )

    assert service.due_follow_ups(application, as_of=date(2026, 7, 20)) == []
    assert len(service.due_follow_ups(application, as_of=date(2026, 7, 26))) == 1
    assert len(service.due_follow_ups(application, as_of=date(2026, 8, 1))) == 1


def test_complete_follow_up_removes_it_from_due_list(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())
    application = service.schedule_follow_up(
        application, due_date=date(2026, 7, 1), reason="Follow up"
    )
    follow_up_id = application.follow_ups[0].id

    application = service.complete_follow_up(application, follow_up_id, now=FIXED_NOW)

    assert application.follow_ups[0].completed
    assert application.follow_ups[0].completed_at == FIXED_NOW
    assert service.due_follow_ups(application, as_of=date(2026, 8, 1)) == []


def test_complete_unknown_follow_up_raises(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())

    with pytest.raises(FollowUpNotFoundError):
        service.complete_follow_up(application, uuid4())


# ---------------------------------------------------------------------------
# Listing / retrieval
# ---------------------------------------------------------------------------


def test_list_by_status(tmp_path):
    service = make_service(tmp_path)

    draft = service.create(create_job())
    applied = service.create(create_job())
    applied = service.update_status(applied, ApplicationStatus.APPLIED)

    assert [a.id for a in service.list_by_status(ApplicationStatus.DRAFT)] == [draft.id]
    assert [a.id for a in service.list_by_status(ApplicationStatus.APPLIED)] == [
        applied.id
    ]


def test_list_returns_all_applications(tmp_path):
    service = make_service(tmp_path)

    created = [service.create(create_job()) for _ in range(3)]

    assert {a.id for a in service.list()} == {a.id for a in created}


def test_delete_application(tmp_path):
    service = make_service(tmp_path)

    application = service.create(create_job())
    service.delete(application.id)

    assert application.id not in {a.id for a in service.list()}
