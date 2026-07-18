"""Shared enumerations used across Atlas."""

from __future__ import annotations

from enum import StrEnum


class JobPlatform(StrEnum):
    """Supported job platforms."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    ASHBY = "ashby"
    LINKEDIN = "linkedin"
