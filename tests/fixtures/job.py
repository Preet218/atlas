"""Factory functions for creating JobPosting test instances."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from atlas.job.enums import (
    Currency,
    EmploymentType,
    ExperienceLevel,
    JobPlatform,
    WorkplaceType,
)
from atlas.job.models import (
    ApplicationInfo,
    Company,
    Compensation,
    JobMetadata,
    JobPosting,
    Location,
)


def create_job(**overrides) -> JobPosting:
    """Create a JobPosting with sensible defaults."""

    data = {
        "id": uuid4(),
        "title": "Senior Data Scientist",
        "company": Company(
            name="OpenAI",
            website="https://openai.com",
        ),
        "location": Location(
            city="Bangalore",
            state="Karnataka",
            country="India",
            workplace_type=WorkplaceType.HYBRID,
        ),
        "compensation": Compensation(
            currency=Currency.INR,
            min_salary=3_500_000,
            max_salary=5_000_000,
        ),
        "employment_type": EmploymentType.FULL_TIME,
        "experience_level": ExperienceLevel.MID,
        "description": "Build AI-powered systems.",
        "requirements": ["Python", "Machine Learning"],
        "preferred_skills": ["LLMs"],
        "responsibilities": ["Develop ML models"],
        "benefits": ["Health Insurance"],
        "application": ApplicationInfo(
            url="https://careers.openai.com/jobs/123",
            platform=JobPlatform.COMPANY,
        ),
        "metadata": JobMetadata(
            source_job_id="123",
            discovered_at=datetime.now(),
            last_updated=datetime.now(),
        ),
    }

    data.update(overrides)
    return JobPosting(**data)
