from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.clients.psx_client import PsxClient
from app.core.config import get_settings


@dataclass(frozen=True)
class MacroContextData:
    sbp_policy_rate: str
    pkr_usd_trend: str
    inflation_view: str
    oil_price_risk: str
    market_condition: str


class MacroService:
    """Provides economy and broad market context."""

    def __init__(self, psx_client: PsxClient | None = None) -> None:
        self._psx = psx_client or PsxClient()
        self._settings = get_settings()

    def get_macro_context(self) -> MacroContextData:
        defaults = _load_macro_defaults(self._settings.macro_config_path)
        market_condition = defaults.get("marketCondition", "neutral")

        try:
            indices = self._psx.fetch_market_indices()
            kse100 = next((item for item in indices if item.get("name") == "KSE100"), None)
            if kse100 and kse100.get("changePercent") is not None:
                market_condition = _market_condition_from_change(float(kse100["changePercent"]))
        except Exception:
            pass

        return MacroContextData(
            sbp_policy_rate=str(defaults.get("sbpPolicyRate", "N/A")),
            pkr_usd_trend=str(defaults.get("pkrUsdTrend", "stable")),
            inflation_view=str(defaults.get("inflationView", "moderating")),
            oil_price_risk=str(defaults.get("oilPriceRisk", "medium")),
            market_condition=market_condition,
        )


def _load_macro_defaults(config_path: str) -> dict[str, str]:
    path = Path(config_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        return {
            "sbpPolicyRate": "11.50%",
            "pkrUsdTrend": "stable",
            "inflationView": "moderating",
            "oilPriceRisk": "medium",
            "marketCondition": "neutral",
        }
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _market_condition_from_change(change_percent: float) -> str:
    if change_percent <= -1.5:
        return "risk-off downtrend"
    if change_percent >= 1.5:
        return "risk-on uptrend"
    return "neutral"
