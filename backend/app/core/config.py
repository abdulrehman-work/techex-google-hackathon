from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator
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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "no", "off"}:
                return False
            if normalized in {"dev", "development", "debug", "true", "1", "yes", "on"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
