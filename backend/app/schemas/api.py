from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from .agent_context import AgentContextPayload


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., examples=["ENGRO"])


class AnalyzeResponse(BaseModel):
    success: bool = True
    ticker: str
    context: AgentContextPayload
    analysis: Optional[dict[str, Any]] = None
    meta: dict[str, Any] = Field(default_factory=dict)
