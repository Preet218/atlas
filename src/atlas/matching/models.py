"""Domain models for job matching and deduplication."""

from __future__ import annotations

from pydantic import BaseModel, Field

from atlas.job.models import JobPosting


class MatchResult(BaseModel):
    """The hard eligibility verdict for a single job posting.

    Unlike RankedJob's continuous score, this is a categorical decision:
    a job either qualifies to be shown to the candidate or it doesn't.
    `reasons` is always populated (positive confirmation or a rejection
    reason) per PEP-007's explainability requirement.
    """

    job: JobPosting

    is_match: bool

    reasons: list[str] = Field(default_factory=list)


class DuplicateGroup(BaseModel):
    """A cluster of postings identified as the same underlying role."""

    canonical: JobPosting

    duplicates: list[JobPosting] = Field(default_factory=list)


class MatchingResult(BaseModel):
    """The full output of processing a batch of jobs for a candidate."""

    eligible: list[JobPosting] = Field(default_factory=list)

    match_results: list[MatchResult] = Field(default_factory=list)

    duplicate_groups: list[DuplicateGroup] = Field(default_factory=list)
