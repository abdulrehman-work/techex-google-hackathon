import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.clients.psx_client import EodBar, ParsedCompanyPage
from app.core.exceptions import DataFetchError
from app.main import app
from app.services.macro_service import MacroContextData
from app.services.news_service import NewsArticle


class AnalyzeRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("app.services.analyze_workflow.PsxClient.fetch_latest_intraday_price", return_value=None)
    @patch("app.services.ai_orchestrator.run_pipeline")
    @patch("app.services.analyze_workflow.PsxClient.fetch_company_page")
    @patch("app.services.analyze_workflow.PsxClient.parse_company_page")
    @patch("app.services.analyze_workflow.PsxClient.fetch_eod_bars")
    @patch("app.services.analyze_workflow.NewsService.get_company_news")
    @patch("app.services.analyze_workflow.MacroService.get_macro_context")
    def test_analyze_endpoint_returns_context_payload(
        self,
        mock_macro,
        mock_news,
        mock_eod,
        mock_parse,
        mock_fetch_html,
        mock_run_pipeline,
        _mock_intraday,
    ) -> None:
        mock_run_pipeline.return_value = {
            "ticker": "ENGRO",
            "signal": "HOLD",
            "confidence": 68,
            "opportunityScore": 61,
            "governanceStatus": "APPROVED",
            "governanceReason": "Recommendation is consistent with moderate risk.",
            "breakdown": {
                "research": {"score": 72, "verdict": "strong", "reasoning": "Stable fundamentals."},
                "macro": {"score": 55, "condition": "mixed", "reasoning": "Mixed macro."},
                "sentiment": {"score": 64, "label": "positive", "reasoning": "Constructive news."},
                "risk": {"riskScore": 42, "riskLevel": "moderate", "warnings": []},
                "portfolio": {"signal": "HOLD", "confidence": 68, "opportunityScore": 61},
                "governance": {"status": "APPROVED", "reason": "Consistent with risk."},
            },
        }
        mock_fetch_html.return_value = "<html></html>"
        mock_parse.return_value = ParsedCompanyPage(
            company_name="Engro Corporation Limited",
            sector="Fertilizer / Conglomerate",
            business_description="Stable conglomerate profile.",
            current_price=312.5,
            change_value=4.3,
            change_percent=1.4,
            volume=1_200_000,
            open_price=308.0,
            ldcp=308.2,
            pe_ratio_ttm=8.1,
            annual_eps=18.2,
            latest_quarter_eps=18.2,
            announcements=[("Oct 29, 2024", "Financial results")],
            payout_snippets=["Dividend payout noted."],
        )
        mock_eod.return_value = [
            EodBar(timestamp=1, close=312.5, volume=1_200_000, open_price=308.0),
            EodBar(timestamp=0, close=308.2, volume=900_000, open_price=305.0),
        ]
        mock_news.return_value = [
            NewsArticle(
                source="Business Recorder",
                headline="Fertilizer sector gains as market sentiment improves",
                snippet="Investors showed renewed interest in fertilizer stocks.",
            )
        ]
        mock_macro.return_value = MacroContextData(
            sbp_policy_rate="11.50%",
            pkr_usd_trend="stable",
            inflation_view="moderating",
            oil_price_risk="medium",
            market_condition="neutral",
        )

        response = self.client.post("/api/analyze", json={"ticker": "engro"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["ticker"], "ENGRO")
        self.assertEqual(body["context"]["companyProfile"]["companyName"], "Engro Corporation Limited")
        self.assertEqual(body["context"]["stockData"]["currentPrice"], 312.5)
        self.assertEqual(body["analysis"]["signal"], "HOLD")
        self.assertEqual(body["analysis"]["governanceStatus"], "APPROVED")
        self.assertEqual(body["meta"]["agentPipeline"], "completed")
        mock_run_pipeline.assert_called_once()
        self.assertEqual(mock_run_pipeline.call_args.args[0]["ticker"], "ENGRO")

    def test_analyze_rejects_invalid_ticker(self) -> None:
        response = self.client.post("/api/analyze", json={"ticker": "bad ticker!"})
        self.assertEqual(response.status_code, 400)

    @patch("app.services.analyze_workflow.PsxClient.fetch_eod_bars")
    def test_analyze_returns_502_when_psx_eod_fetch_fails(self, mock_eod) -> None:
        mock_eod.side_effect = DataFetchError("PSX EOD request failed for ENGRO.")

        response = self.client.post("/api/analyze", json={"ticker": "ENGRO"})

        self.assertEqual(response.status_code, 502)
        self.assertIn("PSX EOD request failed", response.json()["detail"])

    @patch("app.services.analyze_workflow.PsxClient.fetch_latest_intraday_price", return_value=None)
    @patch("app.services.ai_orchestrator.run_pipeline")
    @patch("app.services.analyze_workflow.PsxClient.fetch_company_page")
    @patch("app.services.analyze_workflow.NewsService.get_company_news", return_value=[])
    @patch("app.services.analyze_workflow.MacroService.get_macro_context")
    @patch("app.services.analyze_workflow.PsxClient.fetch_eod_bars")
    def test_analyze_uses_eod_fallback_when_company_page_blocked(
        self,
        mock_eod,
        mock_macro,
        _mock_news,
        mock_fetch_html,
        mock_run_pipeline,
        _mock_intraday,
    ) -> None:
        mock_eod.return_value = [
            EodBar(timestamp=1, close=312.5, volume=1_200_000, open_price=308.0),
            EodBar(timestamp=0, close=308.2, volume=900_000, open_price=305.0),
        ]
        mock_fetch_html.side_effect = DataFetchError(
            "PSX company page request failed for ENGRO: Server disconnected without sending a response."
        )
        mock_macro.return_value = MacroContextData(
            sbp_policy_rate="11.50%",
            pkr_usd_trend="stable",
            inflation_view="moderating",
            oil_price_risk="medium",
            market_condition="neutral",
        )
        mock_run_pipeline.return_value = {
            "ticker": "ENGRO",
            "signal": "HOLD",
            "confidence": 68,
            "opportunityScore": 61,
            "governanceStatus": "APPROVED",
            "governanceReason": "ok",
            "breakdown": {},
        }

        response = self.client.post("/api/analyze", json={"ticker": "ENGRO"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["psxProfileSource"], "eod-fallback")
        self.assertEqual(response.json()["context"]["companyProfile"]["companyName"], "ENGRO")

    @patch("app.services.ai_orchestrator.run_pipeline")
    def test_analyze_context_runs_ai_pipeline_from_payload(self, mock_run_pipeline) -> None:
        mock_run_pipeline.return_value = {
            "ticker": "ENGRO",
            "signal": "BUY",
            "confidence": 74,
            "opportunityScore": 70,
            "governanceStatus": "APPROVED",
            "governanceReason": "Risk controls passed.",
            "breakdown": {},
        }
        payload = {
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

        response = self.client.post("/api/analyze/context", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["analysis"]["signal"], "BUY")
        self.assertEqual(body["meta"]["services"], "provided-context,ai")
        mock_run_pipeline.assert_called_once()


if __name__ == "__main__":
    unittest.main()
