"""Comprehensive tests for the Finance Review Platform.

Covers:
  - Health endpoint
  - Unified runtime brief
  - All quant and advisory route reachability
  - Quant factor scoring correctness
  - Quant risk report invariants
  - Advisory suitability structure
  - Portfolio mix validation
  - Pydantic validation edge cases
  - Error handling for invalid inputs
  - Empty data handling
  - Advisory review pack completeness
  - Execution posture invariants
  - Research pack assembly
  - Factor board structure
  - Advisor handoff structure
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Health endpoint
# ---------------------------------------------------------------------------


def test_health_status() -> None:
    """Health endpoint returns ok status with both domains."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "finance-review-platform"
    assert set(body["domains"]) == {"quant", "advisory"}


# ---------------------------------------------------------------------------
# 2. Unified runtime brief
# ---------------------------------------------------------------------------


def test_runtime_brief_structure() -> None:
    """Runtime brief contains both domain sub-briefs."""
    resp = client.get("/api/runtime/brief")
    assert resp.status_code == 200
    body = resp.json()
    assert body["schema"] == "platform-runtime-brief-v1"
    assert "quant" in body["domains"]
    assert "advisory" in body["domains"]


def test_runtime_brief_quant_has_routes() -> None:
    """Quant sub-brief lists its routes."""
    resp = client.get("/api/runtime/brief")
    body = resp.json()
    quant = body["domains"]["quant"]
    assert "routes" in quant
    assert len(quant["routes"]) > 0


def test_runtime_brief_advisory_has_desk() -> None:
    """Advisory sub-brief includes desk info."""
    resp = client.get("/api/runtime/brief")
    body = resp.json()
    advisory = body["domains"]["advisory"]
    assert advisory["desk"] == "brokerage-client-review"


# ---------------------------------------------------------------------------
# 3. Parametrized route reachability
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
def test_quant_route_reachable(route: str) -> None:
    """Each quant route returns 200 with a schema field."""
    resp = client.get(route)
    assert resp.status_code == 200
    assert "schema" in resp.json()


@pytest.mark.parametrize("route", ADVISORY_ROUTES)
def test_advisory_route_reachable(route: str) -> None:
    """Each advisory route returns 200 with a schema field."""
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
def test_quant_factor_ranking_order(ticker_data: list[dict[str, Any]], expected_first: str) -> None:
    """Higher factor scores rank first in the book."""
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
) -> None:
    """Composite score matches weighted formula."""
    from app.domains.quant.engine import score_ticker
    from app.domains.quant.schemas import TickerSignal

    signal = TickerSignal(ticker="TST", momentum=momentum, quality=quality, value=value, volatility=volatility)
    scored = score_ticker(signal)
    assert scored.score == expected_score


# ---------------------------------------------------------------------------
# 6. Quant domain -- custom weights
# ---------------------------------------------------------------------------


def test_quant_score_with_custom_weights() -> None:
    """Score changes when custom weights are applied."""
    from app.domains.quant.engine import score_ticker
    from app.domains.quant.schemas import FactorWeights, TickerSignal

    signal = TickerSignal(ticker="CW", momentum=0.5, quality=0.5, value=0.5, volatility=0.5)
    default_scored = score_ticker(signal)
    custom_weights = FactorWeights(momentum=0.90, quality=0.05, value=0.05, volatility_penalty=0.0)
    custom_scored = score_ticker(signal, custom_weights)
    assert custom_scored.score != default_scored.score
    assert custom_scored.score is not None
    assert custom_scored.score == round(0.5 * 0.90 + 0.5 * 0.05 + 0.5 * 0.05 - 0.5 * 0.0, 4)


# ---------------------------------------------------------------------------
# 7. Quant domain -- risk report invariants
# ---------------------------------------------------------------------------


def test_quant_risk_report_invariants() -> None:
    """Risk report values stay within expected bounds."""
    from app.domains.quant.engine import risk_report

    report = risk_report()
    assert 0.0 <= report.predicted_turnover <= 1.0
    assert report.gross_exposure > 0
    assert len(report.notes) > 0


# ---------------------------------------------------------------------------
# 8. Quant domain -- execution posture invariants
# ---------------------------------------------------------------------------


def test_quant_execution_posture_invariants() -> None:
    """Execution posture has non-negative slippage and reasoning."""
    from app.domains.quant.engine import execution_posture

    posture = execution_posture()
    assert posture.slippage_assumption_bps >= 0
    assert len(posture.why) > 0
    assert posture.go_live_view != ""


# ---------------------------------------------------------------------------
# 9. Quant domain -- research pack assembly
# ---------------------------------------------------------------------------


def test_quant_research_pack_fields() -> None:
    """Research pack assembles data from factor board, risk, and execution."""
    from app.domains.quant.engine import research_pack

    pack = research_pack()
    assert len(pack.top_longs) > 0
    assert 0.0 <= pack.predicted_turnover <= 1.0
    assert pack.headline != ""
    assert pack.go_live_view != ""


# ---------------------------------------------------------------------------
# 10. Quant domain -- factor board structure
# ---------------------------------------------------------------------------


def test_quant_factor_board_structure() -> None:
    """Factor board has correct top longs and watchlist sizes."""
    from app.domains.quant.engine import factor_board

    board = factor_board()
    assert len(board.top_longs) == 3
    assert len(board.bottom_watchlist) == 2
    assert len(board.rows) == 5
    assert board.signal_family == "quality-momentum-balanced"


# ---------------------------------------------------------------------------
# 11. Quant domain -- empty ticker list raises ValueError
# ---------------------------------------------------------------------------


def test_quant_ranked_book_empty_raises() -> None:
    """Passing an empty ticker list raises ValueError."""
    from app.domains.quant.engine import ranked_book

    with pytest.raises(ValueError, match="must not be empty"):
        ranked_book([])


# ---------------------------------------------------------------------------
# 12. Advisory domain -- client suitability structure
# ---------------------------------------------------------------------------


def test_advisory_suitability_structure() -> None:
    """Suitability pack has expected client and recommendation data."""
    from app.domains.advisory.engine import client_suitability

    pack = client_suitability()
    assert pack.client.client_id == "han-growth-042"
    assert pack.recommendation.suitability_view != ""
    assert len(pack.recommendation.compliance_notes) > 0


# ---------------------------------------------------------------------------
# 13. Advisory domain -- portfolio mix sums approximately to 1.0
# ---------------------------------------------------------------------------


def test_advisory_portfolio_mix_sums_to_one() -> None:
    """Portfolio allocations sum to approximately 1.0."""
    from app.domains.advisory.engine import SEED_PORTFOLIO

    mix = SEED_PORTFOLIO.current_mix
    total = mix.cash + mix.domestic_equity + mix.global_equity + mix.bond + mix.thematic_growth
    assert abs(total - 1.0) < 0.01


# ---------------------------------------------------------------------------
# 14. Advisory domain -- review pack completeness
# ---------------------------------------------------------------------------


def test_advisory_review_pack_fields() -> None:
    """Advisory review pack has all required fields populated."""
    from app.domains.advisory.engine import review_pack

    pack = review_pack()
    assert pack.headline != ""
    assert pack.client_name != ""
    assert pack.handoff_owner != ""
    assert len(pack.key_flags) > 0
    assert pack.next_step != ""
    assert pack.primary_action != ""


# ---------------------------------------------------------------------------
# 15. Advisory domain -- advisor handoff structure
# ---------------------------------------------------------------------------


def test_advisory_handoff_structure() -> None:
    """Advisor handoff has meeting prep and open questions."""
    from app.domains.advisory.engine import advisor_handoff

    handoff = advisor_handoff()
    assert handoff.client_id == "han-growth-042"
    assert handoff.owner != ""
    assert len(handoff.meeting_prep) > 0
    assert len(handoff.open_questions) > 0


# ---------------------------------------------------------------------------
# 16. Advisory domain -- portfolio rationale
# ---------------------------------------------------------------------------


def test_advisory_portfolio_rationale() -> None:
    """Portfolio rationale has house view and advisor copy."""
    from app.domains.advisory.engine import portfolio_rationale

    rationale = portfolio_rationale()
    assert rationale.house_view != ""
    assert rationale.advisor_copy != ""
    assert len(rationale.why_recommendation_travels) > 0


# ---------------------------------------------------------------------------
# 17. Pydantic validation -- TickerSignal rejects out-of-range values
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
def test_ticker_signal_rejects_bad_values(field: str, bad_value: float) -> None:
    """TickerSignal rejects factor values outside [0, 1]."""
    from app.domains.quant.schemas import TickerSignal

    data: dict[str, Any] = {"ticker": "BAD", "momentum": 0.5, "quality": 0.5, "value": 0.5, "volatility": 0.5}
    data[field] = bad_value
    with pytest.raises(ValidationError):
        TickerSignal(**data)


# ---------------------------------------------------------------------------
# 18. Pydantic validation -- TickerSignal rejects empty ticker
# ---------------------------------------------------------------------------


def test_ticker_signal_rejects_empty_ticker() -> None:
    """TickerSignal rejects an empty string ticker."""
    from app.domains.quant.schemas import TickerSignal

    with pytest.raises(ValidationError):
        TickerSignal(ticker="", momentum=0.5, quality=0.5, value=0.5, volatility=0.5)


# ---------------------------------------------------------------------------
# 19. Pydantic validation -- ClientReview rejects invalid risk profile
# ---------------------------------------------------------------------------


def test_client_review_rejects_invalid_risk_profile() -> None:
    """ClientReview rejects an invalid risk profile enum value."""
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
# 20. Pydantic validation -- PortfolioMix rejects negative allocation
# ---------------------------------------------------------------------------


def test_portfolio_mix_rejects_negative() -> None:
    """PortfolioMix rejects negative allocation values."""
    from app.domains.advisory.schemas import PortfolioMix

    with pytest.raises(ValidationError):
        PortfolioMix(cash=-0.1, domestic_equity=0.5, global_equity=0.3, bond=0.2, thematic_growth=0.1)


# ---------------------------------------------------------------------------
# 21. Pydantic validation -- FactorWeights rejects out-of-range
# ---------------------------------------------------------------------------


def test_factor_weights_rejects_out_of_range() -> None:
    """FactorWeights rejects values above 1.0."""
    from app.domains.quant.schemas import FactorWeights

    with pytest.raises(ValidationError):
        FactorWeights(momentum=1.5, quality=0.5, value=0.5, volatility_penalty=0.1)


# ---------------------------------------------------------------------------
# 22. Ticker normalizes to uppercase
# ---------------------------------------------------------------------------


def test_ticker_normalizes_uppercase() -> None:
    """TickerSignal normalizes ticker to uppercase."""
    from app.domains.quant.schemas import TickerSignal

    signal = TickerSignal(ticker="abc", momentum=0.5, quality=0.5, value=0.5, volatility=0.5)
    assert signal.ticker == "ABC"


# ---------------------------------------------------------------------------
# 23. Client ID strips whitespace
# ---------------------------------------------------------------------------


def test_client_id_strips_whitespace() -> None:
    """ClientReview strips whitespace from client_id."""
    from app.domains.advisory.schemas import ClientReview

    review = ClientReview(
        client_id="  test-001  ",
        client_name="Test",
        meeting_type="annual",
        risk_profile="balanced",
        liquidity_need="low",
        current_focus=["test"],
    )
    assert review.client_id == "test-001"


# ---------------------------------------------------------------------------
# 24. 404 on unknown routes
# ---------------------------------------------------------------------------


def test_unknown_route_returns_404() -> None:
    """Unknown API routes return 404."""
    resp = client.get("/api/nonexistent")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 25. Health response model structure
# ---------------------------------------------------------------------------


def test_health_response_model() -> None:
    """HealthResponse model creates valid instances."""
    from app.shared.schemas import HealthResponse

    h = HealthResponse(service="test", domains=["a"])
    assert h.status == "ok"
    assert h.service == "test"
