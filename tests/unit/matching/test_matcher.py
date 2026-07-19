from __future__ import annotations

from atlas.candidate.enums import VisaRequirement
from atlas.candidate.models import Preferences
from atlas.job.enums import WorkplaceType
from atlas.job.models import Compensation, Location
from atlas.matching.matcher import JobMatcher
from tests.fixtures.factories.candidate import create_candidate
from tests.fixtures.factories.job import create_job


def test_default_candidate_and_job_is_a_match():
    candidate = create_candidate()
    job = create_job()

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match
    assert result.reasons == ["Meets all hard eligibility requirements."]


# ---------------------------------------------------------------------------
# Excluded companies
# ---------------------------------------------------------------------------


def test_excluded_company_fails():
    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["OpenAI"])
    )
    job = create_job()  # company.name == "OpenAI"

    result = JobMatcher().evaluate(candidate, job)

    assert not result.is_match
    assert "OpenAI" in result.reasons[0]


def test_excluded_company_match_is_case_insensitive():
    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["openai"])
    )
    job = create_job()

    result = JobMatcher().evaluate(candidate, job)

    assert not result.is_match


# ---------------------------------------------------------------------------
# Visa
# ---------------------------------------------------------------------------


def test_visa_required_and_no_sponsorship_fails():
    candidate = create_candidate(
        preferences=Preferences(visa_requirement=VisaRequirement.REQUIRED)
    )
    job = create_job(visa_sponsorship=False)

    result = JobMatcher().evaluate(candidate, job)

    assert not result.is_match
    assert "sponsorship" in result.reasons[0].lower()


def test_visa_required_but_unknown_sponsorship_passes():
    candidate = create_candidate(
        preferences=Preferences(visa_requirement=VisaRequirement.REQUIRED)
    )
    job = create_job(visa_sponsorship=None)

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_visa_required_and_sponsorship_offered_passes():
    candidate = create_candidate(
        preferences=Preferences(visa_requirement=VisaRequirement.REQUIRED)
    )
    job = create_job(visa_sponsorship=True)

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_visa_not_required_ignores_sponsorship():
    candidate = create_candidate(
        preferences=Preferences(visa_requirement=VisaRequirement.NOT_REQUIRED)
    )
    job = create_job(visa_sponsorship=False)

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_visa_preferred_does_not_hard_fail():
    candidate = create_candidate(
        preferences=Preferences(visa_requirement=VisaRequirement.PREFERRED)
    )
    job = create_job(visa_sponsorship=False)

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------


def test_non_remote_job_outside_preferred_country_fails():
    candidate = create_candidate()  # preferred_countries == ["India"]
    job = create_job(
        location=Location(country="United States", workplace_type=WorkplaceType.ONSITE)
    )

    result = JobMatcher().evaluate(candidate, job)

    assert not result.is_match
    assert "United States" in result.reasons[0]


def test_remote_job_outside_preferred_country_passes():
    candidate = create_candidate()
    job = create_job(
        location=Location(country="United States", workplace_type=WorkplaceType.REMOTE)
    )

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_job_with_unspecified_country_passes():
    candidate = create_candidate()
    job = create_job(
        location=Location(country=None, workplace_type=WorkplaceType.ONSITE)
    )

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_no_preferred_countries_passes_any_location():
    candidate = create_candidate(
        preferences=Preferences(preferred_countries=[])
    )
    job = create_job(
        location=Location(country="United States", workplace_type=WorkplaceType.ONSITE)
    )

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


# ---------------------------------------------------------------------------
# Compensation floor
# ---------------------------------------------------------------------------


def test_compensation_far_below_floor_fails():
    candidate = create_candidate()  # minimum_base_salary == 3,500,000
    job = create_job(
        compensation=Compensation(min_salary=800_000, max_salary=1_000_000)
    )  # below 50% of 3.5M (1.75M floor)

    result = JobMatcher().evaluate(candidate, job)

    assert not result.is_match
    assert "minimum" in result.reasons[0].lower()


def test_compensation_below_minimum_but_above_floor_passes():
    """Below the candidate's minimum but not drastically so — Matching
    lets it through; Ranking's continuous scoring handles the nuance.
    """

    candidate = create_candidate()  # minimum_base_salary == 3,500,000
    job = create_job(
        compensation=Compensation(min_salary=1_800_000, max_salary=2_000_000)
    )  # above the 1.75M floor, below the 3.5M minimum

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_compensation_missing_passes():
    candidate = create_candidate()
    job = create_job(compensation=None)

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


def test_compensation_missing_candidate_minimum_passes():
    candidate = create_candidate(
        preferences=Preferences(minimum_base_salary=None)
    )
    job = create_job(
        compensation=Compensation(min_salary=100, max_salary=200)
    )

    result = JobMatcher().evaluate(candidate, job)

    assert result.is_match


# ---------------------------------------------------------------------------
# Short-circuiting
# ---------------------------------------------------------------------------


def test_first_failing_check_wins_when_multiple_apply():
    candidate = create_candidate(
        preferences=Preferences(excluded_companies=["OpenAI"])
    )
    job = create_job(
        # Also fails location and compensation, but exclusion is checked first.
        location=Location(country="United States", workplace_type=WorkplaceType.ONSITE),
        compensation=Compensation(min_salary=100, max_salary=200),
    )

    result = JobMatcher().evaluate(candidate, job)

    assert not result.is_match
    assert len(result.reasons) == 1
    assert "OpenAI" in result.reasons[0]
