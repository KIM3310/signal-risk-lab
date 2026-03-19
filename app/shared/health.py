"""Unified health check for the finance review platform."""

from __future__ import annotations

from app.shared.schemas import HealthResponse


def health_check() -> HealthResponse:
    return HealthResponse(
        service="finance-review-platform",
        domains=["quant", "advisory"],
    )
