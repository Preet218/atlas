"""Mapper for Lever job payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from atlas.common.enums import JobPlatform
from atlas.discovery.models import DiscoveryTarget
from atlas.job.enums import Currency, EmploymentType, WorkplaceType
from atlas.job.models import (
    ApplicationInfo,
    Company,
    Compensation,
    JobMetadata,
    JobPosting,
    Location,
)


class LeverJobMapper:
    """Maps Lever API payloads to JobPosting."""

    _WORKPLACE_TYPE_MAP: dict[str, WorkplaceType] = {
        "remote": WorkplaceType.REMOTE,
        "hybrid": WorkplaceType.HYBRID,
        "onsite": WorkplaceType.ONSITE,
        "on-site": WorkplaceType.ONSITE,
    }

    _EMPLOYMENT_TYPE_MAP: dict[str, EmploymentType] = {
        "full time": EmploymentType.FULL_TIME,
        "full-time": EmploymentType.FULL_TIME,
        "part time": EmploymentType.PART_TIME,
        "part-time": EmploymentType.PART_TIME,
        "contract": EmploymentType.CONTRACT,
        "contractor": EmploymentType.CONTRACT,
        "intern": EmploymentType.INTERN,
        "internship": EmploymentType.INTERN,
        "temporary": EmploymentType.TEMPORARY,
        "temp": EmploymentType.TEMPORARY,
        "freelance": EmploymentType.FREELANCE,
    }

    def map(
        self,
        payload: dict[str, Any],
        target: DiscoveryTarget | None = None,
    ) -> JobPosting:
        """Convert a Lever payload into a JobPosting."""

        now = datetime.now(timezone.utc)

        company_name = target.identifier if target is not None else "Unknown"

        return JobPosting(
            title=payload["text"],
            company=Company(
                name=company_name,
            ),
            location=self._parse_location(payload),
            compensation=self._parse_compensation(payload),
            employment_type=self._parse_employment_type(payload),
            experience_level=None,
            description=payload["descriptionPlain"],
            application=ApplicationInfo(
                url=payload["hostedUrl"],
                platform=JobPlatform.LEVER,
                posted_at=self._parse_created_at(payload),
            ),
            metadata=JobMetadata(
                source_job_id=payload["id"],
                discovered_at=now,
                last_updated=now,
            ),
        )

    def _parse_location(self, payload: dict[str, Any]) -> Location:
        """Parse location details from a Lever payload."""

        categories = payload.get("categories", {}) or {}
        raw_location = categories.get("location")

        city, state = self._split_city_state(raw_location)

        return Location(
            city=city,
            state=state,
            country=payload.get("country"),
            workplace_type=self._parse_workplace_type(payload),
        )

    def _split_city_state(
        self,
        raw_location: str | None,
    ) -> tuple[str | None, str | None]:
        """Best-effort split of a Lever location string into city/state."""

        if not raw_location:
            return None, None

        if raw_location.lower().startswith("remote"):
            return None, None

        parts = [part.strip() for part in raw_location.split(",")]

        if len(parts) == 1:
            return parts[0] or None, None

        return parts[0] or None, parts[1] or None

    def _parse_workplace_type(
        self,
        payload: dict[str, Any],
    ) -> WorkplaceType | None:
        """Infer the workplace type from the Lever payload."""

        workplace_type = payload.get("workplaceType")

        if not workplace_type:
            return None

        return self._WORKPLACE_TYPE_MAP.get(workplace_type.lower())

    def _parse_employment_type(
        self,
        payload: dict[str, Any],
    ) -> EmploymentType | None:
        """Infer the employment type from the Lever commitment category."""

        categories = payload.get("categories", {}) or {}
        commitment = categories.get("commitment")

        if not commitment:
            return None

        commitment = commitment.lower()

        for keyword, employment_type in self._EMPLOYMENT_TYPE_MAP.items():
            if keyword in commitment:
                return employment_type

        return None

    def _parse_compensation(
        self,
        payload: dict[str, Any],
    ) -> Compensation | None:
        """Parse compensation information from the Lever salary range."""

        salary_range = payload.get("salaryRange")

        if not salary_range:
            return None

        return Compensation(
            currency=self._parse_currency(salary_range.get("currency")),
            min_salary=salary_range.get("min"),
            max_salary=salary_range.get("max"),
        )

    def _parse_currency(self, currency: str | None) -> Currency | None:
        """Parse a currency code into the Currency enum, if supported."""

        if not currency:
            return None

        try:
            return Currency(currency.upper())
        except ValueError:
            return None

    def _parse_created_at(self, payload: dict[str, Any]) -> datetime | None:
        """Convert Lever's millisecond epoch timestamp to a datetime."""

        created_at = payload.get("createdAt")

        if created_at is None:
            return None

        return datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
