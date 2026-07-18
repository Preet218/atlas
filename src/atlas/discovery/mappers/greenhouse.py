"""Mapper for Greenhouse job payloads."""

from __future__ import annotations

from datetime import datetime, timezone

from atlas.common.enums import JobPlatform
from atlas.job.enums import WorkplaceType
from atlas.job.models import (
    ApplicationInfo,
    Company,
    Compensation,
    JobMetadata,
    JobPosting,
    Location,
)


class GreenhouseJobMapper:
    """Maps Greenhouse API payloads to JobPosting."""

    def map(self, payload: dict) -> JobPosting:
        """Convert a Greenhouse payload into a JobPosting."""

        now = datetime.now(timezone.utc)

        location = Location(
            city=payload.get("location", {}).get("name"),
            workplace_type=self._parse_workplace_type(payload),
        )

        company = Company(
            name=payload.get("company_name", "Unknown"),
        )

        application = ApplicationInfo(
            url=payload["absolute_url"],
            platform=JobPlatform.GREENHOUSE,
        )

        metadata = JobMetadata(
            source_job_id=str(payload["id"]),
            discovered_at=now,
            last_updated=now,
        )

        return JobPosting(
            title=payload["title"],
            company=company,
            location=location,
            compensation=self._parse_compensation(payload),
            employment_type=None,
            experience_level=None,
            description=self._build_description(payload),
            application=application,
            metadata=metadata,
        )

    def _build_description(self, payload: dict) -> str:
        """Build a description from Greenhouse payload."""

        content = payload.get("content")

        if isinstance(content, str):
            return content

        return ""

    def _parse_compensation(
        self,
        payload: dict,
    ) -> Compensation | None:
        """Parse compensation information."""

        return None

    def _parse_workplace_type(
        self,
        payload: dict,
    ) -> WorkplaceType | None:
        """Infer workplace type."""

        location = payload.get("location", {}).get("name", "").lower()

        if "remote" in location:
            return WorkplaceType.REMOTE

        return None
