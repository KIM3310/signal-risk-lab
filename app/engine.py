from __future__ import annotations

from pathlib import Path
import json


TICKERS = [
    {"ticker": "KQH", "momentum": 0.74, "quality": 0.66, "value": 0.41, "volatility": 0.28},
    {"ticker": "DMS", "momentum": 0.62, "quality": 0.71, "value": 0.54, "volatility": 0.24},
    {"ticker": "RNT", "momentum": 0.31, "quality": 0.48, "value": 0.69, "volatility": 0.35},
    {"ticker": "SLV", "momentum": 0.18, "quality": 0.37, "value": 0.72, "volatility": 0.41},
    {"ticker": "MXG", "momentum": 0.83, "quality": 0.59, "value": 0.33, "volatility": 0.46},
]


def ranked_book() -> list[dict]:
    ranked = []
    for row in TICKERS:
        score = round(row["momentum"] * 0.45 + row["quality"] * 0.35 + row["value"] * 0.20 - row["volatility"] * 0.10, 4)
        ranked.append({**row, "score": score})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def factor_board() -> dict:
    ranked = ranked_book()
    return {
        "schema": "factor-board-v1",
        "signal_family": "quality-momentum-balanced",
        "top_longs": [row["ticker"] for row in ranked[:3]],
        "bottom_watchlist": [row["ticker"] for row in ranked[-2:]],
        "rows": ranked,
    }


def risk_report() -> dict:
    return {
        "schema": "risk-report-v1",
        "predicted_turnover": 0.19,
        "gross_exposure": 1.35,
        "sector_concentration_flag": "moderate",
        "drawdown_guard": "active",
        "notes": [
            "current book remains tradable after basic turnover guard",
            "single-name crowding is acceptable but not loose",
            "rebalance cadence should stay weekly rather than daily",
        ],
    }


def execution_posture() -> dict:
    return {
        "schema": "execution-posture-v1",
        "slippage_assumption_bps": 14,
        "capacity_bucket": "small-mid",
        "go_live_view": "reviewable paper-trade candidate",
        "why": [
            "signal remains positive after simple cost haircut",
            "turnover is below internal caution line",
            "risk posture is acceptable but still needs crowding watch",
        ],
    }


def research_pack() -> dict:
    board = factor_board()
    risk = risk_report()
    execution = execution_posture()
    return {
        "schema": "quant-research-pack-v1",
        "headline": "The book stays interesting only because signal quality survives cost and turnover scrutiny.",
        "top_longs": board["top_longs"],
        "predicted_turnover": risk["predicted_turnover"],
        "capacity_bucket": execution["capacity_bucket"],
        "go_live_view": execution["go_live_view"],
    }


def runtime_brief() -> dict:
    return {
        "schema": "signal-risk-runtime-brief-v1",
        "deploymentMode": "research-review",
        "routes": [
            "/health",
            "/api/runtime/brief",
            "/api/factor-board",
            "/api/risk-report",
            "/api/execution-posture",
            "/api/research-pack",
        ],
        "focus": [
            "factor signal",
            "risk discipline",
            "execution viability",
        ],
    }


def write_artifacts(base_dir: Path) -> Path:
    artifact_dir = base_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    target = artifact_dir / "latest_signal_report.json"
    target.write_text(json.dumps({
        "runtime_brief": runtime_brief(),
        "factor_board": factor_board(),
        "risk_report": risk_report(),
        "execution_posture": execution_posture(),
        "research_pack": research_pack(),
    }, indent=2), encoding="utf-8")
    return target

