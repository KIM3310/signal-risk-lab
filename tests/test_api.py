from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_routes():
    for route in [
        "/api/runtime/brief",
        "/api/factor-board",
        "/api/risk-report",
        "/api/execution-posture",
        "/api/research-pack",
    ]:
        response = client.get(route)
        assert response.status_code == 200
        assert "schema" in response.json()

