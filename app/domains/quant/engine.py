"""Quant domain engine: factor scoring, risk assessment, and execution readiness."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.domains.quant.schemas import (
    CapacityBucket,
    ConcentrationFlag,
    DrawdownGuard,
    ExecutionPosture,
    FactorBoard,
    FactorWeights,
    QuantResearchPack,
    RiskReport,
    TickerSignal,
)

logger = logging.getLogger(__name__)

SEED_TICKERS: list[dict[str, Any]] = [
    {"ticker": "KQH", "momentum": 0.74, "quality": 0.66, "value": 0.41, "volatility": 0.28},
    {"ticker": "DMS", "momentum": 0.62, "quality": 0.71, "value": 0.54, "volatility": 0.24},
    {"ticker": "RNT", "momentum": 0.31, "quality": 0.48, "value": 0.69, "volatility": 0.35},
    {"ticker": "SLV", "momentum": 0.18, "quality": 0.37, "value": 0.72, "volatility": 0.41},
    {"ticker": "MXG", "momentum": 0.83, "quality": 0.59, "value": 0.33, "volatility": 0.46},
]

DEFAULT_WEIGHTS = FactorWeights()


def score_ticker(ticker: TickerSignal, weights: FactorWeights = DEFAULT_WEIGHTS) -> TickerSignal:
    """Compute composite factor score for a single ticker.

    Args:
        ticker: The ticker signal containing raw factor values.
        weights: Factor weights to apply. Defaults to balanced weights.

    Returns:
        A copy of the ticker with the computed composite score.
    """
    score = round(
        ticker.momentum * weights.momentum
        + ticker.quality * weights.quality
        + ticker.value * weights.value
        - ticker.volatility * weights.volatility_penalty,
        4,
    )
    return ticker.model_copy(update={"score": score})


def ranked_book(
    tickers: list[dict[str, Any]] | None = None,
    weights: FactorWeights = DEFAULT_WEIGHTS,
) -> list[TickerSignal]:
    """Score and rank the ticker universe by composite factor score.

    Args:
        tickers: Optional list of raw ticker dicts. Falls back to seed data.
        weights: Factor weights for scoring.

    Returns:
        List of scored TickerSignal objects sorted descending by score.

    Raises:
        ValueError: If tickers list is provided but empty.
    """
    raw = tickers if tickers is not None else SEED_TICKERS
    if not raw:
        raise ValueError("Ticker list must not be empty")
    logger.info("Scoring %d tickers", len(raw))
    scored = [score_ticker(TickerSignal(**row), weights) for row in raw]
    return sorted(scored, key=lambda t: t.score or 0.0, reverse=True)


def factor_board(tickers: list[dict[str, Any]] | None = None) -> FactorBoard:
    """Build the factor board showing top longs and watchlist.

    Args:
        tickers: Optional list of raw ticker dicts.

    Returns:
        FactorBoard with ranked rows and top/bottom selections.
    """
    ranked = ranked_book(tickers)
    return FactorBoard(
        schema_="factor-board-v1",
        signal_family="quality-momentum-balanced",
        top_longs=[t.ticker for t in ranked[:3]],
        bottom_watchlist=[t.ticker for t in ranked[-2:]],
        rows=ranked,
    )


def risk_report() -> RiskReport:
    """Generate the current risk report with exposure and guard status.

    Returns:
        RiskReport with turnover, exposure, and concentration data.
    """
    return RiskReport(
        schema_="risk-report-v1",
        predicted_turnover=0.19,
        gross_exposure=1.35,
        sector_concentration_flag=ConcentrationFlag.moderate,
        drawdown_guard=DrawdownGuard.active,
        notes=[
            "current book remains tradable after basic turnover guard",
            "single-name crowding is acceptable but not loose",
            "rebalance cadence should stay weekly rather than daily",
        ],
    )


def execution_posture() -> ExecutionPosture:
    """Assess execution viability and capacity for current book.

    Returns:
        ExecutionPosture with slippage, capacity, and go-live assessment.
    """
    return ExecutionPosture(
        schema_="execution-posture-v1",
        slippage_assumption_bps=14,
        capacity_bucket=CapacityBucket.small_mid,
        go_live_view="reviewable paper-trade candidate",
        why=[
            "signal remains positive after simple cost haircut",
            "turnover is below internal caution line",
            "risk posture is acceptable but still needs crowding watch",
        ],
    )


def research_pack() -> QuantResearchPack:
    """Compile the full quant research pack combining all analyses.

    Returns:
        QuantResearchPack summary for research review desk.
    """
    board = factor_board()
    risk = risk_report()
    execution = execution_posture()
    return QuantResearchPack(
        schema_="quant-research-pack-v1",
        headline="The book stays interesting only because signal quality survives cost and turnover scrutiny.",
        top_longs=board.top_longs,
        predicted_turnover=risk.predicted_turnover,
        capacity_bucket=execution.capacity_bucket,
        go_live_view=execution.go_live_view,
    )


def runtime_brief() -> dict[str, Any]:
    """Return quant domain runtime brief for the unified platform view.

    Returns:
        Dictionary describing deployment mode, routes, and focus areas.
    """
    return {
        "schema": "quant-runtime-brief-v1",
        "deploymentMode": "research-review",
        "routes": [
            "/api/quant/factor-board",
            "/api/quant/risk-report",
            "/api/quant/execution-posture",
            "/api/quant/research-pack",
        ],
        "focus": [
            "factor signal",
            "risk discipline",
            "execution viability",
        ],
    }


def write_artifacts(base_dir: Path) -> Path:
    """Serialize all quant outputs to a JSON artifact file.

    Args:
        base_dir: Project root directory. Artifacts are written under ``base_dir/artifacts/``.

    Returns:
        Path to the written artifact file.

    Raises:
        OSError: If the artifact directory cannot be created or written to.
    """
    artifact_dir = base_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    target = artifact_dir / "latest_signal_report.json"
    logger.info("Writing quant artifacts to %s", target)
    try:
        target.write_text(
            json.dumps(
                {
                    "runtime_brief": runtime_brief(),
                    "factor_board": factor_board().model_dump(by_alias=True),
                    "risk_report": risk_report().model_dump(by_alias=True),
                    "execution_posture": execution_posture().model_dump(by_alias=True),
                    "research_pack": research_pack().model_dump(by_alias=True),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        logger.exception("Failed to write artifacts to %s", target)
        raise
    return target
