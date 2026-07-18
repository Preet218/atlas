from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from atlas.common.enums import JobPlatform
from atlas.discovery.connectors.ashby import AshbyConnector
from atlas.discovery.mappers.ashby import AshbyJobMapper
from atlas.discovery.models import DiscoveryTarget


def load_fixture() -> dict:
    fixture = Path(__file__).parents[2] / "fixtures" / "ashby" / "listing.json"

    with fixture.open() as f:
        return json.load(f)


def make_client(payload) -> MagicMock:
    client = MagicMock()

    response = MagicMock()
    response.json.return_value = payload

    client.get = AsyncMock(return_value=response)

    return client


@pytest.mark.asyncio
async def test_discover_returns_mapped_jobs():
    fixture = load_fixture()

    client = make_client(fixture)
    connector = AshbyConnector(client=client, mapper=AshbyJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.ASHBY, identifier="openai")

    jobs = await connector.discover(target)

    assert len(jobs) == len(fixture["jobs"])
    assert jobs[0].title == fixture["jobs"][0]["title"]
    assert jobs[0].company.name == "openai"

    client.get.assert_awaited_once_with(
        f"{AshbyConnector.BASE_URL}/openai",
        params={"includeCompensation": "true"},
    )


@pytest.mark.asyncio
async def test_discover_respects_max_jobs():
    fixture = load_fixture()

    client = make_client(fixture)
    connector = AshbyConnector(client=client, mapper=AshbyJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.ASHBY, identifier="openai", max_jobs=2)

    jobs = await connector.discover(target)

    assert len(jobs) == 2


@pytest.mark.asyncio
async def test_discover_filters_by_department_client_side():
    fixture = load_fixture()

    client = make_client(fixture)
    connector = AshbyConnector(client=client, mapper=AshbyJobMapper())

    target = DiscoveryTarget(
        platform=JobPlatform.ASHBY,
        identifier="openai",
        department="Go To Market",
    )

    jobs = await connector.discover(target)

    assert len(jobs) == 1
    assert jobs[0].title == "Account Director - Tokyo"


@pytest.mark.asyncio
async def test_discover_filters_by_location_client_side():
    fixture = load_fixture()

    client = make_client(fixture)
    connector = AshbyConnector(client=client, mapper=AshbyJobMapper())

    target = DiscoveryTarget(
        platform=JobPlatform.ASHBY,
        identifier="openai",
        location="Tokyo",
    )

    jobs = await connector.discover(target)

    assert len(jobs) == 1
    assert jobs[0].title == "Account Director - Tokyo"


@pytest.mark.asyncio
async def test_discover_filters_remote_only_client_side():
    fixture = load_fixture()

    client = make_client(fixture)
    connector = AshbyConnector(client=client, mapper=AshbyJobMapper())

    target = DiscoveryTarget(
        platform=JobPlatform.ASHBY,
        identifier="openai",
        remote_only=True,
    )

    jobs = await connector.discover(target)

    # Only the "RL Training Infra" fixture entry has isRemote true / Hybrid.
    assert len(jobs) == 1
    assert jobs[0].title == "Software Engineer, RL Training Infra"


@pytest.mark.asyncio
async def test_discover_returns_empty_list_for_unexpected_payload():
    client = make_client({"unexpected": "shape"})
    connector = AshbyConnector(client=client, mapper=AshbyJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.ASHBY, identifier="openai")

    jobs = await connector.discover(target)

    assert jobs == []


def test_connector_metadata():
    connector = AshbyConnector(client=MagicMock(), mapper=AshbyJobMapper())

    assert connector.name == "ashby"
    assert connector.platform == JobPlatform.ASHBY
