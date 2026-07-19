"""ResumeService: the public entry point for turning a resume file into
an updated Candidate profile.

Pipeline: extract text -> LLM-parse into structured data -> merge with
existing preferences -> validate via CandidateBuilder -> save.
"""

from __future__ import annotations

from pathlib import Path

from atlas.candidate.builder import CandidateBuilder
from atlas.candidate.models import Candidate, Preferences
from atlas.candidate.service import CandidateService
from atlas.resume.extractor import ResumeTextExtractor
from atlas.resume.parser import ResumeParser


class ResumeService:
    """Ingests a resume file and creates/updates the candidate's profile."""

    def __init__(
        self,
        candidate_service: CandidateService,
        extractor: ResumeTextExtractor | None = None,
        parser: ResumeParser | None = None,
    ) -> None:
        self._candidate_service = candidate_service
        self._extractor = extractor or ResumeTextExtractor()
        self._parser = parser or ResumeParser()

    def ingest(self, resume_path: Path) -> Candidate:
        """Parse a resume file and save it as the candidate's profile.

        Existing preferences are always preserved across re-uploads —
        a resume never states things like excluded companies or a
        minimum salary, so overwriting preferences on every upload
        would silently wipe out choices the candidate made
        deliberately.
        """

        text = self._extractor.extract_text(resume_path)
        extracted = self._parser.parse(text)

        profile_exists = self._candidate_service.exists()

        preferences = (
            self._candidate_service.load_profile().preferences
            if profile_exists
            else Preferences()
        )

        data = {
            **extracted,
            "preferences": preferences.model_dump(mode="json"),
        }

        candidate = CandidateBuilder().build(data)

        if profile_exists:
            return self._candidate_service.update_profile(candidate)

        return self._candidate_service.create_profile(candidate)
