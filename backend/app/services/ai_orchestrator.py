from __future__ import annotations

from typing import Any

from ai_trading_agent import GeminiConfigurationError, GeminiRequestError, run_pipeline
from ai_trading_agent.agents import AgentResponseError

from app.core.exceptions import AiPipelineError
from app.schemas.agent_context import AgentContextPayload


class AiOrchestrator:
    """Runs the Gemini multi-agent pipeline against backend context."""

    def run_agents(self, context: AgentContextPayload) -> dict[str, Any]:
        try:
            return run_pipeline(context.to_agent_dict())
        except GeminiConfigurationError as exc:
            raise AiPipelineError(
                "Gemini is not configured. Set GEMINI_API_KEY before calling /api/analyze."
            ) from exc
        except GeminiRequestError as exc:
            raise AiPipelineError(f"Gemini request failed: {exc}") from exc
        except AgentResponseError as exc:
            raise AiPipelineError(f"Gemini returned an invalid agent response: {exc}") from exc
        except ValueError as exc:
            raise AiPipelineError(f"AI pipeline returned invalid JSON: {exc}") from exc
