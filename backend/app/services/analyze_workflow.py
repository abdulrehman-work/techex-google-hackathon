from __future__ import annotations

from app.clients.psx_client import PsxClient
from app.core.validators import validate_ticker
from app.schemas.api import AnalyzeResponse
from app.services.ai_orchestrator import AiOrchestrator
from app.services.company_service import CompanyService
from app.services.context_builder_service import AnalysisParts, ContextBuilderService
from app.services.filings_service import FilingsService
from app.services.fundamentals_service import FundamentalsService
from app.services.macro_service import MacroService
from app.services.news_service import NewsService
from app.services.psx_data_service import PsxDataService
from app.services.response_builder import ResponseBuilder
from app.services.risk_data_service import RiskDataService


class AnalyzeWorkflow:
    """Coordinates the full analyze pipeline from ticker to frontend JSON."""

    def __init__(
        self,
        *,
        psx_client: PsxClient | None = None,
        company_service: CompanyService | None = None,
        psx_data_service: PsxDataService | None = None,
        fundamentals_service: FundamentalsService | None = None,
        filings_service: FilingsService | None = None,
        news_service: NewsService | None = None,
        macro_service: MacroService | None = None,
        risk_data_service: RiskDataService | None = None,
        context_builder_service: ContextBuilderService | None = None,
        ai_orchestrator: AiOrchestrator | None = None,
        response_builder: ResponseBuilder | None = None,
    ) -> None:
        self._psx = psx_client or PsxClient()
        self._company_service = company_service or CompanyService(self._psx)
        self._psx_data_service = psx_data_service or PsxDataService(self._psx)
        self._fundamentals_service = fundamentals_service or FundamentalsService(self._psx)
        self._filings_service = filings_service or FilingsService(self._psx)
        self._news_service = news_service or NewsService()
        self._macro_service = macro_service or MacroService(self._psx)
        self._risk_data_service = risk_data_service or RiskDataService()
        self._context_builder_service = context_builder_service or ContextBuilderService()
        self._ai_orchestrator = ai_orchestrator or AiOrchestrator()
        self._response_builder = response_builder or ResponseBuilder()

    def run(self, raw_ticker: str) -> AnalyzeResponse:
        ticker = validate_ticker(raw_ticker)

        company_html = self._psx.fetch_company_page(ticker)
        company_page = self._psx.parse_company_page(company_html)
        eod_bars = self._psx.fetch_eod_bars(ticker)

        company_profile = self._company_service.get_company_profile(
            ticker,
            company_page=company_page,
        )
        stock_data = self._psx_data_service.get_current_stock_data(
            ticker,
            eod_bars=eod_bars,
            company_page=company_page,
        )
        price_history = self._psx_data_service.get_historical_prices(
            ticker,
            eod_bars=eod_bars,
        )
        filings = self._filings_service.get_relevant_filing_text(
            ticker,
            company_page=company_page,
        )
        fundamentals = self._fundamentals_service.get_fundamentals(
            ticker,
            company_page=company_page,
            stock_data=stock_data,
            filing_summary=filings.filing_text,
        )
        news = self._news_service.get_company_news(ticker, company_profile)
        macro_context = self._macro_service.get_macro_context()
        risk_metrics = self._risk_data_service.calculate_risk_metrics(stock_data, price_history)

        context = self._context_builder_service.build_context(
            AnalysisParts(
                ticker=ticker,
                company_profile=company_profile,
                stock_data=stock_data,
                price_history=price_history,
                fundamentals=fundamentals,
                filings=filings,
                news=news,
                macro_context=macro_context,
                risk_metrics=risk_metrics,
            )
        )

        analysis = self._ai_orchestrator.run_agents(context)
        return self._response_builder.build_frontend_response(
            context=context,
            analysis=analysis,
            meta={"services": "company,psx,fundamentals,filings,news,macro,risk,context"},
        )
