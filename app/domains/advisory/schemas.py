"""Pydantic models for the advisory/brokerage client review domain."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.shared.schemas import ReviewPackBase


class RiskProfile(str, Enum):
    """Client investment risk profile classification."""

    conservative = "conservative"
    balanced = "balanced"
    balanced_growth = "balanced-growth"
    growth = "growth"
    aggressive = "aggressive"


class LiquidityNeed(str, Enum):
    """Client liquidity requirement level."""

    low = "low"
    medium = "medium"
    high = "high"


class ClientReview(BaseModel):
    """Client review record for advisory suitability assessment."""

    client_id: str = Field(..., min_length=1, max_length=64)
    client_name: str = Field(..., min_length=1, max_length=128)
    meeting_type: str = Field(..., min_length=1)
    risk_profile: RiskProfile
    liquidity_need: LiquidityNeed
    current_focus: list[str] = Field(..., min_length=1)

    @field_validator("client_id")
    @classmethod
    def client_id_stripped(cls, v: str) -> str:
        """Strip whitespace from client ID."""
        return v.strip()


class PortfolioMix(BaseModel):
    """Portfolio allocation percentages across asset classes."""

    cash: float = Field(..., ge=0.0, le=1.0)
    domestic_equity: float = Field(..., ge=0.0, le=1.0)
    global_equity: float = Field(..., ge=0.0, le=1.0)
    bond: float = Field(..., ge=0.0, le=1.0)
    thematic_growth: float = Field(..., ge=0.0, le=1.0)


class Portfolio(BaseModel):
    """Client portfolio state including mix and flags."""

    current_mix: PortfolioMix
    flags: list[str]


class Recommendation(BaseModel):
    """Advisory recommendation with suitability view and compliance notes."""

    primary_action: str
    suitability_view: str
    why_now: list[str] = Field(..., min_length=1)
    compliance_notes: list[str]


class ClientSuitabilityPack(BaseModel):
    """Complete client suitability assessment package."""

    schema_: str = Field("client-suitability-pack-v1", alias="schema")
    client: ClientReview
    portfolio: Portfolio
    recommendation: Recommendation

    model_config = {"populate_by_name": True}


class PortfolioRationale(BaseModel):
    """Portfolio rationale connecting house view to client recommendation."""

    schema_: str = Field("portfolio-rationale-v1", alias="schema")
    house_view: str
    current_mix: PortfolioMix
    why_recommendation_travels: list[str]
    advisor_copy: str

    model_config = {"populate_by_name": True}


class AdvisorHandoff(BaseModel):
    """Advisor handoff package with meeting prep and open questions."""

    schema_: str = Field("advisor-handoff-pack-v1", alias="schema")
    client_id: str
    owner: str
    next_step: str
    meeting_prep: list[str]
    open_questions: list[str]

    model_config = {"populate_by_name": True}


class AdvisoryReviewPack(ReviewPackBase):
    """Complete advisory review pack for the review desk."""

    client_name: str
    suitability_view: str
    primary_action: str
    key_flags: list[str]
    handoff_owner: str
    next_step: str
