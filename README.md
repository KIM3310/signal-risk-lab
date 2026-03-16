# Signal Risk Lab

`Signal Risk Lab` is a quant-style research surface for factor ranking, portfolio risk posture, and execution readiness.

The repo is intentionally focused on what a skeptical quant or systematic reviewer would want to see fast:

- what the signal says
- what the risk says
- whether the book is still tradable after costs and turnover

## Reviewer path

1. `GET /health`
2. `GET /api/runtime/brief`
3. `GET /api/factor-board`
4. `GET /api/risk-report`
5. `GET /api/execution-posture`
6. `GET /api/research-pack`
7. open `docs/index.html`

## Why this repo fits quant and securities teams

- signal and risk are separated instead of blurred together
- execution posture is visible before anyone claims the strategy is usable
- research output is reviewer-safe and concise

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e ".[dev]"
python3 scripts/build_artifacts.py
uvicorn app.main:app --reload
```

## Verification

```bash
pytest
python3 scripts/build_artifacts.py
```

## Core API

- `GET /health`
- `GET /api/runtime/brief`
- `GET /api/factor-board`
- `GET /api/risk-report`
- `GET /api/execution-posture`
- `GET /api/research-pack`

