"""Matching policy: configurable thresholds for JobMatcher and JobDeduplicator.

Per docs/architecture.md, "Policies encode configurable business rules."
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.matching.exceptions import InvalidPolicyError


@dataclass(frozen=True)
class MatchingPolicy:
    """Configurable thresholds used by the matching domain.

    compensation_floor_ratio:
        A job is hard-excluded if its max salary falls below this
        fraction of the candidate's minimum_base_salary. This is
        intentionally more lenient than a strict "must meet minimum"
        rule — Ranking already scores compensation continuously, so
        Matching only filters out roles that are drastically below
        expectations rather than merely slightly below.

    title_similarity_threshold:
        Minimum ratio (0-1, via difflib.SequenceMatcher) between two
        normalized job titles at the same normalized company for them
        to be treated as duplicate postings.

    require_country_match_for_dedup:
        When True, two postings are only treated as duplicates if their
        countries match (or at least one has no country specified).
        Prevents merging genuinely different open reqs for the same
        title at the same company in different countries.
    """

    compensation_floor_ratio: float = 0.5
    title_similarity_threshold: float = 0.85
    require_country_match_for_dedup: bool = True

    @classmethod
    def default(cls) -> "MatchingPolicy":
        """Return Atlas's default matching policy."""
        return cls()

    def validate(self) -> None:
        """Raise InvalidPolicyError if thresholds are misconfigured."""

        if not (0.0 <= self.compensation_floor_ratio <= 1.0):
            raise InvalidPolicyError(
                "compensation_floor_ratio must be between 0.0 and 1.0, got "
                f"{self.compensation_floor_ratio}."
            )

        if not (0.0 <= self.title_similarity_threshold <= 1.0):
            raise InvalidPolicyError(
                "title_similarity_threshold must be between 0.0 and 1.0, "
                f"got {self.title_similarity_threshold}."
            )
