from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from atlas.candidate.models import Preferences
from atlas.common.enums import JobPlatform
from atlas.discovery.base import BaseConnector
from atlas.discovery.models import DiscoveryTarget
from atlas.discovery.service import DiscoveryService
from atlas.matching.service import MatchingService
from atlas.ranking.service import RankingService
from atlas.workflows.find_opportunities import FindOpportunitiesWorkflow
from tests.fixtures.factories.candidate import create_candidate
from tests.fixtures.factories.job import create_job

FIXED_NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def make_connector(jobs) -> MagicMock:
    connector = MagicMock(spec=BaseConnector)
    connector.platform = JobPlatform.GREENHOUSE
    connector.discover = AsyncMock(return_value=jobs)
    return connector


def make_workflow(jobs) -> FindOpportunitiesWorkflow:
    discovery = DiscoveryService(connectors=[make_connector(jobs)])
    return FindOpportunitiesWorkflow(
        discovery=discovery,
        matching=MatchingService(),
        ranking=RankingService(),
    )


@pytest.mark.asyncio
async def test_run_discovers_matches_and_ranks():
    strong_match = create_job(title="Senior Data Scientist")
    different_role = create_job(title="Product Manager")  # distinct posting, not a duplicate
    duplicate = create_job(title="Senior Data Scientist")  # duplicate of strong_match

    workflow = make_workflow([strong_match, different_role, duplicate])

    candidate = create_candidate(
        preferences=Preferences(excluded_companies=[])
    )

    target = DiscoveryTarget(platform=JobPlatform.GREENHOUSE, identifier="openai")

    results = await workflow.run(candidate, [target], now=FIXED_NOW)

    # duplicate merged away, nothing excluded here, so 2 unique roles survive
    assert len(results) == 2
    assert results[0].overall_score >= results[1].overall_score


@pytest.mark.asyncio
async def test_run_filters_out_excluded_companies():
    job = create_job()  # company.name == "OpenAI"

    workflow = make_workflow([job])

    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["OpenAI"])
    )

    target = DiscoveryTarget(platform=JobPlatform.GREENHOUSE, identifier="openai")

    results = await workflow.run(candidate, [target], now=FIXED_NOW)

    assert results == []


@pytest.mark.asyncio
async def test_run_with_no_discovered_jobs_returns_empty_list():
    workflow = make_workflow([])

    candidate = create_candidate()

    target = DiscoveryTarget(platform=JobPlatform.GREENHOUSE, identifier="openai")

    results = await workflow.run(candidate, [target], now=FIXED_NOW)

    assert results == []


@pytest.mark.asyncio
async def test_run_queries_discovery_for_every_target():
    job = create_job()

    connector = make_connector([job])
    discovery = DiscoveryService(connectors=[connector])
    workflow = FindOpportunitiesWorkflow(
        discovery=discovery,
        matching=MatchingService(),
        ranking=RankingService(),
    )

    candidate = create_candidate()

    targets = [
        DiscoveryTarget(platform=JobPlatform.GREENHOUSE, identifier="openai"),
        DiscoveryTarget(platform=JobPlatform.GREENHOUSE, identifier="anthropic"),
    ]

    await workflow.run(candidate, targets, now=FIXED_NOW)

    assert connector.discover.await_count == 2
