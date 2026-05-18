import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.clients.psx_client import EodBar, ParsedCompanyPage
from app.main import app
from app.services.macro_service import MacroContextData
from app.services.news_service import NewsArticle


class AnalyzeRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("app.services.analyze_workflow.PsxClient.fetch_latest_intraday_price", return_value=None)
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
        _mock_intraday,
    ) -> None:
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
        self.assertEqual(body["analysis"]["status"], "skipped")

    def test_analyze_rejects_invalid_ticker(self) -> None:
        response = self.client.post("/api/analyze", json={"ticker": "bad ticker!"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
