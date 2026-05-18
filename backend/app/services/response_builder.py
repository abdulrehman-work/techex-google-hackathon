from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.schemas.agent_context import AgentContextPayload
from app.schemas.api import AnalyzeResponse


class ResponseBuilder:
    """Builds the frontend-facing API response."""

    def build_frontend_response(
        self,
        *,
        context: AgentContextPayload,
        analysis: dict[str, Any] | None,
        meta: dict[str, Any] | None = None,
    ) -> AnalyzeResponse:
        response_meta = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentPipeline": "completed" if analysis else "pending",
        }
        if meta:
            response_meta.update(meta)

        return AnalyzeResponse(
            success=True,
            ticker=context.ticker,
            context=context,
            analysis=analysis,
            meta=response_meta,
        )
