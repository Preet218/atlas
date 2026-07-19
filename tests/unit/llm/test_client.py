from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from atlas.llm.client import LLMClient
from atlas.llm.exceptions import LLMConfigurationError, LLMResponseError


def make_fake_openai_client(content: str):
    """Build a minimal stand-in for the OpenAI client's response shape."""

    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: fake_response,
            )
        )
    )

    return fake_client


def test_complete_json_returns_parsed_dict():
    payload = {"name": "Preet Patel", "skills": ["Python", "PyTorch"]}
    client = LLMClient(
        client=make_fake_openai_client(json.dumps(payload)),
        model="gpt-4o-mini",
    )

    result = client.complete_json("system prompt", "user prompt")

    assert result == payload


def test_complete_json_raises_on_invalid_json():
    client = LLMClient(
        client=make_fake_openai_client("not valid json"),
        model="gpt-4o-mini",
    )

    with pytest.raises(LLMResponseError):
        client.complete_json("system prompt", "user prompt")


def test_complete_json_passes_prompts_and_model_to_client():
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )

    client = LLMClient(client=fake_client, model="gpt-4o-mini")
    client.complete_json("system prompt", "user prompt")

    assert captured["model"] == "gpt-4o-mini"
    assert captured["messages"][0] == {"role": "system", "content": "system prompt"}
    assert captured["messages"][1] == {"role": "user", "content": "user prompt"}
    assert captured["response_format"] == {"type": "json_object"}
    assert captured["temperature"] == 0.0


def test_missing_api_key_raises_configuration_error(mocker):
    fake_settings = SimpleNamespace(openai_api_key="", openai_model="gpt-4o-mini")
    mocker.patch("atlas.llm.client.get_settings", return_value=fake_settings)

    client = LLMClient()  # no injected client -> lazily builds a real one

    with pytest.raises(LLMConfigurationError):
        client.complete_json("system prompt", "user prompt")


def test_default_model_comes_from_settings_when_not_overridden(mocker):
    fake_settings = SimpleNamespace(openai_api_key="sk-test", openai_model="gpt-4o")
    mocker.patch("atlas.llm.client.get_settings", return_value=fake_settings)

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
        )

    fake_openai_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )

    mock_openai_module = SimpleNamespace(
        OpenAI=lambda api_key: fake_openai_client,
    )
    mocker.patch.dict("sys.modules", {"openai": mock_openai_module})

    client = LLMClient()  # no model override -> should use settings.openai_model
    client.complete_json("system prompt", "user prompt")

    assert captured["model"] == "gpt-4o"
