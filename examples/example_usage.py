"""Example usage for the AI trading agent pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_trading_agent import GeminiConfigurationError, GeminiRequestError, run_pipeline


example_input = {
    "ticker": "XYZ",
    "companyProfile": {
        "companyName": "XYZ Energy Corp",
        "sector": "Oil & Gas / High Volatility"
    },
    "stockData": {
        "currentPrice": 12.4,
        "previousClose": 13.8,
        "changePercent": -10.14,
        "volume": 9800000
    },
    "priceHistory": [
        {
            "date": "2026-05-15",
            "close": 15.2,
            "volume": 12000000
        },
        {
            "date": "2026-05-16",
            "close": 14.1,
            "volume": 11000000
        },
        {
            "date": "2026-05-17",
            "close": 13.8,
            "volume": 10500000
        },
        {
            "date": "2026-05-18",
            "close": 12.4,
            "volume": 9800000
        }
    ],
    "fundamentals": {
        "eps": -2.35,
        "peRatio": 48.7,
        "dividendYield": 0.0,
        "roe": -18.6,
        "financialSummary": "The company is experiencing widening losses, declining revenue, increasing debt, and weakening cash flow. Profitability remains negative."
    },
    "news": [
        {
            "source": "Financial Times",
            "headline": "XYZ Energy reports deeper losses amid demand slowdown",
            "snippet": "Revenue continues to decline as oil demand weakens globally."
        },
        {
            "source": "Market Watch",
            "headline": "Analysts downgrade XYZ Energy due to balance sheet concerns",
            "snippet": "Rising debt and liquidity pressure raise long-term sustainability concerns."
        }
    ],
    "macroContext": {
        "sbpPolicyRate": "13.75%",
        "pkrUsdTrend": "weakening",
        "inflationView": "high inflation",
        "oilPriceRisk": "high volatility",
        "marketCondition": "risk-off downtrend"
    },
    "riskMetrics": {
        "dailyChangePercent": -10.14,
        "simpleVolatility": "high",
        "volumeTrend": "panic selling spike"
    }
}


if __name__ == "__main__":
    try:
        result = run_pipeline(example_input)
    except GeminiConfigurationError as exc:
        print(f"Gemini is not configured: {exc}")
        print(
            "Run `uv pip install -r requirements.txt --python .venv/bin/python`, "
            "then set GEMINI_API_KEY."
        )
    except GeminiRequestError as exc:
        print(f"Gemini request failed: {exc}")
        print("Try: unset GEMINI_MODEL")
    else:
        print(json.dumps(result, indent=2))
