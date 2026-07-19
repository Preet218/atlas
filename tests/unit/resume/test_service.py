from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from atlas.candidate.models import Preferences
from atlas.resume.service import ResumeService
from tests.fixtures.factories.candidate import create_candidate

MINIMAL_EXTRACTION = {
    "personal": {
        "full_name": "Jamie Rivera",
        "years_of_experience": 5,
    },
    "education": [],
    "experience": [],
    "skills": [
        {"name": "Python", "category": "Programming", "proficiency": "Expert"}
    ],
    "awards": [],
    "projects": [],
    "career_dna": {
        "primary_domains": [],
        "secondary_domains": [],
        "strengths": [],
        "target_domains": [],
    },
}


def make_service(candidate_service, extracted=None):
    extractor = MagicMock()
    extractor.extract_text.return_value = "raw resume text"

    parser = MagicMock()
    parser.parse.return_value = extracted or MINIMAL_EXTRACTION

    return ResumeService(
        candidate_service=candidate_service,
        extractor=extractor,
        parser=parser,
    )


def test_ingest_creates_new_profile_when_none_exists():
    candidate_service = MagicMock()
    candidate_service.exists.return_value = False
    candidate_service.create_profile.side_effect = lambda c: c

    service = make_service(candidate_service)

    result = service.ingest(Path("resume.pdf"))

    assert result.personal.full_name == "Jamie Rivera"
    assert len(result.skills) == 1
    assert result.preferences == Preferences()  # defaults, since no prior profile

    candidate_service.create_profile.assert_called_once()
    candidate_service.update_profile.assert_not_called()


def test_ingest_preserves_existing_preferences_on_update():
    existing = create_candidate(
        preferences=Preferences(
            excluded_companies=["Acme Corp"],
            minimum_base_salary=2_500_000,
        )
    )

    candidate_service = MagicMock()
    candidate_service.exists.return_value = True
    candidate_service.load_profile.return_value = existing
    candidate_service.update_profile.side_effect = lambda c: c

    service = make_service(candidate_service)

    result = service.ingest(Path("resume.pdf"))

    assert result.preferences.excluded_companies == ["Acme Corp"]
    assert result.preferences.minimum_base_salary == 2_500_000

    candidate_service.update_profile.assert_called_once()
    candidate_service.create_profile.assert_not_called()


def test_ingest_replaces_resume_derived_fields_on_update():
    """A re-upload should still replace skills/experience/etc with the
    new resume's content, not merge or preserve the old ones — only
    preferences survive across uploads.
    """

    existing = create_candidate()  # has 3 skills by default (see factory)

    candidate_service = MagicMock()
    candidate_service.exists.return_value = True
    candidate_service.load_profile.return_value = existing
    candidate_service.update_profile.side_effect = lambda c: c

    service = make_service(candidate_service)  # MINIMAL_EXTRACTION has 1 skill

    result = service.ingest(Path("resume.pdf"))

    assert len(result.skills) == 1
    assert result.skills[0].name == "Python"


def test_ingest_calls_extractor_and_parser_in_order():
    candidate_service = MagicMock()
    candidate_service.exists.return_value = False
    candidate_service.create_profile.side_effect = lambda c: c

    extractor = MagicMock()
    extractor.extract_text.return_value = "extracted raw text"

    parser = MagicMock()
    parser.parse.return_value = MINIMAL_EXTRACTION

    service = ResumeService(
        candidate_service=candidate_service,
        extractor=extractor,
        parser=parser,
    )

    resume_path = Path("my_resume.pdf")
    service.ingest(resume_path)

    extractor.extract_text.assert_called_once_with(resume_path)
    parser.parse.assert_called_once_with("extracted raw text")
