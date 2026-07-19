from __future__ import annotations

from atlas.llm.client import LLMClient
from atlas.resume.parser import ResumeParser
from atlas.resume.schema import SYSTEM_PROMPT


def make_fake_llm(return_value: dict):
    class FakeLLMClient(LLMClient):
        def __init__(self):
            pass  # skip real LLMClient.__init__, no client/model needed

        def complete_json(self, system_prompt, user_prompt, temperature=0.0):
            self.captured_system_prompt = system_prompt
            self.captured_user_prompt = user_prompt
            return return_value

    return FakeLLMClient()


def test_parse_returns_llm_output_as_is():
    extracted = {
        "personal": {"full_name": "Jamie Rivera", "years_of_experience": 5},
        "education": [],
        "experience": [],
        "skills": [],
        "awards": [],
        "projects": [],
        "career_dna": {
            "primary_domains": [],
            "secondary_domains": [],
            "strengths": [],
            "target_domains": [],
        },
    }

    fake_llm = make_fake_llm(extracted)
    parser = ResumeParser(llm_client=fake_llm)

    result = parser.parse("some resume text")

    assert result == extracted


def test_parse_does_not_include_preferences_key():
    fake_llm = make_fake_llm({"personal": {"full_name": "Jamie Rivera"}})
    parser = ResumeParser(llm_client=fake_llm)

    result = parser.parse("some resume text")

    assert "preferences" not in result


def test_parse_sends_system_prompt_and_wraps_resume_text():
    fake_llm = make_fake_llm({})
    parser = ResumeParser(llm_client=fake_llm)

    parser.parse("Jamie Rivera's resume content")

    assert fake_llm.captured_system_prompt == SYSTEM_PROMPT
    assert "Jamie Rivera's resume content" in fake_llm.captured_user_prompt
