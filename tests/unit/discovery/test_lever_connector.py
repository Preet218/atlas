from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from atlas.common.enums import JobPlatform
from atlas.discovery.connectors.lever import LeverConnector
from atlas.discovery.mappers.lever import LeverJobMapper
from atlas.discovery.models import DiscoveryTarget


def load_fixture() -> list[dict]:
    fixture = Path(__file__).parents[2] / "fixtures" / "lever" / "listing.json"

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
    postings = load_fixture()

    client = make_client(postings)
    connector = LeverConnector(client=client, mapper=LeverJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.LEVER, identifier="dnb")

    jobs = await connector.discover(target)

    assert len(jobs) == len(postings)
    assert jobs[0].title == postings[0]["text"]
    assert jobs[0].company.name == "dnb"

    client.get.assert_awaited_once_with(
        f"{LeverConnector.BASE_URL}/dnb",
        params={"mode": "json"},
    )


@pytest.mark.asyncio
async def test_discover_respects_max_jobs():
    postings = load_fixture()

    client = make_client(postings)
    connector = LeverConnector(client=client, mapper=LeverJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.LEVER, identifier="dnb", max_jobs=1)

    jobs = await connector.discover(target)

    assert len(jobs) == 1


@pytest.mark.asyncio
async def test_discover_passes_department_and_location_filters():
    postings = load_fixture()

    client = make_client(postings)
    connector = LeverConnector(client=client, mapper=LeverJobMapper())

    target = DiscoveryTarget(
        platform=JobPlatform.LEVER,
        identifier="dnb",
        department="Sales",
        location="Remote",
    )

    await connector.discover(target)

    client.get.assert_awaited_once_with(
        f"{LeverConnector.BASE_URL}/dnb",
        params={"mode": "json", "team": "Sales", "location": "Remote"},
    )


@pytest.mark.asyncio
async def test_discover_filters_remote_only_client_side():
    postings = load_fixture()
    postings = [
        {**postings[0], "workplaceType": "remote"},
        {**postings[0], "id": "onsite-job", "workplaceType": "onsite"},
    ]

    client = make_client(postings)
    connector = LeverConnector(client=client, mapper=LeverJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.LEVER, identifier="dnb", remote_only=True)

    jobs = await connector.discover(target)

    assert len(jobs) == 1


@pytest.mark.asyncio
async def test_discover_returns_empty_list_for_unexpected_payload():
    client = make_client({"unexpected": "shape"})
    connector = LeverConnector(client=client, mapper=LeverJobMapper())

    target = DiscoveryTarget(platform=JobPlatform.LEVER, identifier="dnb")

    jobs = await connector.discover(target)

    assert jobs == []


def test_connector_metadata():
    connector = LeverConnector(client=MagicMock(), mapper=LeverJobMapper())

    assert connector.name == "lever"
    assert connector.platform == JobPlatform.LEVER
