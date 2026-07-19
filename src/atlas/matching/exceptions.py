"""Exceptions for the matching module."""


class MatchingError(Exception):
    """Base exception for all matching-related errors."""


class InvalidPolicyError(MatchingError):
    """Raised when a MatchingPolicy is configured with invalid thresholds."""
