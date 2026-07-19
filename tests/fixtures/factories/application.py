"""Factory functions for creating Application test instances."""

from __future__ import annotations

from atlas.application.models import Application
from tests.fixtures.factories.job import create_job


def create_application(**overrides) -> Application:
    """Create an Application with sensible defaults."""

    data = {
        "job": create_job(),
    }

    data.update(overrides)
    return Application(**data)
