import unittest
from unittest.mock import patch

from app.clients.psx_client import EodBar, ParsedCompanyPage
from app.services.company_service import CompanyService
from app.services.context_builder_service import AnalysisParts, ContextBuilderService
from app.services.fundamentals_service import FundamentalsService
from app.services.psx_data_service import PsxDataService, StockDataSnapshot
from app.services.risk_data_service import RiskDataService


def _sample_company_page() -> ParsedCompanyPage:
    return ParsedCompanyPage(
        company_name="Engro Corporation Limited",
        sector="FERTILIZER",
        business_description="Engro manages investments in fertilizers and energy.",
        current_price=312.5,
        change_value=4.3,
        change_percent=1.4,
        volume=1_200_000,
        open_price=308.0,
        ldcp=308.2,
        pe_ratio_ttm=8.1,
        annual_eps=32.26,
        latest_quarter_eps=6.84,
        announcements=[("Oct 29, 2024", "FINANCIAL RESULTS FOR THE NINE MONTHS ENDED SEPTEMBER 30, 2024")],
        payout_snippets=["Nov 20, 2024: Credit of Third Interim Cash Dividend"],
    )


class ServiceUnitTests(unittest.TestCase):
    def test_company_service_from_parsed_page(self) -> None:
        profile = CompanyService().get_company_profile("ENGRO", company_page=_sample_company_page())
        self.assertEqual(profile.company_name, "Engro Corporation Limited")
        self.assertEqual(profile.sector, "FERTILIZER")

    @patch("app.services.psx_data_service.PsxClient.fetch_latest_intraday_price", return_value=None)
    def test_psx_data_service_builds_stock_snapshot(self, _mock_intraday) -> None:
        bars = [
            EodBar(timestamp=1, close=312.5, volume=1_200_000, open_price=308.0),
            EodBar(timestamp=0, close=308.2, volume=900_000, open_price=305.0),
        ]
        snapshot = PsxDataService().get_current_stock_data(
            "ENGRO",
            eod_bars=bars,
            company_page=_sample_company_page(),
        )
        self.assertEqual(snapshot.current_price, 312.5)
        self.assertEqual(snapshot.previous_close, 308.2)
        self.assertEqual(snapshot.change_percent, 1.4)

    def test_fundamentals_service_uses_eps_and_pe(self) -> None:
        stock = StockDataSnapshot(
            current_price=312.5,
            previous_close=308.2,
            change_percent=1.4,
            volume=1_200_000,
        )
        fundamentals = FundamentalsService().get_fundamentals(
            "ENGRO",
            company_page=_sample_company_page(),
            stock_data=stock,
            filing_summary="Recent filing summary.",
        )
        self.assertEqual(fundamentals.eps, 6.84)
        self.assertEqual(fundamentals.pe_ratio, 8.1)
        self.assertIn("Recent filing summary", fundamentals.financial_summary)

    def test_risk_data_service_labels(self) -> None:
        stock = StockDataSnapshot(
            current_price=312.5,
            previous_close=308.2,
            change_percent=1.4,
            volume=1_200_000,
        )
        history = [
            {"date": "2026-05-18", "close": 312.5, "volume": 1_200_000},
            {"date": "2026-05-17", "close": 308.2, "volume": 900_000},
            {"date": "2026-05-16", "close": 305.0, "volume": 850_000},
        ]
        risk = RiskDataService().calculate_risk_metrics(stock, history)
        self.assertEqual(risk.daily_change_percent, 1.4)
        self.assertIn(risk.simple_volatility, {"low", "medium", "high"})

    def test_context_builder_matches_agent_contract(self) -> None:
        from app.services.filings_service import FilingsData, FilingRecord
        from app.services.fundamentals_service import FundamentalsData
        from app.services.macro_service import MacroContextData
        from app.services.news_service import NewsArticle

        parts = AnalysisParts(
            ticker="ENGRO",
            company_profile=CompanyService().get_company_profile("ENGRO", company_page=_sample_company_page()),
            stock_data=StockDataSnapshot(312.5, 308.2, 1.4, 1_200_000),
            price_history=[{"date": "2026-05-18", "close": 312.5, "volume": 1_200_000}],
            fundamentals=FundamentalsData(18.2, 8.1, 7.5, 16.4, "Stable earnings."),
            filings=FilingsData([FilingRecord("Oct 29, 2024", "Financial results")], "Filing text"),
            news=[NewsArticle("Business Recorder", "Sector gains", "Investors showed interest.")],
            macro_context=MacroContextData("11.50%", "stable", "moderating", "medium", "neutral"),
            risk_metrics=RiskDataService().calculate_risk_metrics(
                StockDataSnapshot(312.5, 308.2, 1.4, 1_200_000),
                [{"date": "2026-05-18", "close": 312.5, "volume": 1_200_000}],
            ),
        )
        context = ContextBuilderService().build_context(parts)
        payload = context.to_agent_dict()
        self.assertEqual(payload["ticker"], "ENGRO")
        self.assertEqual(payload["companyProfile"]["companyName"], "Engro Corporation Limited")
        self.assertEqual(payload["stockData"]["currentPrice"], 312.5)
        self.assertEqual(payload["fundamentals"]["peRatio"], 8.1)
        self.assertEqual(len(payload["news"]), 1)


if __name__ == "__main__":
    unittest.main()
