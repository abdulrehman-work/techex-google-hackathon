from __future__ import annotations

from dataclasses import dataclass

from app.clients.psx_client import ParsedCompanyPage, PsxClient


@dataclass(frozen=True)
class CompanyProfileData:
    company_name: str
    sector: str
    business_description: str


class CompanyService:
    """Fetches company identity and profile metadata."""

    def __init__(self, psx_client: PsxClient | None = None) -> None:
        self._psx = psx_client or PsxClient()

    def get_company_profile(self, ticker: str, *, company_page: ParsedCompanyPage | None = None) -> CompanyProfileData:
        page = company_page or self._psx.parse_company_page(self._psx.fetch_company_page(ticker))
        return CompanyProfileData(
            company_name=page.company_name,
            sector=page.sector,
            business_description=page.business_description,
        )
