"""Unified health check for the finance review platform."""

from __future__ import annotations

import logging

from app.shared.schemas import HealthResponse

logger = logging.getLogger(__name__)


def health_check() -> HealthResponse:
    """Return current health status of the platform.

    Returns:
        HealthResponse with service name and active domain list.
    """
    logger.debug("Health check requested")
    return HealthResponse(
        service="finance-review-platform",
        domains=["quant", "advisory"],
    )
