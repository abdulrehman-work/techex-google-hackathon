from __future__ import annotations

from dataclasses import dataclass

from app.schemas.agent_context import (
    AgentContextPayload,
    CompanyProfile,
    Fundamentals,
    MacroContext,
    NewsItem,
    PriceHistoryPoint,
    RiskMetrics,
    StockData,
)
from app.services.company_service import CompanyProfileData
from app.services.filings_service import FilingsData
from app.services.fundamentals_service import FundamentalsData
from app.services.macro_service import MacroContextData
from app.services.news_service import NewsArticle
from app.services.psx_data_service import StockDataSnapshot
from app.services.risk_data_service import RiskMetricsData


@dataclass(frozen=True)
class AnalysisParts:
    ticker: str
    company_profile: CompanyProfileData
    stock_data: StockDataSnapshot
    price_history: list[dict[str, float | int | str]]
    fundamentals: FundamentalsData
    filings: FilingsData
    news: list[NewsArticle]
    macro_context: MacroContextData
    risk_metrics: RiskMetricsData


class ContextBuilderService:
    """Combines service outputs into the agent-ready context payload."""

    def build_context(self, parts: AnalysisParts) -> AgentContextPayload:
        return AgentContextPayload(
            ticker=parts.ticker,
            companyProfile=CompanyProfile(
                companyName=parts.company_profile.company_name,
                sector=parts.company_profile.sector,
            ),
            stockData=StockData(
                currentPrice=parts.stock_data.current_price,
                previousClose=parts.stock_data.previous_close,
                changePercent=parts.stock_data.change_percent,
                volume=parts.stock_data.volume,
            ),
            priceHistory=[PriceHistoryPoint(**point) for point in parts.price_history],
            fundamentals=Fundamentals(
                eps=parts.fundamentals.eps,
                peRatio=parts.fundamentals.pe_ratio,
                dividendYield=parts.fundamentals.dividend_yield,
                roe=parts.fundamentals.roe,
                financialSummary=parts.fundamentals.financial_summary,
            ),
            news=[
                NewsItem(source=item.source, headline=item.headline, snippet=item.snippet)
                for item in parts.news
            ],
            macroContext=MacroContext(
                sbpPolicyRate=parts.macro_context.sbp_policy_rate,
                pkrUsdTrend=parts.macro_context.pkr_usd_trend,
                inflationView=parts.macro_context.inflation_view,
                oilPriceRisk=parts.macro_context.oil_price_risk,
                marketCondition=parts.macro_context.market_condition,
            ),
            riskMetrics=RiskMetrics(
                dailyChangePercent=parts.risk_metrics.daily_change_percent,
                simpleVolatility=parts.risk_metrics.simple_volatility,
                volumeTrend=parts.risk_metrics.volume_trend,
            ),
        )
