import unittest
from unittest.mock import patch

from ai_trading_agent.gemini_client import (
    GeminiClient,
    normalize_model_name,
    resolve_model_chain,
)
from ai_trading_agent import run_pipeline


class FakeGeminiClient:
    def __init__(self):
        self.calls = []

    def generate_json(self, *, agent_name, role, task, payload, response_schema):
        self.calls.append(agent_name)
        responses = {
            "research_agent": {
                "score": 72,
                "verdict": "strong",
                "reasoning": "Fundamentals indicate stable earnings, modest valuation, and dividend support.",
                "keyDrivers": ["stable earnings", "reasonable valuation", "dividend support"],
            },
            "macro_agent": {
                "score": 55,
                "condition": "mixed",
                "reasoning": "Moderating inflation helps, while policy rates and oil risk limit upside.",
                "drivers": ["moderating inflation", "neutral market", "medium oil risk"],
            },
            "sentiment_agent": {
                "score": 64,
                "label": "positive",
                "reasoning": "The available headline suggests renewed investor interest.",
                "sentimentDrivers": ["sector gains", "improving sentiment"],
            },
            "risk_agent": {
                "riskScore": 42,
                "riskLevel": "moderate",
                "warnings": ["medium volatility", "macro backdrop is not strongly supportive"],
                "reasoning": "Risk is manageable but not negligible because volatility and macro conditions are mixed.",
            },
            "portfolio_agent": {
                "signal": "HOLD",
                "confidence": 68,
                "opportunityScore": 61,
                "reasoningSummary": "The stock has fundamental support, but macro and risk signals argue for patience.",
            },
            "governance_agent": {
                "status": "APPROVED",
                "reason": "Recommendation is consistent with moderate risk.",
                "finalNotes": "Monitor macro conditions and volume confirmation.",
            },
        }
        return responses[agent_name]


class GeminiClientFallbackTests(unittest.TestCase):
    def test_resolve_model_chain_puts_primary_first(self):
        with patch.dict("os.environ", {}, clear=True):
            chain = resolve_model_chain("gemini-2.0-flash")
        self.assertEqual(chain[0], "gemini-2.0-flash")
        self.assertIn("gemini-3-flash-preview", chain)

    @patch.dict(
        "os.environ",
        {"GEMINI_MODEL_FALLBACKS": "gemini-2.5-flash, gemini-2.0-flash-lite"},
        clear=True,
    )
    def test_resolve_model_chain_honors_env_fallbacks(self):
        chain = resolve_model_chain("gemini-3-flash-preview")
        self.assertEqual(
            chain,
            ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.0-flash-lite"],
        )

    @patch("ai_trading_agent.gemini_client.time.sleep")
    @patch("ai_trading_agent.gemini_client.GeminiClient.__init__", lambda self, **kwargs: None)
    def test_generate_json_switches_model_after_quota_error(self, _mock_sleep) -> None:
        client = GeminiClient.__new__(GeminiClient)
        client._active_model = "gemini-3-flash-preview"
        client._model_chain = ["gemini-3-flash-preview", "gemini-2.0-flash"]
        client.model = client._active_model
        client.temperature = 0.2

        class FakeAPIError(Exception):
            code = 429

        client._errors = type("Errors", (), {"APIError": FakeAPIError})()
        client._types = type("Types", (), {"GenerateContentConfig": type("Cfg", (), {"model_fields": {}})})()

        class FakeResponse:
            text = '{"score": 70, "verdict": "moderate", "reasoning": "ok", "keyDrivers": ["a"]}'

        calls: list[str] = []

        class FakeModels:
            def generate_content(self, *, model, contents, config):
                calls.append(model)
                if model == "gemini-3-flash-preview":
                    raise FakeAPIError("429 RESOURCE_EXHAUSTED quota exceeded")
                return FakeResponse()

        client._client = type("Client", (), {"models": FakeModels()})()

        result = client.generate_json(
            agent_name="research_agent",
            role="Financial analyst",
            task="analyze",
            payload={},
            response_schema={},
        )

        self.assertEqual(result["score"], 70)
        self.assertEqual(calls, ["gemini-3-flash-preview", "gemini-2.0-flash"])
        self.assertEqual(client.model, "gemini-2.0-flash")


class PipelineSmokeTest(unittest.TestCase):
    def test_normalizes_rest_model_resource_names(self):
        self.assertEqual(
            normalize_model_name("models/gemini-3-flash-preview"),
            "gemini-3-flash-preview",
        )
        self.assertEqual(
            normalize_model_name("gemini-3-flash-preview"),
            "gemini-3-flash-preview",
        )

    def test_pipeline_returns_expected_top_level_contract(self):
        data = {
            "ticker": "ENGRO",
            "companyProfile": {
                "companyName": "Engro Corporation",
                "sector": "Fertilizer / Conglomerate",
            },
            "stockData": {
                "currentPrice": 312.5,
                "previousClose": 308.2,
                "changePercent": 1.4,
                "volume": 1200000,
            },
            "priceHistory": [{"date": "2026-05-15", "close": 312.5, "volume": 1200000}],
            "fundamentals": {
                "eps": 18.2,
                "peRatio": 8.1,
                "dividendYield": 7.5,
                "roe": 16.4,
                "financialSummary": "The company reported stable earnings and maintained dividend payouts.",
            },
            "news": [
                {
                    "source": "Business Recorder",
                    "headline": "Fertilizer sector gains as market sentiment improves",
                    "snippet": "Investors showed renewed interest in fertilizer stocks.",
                }
            ],
            "macroContext": {
                "sbpPolicyRate": "11.50%",
                "pkrUsdTrend": "stable",
                "inflationView": "moderating",
                "oilPriceRisk": "medium",
                "marketCondition": "neutral",
            },
            "riskMetrics": {
                "dailyChangePercent": 1.4,
                "simpleVolatility": "medium",
                "volumeTrend": "increasing",
            },
        }

        fake_llm = FakeGeminiClient()
        result = run_pipeline(data, llm=fake_llm)

        self.assertEqual(result["ticker"], "ENGRO")
        self.assertIn(result["signal"], {"BUY", "HOLD", "SELL"})
        self.assertIn(result["governanceStatus"], {"APPROVED", "FLAGGED"})
        self.assertIn("opportunityScore", result)
        self.assertIn("research", result["breakdown"])
        self.assertIn("portfolio", result["breakdown"])
        self.assertEqual(
            fake_llm.calls,
            [
                "research_agent",
                "macro_agent",
                "sentiment_agent",
                "risk_agent",
                "portfolio_agent",
                "governance_agent",
            ],
        )


if __name__ == "__main__":
    unittest.main()
