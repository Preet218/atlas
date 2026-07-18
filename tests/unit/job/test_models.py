"""Unit tests for job domain models."""

from __future__ import annotations

from tests.fixtures.factories.job import create_job

from atlas.job.enums import (
    EmploymentType,
    JobPlatform,
)
from atlas.job.models import (
    JobPosting,
)


def test_job_creation() -> None:
    """Verify a JobPosting can be created."""

    job = create_job()

    assert job.title == "Senior Data Scientist"
    assert job.company.name == "OpenAI"
    assert job.location.city == "Bangalore"
    assert job.employment_type == EmploymentType.FULL_TIME
    assert job.application.platform == JobPlatform.COMPANY


def test_default_lists_are_empty() -> None:
    """Verify default list fields are initialized."""

    job = create_job()

    job.requirements.clear()
    job.preferred_skills.clear()
    job.responsibilities.clear()
    job.benefits.clear()

    assert job.requirements == []
    assert job.preferred_skills == []
    assert job.responsibilities == []
    assert job.benefits == []


def test_model_serialization() -> None:
    """Verify serialization and deserialization."""

    job = create_job()

    json_data = job.model_dump_json()

    restored = JobPosting.model_validate_json(json_data)

    assert restored == job
