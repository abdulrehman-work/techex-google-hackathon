from __future__ import annotations

from typing import Any

from app.schemas.agent_context import AgentContextPayload


class AiOrchestrator:
    """Runs the multi-agent pipeline (stubbed until Gemini integration is wired)."""

    def run_agents(self, context: AgentContextPayload) -> dict[str, Any] | None:
        return {
            "status": "skipped",
            "message": "Agent pipeline not enabled in backend yet. Context payload is ready for ai_trading_agent.run_pipeline().",
            "ticker": context.ticker,
        }
