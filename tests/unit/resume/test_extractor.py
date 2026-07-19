from __future__ import annotations

from types import SimpleNamespace

import pytest

from atlas.resume.exceptions import ResumeExtractionError, UnsupportedResumeFormatError
from atlas.resume.extractor import ResumeTextExtractor


def test_extract_text_from_plain_txt(tmp_path):
    path = tmp_path / "resume.txt"
    path.write_text("Jamie Rivera\nSenior Data Scientist", encoding="utf-8")

    text = ResumeTextExtractor().extract_text(path)

    assert text == "Jamie Rivera\nSenior Data Scientist"


def test_extract_text_from_markdown(tmp_path):
    path = tmp_path / "resume.md"
    path.write_text("# Jamie Rivera", encoding="utf-8")

    text = ResumeTextExtractor().extract_text(path)

    assert text == "# Jamie Rivera"


def test_unsupported_format_raises(tmp_path):
    path = tmp_path / "resume.xyz"
    path.write_text("content", encoding="utf-8")

    with pytest.raises(UnsupportedResumeFormatError):
        ResumeTextExtractor().extract_text(path)


def test_empty_text_raises_extraction_error(tmp_path):
    path = tmp_path / "resume.txt"
    path.write_text("   \n  ", encoding="utf-8")

    with pytest.raises(ResumeExtractionError):
        ResumeTextExtractor().extract_text(path)


def test_extract_text_from_pdf(tmp_path, mocker):
    path = tmp_path / "resume.pdf"
    path.write_bytes(b"%PDF-fake")  # content is irrelevant, pypdf is mocked

    fake_page_1 = SimpleNamespace(extract_text=lambda: "Page one text")
    fake_page_2 = SimpleNamespace(extract_text=lambda: "Page two text")
    fake_reader = SimpleNamespace(pages=[fake_page_1, fake_page_2])

    mock_pypdf = SimpleNamespace(PdfReader=lambda p: fake_reader)
    mocker.patch.dict("sys.modules", {"pypdf": mock_pypdf})

    text = ResumeTextExtractor().extract_text(path)

    assert text == "Page one text\nPage two text"


def test_extract_pdf_wraps_failures(tmp_path, mocker):
    path = tmp_path / "resume.pdf"
    path.write_bytes(b"%PDF-fake")

    def boom(p):
        raise ValueError("corrupt PDF")

    mock_pypdf = SimpleNamespace(PdfReader=boom)
    mocker.patch.dict("sys.modules", {"pypdf": mock_pypdf})

    with pytest.raises(ResumeExtractionError):
        ResumeTextExtractor().extract_text(path)


def test_extract_text_from_docx(tmp_path, mocker):
    path = tmp_path / "resume.docx"
    path.write_bytes(b"fake docx bytes")  # content is irrelevant, docx is mocked

    fake_paragraphs = [
        SimpleNamespace(text="Jamie Rivera"),
        SimpleNamespace(text="Senior Data Scientist"),
    ]
    fake_document = SimpleNamespace(paragraphs=fake_paragraphs)

    mock_docx = SimpleNamespace(Document=lambda p: fake_document)
    mocker.patch.dict("sys.modules", {"docx": mock_docx})

    text = ResumeTextExtractor().extract_text(path)

    assert text == "Jamie Rivera\nSenior Data Scientist"


def test_extract_docx_wraps_failures(tmp_path, mocker):
    path = tmp_path / "resume.docx"
    path.write_bytes(b"fake docx bytes")

    def boom(p):
        raise ValueError("corrupt docx")

    mock_docx = SimpleNamespace(Document=boom)
    mocker.patch.dict("sys.modules", {"docx": mock_docx})

    with pytest.raises(ResumeExtractionError):
        ResumeTextExtractor().extract_text(path)
