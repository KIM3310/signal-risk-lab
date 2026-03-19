"""FastAPI router for the advisory/brokerage client review domain."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from app.domains.advisory.engine import (
    advisor_handoff,
    client_suitability,
    portfolio_rationale,
    review_pack,
    runtime_brief,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advisory", tags=["advisory"])


@router.get("/brief")
def advisory_brief() -> dict[str, Any]:
    """Return advisory domain runtime brief."""
    logger.info("Advisory brief requested")
    return runtime_brief()


@router.get("/client-suitability")
def client_suitability_route() -> dict[str, Any]:
    """Return client suitability assessment."""
    logger.info("Client suitability requested")
    return client_suitability().model_dump(by_alias=True)


@router.get("/portfolio-rationale")
def portfolio_rationale_route() -> dict[str, Any]:
    """Return portfolio rationale with house view."""
    logger.info("Portfolio rationale requested")
    return portfolio_rationale().model_dump(by_alias=True)


@router.get("/advisor-handoff")
def advisor_handoff_route() -> dict[str, Any]:
    """Return advisor handoff package."""
    logger.info("Advisor handoff requested")
    return advisor_handoff().model_dump(by_alias=True)


@router.get("/review-pack")
def review_pack_route() -> dict[str, Any]:
    """Return the complete advisory review pack."""
    logger.info("Advisory review pack requested")
    return review_pack().model_dump(by_alias=True)
