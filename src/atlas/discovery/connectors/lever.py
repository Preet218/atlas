"""Lever job discovery connector."""

from __future__ import annotations

from typing import Any

from atlas.common.enums import JobPlatform
from atlas.discovery.base import BaseConnector
from atlas.discovery.client import DiscoveryHttpClient
from atlas.discovery.mappers.lever import LeverJobMapper
from atlas.discovery.models import DiscoveryTarget
from atlas.job.models import JobPosting


class LeverConnector(BaseConnector):
    """Connector for the Lever Postings API."""

    BASE_URL = "https://api.lever.co/v0/postings"

    def __init__(
        self,
        client: DiscoveryHttpClient,
        mapper: LeverJobMapper,
    ) -> None:
        self._client = client
        self._mapper = mapper

    @property
    def name(self) -> str:
        """Return the connector name."""
        return "lever"

    @property
    def platform(self) -> JobPlatform:
        return JobPlatform.LEVER

    async def discover(
        self,
        target: DiscoveryTarget,
    ) -> list[JobPosting]:
        """Discover jobs from a Lever posting board."""

        postings = await self._fetch_postings(target)

        jobs = [self._mapper.map(posting, target) for posting in postings]

        if target.max_jobs is not None:
            jobs = jobs[: target.max_jobs]

        return jobs

    async def _fetch_postings(
        self,
        target: DiscoveryTarget,
    ) -> list[dict[str, Any]]:
        """Fetch job postings from the Lever board."""

        params: dict[str, Any] = {"mode": "json"}

        if target.department:
            params["team"] = target.department

        if target.location:
            params["location"] = target.location

        response = await self._client.get(
            f"{self.BASE_URL}/{target.identifier}",
            params=params,
        )

        payload: Any = response.json()

        if not isinstance(payload, list):
            return []

        if target.remote_only:
            payload = [
                posting
                for posting in payload
                if str(posting.get("workplaceType", "")).lower() == "remote"
            ]

        return payload
