# AI Trading Agent

A modular, explainable, Gemini-powered financial intelligence pipeline for
single-stock analysis. Each agent is an independent Gemini API call with a
specialized financial role and strict JSON output.

## Suggested File Structure

```text
ai_trading_agent/
  __init__.py
  agents.py
  gemini_client.py
  orchestrator.py
examples/
  example_usage.py
tests/
  test_pipeline.py
```

## Setup

```bash
uv venv .venv
uv pip install -r requirements.txt --python .venv/bin/python
uv pip install -e . --python .venv/bin/python
source .venv/bin/activate
export GEMINI_API_KEY="your-key"
```

Optionally set a model:

```bash
export GEMINI_MODEL="gemini-3-flash-preview"
```

If you see `unexpected model name format`, clear any old model override:

```bash
unset GEMINI_MODEL
```

## Run The Example

```bash
python examples/example_usage.py
```

On Ubuntu/Debian, avoid installing with system `pip install -r requirements.txt`.
Those distributions may block system-wide installs with an
`externally-managed-environment` error. Use the project virtual environment
above instead.

## Use In Code

```python
from ai_trading_agent import run_pipeline

result = run_pipeline(stock_payload)
```

The returned response includes:

```json
{
  "ticker": "ENGRO",
  "signal": "BUY | HOLD | SELL",
  "confidence": 0,
  "opportunityScore": 0,
  "governanceStatus": "APPROVED | FLAGGED",
  "governanceReason": "Gemini-generated governance reason",
  "breakdown": {
    "research": {},
    "macro": {},
    "sentiment": {},
    "risk": {},
    "portfolio": {},
    "governance": {}
  }
}
```

No scraping or ETL happens inside this package. The backend is expected to pass
clean structured JSON.

## Run The Backend API

The FastAPI backend builds the stock context, sends it into the Gemini agent
pipeline, and returns the final analysis in the `analysis` field.

```bash
source .venv/bin/activate
export GEMINI_API_KEY="your-key"
PYTHONPATH=backend uvicorn app.main:app --reload
```

If you start the server from inside the `backend/` directory, include the
project root on `PYTHONPATH`:

```bash
cd backend
PYTHONPATH=.. uvicorn app.main:app --reload
```

Analyze a ticker:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"ENGRO"}'
```

If PSX blocks or rejects the upstream market-data request, this endpoint returns
`502` with the upstream fetch error in `detail`.

To test the AI pipeline without depending on PSX, post a complete structured
context directly:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze/context" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ENGRO",
    "companyProfile": {
      "companyName": "Engro Corporation",
      "sector": "Fertilizer / Conglomerate"
    },
    "stockData": {
      "currentPrice": 312.5,
      "previousClose": 308.2,
      "changePercent": 1.4,
      "volume": 1200000
    },
    "priceHistory": [
      {
        "date": "2026-05-15",
        "close": 312.5,
        "volume": 1200000
      }
    ],
    "fundamentals": {
      "eps": 18.2,
      "peRatio": 8.1,
      "dividendYield": 7.5,
      "roe": 16.4,
      "financialSummary": "The company reported stable earnings and maintained dividend payouts."
    },
    "news": [
      {
        "source": "Business Recorder",
        "headline": "Fertilizer sector gains as market sentiment improves",
        "snippet": "Investors showed renewed interest in fertilizer stocks."
      }
    ],
    "macroContext": {
      "sbpPolicyRate": "11.50%",
      "pkrUsdTrend": "stable",
      "inflationView": "moderating",
      "oilPriceRisk": "medium",
      "marketCondition": "neutral"
    },
    "riskMetrics": {
      "dailyChangePercent": 1.4,
      "simpleVolatility": "medium",
      "volumeTrend": "increasing"
    }
  }'
```

If `GEMINI_API_KEY` is missing or Gemini rejects the request, `/api/analyze`
returns a `502` with the AI pipeline error in `detail`.

## Run Tests

```bash
PYTHONPATH=backend python -m unittest discover -s backend/tests
python -m unittest discover -s tests
```
