"""Greenhouse job discovery connector."""

from __future__ import annotations

from typing import Any

from atlas.discovery.base import BaseConnector
from atlas.discovery.client import DiscoveryHttpClient
from atlas.discovery.mappers.greenhouse import GreenhouseJobMapper
from atlas.discovery.models import DiscoveryTarget
from atlas.job.models import JobPosting
from atlas.common.enums import JobPlatform


class GreenhouseConnector(BaseConnector):
    """Connector for the Greenhouse Job Board API."""

    BASE_URL = "https://boards-api.greenhouse.io/v1"

    def __init__(
        self,
        client: DiscoveryHttpClient,
        mapper: GreenhouseJobMapper,
    ) -> None:
        self._client = client
        self._mapper = mapper

    @property
    def name(self) -> str:
        """Return the connector name."""
        return "greenhouse"

    @property
    def platform(self) -> JobPlatform:
        return JobPlatform.GREENHOUSE

    async def discover(
        self,
        target: DiscoveryTarget,
    ) -> list[JobPosting]:
        """Discover jobs from a Greenhouse board."""

        summaries = await self._fetch_job_summaries(target)

        jobs: list[JobPosting] = []

        for summary in summaries:
            job = await self._fetch_job(
                target=target,
                job_id=summary["id"],
            )
            jobs.append(job)

        return jobs

    async def _fetch_job_summaries(
        self,
        target: DiscoveryTarget,
    ) -> list[dict[str, Any]]:
        """Fetch job summaries from the Greenhouse board."""

        response = await self._client.get(f"{self.BASE_URL}/boards/{target.identifier}/jobs")

        payload: dict[str, Any] = response.json()

        return payload.get("jobs", [])

    async def _fetch_job(
        self,
        target: DiscoveryTarget,
        job_id: int,
    ) -> JobPosting:
        """Fetch and map a single job."""

        payload = await self._fetch_job_details(
            target=target,
            job_id=job_id,
        )

        return self._mapper.map(payload)

    async def _fetch_job_details(
        self,
        target: DiscoveryTarget,
        job_id: int,
    ) -> dict[str, Any]:
        """Fetch a detailed job payload from Greenhouse."""

        response = await self._client.get(
            f"{self.BASE_URL}/boards/{target.identifier}/jobs/{job_id}"
        )

        payload: dict[str, Any] = response.json()

        return payload
