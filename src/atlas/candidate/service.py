"""
Candidate service.

The service layer provides the public API for working with the
Canonical Candidate Profile (CCP). All modules should interact with
candidate data through this service rather than accessing storage
directly.
"""

from __future__ import annotations

from pathlib import Path

from atlas.candidate.models import Candidate
from atlas.candidate.storage import CandidateStorage


class CandidateService:
    """
    Service responsible for managing the candidate profile.
    """

    def __init__(self, storage_path: Path):
        self._storage = CandidateStorage(storage_path)

    def exists(self) -> bool:
        """Return True if a candidate profile exists."""
        return self._storage.exists()

    def create_profile(self, candidate: Candidate) -> Candidate:
        """
        Create a new candidate profile.

        For the MVP we overwrite any existing profile.
        Versioning will be added later.
        """
        self._storage.save(candidate)
        return candidate

    def load_profile(self) -> Candidate:
        """
        Load the current candidate profile.
        """
        return self._storage.load()

    def update_profile(self, candidate: Candidate) -> Candidate:
        """
        Replace the existing profile.
        """
        self._storage.save(candidate)
        return candidate

    def delete_profile(self) -> None:
        """
        Delete the current profile.
        """
        self._storage.delete()

    def show_profile(self) -> str:
        """
        Return a human-readable summary of the candidate profile.
        """
        candidate = self.load_profile()

        lines = [
            "=" * 60,
            "ATLAS CANDIDATE PROFILE",
            "=" * 60,
            f"Name: {candidate.personal.full_name}",
            f"Current Role: {candidate.personal.current_role}",
            f"Company: {candidate.personal.current_company}",
            f"Location: {candidate.personal.location}",
            f"Experience: {candidate.personal.years_of_experience} years",
            "",
            "Preferred Roles:",
        ]

        for role in candidate.preferences.preferred_roles:
            lines.append(f"  • {role}")

        lines.extend(
            [
                "",
                "Preferred Countries:",
            ]
        )

        for country in candidate.preferences.preferred_countries:
            lines.append(f"  • {country}")

        lines.extend(
            [
                "",
                "Excluded Companies:",
            ]
        )

        for company in candidate.preferences.excluded_companies:
            lines.append(f"  • {company}")

        return "\n".join(lines)
