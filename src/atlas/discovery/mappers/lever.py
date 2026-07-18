from __future__ import annotations

from atlas.common.enums import JobPlatform
from atlas.job.models import (
    ApplicationInfo,
    Company,
    JobMetadata,
    JobPosting,
    Location,
)


class LeverJobMapper:
    """Maps Lever API payloads to JobPosting."""

    def map(self, payload: dict) -> JobPosting:
        return JobPosting(
            title=payload["text"],
            description=payload["descriptionPlain"],
            company=Company(
                name="Unknown",
            ),
            location=Location(),
            application=ApplicationInfo(
                url=payload["hostedUrl"],
                platform=JobPlatform.LEVER,
            ),
            metadata=JobMetadata(
                source_job_id=payload["id"],
            ),
        )