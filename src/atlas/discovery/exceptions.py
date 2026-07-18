"""Exceptions for the discovery module."""


class DiscoveryError(Exception):
    """Base exception for all discovery-related errors."""


class ConnectorNotFoundError(DiscoveryError):
    """Raised when no connector is registered for a platform."""
