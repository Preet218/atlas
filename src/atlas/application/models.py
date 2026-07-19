"""Domain models for application tracking.

Per docs/architecture.md, "Applications Domain owns application
history." Resume selection/optimization and cover-letter generation
(also named under spec 5.3 Application Intelligence) are intentionally
out of scope here — they depend on LLM and Resume-domain integration
that doesn't exist yet (atlas.llm is an empty scaffold). This module
covers what's buildable and testable today: tracking an application
through its lifecycle, its status history, recruiter contacts, and
follow-up reminders. `resume_reference` and `cover_letter` are plain
string fields so this domain has somewhere to record that information
once resume/cover-letter generation exists.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from atlas.application.enums import ApplicationStatus
from atlas.job.models import JobPosting


class RecruiterContact(BaseModel):
    """A person involved in the hiring process for this application."""

    name: str
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    notes: str | None = None


class StatusChange(BaseModel):
    """An immutable record of a status transition."""

    status: ApplicationStatus

    changed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    note: str | None = None


class FollowUp(BaseModel):
    """A scheduled reminder to follow up on an application."""

    id: UUID = Field(default_factory=uuid4)

    due_date: date

    reason: str

    completed: bool = False

    completed_at: datetime | None = None


class Application(BaseModel):
    """Tracks a single job application through its lifecycle."""

    id: UUID = Field(default_factory=uuid4)

    job: JobPosting

    status: ApplicationStatus = ApplicationStatus.DRAFT

    status_history: list[StatusChange] = Field(default_factory=list)

    applied_at: datetime | None = None

    resume_reference: str | None = None

    cover_letter: str | None = None

    recruiter_contacts: list[RecruiterContact] = Field(default_factory=list)

    follow_ups: list[FollowUp] = Field(default_factory=list)

    notes: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
