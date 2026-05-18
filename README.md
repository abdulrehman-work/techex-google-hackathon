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
