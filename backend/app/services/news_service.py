from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import httpx

from app.core.config import get_settings
from app.services.company_service import CompanyProfileData


@dataclass(frozen=True)
class NewsArticle:
    source: str
    headline: str
    snippet: str


class NewsService:
    """Fetches latest company headlines and snippets."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def get_company_news(self, ticker: str, company_profile: CompanyProfileData) -> list[NewsArticle]:
        query = quote_plus(f"{company_profile.company_name} {ticker} Pakistan stock")
        url = (
            "https://news.google.com/rss/search"
            f"?q={query}&hl=en-PK&gl=PK&ceid=PK:en"
        )
        headers = {"User-Agent": self._settings.user_agent}

        try:
            with httpx.Client(timeout=self._settings.psx_request_timeout_seconds, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                root = ET.fromstring(response.text)
        except (httpx.HTTPError, ET.ParseError):
            return _fallback_news(ticker, company_profile)

        articles: list[NewsArticle] = []
        for item in root.findall(".//item")[: self._settings.news_max_items]:
            title = _node_text(item.find("title"))
            source = _node_text(item.find("source")) or "Google News"
            description = _clean_snippet(_node_text(item.find("description")))
            if not title:
                continue
            articles.append(
                NewsArticle(
                    source=source,
                    headline=title,
                    snippet=description or title,
                )
            )

        if articles:
            return articles
        return _fallback_news(ticker, company_profile)


def _node_text(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return unescape(node.text.strip())


def _clean_snippet(raw: str) -> str:
    if not raw:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(unescape(without_tags).split())


def _fallback_news(ticker: str, profile: CompanyProfileData) -> list[NewsArticle]:
    return [
        NewsArticle(
            source="PSX Data Portal",
            headline=f"Latest market activity for {ticker}",
            snippet=(
                f"No external headlines were retrieved. Use PSX announcements and price action for "
                f"{profile.company_name}."
            ),
        )
    ]
