"""Exceptions for the resume module."""


class ResumeError(Exception):
    """Base exception for all resume-related errors."""


class UnsupportedResumeFormatError(ResumeError):
    """Raised when a resume file's format isn't supported for extraction."""


class ResumeExtractionError(ResumeError):
    """Raised when text can't be extracted from a resume file."""
