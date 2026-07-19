"""Exceptions for the LLM module."""


class LLMError(Exception):
    """Base exception for all LLM-related errors."""


class LLMConfigurationError(LLMError):
    """Raised when the LLM client is used without a valid API key."""


class LLMResponseError(LLMError):
    """Raised when the LLM's response can't be parsed as valid JSON."""
