from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_MACRO_CONFIG = _BACKEND_ROOT / "data" / "macro_defaults.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Trading Agent API"
    debug: bool = False
    psx_base_url: str = "https://dps.psx.com.pk"
    psx_request_timeout_seconds: float = 20.0
    price_history_days: int = 30
    news_max_items: int = 5
    filings_max_items: int = 3
    macro_config_path: str = str(_DEFAULT_MACRO_CONFIG)
    user_agent: str = (
        "Mozilla/5.0 (compatible; TechexTradingAgent/1.0; +https://github.com/techex-hackathon)"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
