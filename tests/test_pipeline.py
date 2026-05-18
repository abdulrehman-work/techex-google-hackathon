import unittest

from ai_trading_agent.gemini_client import normalize_model_name
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
