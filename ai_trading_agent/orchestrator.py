"""Orchestration layer for the financial intelligence pipeline."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .agents import (
    LLMClient,
    governance_agent,
    macro_agent,
    portfolio_agent,
    research_agent,
    risk_agent,
    sentiment_agent,
)
from .gemini_client import GeminiClient


def build_context(data: dict[str, Any]) -> dict[str, Any]:
    """Create a clean context object from already-structured single-stock input."""
    return {
        "ticker": data.get("ticker", "UNKNOWN"),
        "companyProfile": deepcopy(data.get("companyProfile", {})),
        "stockData": deepcopy(data.get("stockData", {})),
        "priceHistory": deepcopy(data.get("priceHistory", [])),
        "fundamentals": deepcopy(data.get("fundamentals", {})),
        "news": deepcopy(data.get("news", [])),
        "macroContext": deepcopy(data.get("macroContext", {})),
        "riskMetrics": deepcopy(data.get("riskMetrics", {})),
    }


def run_pipeline(data: dict[str, Any], llm: LLMClient | None = None) -> dict[str, Any]:
    """Run the full Gemini multi-agent decision pipeline.

    Agent call order:
        research_agent(ctx, llm)
        macro_agent(ctx, llm)
        sentiment_agent(ctx, llm)
        risk_agent(ctx, research, macro, sentiment, llm)
        portfolio_agent(research, macro, sentiment, risk, llm)
        governance_agent(signal, risk, ctx, llm)
    """
    ctx = build_context(data)
    llm_client = llm or GeminiClient()

    research = research_agent(ctx, llm_client)
    macro = macro_agent(ctx, llm_client)
    sentiment = sentiment_agent(ctx, llm_client)
    risk = risk_agent(ctx, research, macro, sentiment, llm_client)
    signal = portfolio_agent(research, macro, sentiment, risk, llm_client)
    governance = governance_agent(signal, risk, ctx, llm_client)

    return {
        "ticker": ctx["ticker"],
        "signal": signal["signal"],
        "confidence": signal["confidence"],
        "opportunityScore": signal["opportunityScore"],
        "governanceStatus": governance["status"],
        "governanceReason": governance["reason"],
        "breakdown": {
            "research": research,
            "macro": macro,
            "sentiment": sentiment,
            "risk": risk,
            "portfolio": signal,
            "governance": governance,
        },
    }
