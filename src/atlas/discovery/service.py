"""Discovery service."""

from __future__ import annotations

from atlas.common.enums import JobPlatform
from atlas.discovery.base import BaseConnector
from atlas.discovery.exceptions import ConnectorNotFoundError
from atlas.discovery.models import DiscoveryTarget
from atlas.job.models import JobPosting


class DiscoveryService:
    """Coordinates job discovery across connectors."""

    def __init__(
        self,
        connectors: list[BaseConnector],
    ) -> None:
        self._connectors = {connector.platform: connector for connector in connectors}

    async def discover(
        self,
        target: DiscoveryTarget,
    ) -> list[JobPosting]:
        """Discover jobs for a single target."""

        connector = self._get_connector(target.platform)

        return await connector.discover(target)

    async def discover_many(
        self,
        targets: list[DiscoveryTarget],
    ) -> list[JobPosting]:
        """Discover jobs for multiple targets."""

        jobs: list[JobPosting] = []

        for target in targets:
            jobs.extend(await self.discover(target))

        return jobs

    def _get_connector(
        self,
        platform: JobPlatform,
    ) -> BaseConnector:
        """Return the connector for the requested platform."""

        try:
            return self._connectors[platform]
        except KeyError as exc:
            raise ConnectorNotFoundError(
                f"No connector registered for '{platform.value}'."
            ) from exc
