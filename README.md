# Signal Risk Lab

[![CI](https://github.com/KIM3310/signal-risk-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/KIM3310/signal-risk-lab/actions/workflows/ci.yml)
![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

A domain-driven FastAPI application that unifies **quant signal/risk research** and **brokerage advisory review** into a single platform.

The design demonstrates how two distinct finance domains -- systematic trading research and wealth-management client review -- can coexist under a shared architecture without blurring their boundaries.

## Architecture

```
app/
  main.py                      # Unified FastAPI entry point
  shared/                      # Cross-domain concerns
    schemas.py                 # Shared Pydantic models (health, base review pack)
    health.py                  # Platform health check
  domains/
    quant/                     # Quant signal/risk bounded context
      schemas.py               # TickerSignal, FactorBoard, RiskReport, etc.
      engine.py                # Factor scoring, risk assessment, execution readiness
      router.py                # /api/quant/* routes
    advisory/                  # Brokerage advisory bounded context
      schemas.py               # ClientReview, PortfolioMix, AdvisorHandoff, etc.
      engine.py                # Suitability, rationale, handoff logic
      router.py                # /api/advisory/* routes
```

Each domain owns its **schemas**, **engine logic**, and **router** -- the hallmark of domain-driven design applied to financial services.

## Why this matters for finance teams

### Quant domain
- Signal and risk are separated instead of blurred behind a single score
- Factor weights are explicit and testable
- Execution posture is visible before anyone claims a strategy is production-ready

### Advisory domain
- Client suitability, portfolio rationale, and recommendation travel together
- Compliance notes and advisor handoff are first-class workflow steps
- Explanation language stays plain and product-neutral

### Platform-level
- Pydantic validation enforces input constraints at every boundary (factor scores in [0,1], valid risk profiles, non-negative allocations)
- Both domains share health checks and base schemas without coupling their logic
- Parametrized test suite covers scoring correctness, validation edge cases, and route reachability across both domains

## API reference

### Platform
| Route | Description |
|---|---|
| `GET /health` | Unified health check |
| `GET /api/runtime/brief` | Platform-wide runtime brief |

### Quant domain (`/api/quant/`)
| Route | Description |
|---|---|
| `GET /api/quant/brief` | Quant runtime brief |
| `GET /api/quant/factor-board` | Factor-ranked ticker universe |
| `GET /api/quant/risk-report` | Portfolio risk posture |
| `GET /api/quant/execution-posture` | Execution readiness assessment |
| `GET /api/quant/research-pack` | Combined quant research summary |

### Advisory domain (`/api/advisory/`)
| Route | Description |
|---|---|
| `GET /api/advisory/brief` | Advisory runtime brief |
| `GET /api/advisory/client-suitability` | Client profile, portfolio, and recommendation |
| `GET /api/advisory/portfolio-rationale` | House view and rebalance rationale |
| `GET /api/advisory/advisor-handoff` | Handoff notes and meeting prep |
| `GET /api/advisory/review-pack` | Combined advisory review summary |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000`.

## Verification

```bash
pytest -v
python3 scripts/build_artifacts.py
python3 scripts/exercise_runtime.py
```

## What this proves

- **Domain-driven design** applied to real finance workflows, not toy examples
- **Pydantic-first validation** at every schema boundary
- **Parametrized testing** covering scoring math, validation constraints, and full route coverage
- **Clean separation** that lets quant and advisory teams evolve independently
- **Inspectable outputs** where every claim is backed by structured data
