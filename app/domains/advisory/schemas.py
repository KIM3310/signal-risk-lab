"""Pydantic models for the advisory/brokerage client review domain."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.shared.schemas import ReviewPackBase


class RiskProfile(str, Enum):
    conservative = "conservative"
    balanced = "balanced"
    balanced_growth = "balanced-growth"
    growth = "growth"
    aggressive = "aggressive"


class LiquidityNeed(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ClientReview(BaseModel):
    client_id: str = Field(..., min_length=1, max_length=64)
    client_name: str = Field(..., min_length=1, max_length=128)
    meeting_type: str = Field(..., min_length=1)
    risk_profile: RiskProfile
    liquidity_need: LiquidityNeed
    current_focus: list[str] = Field(..., min_length=1)

    @field_validator("client_id")
    @classmethod
    def client_id_stripped(cls, v: str) -> str:
        return v.strip()


class PortfolioMix(BaseModel):
    cash: float = Field(..., ge=0.0, le=1.0)
    domestic_equity: float = Field(..., ge=0.0, le=1.0)
    global_equity: float = Field(..., ge=0.0, le=1.0)
    bond: float = Field(..., ge=0.0, le=1.0)
    thematic_growth: float = Field(..., ge=0.0, le=1.0)


class Portfolio(BaseModel):
    current_mix: PortfolioMix
    flags: list[str]


class Recommendation(BaseModel):
    primary_action: str
    suitability_view: str
    why_now: list[str] = Field(..., min_length=1)
    compliance_notes: list[str]


class ClientSuitabilityPack(BaseModel):
    schema_: str = Field("client-suitability-pack-v1", alias="schema")
    client: ClientReview
    portfolio: Portfolio
    recommendation: Recommendation

    model_config = {"populate_by_name": True}


class PortfolioRationale(BaseModel):
    schema_: str = Field("portfolio-rationale-v1", alias="schema")
    house_view: str
    current_mix: PortfolioMix
    why_recommendation_travels: list[str]
    advisor_copy: str

    model_config = {"populate_by_name": True}


class AdvisorHandoff(BaseModel):
    schema_: str = Field("advisor-handoff-pack-v1", alias="schema")
    client_id: str
    owner: str
    next_step: str
    meeting_prep: list[str]
    open_questions: list[str]

    model_config = {"populate_by_name": True}


class AdvisoryReviewPack(ReviewPackBase):
    client_name: str
    suitability_view: str
    primary_action: str
    key_flags: list[str]
    handoff_owner: str
    next_step: str
