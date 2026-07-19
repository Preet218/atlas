"""Exceptions for the application module."""


class ApplicationError(Exception):
    """Base exception for all application-related errors."""


class InvalidStatusTransitionError(ApplicationError):
    """Raised when an application's status cannot legally change as requested."""


class FollowUpNotFoundError(ApplicationError):
    """Raised when a follow-up reminder can't be found on an application."""
