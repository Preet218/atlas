from __future__ import annotations

from datetime import datetime, timezone

from atlas.job.models import Company, JobMetadata, Location
from atlas.matching.deduplicator import (
    JobDeduplicator,
    normalize_company,
    normalize_title,
)
from atlas.matching.policy import MatchingPolicy
from tests.fixtures.factories.job import create_job


def test_normalize_company_strips_common_suffixes():
    assert normalize_company("OpenAI Inc.") == "openai"
    assert normalize_company("Acme Corporation") == "acme"
    assert normalize_company("OpenAI") == "openai"


def test_normalize_title_strips_punctuation_and_case():
    assert normalize_title("Senior Data Scientist") == "senior data scientist"
    assert normalize_title("Software Engineer, Developer Productivity") == (
        "software engineer developer productivity"
    )


def test_no_merge_when_companies_differ():
    job1 = create_job(company=Company(name="OpenAI"))
    job2 = create_job(company=Company(name="Anthropic"))

    deduplicated, groups = JobDeduplicator().deduplicate([job1, job2])

    assert len(deduplicated) == 2
    assert groups == []


def test_exact_duplicate_is_merged():
    job1 = create_job()
    job2 = create_job(title="Senior Data Scientist")  # same company & title

    deduplicated, groups = JobDeduplicator().deduplicate([job1, job2])

    assert len(deduplicated) == 1
    assert len(groups) == 1
    assert len(groups[0].duplicates) == 1


def test_near_duplicate_title_within_threshold_is_merged():
    job1 = create_job(title="Senior Data Scientist")
    job2 = create_job(title="Sr. Data Scientist")

    deduplicated, groups = JobDeduplicator().deduplicate([job1, job2])

    assert len(deduplicated) == 1
    assert len(groups) == 1


def test_dissimilar_title_is_not_merged():
    job1 = create_job(title="Senior Data Scientist")
    job2 = create_job(title="Corporate Recruiter")

    deduplicated, groups = JobDeduplicator().deduplicate([job1, job2])

    assert len(deduplicated) == 2
    assert groups == []


def test_country_mismatch_prevents_merge_by_default():
    job1 = create_job(location=Location(country="India"))
    job2 = create_job(location=Location(country="United States"))

    deduplicated, groups = JobDeduplicator().deduplicate([job1, job2])

    assert len(deduplicated) == 2
    assert groups == []


def test_country_mismatch_allowed_when_policy_disabled():
    job1 = create_job(location=Location(country="India"))
    job2 = create_job(location=Location(country="United States"))

    policy = MatchingPolicy(require_country_match_for_dedup=False)

    deduplicated, groups = JobDeduplicator(policy=policy).deduplicate([job1, job2])

    assert len(deduplicated) == 1
    assert len(groups) == 1


def test_missing_country_on_one_side_still_merges():
    job1 = create_job(location=Location(country="India"))
    job2 = create_job(location=Location(country=None))

    deduplicated, groups = JobDeduplicator().deduplicate([job1, job2])

    assert len(deduplicated) == 1
    assert len(groups) == 1


def test_canonical_prefers_more_complete_posting():
    complete = create_job(
        metadata=JobMetadata(
            source_job_id="complete",
            discovered_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
            last_updated=datetime(2026, 7, 1, tzinfo=timezone.utc),
        )
    )  # factory default has all optional fields populated
    sparse = create_job(
        requirements=[],
        preferred_skills=[],
        responsibilities=[],
        benefits=[],
        compensation=None,
        experience_level=None,
        location=Location(city=None, country="India"),
        metadata=JobMetadata(
            source_job_id="sparse",
            discovered_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
            last_updated=datetime(2026, 7, 1, tzinfo=timezone.utc),
        ),
    )

    _, groups = JobDeduplicator().deduplicate([sparse, complete])

    assert len(groups) == 1
    assert groups[0].canonical.metadata.source_job_id == "complete"


def test_canonical_prefers_more_recent_when_completeness_ties():
    older = create_job(
        metadata=JobMetadata(
            source_job_id="older",
            discovered_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
            last_updated=datetime(2026, 7, 1, tzinfo=timezone.utc),
        )
    )
    newer = create_job(
        metadata=JobMetadata(
            source_job_id="newer",
            discovered_at=datetime(2026, 7, 15, tzinfo=timezone.utc),
            last_updated=datetime(2026, 7, 15, tzinfo=timezone.utc),
        )
    )

    _, groups = JobDeduplicator().deduplicate([older, newer])

    assert len(groups) == 1
    assert groups[0].canonical.metadata.source_job_id == "newer"


def test_deduplicate_preserves_first_seen_order_for_uniques():
    job1 = create_job(title="Senior Data Scientist")
    job2 = create_job(title="Corporate Recruiter")
    job3 = create_job(title="Product Manager")

    deduplicated, _ = JobDeduplicator().deduplicate([job1, job2, job3])

    assert [j.title for j in deduplicated] == [
        "Senior Data Scientist",
        "Corporate Recruiter",
        "Product Manager",
    ]


def test_deduplicate_empty_list():
    deduplicated, groups = JobDeduplicator().deduplicate([])

    assert deduplicated == []
    assert groups == []
