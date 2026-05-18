from __future__ import annotations

from dataclasses import dataclass

from app.clients.psx_client import ParsedCompanyPage, PsxClient
from app.core.config import get_settings


@dataclass(frozen=True)
class FilingRecord:
    date: str
    title: str


@dataclass(frozen=True)
class FilingsData:
    records: list[FilingRecord]
    filing_text: str


class FilingsService:
    """Collects company report and filing text from PSX announcements."""

    def __init__(self, psx_client: PsxClient | None = None) -> None:
        self._psx = psx_client or PsxClient()
        self._settings = get_settings()

    def get_relevant_filing_text(
        self,
        ticker: str,
        *,
        company_page: ParsedCompanyPage | None = None,
    ) -> FilingsData:
        page = company_page or self._psx.parse_company_page(self._psx.fetch_company_page(ticker))
        limit = self._settings.filings_max_items

        records = [
            FilingRecord(date=date, title=title)
            for date, title in page.announcements[:limit]
        ]

        if not records and page.business_description:
            filing_text = page.business_description
        else:
            filing_text = _build_filing_text(records, page.business_description)

        return FilingsData(records=records, filing_text=filing_text)


def _build_filing_text(records: list[FilingRecord], business_description: str) -> str:
    lines = []
    if business_description:
        lines.append(business_description)
    if records:
        lines.append("Recent PSX filings and announcements:")
        for record in records:
            lines.append(f"- {record.date}: {record.title}")
    return " ".join(lines).strip()
