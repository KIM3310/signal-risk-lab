"""FastAPI router for the quant signal/risk domain."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from app.domains.quant.engine import (
    execution_posture,
    factor_board,
    research_pack,
    risk_report,
    runtime_brief,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quant", tags=["quant"])


@router.get("/brief")
def quant_brief() -> dict[str, Any]:
    """Return quant domain runtime brief."""
    logger.info("Quant brief requested")
    return runtime_brief()


@router.get("/factor-board")
def factor_board_route() -> dict[str, Any]:
    """Return the current factor signal board with ranked tickers."""
    logger.info("Factor board requested")
    return factor_board().model_dump(by_alias=True)


@router.get("/risk-report")
def risk_report_route() -> dict[str, Any]:
    """Return the current risk report."""
    logger.info("Risk report requested")
    return risk_report().model_dump(by_alias=True)


@router.get("/execution-posture")
def execution_posture_route() -> dict[str, Any]:
    """Return execution viability assessment."""
    logger.info("Execution posture requested")
    return execution_posture().model_dump(by_alias=True)


@router.get("/research-pack")
def research_pack_route() -> dict[str, Any]:
    """Return the complete quant research pack."""
    logger.info("Quant research pack requested")
    return research_pack().model_dump(by_alias=True)
