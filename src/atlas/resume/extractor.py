"""
Extracts raw resume data (text, sections) from uploaded files (PDF, DOCX, etc).
"""


class ResumeExtractor:
    def extract(self, file_path: str) -> str:
        """Extract raw text content from a resume file."""
        raise NotImplementedError
