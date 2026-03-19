"""Shared Pydantic models used across both quant and advisory domains."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Platform health check response."""

    status: str = "ok"
    service: str
    domains: list[str]


class RuntimeBrief(BaseModel):
    """Base model for domain runtime briefs."""

    schema_: str = Field(..., alias="schema")
    deployment_mode: str = Field(..., alias="deploymentMode")
    routes: list[str]
    focus: list[str]

    model_config = {"populate_by_name": True}


class ReviewPackBase(BaseModel):
    """Base class for domain-specific review packs."""

    schema_: str = Field(..., alias="schema")
    headline: str

    model_config = {"populate_by_name": True}
