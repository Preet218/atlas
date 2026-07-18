"""Service layer for job postings."""

from __future__ import annotations

from uuid import UUID

from .models import JobPosting
from .storage import JobStorage


class JobService:
    """Provides high-level operations for job postings."""

    def __init__(self, storage: JobStorage | None = None) -> None:
        self._storage = storage or JobStorage()

    def save(self, job: JobPosting) -> None:
        """Save a job posting."""
        self._storage.save(job)

    def get(self, platform: str, job_id: UUID) -> JobPosting:
        """Retrieve a job posting."""
        return self._storage.load(platform, job_id)

    def exists(self, platform: str, job_id: UUID) -> bool:
        """Check if a job posting exists."""
        return self._storage.exists(platform, job_id)

    def delete(self, platform: str, job_id: UUID) -> None:
        """Delete a job posting."""
        self._storage.delete(platform, job_id)

    def list(self, platform: str):
        """List all stored jobs for a platform."""
        return self._storage.list(platform)
