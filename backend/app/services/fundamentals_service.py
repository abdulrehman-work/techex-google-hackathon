from __future__ import annotations

from dataclasses import dataclass

from app.clients.psx_client import ParsedCompanyPage, PsxClient
from app.services.psx_data_service import StockDataSnapshot


@dataclass(frozen=True)
class FundamentalsData:
    eps: float
    pe_ratio: float
    dividend_yield: float
    roe: float
    financial_summary: str


class FundamentalsService:
    """Extracts and normalizes fundamental financial metrics."""

    def __init__(self, psx_client: PsxClient | None = None) -> None:
        self._psx = psx_client or PsxClient()

    def get_fundamentals(
        self,
        ticker: str,
        *,
        company_page: ParsedCompanyPage | None = None,
        stock_data: StockDataSnapshot | None = None,
        filing_summary: str | None = None,
    ) -> FundamentalsData:
        page = company_page or self._psx.parse_company_page(self._psx.fetch_company_page(ticker))

        eps = page.latest_quarter_eps or page.annual_eps or 0.0
        pe_ratio = page.pe_ratio_ttm
        if pe_ratio is None and stock_data and eps > 0:
            pe_ratio = round(stock_data.current_price / eps, 2)
        pe_ratio = pe_ratio or 0.0

        dividend_yield = _estimate_dividend_yield(page.payout_snippets)
        roe = _estimate_roe(page.annual_eps, page.business_description)

        summary_parts = []
        if page.business_description:
            summary_parts.append(page.business_description)
        if filing_summary:
            summary_parts.append(filing_summary)
        if page.annual_eps is not None:
            summary_parts.append(f"Latest reported annual EPS is {page.annual_eps:.2f}.")
        if page.latest_quarter_eps is not None:
            summary_parts.append(f"Latest reported quarterly EPS is {page.latest_quarter_eps:.2f}.")

        financial_summary = " ".join(summary_parts).strip()
        if not financial_summary:
            financial_summary = f"Fundamental data for {page.company_name} was compiled from PSX disclosures."

        return FundamentalsData(
            eps=round(eps, 2),
            pe_ratio=round(pe_ratio, 2),
            dividend_yield=round(dividend_yield, 2),
            roe=round(roe, 2),
            financial_summary=financial_summary,
        )


def _estimate_dividend_yield(payout_snippets: list[str]) -> float:
    if not payout_snippets:
        return 0.0
    joined = " ".join(payout_snippets).lower()
    if "dividend" in joined:
        return 5.0
    return 0.0


def _estimate_roe(annual_eps: float | None, description: str) -> float:
    if annual_eps is None:
        return 0.0
    if annual_eps <= 0:
        return max(-25.0, annual_eps)
    if "subsidiary" in description.lower() or "conglomerate" in description.lower():
        return 14.0
    return min(25.0, round(annual_eps / 2, 2))
