"""
Candidate profile persistence.

Responsible for saving and loading the Canonical Candidate Profile (CCP)
from disk.
"""

from __future__ import annotations

import json
from pathlib import Path

from atlas.candidate.exceptions import (
    CandidateNotFoundError,
    CandidateSerializationError,
    CandidateStorageError,
)
from atlas.candidate.models import Candidate


class CandidateStorage:
    """
    Handles persistence of the Candidate Profile.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def exists(self) -> bool:
        """Return True if a profile exists."""
        return self.storage_path.exists()

    def save(self, candidate: Candidate) -> None:
        """
        Save a candidate profile.
        """
        try:
            self.storage_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.storage_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    candidate.model_dump(
                        mode="json",
                    ),
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except Exception as exc:
            raise CandidateStorageError(
                f"Unable to save candidate profile: {exc}"
            ) from exc

    def load(self) -> Candidate:
        """
        Load a candidate profile.
        """

        if not self.exists():
            raise CandidateNotFoundError(
                str(self.storage_path)
            )

        try:
            with self.storage_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return Candidate.model_validate(data)

        except Exception as exc:
            raise CandidateSerializationError(
                f"Unable to deserialize candidate profile: {exc}"
            ) from exc

    def delete(self) -> None:
        """
        Delete the stored profile.
        """

        if self.exists():
            self.storage_path.unlink()
