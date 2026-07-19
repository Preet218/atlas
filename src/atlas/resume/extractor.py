"""Extracts raw text from resume files (PDF, DOCX, or plain text).

NOTE: PDF/DOCX extraction (`pypdf`/`python-docx`) hasn't been exercised
in this environment (no network access to install these packages
here). The usage below follows each library's standard, documented
API — treat it as unverified until it's been run once against a real
file after `uv sync` pulls the new dependencies.
"""

from __future__ import annotations

from pathlib import Path

from atlas.resume.exceptions import ResumeExtractionError, UnsupportedResumeFormatError

_SUPPORTED_SUFFIXES = (".pdf", ".docx", ".txt", ".md")


class ResumeTextExtractor:
    """Extracts plain text from a resume file, regardless of format."""

    def extract_text(self, path: Path) -> str:
        """Extract text from a .pdf, .docx, .txt, or .md file."""

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            text = self._extract_pdf(path)
        elif suffix == ".docx":
            text = self._extract_docx(path)
        elif suffix in (".txt", ".md"):
            text = path.read_text(encoding="utf-8")
        else:
            raise UnsupportedResumeFormatError(
                f"Unsupported resume format: {suffix!r}. Supported: "
                f"{', '.join(_SUPPORTED_SUFFIXES)}"
            )

        text = text.strip()

        if not text:
            raise ResumeExtractionError(
                f"No extractable text found in {path.name} — it may be a "
                "scanned/image-only PDF, which isn't supported yet."
            )

        return text

    def _extract_pdf(self, path: Path) -> str:
        import pypdf

        try:
            reader = pypdf.PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as exc:
            raise ResumeExtractionError(f"Failed to read PDF {path.name}: {exc}") from exc

        return "\n".join(pages)

    def _extract_docx(self, path: Path) -> str:
        import docx

        try:
            document = docx.Document(str(path))
            paragraphs = [p.text for p in document.paragraphs]
        except Exception as exc:
            raise ResumeExtractionError(f"Failed to read DOCX {path.name}: {exc}") from exc

        return "\n".join(paragraphs)
