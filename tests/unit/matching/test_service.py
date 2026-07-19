from __future__ import annotations

from atlas.candidate.models import Preferences
from atlas.job.models import Company
from atlas.matching.service import MatchingService
from tests.fixtures.factories.candidate import create_candidate
from tests.fixtures.factories.job import create_job


def test_process_deduplicates_before_matching():
    candidate = create_candidate()

    duplicate_a = create_job()
    duplicate_b = create_job(title="Senior Data Scientist")  # same company & title

    service = MatchingService()

    result = service.process(candidate, [duplicate_a, duplicate_b])

    assert len(result.eligible) == 1
    assert len(result.match_results) == 1
    assert len(result.duplicate_groups) == 1


def test_process_excludes_ineligible_jobs_from_eligible_list():
    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["OpenAI"]),
    )
    job = create_job()  # company.name == "OpenAI"

    service = MatchingService()

    result = service.process(candidate, [job])

    assert result.eligible == []
    assert len(result.match_results) == 1
    assert not result.match_results[0].is_match


def test_filter_eligible_convenience_method():
    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["OpenAI"]),
    )
    excluded = create_job(company=Company(name="OpenAI"))
    allowed = create_job(company=Company(name="Anthropic"))

    service = MatchingService()

    eligible = service.filter_eligible(candidate, [excluded, allowed])

    assert [job.company.name for job in eligible] == ["Anthropic"]


def test_process_empty_input():
    candidate = create_candidate()

    service = MatchingService()

    result = service.process(candidate, [])

    assert result.eligible == []
    assert result.match_results == []
    assert result.duplicate_groups == []
