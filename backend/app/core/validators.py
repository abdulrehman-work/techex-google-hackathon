import re

from .exceptions import TickerValidationError

_TICKER_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.-]{0,14}$")


def validate_ticker(raw_ticker: str) -> str:
    """Normalize and validate a PSX ticker symbol."""
    if not raw_ticker or not raw_ticker.strip():
        raise TickerValidationError("Ticker is required.")

    ticker = raw_ticker.strip().upper()
    if not _TICKER_PATTERN.fullmatch(ticker):
        raise TickerValidationError(
            "Ticker must be 1-15 characters and contain only letters, numbers, dots, or hyphens."
        )
    return ticker
