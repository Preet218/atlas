"""RankingService: the public entry point for the ranking domain.

Other modules should rank jobs through this service rather than
constructing a JobRanker directly, matching the pattern used by
DiscoveryService, CandidateService, and JobService.
"""

from __future__ import annotations

from datetime import datetime

from atlas.candidate.models import Candidate
from atlas.job.models import JobPosting
from atlas.ranking.models import RankedJob
from atlas.ranking.policy import RankingPolicy
from atlas.ranking.ranker import JobRanker


class RankingService:
    """Provides the RankJobs use case: score and order jobs for a candidate."""

    def __init__(
        self,
        ranker: JobRanker | None = None,
        policy: RankingPolicy | None = None,
    ) -> None:
        self._ranker = ranker or JobRanker(policy=policy)

    def rank(
        self,
        candidate: Candidate,
        jobs: list[JobPosting],
        now: datetime | None = None,
    ) -> list[RankedJob]:
        """Rank job postings for a candidate, best match first.

        `jobs` is expected to already be filtered for hard eligibility
        via atlas.matching.MatchingService — this method scores and
        orders by fit, it doesn't decide who's eligible. The typical
        pipeline is: discover -> MatchingService.filter_eligible ->
        RankingService.rank.
        """

        scored = [self._ranker.score(candidate, job, now=now) for job in jobs]

        scored.sort(key=lambda ranked: ranked.overall_score, reverse=True)

        return scored

