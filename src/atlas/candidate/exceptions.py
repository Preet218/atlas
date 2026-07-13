"""
Candidate domain exceptions.

Keeping domain-specific exceptions together makes error handling
predictable and avoids leaking generic Python exceptions into
higher layers such as services, APIs, and CLIs.
"""


class CandidateError(Exception):
    """Base exception for the Candidate domain."""

    pass


class CandidateNotFoundError(CandidateError):
    """Raised when a candidate profile cannot be found."""

    def __init__(self, path: str):
        super().__init__(f"Candidate profile not found: {path}")


class CandidateAlreadyExistsError(CandidateError):
    """Raised when attempting to create an existing profile."""

    def __init__(self, identifier: str):
        super().__init__(
            f"Candidate profile '{identifier}' already exists."
        )


class CandidateValidationError(CandidateError):
    """Raised when candidate data is invalid."""

    def __init__(self, message: str):
        super().__init__(message)


class CandidateStorageError(CandidateError):
    """Raised when reading or writing candidate data fails."""

    def __init__(self, message: str):
        super().__init__(message)


class CandidateSerializationError(CandidateError):
    """Raised when serialization or deserialization fails."""

    def __init__(self, message: str):
        super().__init__(message)
