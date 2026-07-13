"""
Parses raw resume text into structured fields (name, skills, experience, etc).
"""


class ResumeParser:
    def parse(self, raw_text: str) -> dict:
        """Parse raw resume text into a structured dictionary."""
        raise NotImplementedError
