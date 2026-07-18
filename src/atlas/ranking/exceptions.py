"""Exceptions for the ranking module."""


class RankingError(Exception):
    """Base exception for all ranking-related errors."""


class InvalidPolicyError(RankingError):
    """Raised when a RankingPolicy's weights are not configured correctly."""
