"""Enumerations for the ranking domain."""

from __future__ import annotations

from enum import Enum


class MatchStrength(str, Enum):
    """Human-readable tier derived from a job's overall ranking score."""

    STRONG = "strong"
    GOOD = "good"
    FAIR = "fair"
    WEAK = "weak"

    @classmethod
    def from_score(cls, score: float) -> "MatchStrength":
        """Map a 0-100 overall score to a match strength tier."""

        if score >= 80:
            return cls.STRONG

        if score >= 60:
            return cls.GOOD

        if score >= 40:
            return cls.FAIR

        return cls.WEAK
