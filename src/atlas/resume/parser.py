"""ResumeParser: turns raw resume text into a CandidateBuilder-shaped dict."""

from __future__ import annotations

from typing import Any

from atlas.llm.client import LLMClient
from atlas.resume.schema import SYSTEM_PROMPT, build_user_prompt


class ResumeParser:
    """Extracts structured candidate data from raw resume text via an LLM."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    def parse(self, resume_text: str) -> dict[str, Any]:
        """Extract structured data matching CandidateBuilder's input shape.

        The returned dict deliberately has no "preferences" key — see
        atlas.resume.schema for why that's left for the caller to merge
        in from the candidate's existing profile.
        """

        return self._llm.complete_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(resume_text),
        )
