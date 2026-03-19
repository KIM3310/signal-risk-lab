"""Finance Review Platform -- unified FastAPI application.

Combines two bounded contexts under one roof:
  * Quant domain  -- factor signals, risk posture, execution readiness
  * Advisory domain -- client suitability, portfolio rationale, advisor handoff
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.domains.advisory.router import router as advisory_router
from app.domains.quant.router import router as quant_router
from app.shared.health import health_check
from app.shared.schemas import HealthResponse

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app = FastAPI(
    title="Finance Review Platform",
    version="1.0.0",
    description="Domain-driven finance review surface spanning quant research and brokerage advisory.",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(quant_router)
app.include_router(advisory_router)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions with a structured JSON response."""
    logger.warning("ValueError on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, Any]:
    """Return platform health status including active domains."""
    return health_check().model_dump()


@app.get("/")
def root() -> FileResponse:
    """Serve the static landing page."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/runtime/brief")
def runtime_brief() -> dict[str, Any]:
    """Unified runtime brief covering both domains."""
    from app.domains.advisory.engine import runtime_brief as adv_brief
    from app.domains.quant.engine import runtime_brief as quant_brief

    logger.info("Generating unified runtime brief")
    return {
        "schema": "platform-runtime-brief-v1",
        "platform": "finance-review-platform",
        "domains": {
            "quant": quant_brief(),
            "advisory": adv_brief(),
        },
    }
