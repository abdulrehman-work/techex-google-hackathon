"""Gemini-powered financial analysis agents.

Every agent in this module delegates reasoning to Gemini and requests strict
JSON output. The local code only builds prompts, supplies schemas, and validates
that the returned shape matches the contract expected by the orchestrator.
"""

from __future__ import annotations

import json
from typing import Any, Protocol


AgentOutput = dict[str, Any]


class LLMClient(Protocol):
    """Minimal client interface used by the agents."""

    def generate_json(
        self,
        *,
        agent_name: str,
        role: str,
        task: str,
        payload: dict[str, Any],
        response_schema: dict[str, Any],
    ) -> AgentOutput:
        """Generate a schema-constrained JSON response."""


class AgentResponseError(ValueError):
    """Raised when Gemini returns JSON that does not satisfy an agent contract."""


def _json_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _schema(
    properties: dict[str, Any],
    required: list[str],
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _array_of_strings(description: str) -> dict[str, Any]:
    return {
        "type": "array",
        "description": description,
        "items": {"type": "string"},
    }


def _score(description: str) -> dict[str, Any]:
    return {
        "type": "number",
        "description": f"{description} Must be normalized from 0 to 100.",
    }


def _require_fields(agent_name: str, output: AgentOutput, required: list[str]) -> None:
    missing = [field for field in required if field not in output]
    if missing:
        raise AgentResponseError(f"{agent_name} response missing fields: {', '.join(missing)}")


def _require_score(agent_name: str, output: AgentOutput, field: str) -> None:
    value = output.get(field)
    if not isinstance(value, (int, float)) or not 0 <= value <= 100:
        raise AgentResponseError(f"{agent_name} field '{field}' must be a 0-100 number.")


def _require_enum(agent_name: str, output: AgentOutput, field: str, allowed: set[str]) -> None:
    value = output.get(field)
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise AgentResponseError(f"{agent_name} field '{field}' must be one of: {allowed_values}.")


def research_agent(ctx: dict[str, Any], llm: LLMClient) -> AgentOutput:
    """Analyze company strength, valuation, and financial health with Gemini."""
    required = ["score", "verdict", "reasoning", "keyDrivers"]
    schema = _schema(
        {
            "score": _score("Overall fundamental quality score."),
            "verdict": {
                "type": "string",
                "enum": ["strong", "moderate", "weak"],
                "description": "Qualitative verdict on company fundamentals.",
            },
            "reasoning": {
                "type": "string",
                "description": "Explain valuation, earnings, profitability, dividends, and financial health.",
            },
            "keyDrivers": _array_of_strings("Most important fundamental drivers behind the score."),
        },
        required,
    )
    payload = {
        "companyProfile": ctx.get("companyProfile", {}),
        "fundamentals": ctx.get("fundamentals", {}),
        "priceHistory": ctx.get("priceHistory", []),
    }
    task = (
        "Analyze this stock as a financial analyst. Evaluate company strength, valuation, "
        "profitability, dividend support, financial health, and recent price context. "
        "Return JSON only using the provided schema.\n\nInput JSON:\n"
        f"{_json_payload(payload)}"
    )
    output = llm.generate_json(
        agent_name="research_agent",
        role="Financial analyst",
        task=task,
        payload=payload,
        response_schema=schema,
    )
    _require_fields("research_agent", output, required)
    _require_score("research_agent", output, "score")
    _require_enum("research_agent", output, "verdict", {"strong", "moderate", "weak"})
    return output


def macro_agent(ctx: dict[str, Any], llm: LLMClient) -> AgentOutput:
    """Analyze macroeconomic environment and market conditions with Gemini."""
    required = ["score", "condition", "reasoning", "drivers"]
    schema = _schema(
        {
            "score": _score("Macro support score for the stock."),
            "condition": {
                "type": "string",
                "enum": ["supportive", "mixed", "hostile"],
                "description": "Overall macro condition for this investment decision.",
            },
            "reasoning": {
                "type": "string",
                "description": "Explain policy rate, inflation, FX, oil risk, and market condition impacts.",
            },
            "drivers": _array_of_strings("Key macro factors influencing the score."),
        },
        required,
    )
    payload = {"macroContext": ctx.get("macroContext", {})}
    task = (
        "Analyze the macroeconomic backdrop as a macroeconomist. Consider policy rate, "
        "currency trend, inflation view, oil price risk, and broad market condition. "
        "Return JSON only using the provided schema.\n\nInput JSON:\n"
        f"{_json_payload(payload)}"
    )
    output = llm.generate_json(
        agent_name="macro_agent",
        role="Macroeconomist",
        task=task,
        payload=payload,
        response_schema=schema,
    )
    _require_fields("macro_agent", output, required)
    _require_score("macro_agent", output, "score")
    _require_enum("macro_agent", output, "condition", {"supportive", "mixed", "hostile"})
    return output


def sentiment_agent(ctx: dict[str, Any], llm: LLMClient) -> AgentOutput:
    """Analyze news sentiment and likely market reaction with Gemini."""
    required = ["score", "label", "reasoning", "sentimentDrivers"]
    schema = _schema(
        {
            "score": _score("News sentiment score."),
            "label": {
                "type": "string",
                "enum": ["positive", "neutral", "negative"],
                "description": "Overall sentiment label from available news.",
            },
            "reasoning": {
                "type": "string",
                "description": "Explain how the headlines and snippets may affect market mood.",
            },
            "sentimentDrivers": _array_of_strings("Specific news-driven factors behind the sentiment score."),
        },
        required,
    )
    payload = {"news": ctx.get("news", [])}
    task = (
        "Analyze market sentiment as a sentiment analyst. Use only the provided headlines "
        "and snippets, infer likely investor reaction, and avoid inventing missing facts. "
        "Return JSON only using the provided schema.\n\nInput JSON:\n"
        f"{_json_payload(payload)}"
    )
    output = llm.generate_json(
        agent_name="sentiment_agent",
        role="Market sentiment analyst",
        task=task,
        payload=payload,
        response_schema=schema,
    )
    _require_fields("sentiment_agent", output, required)
    _require_score("sentiment_agent", output, "score")
    _require_enum("sentiment_agent", output, "label", {"positive", "neutral", "negative"})
    return output


def risk_agent(
    ctx: dict[str, Any],
    research: AgentOutput,
    macro: AgentOutput,
    sentiment: AgentOutput,
    llm: LLMClient,
) -> AgentOutput:
    """Evaluate downside risk and threats with Gemini."""
    required = ["riskScore", "riskLevel", "warnings", "reasoning"]
    schema = _schema(
        {
            "riskScore": _score("Downside risk score, where higher means riskier."),
            "riskLevel": {
                "type": "string",
                "enum": ["low", "moderate", "high"],
                "description": "Overall downside risk level.",
            },
            "warnings": _array_of_strings("Concrete risk warnings and threats."),
            "reasoning": {
                "type": "string",
                "description": "Explain how risk metrics and prior agent outputs affect downside risk.",
            },
        },
        required,
    )
    payload = {
        "riskMetrics": ctx.get("riskMetrics", {}),
        "researchOutput": research,
        "macroOutput": macro,
        "sentimentOutput": sentiment,
    }
    task = (
        "Act as a risk management expert. Evaluate downside risk using the risk metrics "
        "and the prior agent outputs. Risk score should increase when downside threats "
        "are more severe. Return JSON only using the provided schema.\n\nInput JSON:\n"
        f"{_json_payload(payload)}"
    )
    output = llm.generate_json(
        agent_name="risk_agent",
        role="Risk management expert",
        task=task,
        payload=payload,
        response_schema=schema,
    )
    _require_fields("risk_agent", output, required)
    _require_score("risk_agent", output, "riskScore")
    _require_enum("risk_agent", output, "riskLevel", {"low", "moderate", "high"})
    return output


def portfolio_agent(
    research: AgentOutput,
    macro: AgentOutput,
    sentiment: AgentOutput,
    risk: AgentOutput,
    llm: LLMClient,
) -> AgentOutput:
    """Decide the final investment recommendation with Gemini."""
    required = ["signal", "confidence", "opportunityScore", "reasoningSummary"]
    schema = _schema(
        {
            "signal": {
                "type": "string",
                "enum": ["BUY", "HOLD", "SELL"],
                "description": "Final investment recommendation.",
            },
            "confidence": _score("Confidence in the final recommendation."),
            "opportunityScore": _score("Investment opportunity score after considering reward and risk."),
            "reasoningSummary": {
                "type": "string",
                "description": "Concise explanation for the final recommendation.",
            },
        },
        required,
    )
    payload = {
        "researchOutput": research,
        "macroOutput": macro,
        "sentimentOutput": sentiment,
        "riskOutput": risk,
    }
    task = (
        "Act as an investment strategist. Make a consensus-driven BUY, HOLD, or SELL "
        "decision from the agent outputs. Balance fundamental quality, macro backdrop, "
        "sentiment, and downside risk. Return JSON only using the provided schema.\n\n"
        f"Input JSON:\n{_json_payload(payload)}"
    )
    output = llm.generate_json(
        agent_name="portfolio_agent",
        role="Investment strategist",
        task=task,
        payload=payload,
        response_schema=schema,
    )
    _require_fields("portfolio_agent", output, required)
    _require_score("portfolio_agent", output, "confidence")
    _require_score("portfolio_agent", output, "opportunityScore")
    _require_enum("portfolio_agent", output, "signal", {"BUY", "HOLD", "SELL"})
    return output


def governance_agent(
    signal: AgentOutput,
    risk: AgentOutput,
    ctx: dict[str, Any],
    llm: LLMClient,
) -> AgentOutput:
    """Validate recommendation safety and compliance with Gemini."""
    required = ["status", "reason", "finalNotes"]
    schema = _schema(
        {
            "status": {
                "type": "string",
                "enum": ["APPROVED", "FLAGGED"],
                "description": "Whether the recommendation passes governance review.",
            },
            "reason": {
                "type": "string",
                "description": "Primary governance reason for approval or flag.",
            },
            "finalNotes": {
                "type": "string",
                "description": "Additional safety, uncertainty, or review notes.",
            },
        },
        required,
    )
    payload = {
        "ticker": ctx.get("ticker"),
        "fullContext": ctx,
        "portfolioDecision": signal,
        "riskAnalysis": risk,
    }
    task = (
        "Act as a compliance auditor for an AI investment decision. Validate whether the "
        "portfolio recommendation is safe, explainable, and consistent with the risk "
        "analysis and full input context. Flag material risk conflicts, unsupported "
        "confidence, or insufficient evidence. Return JSON only using the provided schema.\n\n"
        f"Input JSON:\n{_json_payload(payload)}"
    )
    output = llm.generate_json(
        agent_name="governance_agent",
        role="Compliance auditor",
        task=task,
        payload=payload,
        response_schema=schema,
    )
    _require_fields("governance_agent", output, required)
    _require_enum("governance_agent", output, "status", {"APPROVED", "FLAGGED"})
    return output
