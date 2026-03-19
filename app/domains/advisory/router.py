"""FastAPI router for the advisory/brokerage client review domain."""

from __future__ import annotations

from fastapi import APIRouter

from app.domains.advisory.engine import (
    advisor_handoff,
    client_suitability,
    portfolio_rationale,
    review_pack,
    runtime_brief,
)

router = APIRouter(prefix="/api/advisory", tags=["advisory"])


@router.get("/brief")
def advisory_brief() -> dict:
    return runtime_brief()


@router.get("/client-suitability")
def client_suitability_route() -> dict:
    return client_suitability().model_dump(by_alias=True)


@router.get("/portfolio-rationale")
def portfolio_rationale_route() -> dict:
    return portfolio_rationale().model_dump(by_alias=True)


@router.get("/advisor-handoff")
def advisor_handoff_route() -> dict:
    return advisor_handoff().model_dump(by_alias=True)


@router.get("/review-pack")
def review_pack_route() -> dict:
    return review_pack().model_dump(by_alias=True)
