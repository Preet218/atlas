from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from atlas.candidate.models import Preferences
from atlas.job.enums import Currency, ExperienceLevel, WorkplaceType
from atlas.job.models import Compensation, JobMetadata, Location
from atlas.ranking.enums import MatchStrength
from atlas.ranking.ranker import JobRanker
from tests.fixtures.factories.candidate import create_candidate
from tests.fixtures.factories.job import create_job

FIXED_NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def dimension(ranked_job, name):
    return next(d for d in ranked_job.dimension_scores if d.name == name)


# ---------------------------------------------------------------------------
# End-to-end happy path
# ---------------------------------------------------------------------------


def test_score_full_match_scores_highly_and_is_deterministic():
    candidate = create_candidate()
    job = create_job(
        metadata=JobMetadata(
            source_job_id="123",
            discovered_at=FIXED_NOW - timedelta(days=1),
            last_updated=FIXED_NOW - timedelta(days=1),
        )
    )

    ranker = JobRanker()

    result = ranker.score(candidate, job, now=FIXED_NOW)

    # skills 100*.35 + role 100*.15 + location 100*.15 + compensation
    # 100*.15 + experience 85*.10 + recency 100*.10 = 98.5
    assert result.overall_score == 98.5
    assert result.match_strength == MatchStrength.STRONG
    assert not result.disqualified
    assert len(result.reasons) > 0


def test_score_is_deterministic_across_repeated_calls():
    candidate = create_candidate()
    job = create_job()

    ranker = JobRanker()

    first = ranker.score(candidate, job, now=FIXED_NOW)
    second = ranker.score(candidate, job, now=FIXED_NOW)

    assert first.overall_score == second.overall_score
    assert [d.reason for d in first.dimension_scores] == [
        d.reason for d in second.dimension_scores
    ]


# ---------------------------------------------------------------------------
# Disqualification
# ---------------------------------------------------------------------------


def test_excluded_company_is_disqualified():
    candidate = create_candidate(
        preferences=Preferences(
            excluded_companies=["OpenAI"],
        )
    )
    job = create_job()  # company.name == "OpenAI"

    ranker = JobRanker()

    result = ranker.score(candidate, job, now=FIXED_NOW)

    assert result.disqualified
    assert result.overall_score == 0.0
    assert result.match_strength == MatchStrength.WEAK
    assert result.dimension_scores == []
    assert "OpenAI" in result.disqualification_reason


def test_excluded_company_match_is_case_insensitive():
    candidate = create_candidate(
        preferences=Preferences(
            excluded_companies=["openai"],
        )
    )
    job = create_job()

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert result.disqualified


# ---------------------------------------------------------------------------
# Skills dimension
# ---------------------------------------------------------------------------


def test_skills_full_match():
    candidate = create_candidate()
    job = create_job(requirements=["Python", "Machine Learning"], preferred_skills=["LLMs"])

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "skills").score == 100.0


def test_skills_partial_match():
    candidate = create_candidate()
    job = create_job(requirements=["Python", "Rust", "Go"], preferred_skills=[])

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "skills").score == pytest.approx(33.3, abs=0.1)


def test_skills_no_requirements_is_neutral():
    candidate = create_candidate()
    job = create_job(requirements=[], preferred_skills=[])

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "skills").score == 50.0


def test_skills_zero_match():
    candidate = create_candidate()
    job = create_job(requirements=["Rust", "Go"], preferred_skills=[])

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "skills").score == 0.0


# ---------------------------------------------------------------------------
# Role dimension
# ---------------------------------------------------------------------------


def test_role_exact_match():
    candidate = create_candidate()
    job = create_job(title="Senior Data Scientist")

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "role").score == 100.0


def test_role_domain_match():
    candidate = create_candidate()
    job = create_job(title="Machine Learning Researcher")

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "role").score == 60.0


def test_role_no_match():
    candidate = create_candidate()
    job = create_job(title="Corporate Recruiter")

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "role").score == 30.0


def test_role_no_preference_is_neutral():
    candidate = create_candidate(
        preferences=Preferences(preferred_roles=[])
    )
    job = create_job(title="Corporate Recruiter")

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "role").score == 50.0


# ---------------------------------------------------------------------------
# Location dimension
# ---------------------------------------------------------------------------


def test_location_country_and_mode_match():
    candidate = create_candidate()
    job = create_job(
        location=Location(country="India", workplace_type=WorkplaceType.HYBRID)
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "location").score == 100.0


def test_location_country_mismatch_halves_score():
    candidate = create_candidate()
    job = create_job(
        location=Location(country="United States", workplace_type=WorkplaceType.HYBRID)
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "location").score == 50.0


def test_location_unspecified_workplace_type_is_neutral_component():
    candidate = create_candidate()
    job = create_job(location=Location(country="India", workplace_type=None))

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    # country match (100) + neutral work-mode (50) averaged
    assert dimension(result, "location").score == 75.0


def test_location_no_preferences_is_neutral():
    candidate = create_candidate(
        preferences=Preferences(
            preferred_countries=[],
            preferred_work_modes=[],
        )
    )
    job = create_job(
        location=Location(country="India", workplace_type=WorkplaceType.HYBRID)
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "location").score == 50.0


# ---------------------------------------------------------------------------
# Compensation dimension
# ---------------------------------------------------------------------------


def test_compensation_meets_minimum():
    candidate = create_candidate()
    job = create_job(
        compensation=Compensation(
            currency=Currency.INR, min_salary=4_000_000, max_salary=6_000_000
        )
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "compensation").score == 100.0


def test_compensation_below_minimum_is_proportional():
    candidate = create_candidate()
    job = create_job(
        compensation=Compensation(
            currency=Currency.INR, min_salary=1_500_000, max_salary=2_000_000
        )
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    # 2,000,000 / 3,500,000 == 0.5714...
    assert dimension(result, "compensation").score == pytest.approx(57.1, abs=0.1)


def test_compensation_missing_is_neutral():
    candidate = create_candidate()
    job = create_job(compensation=None)

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "compensation").score == 50.0


def test_compensation_missing_candidate_minimum_is_neutral():
    candidate = create_candidate(
        preferences=Preferences(minimum_base_salary=None)
    )
    job = create_job()

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "compensation").score == 50.0


def test_compensation_no_published_range_is_neutral():
    candidate = create_candidate()
    job = create_job(
        compensation=Compensation(currency=Currency.INR, min_salary=None, max_salary=None)
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "compensation").score == 50.0


# ---------------------------------------------------------------------------
# Experience dimension
# ---------------------------------------------------------------------------


def test_experience_within_range():
    candidate = create_candidate()  # 6 years
    job = create_job(experience_level=ExperienceLevel.SENIOR)  # 5-8

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "experience").score == 100.0


def test_experience_slightly_outside_range():
    candidate = create_candidate()  # 6 years
    job = create_job(experience_level=ExperienceLevel.MID)  # 2-5

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "experience").score == 85.0


def test_experience_far_outside_range_clips_to_zero():
    candidate = create_candidate(
        personal={
            **create_candidate().personal.model_dump(),
            "years_of_experience": 0,
        }
    )
    job = create_job(experience_level=ExperienceLevel.EXECUTIVE)  # 12-30

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "experience").score == 0.0


def test_experience_unspecified_is_neutral():
    candidate = create_candidate()
    job = create_job(experience_level=None)

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "experience").score == 50.0


# ---------------------------------------------------------------------------
# Recency dimension
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "days_old,expected_score",
    [
        (0, 100.0),
        (2, 100.0),
        (5, 80.0),
        (10, 60.0),
        (20, 40.0),
        (60, 20.0),
    ],
)
def test_recency_scoring(days_old, expected_score):
    candidate = create_candidate()
    job = create_job(
        metadata=JobMetadata(
            source_job_id="123",
            discovered_at=FIXED_NOW - timedelta(days=days_old),
            last_updated=FIXED_NOW - timedelta(days=days_old),
        )
    )

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "recency").score == expected_score


def test_recency_prefers_posted_at_over_discovered_at():
    candidate = create_candidate()
    job = create_job(
        metadata=JobMetadata(
            source_job_id="123",
            discovered_at=FIXED_NOW - timedelta(days=60),
            last_updated=FIXED_NOW - timedelta(days=60),
        )
    )
    job.application.posted_at = FIXED_NOW - timedelta(days=1)

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "recency").score == 100.0


def test_recency_handles_naive_discovered_at_without_raising():
    candidate = create_candidate()
    job = create_job()  # factory default uses naive datetime.now()

    result = JobRanker().score(candidate, job, now=FIXED_NOW)

    assert dimension(result, "recency").score in {20.0, 40.0, 60.0, 80.0, 100.0}
