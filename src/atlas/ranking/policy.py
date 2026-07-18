"""Ranking policy: configurable weights for the JobRanker.

Per docs/architecture.md, "Policies encode configurable business rules"
and "allow behavior to evolve without changing service structure." The
weights below are the business rule; JobRanker is the mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.ranking.exceptions import InvalidPolicyError

_WEIGHT_TOLERANCE = 1e-6


@dataclass(frozen=True)
class RankingPolicy:
    """Configurable weights used to combine dimension scores.

    Weights must sum to 1.0 so that `overall_score` stays on a 0-100
    scale. Use `RankingPolicy.default()` unless a candidate or workflow
    needs a different emphasis (e.g. weighting compensation more heavily
    for a candidate optimizing purely for pay).
    """

    skills_weight: float = 0.35
    role_weight: float = 0.15
    location_weight: float = 0.15
    compensation_weight: float = 0.15
    experience_weight: float = 0.10
    recency_weight: float = 0.10

    @classmethod
    def default(cls) -> "RankingPolicy":
        """Return Atlas's default ranking policy."""
        return cls()

    def validate(self) -> None:
        """Raise InvalidPolicyError if the weights are misconfigured."""

        weights = [
            self.skills_weight,
            self.role_weight,
            self.location_weight,
            self.compensation_weight,
            self.experience_weight,
            self.recency_weight,
        ]

        if any(weight < 0 for weight in weights):
            raise InvalidPolicyError("Ranking policy weights must not be negative.")

        total = sum(weights)

        if abs(total - 1.0) > _WEIGHT_TOLERANCE:
            raise InvalidPolicyError(
                f"Ranking policy weights must sum to 1.0, got {total}."
            )
