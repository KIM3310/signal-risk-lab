"""Smoke-test every route in the unified platform."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    """Run a quick smoke test against all platform routes."""
    test_client = TestClient(app)
    routes: list[str] = [
        "/health",
        "/api/runtime/brief",
        "/api/quant/brief",
        "/api/quant/factor-board",
        "/api/quant/risk-report",
        "/api/quant/execution-posture",
        "/api/quant/research-pack",
        "/api/advisory/brief",
        "/api/advisory/client-suitability",
        "/api/advisory/portfolio-rationale",
        "/api/advisory/advisor-handoff",
        "/api/advisory/review-pack",
    ]
    for route in routes:
        response = test_client.get(route)
        response.raise_for_status()
    print(f"finance-review-platform smoke ok ({len(routes)} routes)")


if __name__ == "__main__":
    main()
