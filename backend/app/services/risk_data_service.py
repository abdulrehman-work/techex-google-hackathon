from __future__ import annotations

import math
from dataclasses import dataclass

from app.services.psx_data_service import StockDataSnapshot


@dataclass(frozen=True)
class RiskMetricsData:
    daily_change_percent: float
    simple_volatility: str
    volume_trend: str


class RiskDataService:
    """Calculates basic risk metrics from market data."""

    def calculate_risk_metrics(
        self,
        stock_data: StockDataSnapshot,
        price_history: list[dict[str, float | int | str]],
    ) -> RiskMetricsData:
        closes = [float(point["close"]) for point in price_history if point.get("close") is not None]
        volumes = [int(point["volume"]) for point in price_history if point.get("volume") is not None]

        daily_change_percent = round(stock_data.change_percent, 2)
        simple_volatility = _volatility_label(closes)
        volume_trend = _volume_trend(volumes)

        return RiskMetricsData(
            daily_change_percent=daily_change_percent,
            simple_volatility=simple_volatility,
            volume_trend=volume_trend,
        )


def _volatility_label(closes: list[float]) -> str:
    if len(closes) < 3:
        return "medium"

    returns = []
    for index in range(len(closes) - 1):
        previous = closes[index + 1]
        if previous == 0:
            continue
        returns.append((closes[index] - previous) / previous)

    if not returns:
        return "medium"

    mean = sum(returns) / len(returns)
    variance = sum((value - mean) ** 2 for value in returns) / len(returns)
    std_dev = math.sqrt(variance)

    if std_dev >= 0.035:
        return "high"
    if std_dev <= 0.015:
        return "low"
    return "medium"


def _volume_trend(volumes: list[int]) -> str:
    if len(volumes) < 3:
        return "stable"

    recent = volumes[0]
    prior_window = volumes[1:6]
    if not prior_window:
        return "stable"

    prior_average = sum(prior_window) / len(prior_window)
    if prior_average == 0:
        return "stable"

    ratio = recent / prior_average
    if ratio >= 1.5:
        return "increasing"
    if ratio <= 0.7:
        return "decreasing"
    if ratio >= 1.2 and recent > prior_average * 1.35:
        return "panic selling spike" if recent > prior_average else "increasing"
    return "stable"
