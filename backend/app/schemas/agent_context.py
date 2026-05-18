from typing import Any

from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    companyName: str
    sector: str


class StockData(BaseModel):
    currentPrice: float
    previousClose: float
    changePercent: float
    volume: int


class PriceHistoryPoint(BaseModel):
    date: str
    close: float
    volume: int


class Fundamentals(BaseModel):
    eps: float
    peRatio: float
    dividendYield: float
    roe: float
    financialSummary: str


class NewsItem(BaseModel):
    source: str
    headline: str
    snippet: str


class MacroContext(BaseModel):
    sbpPolicyRate: str
    pkrUsdTrend: str
    inflationView: str
    oilPriceRisk: str
    marketCondition: str


class RiskMetrics(BaseModel):
    dailyChangePercent: float
    simpleVolatility: str
    volumeTrend: str


class AgentContextPayload(BaseModel):
    """Structured context passed to the AI agent pipeline."""

    ticker: str
    companyProfile: CompanyProfile
    stockData: StockData
    priceHistory: list[PriceHistoryPoint]
    fundamentals: Fundamentals
    news: list[NewsItem]
    macroContext: MacroContext
    riskMetrics: RiskMetrics

    def to_agent_dict(self) -> dict[str, Any]:
        return self.model_dump()
