"""Domain models for normalized job postings."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from datetime import timezone

from pydantic import BaseModel, Field, HttpUrl
from uuid import uuid4

from .enums import (
    Currency,
    EmploymentType,
    ExperienceLevel,
    JobPlatform,
    WorkplaceType,
)


class Company(BaseModel):
    """Represents the hiring company."""

    name: str
    website: HttpUrl | None = None
    industry: str | None = None
    size: str | None = None
    description: str | None = None


class Location(BaseModel):
    """Represents the job location."""

    city: str | None = None
    state: str | None = None
    country: str | None = None

    workplace_type: WorkplaceType | None = None


class Compensation(BaseModel):
    """Represents the compensation offered for the role."""

    currency: Currency | None = None
    min_salary: float | None = None
    max_salary: float | None = None


class ApplicationInfo(BaseModel):
    """Represents application details."""

    url: HttpUrl
    platform: JobPlatform
    posted_at: datetime | None = None
    deadline: datetime | None = None


class JobMetadata(BaseModel):
    source_job_id: str

    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobPosting(BaseModel):
    """Normalized representation of a job posting."""

    id: UUID = Field(default_factory=uuid4)

    title: str

    company: Company

    location: Location

    compensation: Compensation | None = None

    employment_type: EmploymentType | None = None

    experience_level: ExperienceLevel | None = None

    visa_sponsorship: bool | None = Field(
        default=None,
        description=(
            "Whether this role offers visa/work-authorization sponsorship. "
            "None means unknown/unspecified — no connector currently "
            "populates this field, since none of Greenhouse, Lever, or "
            "Ashby's public APIs expose it. It exists so the Matching "
            "domain has somewhere to check once a data source (job "
            "description parsing, a future connector, or manual entry) "
            "can populate it."
        ),
    )

    description: str

    requirements: list[str] = Field(default_factory=list)

    preferred_skills: list[str] = Field(default_factory=list)

    responsibilities: list[str] = Field(default_factory=list)

    benefits: list[str] = Field(default_factory=list)

    application: ApplicationInfo

    metadata: JobMetadata
