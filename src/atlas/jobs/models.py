"""Domain models for normalized job postings."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

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
    workplace_type: WorkplaceType


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
    """Internal metadata maintained by Atlas."""

    source_job_id: str
    discovered_at: datetime
    last_updated: datetime


class JobPosting(BaseModel):
    """Normalized representation of a job posting."""

    id: UUID

    title: str

    company: Company

    location: Location

    compensation: Compensation | None = None

    employment_type: EmploymentType

    experience_level: ExperienceLevel | None = None

    description: str

    requirements: list[str] = Field(default_factory=list)

    preferred_skills: list[str] = Field(default_factory=list)

    responsibilities: list[str] = Field(default_factory=list)

    benefits: list[str] = Field(default_factory=list)

    application: ApplicationInfo

    metadata: JobMetadata
