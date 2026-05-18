from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.core.config import Settings, get_settings
from app.core.exceptions import DataFetchError


@dataclass(frozen=True)
class EodBar:
    timestamp: int
    close: float
    volume: int
    open_price: float | None


@dataclass(frozen=True)
class ParsedCompanyPage:
    company_name: str
    sector: str
    business_description: str
    current_price: float | None
    change_value: float | None
    change_percent: float | None
    volume: int | None
    open_price: float | None
    ldcp: float | None
    pe_ratio_ttm: float | None
    annual_eps: float | None
    latest_quarter_eps: float | None
    announcements: list[tuple[str, str]]
    payout_snippets: list[str]


class PsxClient:
    """HTTP client for Pakistan Stock Exchange data portal endpoints."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._headers = {"User-Agent": self._settings.user_agent}

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self._settings.psx_base_url,
            headers=self._headers,
            timeout=self._settings.psx_request_timeout_seconds,
            follow_redirects=True,
        )

    def fetch_eod_bars(self, ticker: str) -> list[EodBar]:
        try:
            with self._client() as client:
                response = client.get(f"/timeseries/eod/{ticker}")
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise DataFetchError(f"PSX EOD request failed for {ticker}: {exc}") from exc

        if payload.get("status") != 1:
            raise DataFetchError(f"PSX EOD request failed for {ticker}.")

        bars: list[EodBar] = []
        for row in payload.get("data", []):
            if not isinstance(row, list) or len(row) < 3:
                continue
            bars.append(
                EodBar(
                    timestamp=int(row[0]),
                    close=float(row[1]),
                    volume=int(row[2]),
                    open_price=float(row[3]) if len(row) > 3 else None,
                )
            )
        if not bars:
            raise DataFetchError(f"No end-of-day price history found for {ticker}.")
        return bars

    def fetch_latest_intraday_price(self, ticker: str) -> float | None:
        try:
            with self._client() as client:
                response = client.get(f"/timeseries/int/{ticker}")
                if response.status_code >= 400:
                    return None
                payload = response.json()
        except httpx.HTTPError:
            return None

        data = payload.get("data") or []
        if not data:
            return None
        return float(data[0][1])

    def fetch_company_page(self, ticker: str) -> str:
        try:
            with self._client() as client:
                response = client.get(f"/company/{ticker}")
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as exc:
            raise DataFetchError(f"PSX company page request failed for {ticker}: {exc}") from exc

    def parse_company_page(self, html: str) -> ParsedCompanyPage:
        soup = BeautifulSoup(html, "html.parser")

        company_name = _text(soup.select_one(".quote__name")) or "Unknown Company"
        company_name = re.sub(r"\s+", " ", company_name.split("DELISTED")[0]).strip()

        sector_node = soup.select_one(".quote__sector span")
        sector = _text(sector_node) or "General / PSX Listed"

        description_node = soup.select_one(".profile__item--decription p")
        business_description = _text(description_node) or ""

        current_price = _parse_money(_text(soup.select_one(".quote__close")))
        change_value = _parse_money(_first_match(soup.select_one(".change__value")))
        change_percent = _parse_percent(_first_match(soup.select_one(".change__percent")))

        volume = None
        open_price = None
        ldcp = None
        pe_ratio_ttm = None
        for item in soup.select(".stats_item"):
            label = _text(item.select_one(".stats_label"))
            value = _text(item.select_one(".stats_value"))
            if not label:
                continue
            if label == "Volume":
                volume = _parse_int(value)
            elif label == "Open":
                open_price = _parse_money(value)
            elif label == "LDCP":
                ldcp = _parse_money(value)
            elif label.startswith("P/E Ratio"):
                pe_ratio_ttm = _parse_money(value)

        annual_eps = _extract_table_metric(soup, panel_name="Annual", row_label="EPS")
        latest_quarter_eps = _extract_table_metric(soup, panel_name="Quarterly", row_label="EPS")

        announcements: list[tuple[str, str]] = []
        for row in soup.select('#announcements .tbl__body tr'):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            date_text = _text(cells[0])
            title = _text(cells[1])
            if date_text and title:
                announcements.append((date_text, title))

        payout_snippets: list[str] = []
        for row in soup.select('#payouts .tbl__body tr'):
            cells = row.find_all("td")
            if len(cells) >= 2:
                payout_snippets.append(f"{_text(cells[0])}: {_text(cells[1])}")

        return ParsedCompanyPage(
            company_name=company_name,
            sector=sector,
            business_description=business_description,
            current_price=current_price,
            change_value=change_value,
            change_percent=change_percent,
            volume=volume,
            open_price=open_price,
            ldcp=ldcp,
            pe_ratio_ttm=pe_ratio_ttm,
            annual_eps=annual_eps,
            latest_quarter_eps=latest_quarter_eps,
            announcements=announcements,
            payout_snippets=payout_snippets,
        )

    def fetch_market_indices(self) -> list[dict[str, Any]]:
        try:
            with self._client() as client:
                response = client.get("/")
                response.raise_for_status()
                html = response.text
        except httpx.HTTPError as exc:
            raise DataFetchError(f"PSX market indices request failed: {exc}") from exc

        soup = BeautifulSoup(html, "html.parser")
        indices: list[dict[str, Any]] = []
        for item in soup.select(".topIndices__item"):
            name = _text(item.select_one(".topIndices__item__name"))
            value_text = _text(item.select_one(".topIndices__item__val"))
            change_text = _text(item.select_one(".topIndices__item__changep"))
            if not name:
                continue
            indices.append(
                {
                    "name": name,
                    "value": _parse_money(value_text),
                    "changePercent": _parse_percent(change_text),
                }
            )
        return indices


def eod_bar_to_history_point(bar: EodBar) -> dict[str, Any]:
    date = datetime.fromtimestamp(bar.timestamp, tz=timezone.utc).date().isoformat()
    return {"date": date, "close": round(bar.close, 2), "volume": bar.volume}


def _text(node: Any) -> str:
    if node is None:
        return ""
    return " ".join(node.get_text(" ", strip=True).split())


def _first_match(node: Any) -> str:
    return _text(node)


def _parse_money(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace("Rs.", "").replace(",", "").replace("%", "").strip()
    if cleaned.upper() in {"", "N/A", "NA", "-"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_percent(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace("(", "").replace(")", "").replace("%", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_int(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = value.replace(",", "").strip()
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _extract_table_metric(soup: BeautifulSoup, *, panel_name: str, row_label: str) -> float | None:
    panel = soup.select_one(f'.tabs__panel[data-name="{panel_name}"]')
    if panel is None:
        return None
    for row in panel.select("tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        if _text(cells[0]).upper() == row_label.upper():
            return _parse_money(_text(cells[1]))
    return None
