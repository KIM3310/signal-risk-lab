"""Pydantic models for the quant signal/risk domain."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.shared.schemas import ReviewPackBase


class ConcentrationFlag(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class DrawdownGuard(str, Enum):
    active = "active"
    inactive = "inactive"
    triggered = "triggered"


class CapacityBucket(str, Enum):
    micro = "micro"
    small_mid = "small-mid"
    mid = "mid"
    large = "large"


class TickerSignal(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Equity ticker symbol")
    momentum: float = Field(..., ge=0.0, le=1.0)
    quality: float = Field(..., ge=0.0, le=1.0)
    value: float = Field(..., ge=0.0, le=1.0)
    volatility: float = Field(..., ge=0.0, le=1.0)
    score: Optional[float] = None

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper().strip()


class FactorWeights(BaseModel):
    momentum: float = Field(0.45, ge=0.0, le=1.0)
    quality: float = Field(0.35, ge=0.0, le=1.0)
    value: float = Field(0.20, ge=0.0, le=1.0)
    volatility_penalty: float = Field(0.10, ge=0.0, le=1.0)


class FactorBoard(BaseModel):
    schema_: str = Field("factor-board-v1", alias="schema")
    signal_family: str
    top_longs: list[str]
    bottom_watchlist: list[str]
    rows: list[TickerSignal]

    model_config = {"populate_by_name": True}


class RiskReport(BaseModel):
    schema_: str = Field("risk-report-v1", alias="schema")
    predicted_turnover: float = Field(..., ge=0.0, le=1.0)
    gross_exposure: float = Field(..., ge=0.0)
    sector_concentration_flag: ConcentrationFlag
    drawdown_guard: DrawdownGuard
    notes: list[str]

    model_config = {"populate_by_name": True}


class ExecutionPosture(BaseModel):
    schema_: str = Field("execution-posture-v1", alias="schema")
    slippage_assumption_bps: int = Field(..., ge=0)
    capacity_bucket: CapacityBucket
    go_live_view: str
    why: list[str]

    model_config = {"populate_by_name": True}


class QuantResearchPack(ReviewPackBase):
    top_longs: list[str]
    predicted_turnover: float = Field(..., ge=0.0, le=1.0)
    capacity_bucket: CapacityBucket
    go_live_view: str
