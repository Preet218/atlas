"""
Canonical Candidate Profile (CCP) domain models.

These models represent the single source of truth about a candidate.
Every other Atlas module (resume generation, ranking, applications,
job discovery, interview preparation) should consume these models
instead of reading raw resume files.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from atlas.candidate.enums import (
    EducationLevel,
    EmploymentType,
    NoticePeriod,
    ProfileStatus,
    ProficiencyLevel,
    SkillCategory,
    TravelPreference,
    VisaRequirement,
    WorkMode,
)


class AtlasBaseModel(BaseModel):
    """
    Base model for every Atlas domain object.

    Shared configuration lives here so that all models behave
    consistently throughout the application.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class PersonalInfo(AtlasBaseModel):
    """
    Candidate personal information.
    """

    full_name: str = Field(
        ...,
        description="Candidate full name",
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Primary email address",
    )

    phone: Optional[str] = Field(
        default=None,
        description="Primary contact number",
    )

    location: str = Field(
        ...,
        description="Current city",
    )

    nationality: str = Field(
        ...,
        description="Nationality",
    )

    current_company: str = Field(
        ...,
        description="Current employer",
    )

    current_role: str = Field(
        ...,
        description="Current job title",
    )

    years_of_experience: float = Field(
        ...,
        ge=0,
        description="Professional experience in years",
    )

    notice_period: NoticePeriod = Field(
        default=NoticePeriod.NEGOTIABLE,
    )

    linkedin_url: Optional[str] = None

    github_url: Optional[str] = None

    portfolio_url: Optional[str] = None


class Metadata(AtlasBaseModel):
    """
    Atlas metadata.

    This information is maintained automatically
    and should never come from the resume.
    """

    profile_version: str = "1.0.0"

    atlas_version: str = "0.1.0"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    status: ProfileStatus = ProfileStatus.DRAFT


class Education(AtlasBaseModel):
    """
    Educational qualification.
    """

    degree: EducationLevel

    institution: str

    specialization: str | None = None

    cgpa: float | None = Field(
        default=None,
        ge=0,
    )

    start_date: date | None = None

    end_date: date | None = None


class Skill(AtlasBaseModel):
    """
    Candidate skill.
    """

    name: str

    category: SkillCategory

    proficiency: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE

    years_of_experience: float | None = Field(
        default=None,
        ge=0,
    )


class Award(AtlasBaseModel):
    """
    Award or achievement.
    """

    title: str

    issuer: str

    award_date: date | None = None

    description: str | None = None


class Project(AtlasBaseModel):
    """
    Professional or academic project.
    """

    name: str

    objective: str

    description: str

    technologies: list[str] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)

    business_metrics: list[str] = Field(default_factory=list)


class Experience(AtlasBaseModel):
    """
    Professional work experience.
    """

    company: str

    title: str

    employment_type: EmploymentType = EmploymentType.FULL_TIME

    start_date: date

    end_date: date | None = None

    current: bool = False

    location: str | None = None

    summary: str | None = None

    projects: list[Project] = Field(default_factory=list)


class Preferences(AtlasBaseModel):
    """
    Candidate job preferences.
    """

    preferred_roles: list[str] = Field(default_factory=list)

    preferred_countries: list[str] = Field(default_factory=list)

    preferred_work_modes: list[WorkMode] = Field(default_factory=list)

    minimum_base_salary: float | None = Field(
        default=None,
        ge=0,
    )

    target_total_compensation: float | None = Field(
        default=None,
        ge=0,
    )

    visa_requirement: VisaRequirement = VisaRequirement.PREFERRED

    travel_preference: TravelPreference = TravelPreference.NONE

    excluded_companies: list[str] = Field(default_factory=list)


class CareerDNA(AtlasBaseModel):
    """
    High-level representation of the candidate's career.
    """

    primary_domains: list[str] = Field(default_factory=list)

    secondary_domains: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)

    target_domains: list[str] = Field(default_factory=list)


class Candidate(AtlasBaseModel):
    """
    Canonical Candidate Profile (CCP).

    This is the single source of truth used throughout Atlas.
    """

    personal: PersonalInfo

    education: list[Education] = Field(default_factory=list)

    experience: list[Experience] = Field(default_factory=list)

    skills: list[Skill] = Field(default_factory=list)

    awards: list[Award] = Field(default_factory=list)

    preferences: Preferences

    career_dna: CareerDNA

    metadata: Metadata = Field(default_factory=Metadata)
