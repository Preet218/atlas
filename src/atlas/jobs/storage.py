"""Storage layer for job postings."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from atlas.config.paths import DATA_DIR

from .models import JobPosting


class JobStorage:
    """Handles persistence of job postings."""

    def __init__(self) -> None:
        self._root = DATA_DIR / "jobs"

    def _platform_directory(self, platform: str) -> Path:
        directory = self._root / platform
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _job_path(self, platform: str, job_id: UUID) -> Path:
        return self._platform_directory(platform) / f"{job_id}.json"

    def save(self, job: JobPosting) -> None:
        """Save a job posting."""

        path = self._job_path(
            job.application.platform.value,
            job.id,
        )

        path.write_text(
            job.model_dump_json(indent=4),
            encoding="utf-8",
        )

    def load(
        self,
        platform: str,
        job_id: UUID,
    ) -> JobPosting:
        """Load a job posting."""

        path = self._job_path(platform, job_id)

        return JobPosting.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def exists(
        self,
        platform: str,
        job_id: UUID,
    ) -> bool:
        return self._job_path(platform, job_id).exists()

    def delete(
        self,
        platform: str,
        job_id: UUID,
    ) -> None:
        path = self._job_path(platform, job_id)

        if path.exists():
            path.unlink()

    def list(self, platform: str) -> list[Path]:
        directory = self._platform_directory(platform)

        return sorted(directory.glob("*.json"))
