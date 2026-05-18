"""Google Gemini client adapter for the agent pipeline."""

from __future__ import annotations

import json
import os
from typing import Any


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini SDK or API key is unavailable."""


class GeminiRequestError(RuntimeError):
    """Raised when Gemini rejects or fails a generation request."""


def normalize_model_name(model: str) -> str:
    """Normalize common Gemini model name inputs for the GenAI SDK.

    The Google GenAI SDK examples use short names such as
    ``gemini-3-flash-preview``. Users sometimes copy REST resource names like
    ``models/gemini-3-flash-preview``; the SDK can often handle both, but using
    the short name keeps behavior aligned with the current Python docs.
    """
    cleaned = model.strip()
    if cleaned.startswith("models/"):
        return cleaned.removeprefix("models/")
    return cleaned


class GeminiClient:
    """Thin wrapper around the official Google GenAI SDK."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        try:
            from google import genai
            from google.genai import errors, types
        except ImportError as exc:
            raise GeminiConfigurationError(
                "Missing Gemini SDK. Install it with: pip install google-genai"
            ) from exc

        self.model = normalize_model_name(
            model or os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        )
        self.temperature = temperature
        self._errors = errors
        self._types = types
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is required for Gemini-powered agents."
            )

        self._client = genai.Client(api_key=resolved_key)

    def _generation_config(
        self,
        *,
        system_instruction: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        config: dict[str, Any] = {
            "system_instruction": system_instruction,
            "temperature": self.temperature,
        }

        fields = getattr(self._types.GenerateContentConfig, "model_fields", {})
        if "response_format" in fields:
            config["response_format"] = {
                "text": {
                    "mime_type": "application/json",
                    "schema": response_schema,
                }
            }
        else:
            config["response_mime_type"] = "application/json"
            config["response_json_schema"] = response_schema

        return config

    def generate_json(
        self,
        *,
        agent_name: str,
        role: str,
        task: str,
        payload: dict[str, Any],
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        system_instruction = (
            f"You are the {agent_name}, acting as a {role}. "
            "Use only the supplied JSON input. Do not scrape, browse, or invent external facts. "
            "Return valid JSON only. All numeric scores must be on a 0-100 scale."
        )
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=task,
                config=self._generation_config(
                    system_instruction=system_instruction,
                    response_schema=response_schema,
                ),
            )
        except self._errors.APIError as exc:
            raise GeminiRequestError(
                f"{agent_name} Gemini request failed for model '{self.model}'. "
                "Check GEMINI_MODEL or unset it to use the default "
                "'gemini-3-flash-preview'. Original error: "
                f"{exc}"
            ) from exc

        try:
            return json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{agent_name} returned invalid JSON: {response.text}") from exc
