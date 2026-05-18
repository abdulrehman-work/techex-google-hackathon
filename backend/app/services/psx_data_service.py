from __future__ import annotations

from dataclasses import dataclass

from app.clients.psx_client import EodBar, ParsedCompanyPage, PsxClient, eod_bar_to_history_point
from app.core.config import get_settings


@dataclass(frozen=True)
class StockDataSnapshot:
    current_price: float
    previous_close: float
    change_percent: float
    volume: int


class PsxDataService:
    """Fetches current and historical PSX market data."""

    def __init__(self, psx_client: PsxClient | None = None) -> None:
        self._psx = psx_client or PsxClient()
        self._settings = get_settings()

    def get_current_stock_data(
        self,
        ticker: str,
        *,
        eod_bars: list[EodBar] | None = None,
        company_page: ParsedCompanyPage | None = None,
    ) -> StockDataSnapshot:
        bars = eod_bars or self._psx.fetch_eod_bars(ticker)
        latest = bars[0]
        previous = bars[1] if len(bars) > 1 else latest

        intraday_price = self._psx.fetch_latest_intraday_price(ticker)
        current_price = intraday_price or company_page.current_price if company_page else None
        current_price = current_price or latest.close

        previous_close = company_page.ldcp if company_page and company_page.ldcp else previous.close
        volume = company_page.volume if company_page and company_page.volume else latest.volume

        if company_page and company_page.change_percent is not None:
            change_percent = company_page.change_percent
        else:
            change_percent = _percent_change(current_price, previous_close)

        return StockDataSnapshot(
            current_price=round(current_price, 2),
            previous_close=round(previous_close, 2),
            change_percent=round(change_percent, 2),
            volume=int(volume),
        )

    def get_historical_prices(
        self,
        ticker: str,
        *,
        eod_bars: list[EodBar] | None = None,
    ) -> list[dict[str, float | int | str]]:
        bars = eod_bars or self._psx.fetch_eod_bars(ticker)
        limit = self._settings.price_history_days
        return [eod_bar_to_history_point(bar) for bar in bars[:limit]]


def _percent_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0
