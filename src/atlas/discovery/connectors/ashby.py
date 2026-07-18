"""Ashby job discovery connector."""

from __future__ import annotations

from typing import Any

from atlas.common.enums import JobPlatform
from atlas.discovery.base import BaseConnector
from atlas.discovery.client import DiscoveryHttpClient
from atlas.discovery.mappers.ashby import AshbyJobMapper
from atlas.discovery.models import DiscoveryTarget
from atlas.job.models import JobPosting


class AshbyConnector(BaseConnector):
    """Connector for the Ashby Job Postings API.

    The public Ashby Job Postings API does not support server-side
    filtering or search, so `department`/`location`/`remote_only` on the
    DiscoveryTarget are applied client-side against the raw payload.
    """

    BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"

    def __init__(
        self,
        client: DiscoveryHttpClient,
        mapper: AshbyJobMapper,
    ) -> None:
        self._client = client
        self._mapper = mapper

    @property
    def name(self) -> str:
        """Return the connector name."""
        return "ashby"

    @property
    def platform(self) -> JobPlatform:
        return JobPlatform.ASHBY

    async def discover(
        self,
        target: DiscoveryTarget,
    ) -> list[JobPosting]:
        """Discover jobs from an Ashby job board."""

        postings = await self._fetch_postings(target)

        jobs = [self._mapper.map(posting, target) for posting in postings]

        if target.max_jobs is not None:
            jobs = jobs[: target.max_jobs]

        return jobs

    async def _fetch_postings(
        self,
        target: DiscoveryTarget,
    ) -> list[dict[str, Any]]:
        """Fetch job postings from the Ashby job board."""

        response = await self._client.get(
            f"{self.BASE_URL}/{target.identifier}",
            params={"includeCompensation": "true"},
        )

        payload: Any = response.json()

        postings = payload.get("jobs", []) if isinstance(payload, dict) else []

        if target.department:
            postings = [
                posting
                for posting in postings
                if self._matches_department(posting, target.department)
            ]

        if target.location:
            postings = [
                posting
                for posting in postings
                if self._matches_location(posting, target.location)
            ]

        if target.remote_only:
            postings = [
                posting
                for posting in postings
                if str(posting.get("workplaceType", "")).lower() == "remote"
                or posting.get("isRemote") is True
            ]

        return postings

    def _matches_department(self, posting: dict[str, Any], department: str) -> bool:
        """Check whether a raw posting matches the requested department/team."""

        department = department.lower()

        return department in str(posting.get("department", "")).lower() or (
            department in str(posting.get("team", "")).lower()
        )

    def _matches_location(self, posting: dict[str, Any], location: str) -> bool:
        """Check whether a raw posting matches the requested location."""

        return location.lower() in str(posting.get("location", "")).lower()
