"""Advisory domain engine: client suitability, portfolio rationale, and advisor handoff."""

from __future__ import annotations

import logging
from typing import Any

from app.domains.advisory.schemas import (
    AdvisorHandoff,
    AdvisoryReviewPack,
    ClientReview,
    ClientSuitabilityPack,
    LiquidityNeed,
    Portfolio,
    PortfolioMix,
    PortfolioRationale,
    Recommendation,
    RiskProfile,
)

logger = logging.getLogger(__name__)

SEED_CLIENT = ClientReview(
    client_id="han-growth-042",
    client_name="Han Family Growth Account",
    meeting_type="quarterly review",
    risk_profile=RiskProfile.balanced_growth,
    liquidity_need=LiquidityNeed.medium,
    current_focus=[
        "reduce single-theme concentration",
        "preserve long-term growth exposure",
        "keep explanation simple for family decision makers",
    ],
)

SEED_PORTFOLIO = Portfolio(
    current_mix=PortfolioMix(
        cash=0.08,
        domestic_equity=0.36,
        global_equity=0.31,
        bond=0.17,
        thematic_growth=0.08,
    ),
    flags=[
        "thematic allocation is above internal comfort band",
        "client explanation notes are too product-heavy",
        "income cushion remains acceptable",
    ],
)

SEED_RECOMMENDATION = Recommendation(
    primary_action="rebalance a portion of thematic growth into a diversified global quality sleeve",
    suitability_view="suitable with explanation-required handoff",
    why_now=[
        "portfolio remains growth-oriented after rebalance",
        "client risk profile does not support further concentration",
        "house view favors steadier compounding over narrative-heavy positioning",
    ],
    compliance_notes=[
        "confirm family decision maker understands concentration risk",
        "keep recommendation language plain and product-neutral",
        "document long-term objective and risk explanation in call notes",
    ],
)

SEED_HANDOFF: dict[str, Any] = {
    "owner": "relationship manager",
    "next_step": "prepare one-page call brief and reallocation rationale",
    "meeting_prep": [
        "show current concentration in simple chart language",
        "connect recommendation to long-term household objective",
        "avoid jargon when discussing diversification",
    ],
    "open_questions": [
        "does the client expect a near-term education or housing outflow",
        "is the household comfortable with reduced thematic upside in exchange for lower concentration",
    ],
}


def client_suitability() -> ClientSuitabilityPack:
    """Assess client suitability based on profile, portfolio, and recommendation.

    Returns:
        ClientSuitabilityPack containing client review, portfolio state, and recommendation.
    """
    logger.info("Generating client suitability pack for %s", SEED_CLIENT.client_id)
    return ClientSuitabilityPack(
        schema_="client-suitability-pack-v1",
        client=SEED_CLIENT,
        portfolio=SEED_PORTFOLIO,
        recommendation=SEED_RECOMMENDATION,
    )


def portfolio_rationale() -> PortfolioRationale:
    """Build the portfolio rationale linking house view to recommendation.

    Returns:
        PortfolioRationale with current mix, house view, and advisor copy.
    """
    return PortfolioRationale(
        schema_="portfolio-rationale-v1",
        house_view="keep growth exposure but reduce concentration and explanation risk",
        current_mix=SEED_PORTFOLIO.current_mix,
        why_recommendation_travels=[
            "aligned with balanced-growth profile",
            "easy to explain in client language",
            "lower concentration without flipping overall posture",
        ],
        advisor_copy=(
            "Move from concentrated narrative exposure toward steadier diversified growth"
            " while keeping the long-term plan intact."
        ),
    )


def advisor_handoff() -> AdvisorHandoff:
    """Prepare advisor handoff pack with meeting prep and open questions.

    Returns:
        AdvisorHandoff with owner, next steps, and preparation details.
    """
    return AdvisorHandoff(
        schema_="advisor-handoff-pack-v1",
        client_id=SEED_CLIENT.client_id,
        owner=SEED_HANDOFF["owner"],
        next_step=SEED_HANDOFF["next_step"],
        meeting_prep=SEED_HANDOFF["meeting_prep"],
        open_questions=SEED_HANDOFF["open_questions"],
    )


def review_pack() -> AdvisoryReviewPack:
    """Compile the advisory review pack for the review desk.

    Returns:
        AdvisoryReviewPack summary with suitability, actions, and handoff info.
    """
    return AdvisoryReviewPack(
        schema_="advisor-review-pack-v1",
        headline=(
            "Suitability stays positive if the recommendation is delivered"
            " as a diversification conversation, not a product pitch."
        ),
        client_name=SEED_CLIENT.client_name,
        suitability_view=SEED_RECOMMENDATION.suitability_view,
        primary_action=SEED_RECOMMENDATION.primary_action,
        key_flags=SEED_PORTFOLIO.flags,
        handoff_owner=SEED_HANDOFF["owner"],
        next_step=SEED_HANDOFF["next_step"],
    )


def runtime_brief() -> dict[str, Any]:
    """Return advisory domain runtime brief for the unified platform view.

    Returns:
        Dictionary describing deployment mode, desk, client, routes, and focus areas.
    """
    return {
        "schema": "advisory-runtime-brief-v1",
        "deploymentMode": "review-only",
        "desk": "brokerage-client-review",
        "client": SEED_CLIENT.client_name,
        "routes": [
            "/api/advisory/client-suitability",
            "/api/advisory/portfolio-rationale",
            "/api/advisory/advisor-handoff",
            "/api/advisory/review-pack",
        ],
        "focus": [
            "client suitability",
            "portfolio rationale",
            "advisor handoff",
        ],
    }
