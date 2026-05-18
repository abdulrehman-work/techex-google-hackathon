"""Google Gemini client adapter for the agent pipeline."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini SDK or API key is unavailable."""


class GeminiRequestError(RuntimeError):
    """Raised when Gemini rejects or fails a generation request."""


DEFAULT_MODEL_FALLBACKS: tuple[str, ...] = (
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-3-flash-preview",
)


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


def resolve_model_chain(primary: str | None = None) -> list[str]:
    """Build an ordered list of models to try, primary first, without duplicates."""
    env_fallbacks = os.getenv("GEMINI_MODEL_FALLBACKS", "").strip()
    if env_fallbacks:
        candidates = [
            normalize_model_name(part)
            for part in env_fallbacks.split(",")
            if part.strip()
        ]
    else:
        candidates = [normalize_model_name(name) for name in DEFAULT_MODEL_FALLBACKS]

    if primary:
        primary_name = normalize_model_name(primary)
        chain = [primary_name]
        for model in candidates:
            if model not in chain:
                chain.append(model)
        return chain

    deduped: list[str] = []
    for model in candidates:
        if model not in deduped:
            deduped.append(model)
    return deduped


def _api_error_code(exc: Exception) -> int | None:
    """Extract an HTTP-style status code from SDK errors."""
    for attr in ("code", "status_code", "status"):
        value = getattr(exc, attr, None)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue

    match = re.search(r"\b([45]\d{2})\b", str(exc))
    if match:
        return int(match.group(1))
    return None


def _should_retry_same_model(exc: Exception) -> bool:
    """Retry the current model for transient overload errors."""
    code = _api_error_code(exc)
    if code in {500, 503}:
        return True

    message = str(exc).lower()
    return any(
        marker in message
        for marker in ("unavailable", "high demand", "overloaded", "try again later")
    )


def _should_try_next_model(exc: Exception) -> bool:
    """Return True when another model in the chain may succeed."""
    code = _api_error_code(exc)
    if code in {404, 429, 500, 503}:
        return True

    message = str(exc).lower()
    retriable_markers = (
        "resource_exhausted",
        "quota",
        "rate limit",
        "429",
        "unavailable",
        "high demand",
        "not found",
        "unexpected model name",
        "overloaded",
    )
    return any(marker in message for marker in retriable_markers)


def _same_model_retry_limit(exc: Exception) -> int:
    """How many attempts to make on one model before switching."""
    configured = os.getenv("GEMINI_MAX_RETRIES", "").strip()
    if configured.isdigit():
        return max(1, int(configured))

    code = _api_error_code(exc)
    if code == 503:
        return 3
    if code == 429:
        return 1
    return 2


def _retry_delay_seconds(exc: Exception, attempt: int) -> float:
    """Use API retry hints when present; otherwise exponential backoff."""
    message = str(exc)
    match = re.search(r"retry in ([0-9]+(?:\.[0-9]+)?)s", message, flags=re.IGNORECASE)
    if match:
        return min(float(match.group(1)), 60.0)

    code = _api_error_code(exc)
    if code == 503:
        return min(2.0 * attempt, 8.0)
    return min(1.0 * attempt, 4.0)


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

        primary_model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._model_chain = resolve_model_chain(primary_model)
        self._active_model = self._model_chain[0]
        self.model = self._active_model
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

    def _models_to_try(self) -> list[str]:
        ordered = [self._active_model]
        for model in self._model_chain:
            if model not in ordered:
                ordered.append(model)
        return ordered

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
        failures: list[str] = []
        models_to_try = self._models_to_try()
        for index, model_name in enumerate(models_to_try):
            for attempt in range(1, 4):
                try:
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=task,
                        config=self._generation_config(
                            system_instruction=system_instruction,
                            response_schema=response_schema,
                        ),
                    )
                except self._errors.APIError as exc:
                    failures.append(f"{model_name} (attempt {attempt}): {exc}")
                    retry_limit = _same_model_retry_limit(exc)
                    if _should_retry_same_model(exc) and attempt < retry_limit:
                        time.sleep(_retry_delay_seconds(exc, attempt))
                        continue

                    if _should_try_next_model(exc) and index < len(models_to_try) - 1:
                        time.sleep(_retry_delay_seconds(exc, attempt))
                        break

                    tried = ", ".join(models_to_try)
                    detail = " | ".join(failures)
                    raise GeminiRequestError(
                        f"{agent_name} Gemini request failed for all models [{tried}]. "
                        "Set GEMINI_MODEL / GEMINI_MODEL_FALLBACKS or enable billing. "
                        f"Errors: {detail}"
                    ) from exc
                else:
                    self._active_model = model_name
                    self.model = model_name
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"{agent_name} returned invalid JSON: {response.text}"
                        ) from exc

        tried = ", ".join(models_to_try)
        detail = " | ".join(failures) if failures else "unknown error"
        raise GeminiRequestError(
            f"{agent_name} Gemini request failed for all models [{tried}]. "
            "Set GEMINI_MODEL / GEMINI_MODEL_FALLBACKS or enable billing. "
            f"Errors: {detail}"
        )
