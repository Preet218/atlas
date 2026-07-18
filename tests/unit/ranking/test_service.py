from __future__ import annotations

from datetime import datetime, timezone

from atlas.candidate.models import Preferences
from atlas.job.enums import ExperienceLevel
from atlas.ranking.service import RankingService
from tests.fixtures.factories.candidate import create_candidate
from tests.fixtures.factories.job import create_job

FIXED_NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def test_rank_orders_jobs_best_match_first():
    candidate = create_candidate()

    strong_match = create_job(
        title="Senior Data Scientist",
        experience_level=ExperienceLevel.SENIOR,
    )
    weak_match = create_job(
        title="Corporate Recruiter",
        requirements=["Sales"],
        preferred_skills=[],
        experience_level=ExperienceLevel.EXECUTIVE,
    )

    service = RankingService()

    results = service.rank(candidate, [weak_match, strong_match], now=FIXED_NOW)

    assert [r.job.title for r in results] == ["Senior Data Scientist", "Corporate Recruiter"]
    assert results[0].overall_score >= results[1].overall_score


def test_rank_excludes_disqualified_jobs():
    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["OpenAI"]),
    )

    excluded_job = create_job()  # company.name == "OpenAI"

    service = RankingService()

    results = service.rank(candidate, [excluded_job], now=FIXED_NOW)

    assert results == []


def test_rank_returns_empty_list_for_no_jobs():
    candidate = create_candidate()

    service = RankingService()

    results = service.rank(candidate, [], now=FIXED_NOW)

    assert results == []
