"""ApplicationService: the public entry point for application tracking.

Covers the "owns application history" responsibility from
docs/architecture.md — creating applications, moving them through
their status lifecycle, logging recruiter contacts, and scheduling/
completing follow-up reminders.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from atlas.application.enums import ApplicationStatus
from atlas.application.exceptions import (
    FollowUpNotFoundError,
    InvalidStatusTransitionError,
)
from atlas.application.models import (
    Application,
    FollowUp,
    RecruiterContact,
    StatusChange,
)
from atlas.application.storage import ApplicationStorage
from atlas.application.transitions import is_valid_transition
from atlas.job.models import JobPosting


class ApplicationService:
    """Provides high-level operations for tracking job applications."""

    def __init__(self, storage: ApplicationStorage | None = None) -> None:
        self._storage = storage or ApplicationStorage()

    def create(
        self,
        job: JobPosting,
        resume_reference: str | None = None,
        cover_letter: str | None = None,
        notes: str | None = None,
    ) -> Application:
        """Create a new application in DRAFT status."""

        application = Application(
            job=job,
            resume_reference=resume_reference,
            cover_letter=cover_letter,
            notes=notes,
            status_history=[StatusChange(status=ApplicationStatus.DRAFT)],
        )

        self._storage.save(application)

        return application

    def update_status(
        self,
        application: Application,
        new_status: ApplicationStatus,
        note: str | None = None,
        now: datetime | None = None,
    ) -> Application:
        """Move an application to a new status.

        Raises InvalidStatusTransitionError if the transition isn't
        legal from the application's current status (see
        atlas.application.transitions).
        """

        if not is_valid_transition(application.status, new_status):
            raise InvalidStatusTransitionError(
                f"Cannot move an application from {application.status.value} "
                f"to {new_status.value}."
            )

        now = now or datetime.now(timezone.utc)

        updated = application.model_copy(
            update={
                "status": new_status,
                "status_history": [
                    *application.status_history,
                    StatusChange(status=new_status, changed_at=now, note=note),
                ],
                "applied_at": (
                    now
                    if new_status == ApplicationStatus.APPLIED
                    and application.applied_at is None
                    else application.applied_at
                ),
                "updated_at": now,
            }
        )

        self._storage.save(updated)

        return updated

    def add_recruiter_contact(
        self,
        application: Application,
        contact: RecruiterContact,
    ) -> Application:
        """Log a recruiter/hiring-manager contact on an application."""

        updated = application.model_copy(
            update={
                "recruiter_contacts": [*application.recruiter_contacts, contact],
                "updated_at": datetime.now(timezone.utc),
            }
        )

        self._storage.save(updated)

        return updated

    def schedule_follow_up(
        self,
        application: Application,
        due_date: date,
        reason: str,
    ) -> Application:
        """Schedule a follow-up reminder on an application."""

        follow_up = FollowUp(due_date=due_date, reason=reason)

        updated = application.model_copy(
            update={
                "follow_ups": [*application.follow_ups, follow_up],
                "updated_at": datetime.now(timezone.utc),
            }
        )

        self._storage.save(updated)

        return updated

    def complete_follow_up(
        self,
        application: Application,
        follow_up_id: UUID,
        now: datetime | None = None,
    ) -> Application:
        """Mark a scheduled follow-up as completed."""

        now = now or datetime.now(timezone.utc)

        if not any(f.id == follow_up_id for f in application.follow_ups):
            raise FollowUpNotFoundError(
                f"No follow-up with id {follow_up_id} on this application."
            )

        updated_follow_ups = [
            (
                f.model_copy(update={"completed": True, "completed_at": now})
                if f.id == follow_up_id
                else f
            )
            for f in application.follow_ups
        ]

        updated = application.model_copy(
            update={
                "follow_ups": updated_follow_ups,
                "updated_at": now,
            }
        )

        self._storage.save(updated)

        return updated

    def due_follow_ups(
        self,
        application: Application,
        as_of: date | None = None,
    ) -> list[FollowUp]:
        """Return incomplete follow-ups due on or before `as_of`."""

        as_of = as_of or date.today()

        return [
            f
            for f in application.follow_ups
            if not f.completed and f.due_date <= as_of
        ]

    def get(self, application_id: UUID) -> Application:
        """Retrieve a stored application by id."""
        return self._storage.load(application_id)

    def list(self) -> list[Application]:
        """List all stored applications."""
        return self._storage.load_all()

    def list_by_status(self, status: ApplicationStatus) -> list[Application]:
        """List all stored applications currently in a given status."""
        return [app for app in self.list() if app.status == status]

    def delete(self, application_id: UUID) -> None:
        """Delete a stored application."""
        self._storage.delete(application_id)
