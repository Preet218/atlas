"""MatchingService: the public entry point for the matching domain.

Combines deduplication and hard eligibility filtering. Intended to run
between Discovery and Ranking: discover -> match -> rank.
"""

from __future__ import annotations

from atlas.candidate.models import Candidate
from atlas.job.models import JobPosting
from atlas.matching.deduplicator import JobDeduplicator
from atlas.matching.matcher import JobMatcher
from atlas.matching.models import MatchingResult
from atlas.matching.policy import MatchingPolicy


class MatchingService:
    """Provides the deduplicate-and-match use case."""

    def __init__(
        self,
        matcher: JobMatcher | None = None,
        deduplicator: JobDeduplicator | None = None,
        policy: MatchingPolicy | None = None,
    ) -> None:
        self._matcher = matcher or JobMatcher(policy=policy)
        self._deduplicator = deduplicator or JobDeduplicator(policy=policy)

    def process(
        self,
        candidate: Candidate,
        jobs: list[JobPosting],
    ) -> MatchingResult:
        """Deduplicate a batch of jobs, then evaluate each for eligibility."""

        deduplicated, duplicate_groups = self._deduplicator.deduplicate(jobs)

        match_results = [
            self._matcher.evaluate(candidate, job) for job in deduplicated
        ]

        eligible = [result.job for result in match_results if result.is_match]

        return MatchingResult(
            eligible=eligible,
            match_results=match_results,
            duplicate_groups=duplicate_groups,
        )

    def filter_eligible(
        self,
        candidate: Candidate,
        jobs: list[JobPosting],
    ) -> list[JobPosting]:
        """Convenience method: return only the deduplicated, eligible jobs."""

        return self.process(candidate, jobs).eligible
