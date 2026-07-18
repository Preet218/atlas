"""Domain models for job discovery."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from atlas.common.enums import JobPlatform


class DiscoveryTarget(BaseModel):
    """Represents a target from which jobs should be discovered."""

    platform: JobPlatform
    identifier: str

    location: str | None = None
    department: str | None = None

    remote_only: bool = False

    max_jobs: int | None = None


class DiscoveryResult(BaseModel):
    """Represents the outcome of a discovery operation."""

    connector: JobPlatform

    target: str

    discovered_jobs: int = 0

    started_at: datetime

    completed_at: datetime

    successful: bool = True

    error: str | None = None


class DiscoveryStatistics(BaseModel):
    """Aggregated statistics across multiple discovery runs."""

    connectors_run: int = 0

    jobs_discovered: int = 0

    jobs_saved: int = 0

    jobs_skipped: int = 0

    failed_connectors: int = 0

    started_at: datetime

    completed_at: datetime
