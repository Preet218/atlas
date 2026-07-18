"""Domain models for job ranking."""

from __future__ import annotations

from pydantic import BaseModel, Field

from atlas.job.models import JobPosting
from atlas.ranking.enums import MatchStrength


class DimensionScore(BaseModel):
    """The score contributed by a single ranking dimension.

    Kept as an explicit value object (rather than a bare float) so every
    ranking result carries its own explanation, per PEP-007 (Explainable
    Intelligence): a candidate should always understand why a job scored
    the way it did.
    """

    name: str

    score: float = Field(ge=0, le=100)

    weight: float = Field(ge=0, le=1)

    reason: str

    @property
    def weighted_score(self) -> float:
        """The contribution this dimension makes to the overall score."""
        return self.score * self.weight


class RankedJob(BaseModel):
    """A job posting scored against a candidate profile."""

    job: JobPosting

    overall_score: float = Field(ge=0, le=100)

    match_strength: MatchStrength

    dimension_scores: list[DimensionScore] = Field(default_factory=list)

    reasons: list[str] = Field(default_factory=list)

    disqualified: bool = False

    disqualification_reason: str | None = None
