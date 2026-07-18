from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from atlas.common.enums import JobPlatform
from atlas.discovery.base import BaseConnector
from atlas.discovery.exceptions import ConnectorNotFoundError
from atlas.discovery.models import DiscoveryTarget
from atlas.discovery.service import DiscoveryService
from tests.fixtures.factories.job import create_job


@pytest.mark.asyncio
async def test_discover() -> None:
    connector = MagicMock(spec=BaseConnector)
    connector.platform = JobPlatform.GREENHOUSE
    connector.discover = AsyncMock(
        return_value=[
            create_job(title="Job 1"),
            create_job(title="Job 2"),
        ]
    )

    service = DiscoveryService(connectors=[connector])

    target = DiscoveryTarget(
        platform=JobPlatform.GREENHOUSE,
        identifier="canonical",
    )

    jobs = await service.discover(target)

    connector.discover.assert_awaited_once_with(target)

    assert len(jobs) == 2
    assert jobs[0].title == "Job 1"
    assert jobs[1].title == "Job 2"


@pytest.mark.asyncio
async def test_missing_connector() -> None:
    service = DiscoveryService(connectors=[])

    target = DiscoveryTarget(
        platform=JobPlatform.GREENHOUSE,
        identifier="canonical",
    )

    with pytest.raises(ConnectorNotFoundError):
        await service.discover(target)


@pytest.mark.asyncio
async def test_discover_many() -> None:
    connector = MagicMock(spec=BaseConnector)
    connector.platform = JobPlatform.GREENHOUSE
    connector.discover = AsyncMock(
        side_effect=[
            [create_job(title="Job 1")],
            [create_job(title="Job 2")],
        ]
    )

    service = DiscoveryService(connectors=[connector])

    targets = [
        DiscoveryTarget(
            platform=JobPlatform.GREENHOUSE,
            identifier="company-1",
        ),
        DiscoveryTarget(
            platform=JobPlatform.GREENHOUSE,
            identifier="company-2",
        ),
    ]

    jobs = await service.discover_many(targets)

    assert connector.discover.await_count == 2
    assert len(jobs) == 2
    assert jobs[0].title == "Job 1"
    assert jobs[1].title == "Job 2"
