"""Mapper for Ashby job payloads."""

from __future__ import annotations

from datetime import datetime
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


class AshbyJobMapper:
    """Maps Ashby Job Postings API payloads to JobPosting."""

    _WORKPLACE_TYPE_MAP: dict[str, WorkplaceType] = {
        "onsite": WorkplaceType.ONSITE,
        "remote": WorkplaceType.REMOTE,
        "hybrid": WorkplaceType.HYBRID,
    }

    _EMPLOYMENT_TYPE_MAP: dict[str, EmploymentType] = {
        "fulltime": EmploymentType.FULL_TIME,
        "parttime": EmploymentType.PART_TIME,
        "intern": EmploymentType.INTERN,
        "contract": EmploymentType.CONTRACT,
        "temporary": EmploymentType.TEMPORARY,
    }

    def map(
        self,
        payload: dict[str, Any],
        target: DiscoveryTarget | None = None,
    ) -> JobPosting:
        """Convert an Ashby payload into a JobPosting."""

        company_name = target.identifier if target is not None else "Unknown"

        return JobPosting(
            title=payload["title"],
            company=Company(
                name=company_name,
            ),
            location=self._parse_location(payload),
            compensation=self._parse_compensation(payload),
            employment_type=self._parse_employment_type(payload),
            experience_level=None,
            description=payload.get("descriptionPlain", ""),
            application=ApplicationInfo(
                url=payload["jobUrl"],
                platform=JobPlatform.ASHBY,
                posted_at=self._parse_published_at(payload),
            ),
            metadata=JobMetadata(
                source_job_id=payload["id"],
            ),
        )

    def _parse_location(self, payload: dict[str, Any]) -> Location:
        """Parse location details from the Ashby postal address."""

        postal_address = payload.get("address", {}).get("postalAddress", {}) or {}

        return Location(
            city=postal_address.get("addressLocality"),
            state=postal_address.get("addressRegion"),
            country=postal_address.get("addressCountry"),
            workplace_type=self._parse_workplace_type(payload),
        )

    def _parse_workplace_type(
        self,
        payload: dict[str, Any],
    ) -> WorkplaceType | None:
        """Infer the workplace type from the Ashby payload."""

        workplace_type = payload.get("workplaceType")

        if workplace_type:
            mapped = self._WORKPLACE_TYPE_MAP.get(workplace_type.lower())

            if mapped is not None:
                return mapped

        if payload.get("isRemote"):
            return WorkplaceType.REMOTE

        return None

    def _parse_employment_type(
        self,
        payload: dict[str, Any],
    ) -> EmploymentType | None:
        """Infer the employment type from the Ashby employmentType enum."""

        employment_type = payload.get("employmentType")

        if not employment_type:
            return None

        return self._EMPLOYMENT_TYPE_MAP.get(employment_type.lower())

    def _parse_compensation(
        self,
        payload: dict[str, Any],
    ) -> Compensation | None:
        """Parse compensation from Ashby's summaryComponents, when present.

        Compensation is only included when the request used
        `includeCompensation=true` and the organization has published a
        salary range for the role. We look for a "Salary" component in
        `compensation.summaryComponents`.
        """

        compensation = payload.get("compensation")

        if not compensation:
            return None

        for component in compensation.get("summaryComponents", []):
            if component.get("compensationType") == "Salary":
                return Compensation(
                    currency=self._parse_currency(component.get("currencyCode")),
                    min_salary=component.get("minValue"),
                    max_salary=component.get("maxValue"),
                )

        return None

    def _parse_currency(self, currency: str | None) -> Currency | None:
        """Parse a currency code into the Currency enum, if supported."""

        if not currency:
            return None

        try:
            return Currency(currency.upper())
        except ValueError:
            return None

    def _parse_published_at(self, payload: dict[str, Any]) -> datetime | None:
        """Parse the ISO 8601 publishedAt timestamp."""

        published_at = payload.get("publishedAt")

        if not published_at:
            return None

        try:
            return datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        except ValueError:
            return None
