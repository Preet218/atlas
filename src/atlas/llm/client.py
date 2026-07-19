"""Thin wrapper around the OpenAI client for structured JSON extraction.

Kept deliberately minimal: one method, one job. Higher-level parsing
logic (prompts, controlled vocabularies, retries) lives in the modules
that use this — e.g. atlas.resume.parser — this client only knows how
to ask an LLM for JSON and hand back a dict.

NOTE: this makes a real network call to OpenAI's API when used without
an injected client. It has not been exercised against a live API in
this environment (no network access here) — the `openai` SDK usage
below follows their documented, stable chat-completions + JSON-mode
pattern, but treat this as unverified until it's been run once against
a real API key.
"""

from __future__ import annotations

import json
from typing import Any

from atlas.config.settings import get_settings
from atlas.llm.exceptions import LLMConfigurationError, LLMResponseError


class LLMClient:
    """Thin, injectable wrapper around the OpenAI chat completions API."""

    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        """
        Args:
            client: An already-constructed OpenAI client (or any object
                exposing the same `chat.completions.create` interface).
                Inject a fake/mock here in tests. If not provided, a
                real client is lazily constructed from settings on
                first use, so importing/instantiating this class never
                requires an API key up front — only actually calling
                `complete_json` does.
            model: Model name to use. Defaults to settings.openai_model.
        """
        self._client = client
        self._model = model

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        settings = get_settings()

        if not settings.openai_api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is not set. Set it in your .env file to "
                "use LLM-based features like resume parsing."
            )

        import openai

        self._client = openai.OpenAI(api_key=settings.openai_api_key)
        return self._client

    def _get_model(self) -> str:
        if self._model is not None:
            return self._model

        return get_settings().openai_model

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """Ask the model for a JSON object and return it as a dict.

        Uses temperature=0 by default for as-deterministic-as-possible
        extraction — this is a data-extraction task, not a creative one.
        """

        client = self._get_client()

        response = client.chat.completions.create(
            model=self._get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError) as exc:
            raise LLMResponseError(f"LLM response was not valid JSON: {exc}") from exc
