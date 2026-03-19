"""Comprehensive parametrized tests for the Finance Review Platform."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Health endpoint
# ---------------------------------------------------------------------------

def test_health_status():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "finance-review-platform"
    assert set(body["domains"]) == {"quant", "advisory"}


# ---------------------------------------------------------------------------
# 2. Unified runtime brief
# ---------------------------------------------------------------------------

def test_runtime_brief_structure():
    resp = client.get("/api/runtime/brief")
    assert resp.status_code == 200
    body = resp.json()
    assert body["schema"] == "platform-runtime-brief-v1"
    assert "quant" in body["domains"]
    assert "advisory" in body["domains"]


# ---------------------------------------------------------------------------
# 3. Parametrized route reachability -- all domain routes return 200 + schema
# ---------------------------------------------------------------------------

QUANT_ROUTES = [
    "/api/quant/brief",
    "/api/quant/factor-board",
    "/api/quant/risk-report",
    "/api/quant/execution-posture",
    "/api/quant/research-pack",
]

ADVISORY_ROUTES = [
    "/api/advisory/brief",
    "/api/advisory/client-suitability",
    "/api/advisory/portfolio-rationale",
    "/api/advisory/advisor-handoff",
    "/api/advisory/review-pack",
]


@pytest.mark.parametrize("route", QUANT_ROUTES)
def test_quant_route_reachable(route: str):
    resp = client.get(route)
    assert resp.status_code == 200
    assert "schema" in resp.json()


@pytest.mark.parametrize("route", ADVISORY_ROUTES)
def test_advisory_route_reachable(route: str):
    resp = client.get(route)
    assert resp.status_code == 200
    assert "schema" in resp.json()


# ---------------------------------------------------------------------------
# 4. Quant domain -- factor scoring correctness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "ticker_data,expected_first",
    [
        (
            [
                {"ticker": "AAA", "momentum": 0.9, "quality": 0.9, "value": 0.9, "volatility": 0.1},
                {"ticker": "ZZZ", "momentum": 0.1, "quality": 0.1, "value": 0.1, "volatility": 0.9},
            ],
            "AAA",
        ),
        (
            [
                {"ticker": "LOW", "momentum": 0.2, "quality": 0.2, "value": 0.2, "volatility": 0.8},
                {"ticker": "HIGH", "momentum": 0.8, "quality": 0.8, "value": 0.8, "volatility": 0.2},
            ],
            "HIGH",
        ),
    ],
)
def test_quant_factor_ranking_order(ticker_data: list[dict], expected_first: str):
    from app.domains.quant.engine import ranked_book

    ranked = ranked_book(ticker_data)
    assert ranked[0].ticker == expected_first


# ---------------------------------------------------------------------------
# 5. Quant domain -- score computation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "momentum,quality,value,volatility,expected_score",
    [
        (1.0, 1.0, 1.0, 0.0, round(0.45 + 0.35 + 0.20, 4)),
        (0.0, 0.0, 0.0, 1.0, round(-0.10, 4)),
        (0.5, 0.5, 0.5, 0.5, round(0.5 * 0.45 + 0.5 * 0.35 + 0.5 * 0.20 - 0.5 * 0.10, 4)),
    ],
)
def test_quant_score_computation(
    momentum: float, quality: float, value: float, volatility: float, expected_score: float
):
    from app.domains.quant.engine import score_ticker
    from app.domains.quant.schemas import TickerSignal

    signal = TickerSignal(ticker="TST", momentum=momentum, quality=quality, value=value, volatility=volatility)
    scored = score_ticker(signal)
    assert scored.score == expected_score


# ---------------------------------------------------------------------------
# 6. Quant domain -- risk report invariants
# ---------------------------------------------------------------------------

def test_quant_risk_report_invariants():
    from app.domains.quant.engine import risk_report

    report = risk_report()
    assert 0.0 <= report.predicted_turnover <= 1.0
    assert report.gross_exposure > 0
    assert len(report.notes) > 0


# ---------------------------------------------------------------------------
# 7. Advisory domain -- client suitability structure
# ---------------------------------------------------------------------------

def test_advisory_suitability_structure():
    from app.domains.advisory.engine import client_suitability

    pack = client_suitability()
    assert pack.client.client_id == "han-growth-042"
    assert pack.recommendation.suitability_view != ""
    assert len(pack.recommendation.compliance_notes) > 0


# ---------------------------------------------------------------------------
# 8. Advisory domain -- portfolio mix sums approximately to 1.0
# ---------------------------------------------------------------------------

def test_advisory_portfolio_mix_sums_to_one():
    from app.domains.advisory.engine import SEED_PORTFOLIO

    mix = SEED_PORTFOLIO.current_mix
    total = mix.cash + mix.domestic_equity + mix.global_equity + mix.bond + mix.thematic_growth
    assert abs(total - 1.0) < 0.01


# ---------------------------------------------------------------------------
# 9. Pydantic validation -- TickerSignal rejects out-of-range values
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("momentum", 1.5),
        ("quality", -0.1),
        ("value", 2.0),
        ("volatility", -1.0),
    ],
)
def test_ticker_signal_rejects_bad_values(field: str, bad_value: float):
    from pydantic import ValidationError
    from app.domains.quant.schemas import TickerSignal

    data = {"ticker": "BAD", "momentum": 0.5, "quality": 0.5, "value": 0.5, "volatility": 0.5}
    data[field] = bad_value
    with pytest.raises(ValidationError):
        TickerSignal(**data)


# ---------------------------------------------------------------------------
# 10. Pydantic validation -- ClientReview rejects invalid risk profile
# ---------------------------------------------------------------------------

def test_client_review_rejects_invalid_risk_profile():
    from pydantic import ValidationError
    from app.domains.advisory.schemas import ClientReview

    with pytest.raises(ValidationError):
        ClientReview(
            client_id="bad-001",
            client_name="Bad Client",
            meeting_type="annual",
            risk_profile="yolo",
            liquidity_need="medium",
            current_focus=["test"],
        )


# ---------------------------------------------------------------------------
# 11. Pydantic validation -- PortfolioMix rejects negative allocation
# ---------------------------------------------------------------------------

def test_portfolio_mix_rejects_negative():
    from pydantic import ValidationError
    from app.domains.advisory.schemas import PortfolioMix

    with pytest.raises(ValidationError):
        PortfolioMix(cash=-0.1, domestic_equity=0.5, global_equity=0.3, bond=0.2, thematic_growth=0.1)


# ---------------------------------------------------------------------------
# 12. Advisory review pack has required fields
# ---------------------------------------------------------------------------

def test_advisory_review_pack_fields():
    from app.domains.advisory.engine import review_pack

    pack = review_pack()
    assert pack.headline != ""
    assert pack.client_name != ""
    assert pack.handoff_owner != ""
    assert len(pack.key_flags) > 0
