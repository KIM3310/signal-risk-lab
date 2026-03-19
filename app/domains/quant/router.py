"""FastAPI router for the quant signal/risk domain."""

from __future__ import annotations

from fastapi import APIRouter

from app.domains.quant.engine import (
    execution_posture,
    factor_board,
    research_pack,
    risk_report,
    runtime_brief,
)

router = APIRouter(prefix="/api/quant", tags=["quant"])


@router.get("/brief")
def quant_brief() -> dict:
    return runtime_brief()


@router.get("/factor-board")
def factor_board_route() -> dict:
    return factor_board().model_dump(by_alias=True)


@router.get("/risk-report")
def risk_report_route() -> dict:
    return risk_report().model_dump(by_alias=True)


@router.get("/execution-posture")
def execution_posture_route() -> dict:
    return execution_posture().model_dump(by_alias=True)


@router.get("/research-pack")
def research_pack_route() -> dict:
    return research_pack().model_dump(by_alias=True)
