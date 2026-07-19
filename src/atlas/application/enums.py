"""Enumerations for the application domain."""

from __future__ import annotations

from enum import Enum


class ApplicationStatus(str, Enum):
    """The lifecycle stage of a submitted job application."""

    DRAFT = "draft"
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
