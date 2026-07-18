from abc import ABC, abstractmethod

from atlas.common.enums import JobPlatform
from atlas.discovery.models import DiscoveryTarget
from atlas.job.models import JobPosting


class BaseConnector(ABC):
    """Abstract base class for all discovery connectors."""

    @property
    @abstractmethod
    def platform(self) -> JobPlatform:
        """Return the platform supported by this connector."""

    @abstractmethod
    async def discover(
        self,
        target: DiscoveryTarget,
    ) -> list[JobPosting]:
        """Discover jobs for the supplied target."""
