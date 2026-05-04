from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "MarketMind Agent is running"


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "MarketMind Agent"


def test_empty_query() -> None:
    response = client.post("/briefing", json={"query": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty."


def test_briefing_accepts_query_only() -> None:
    response = client.post("/briefing", json={"query": "Tesla"})
    # This may be 200 or 404 depending on live/fallback data, but should not be 422
    assert response.status_code in [200, 404]


def test_briefing_accepts_query_and_ticker() -> None:
    response = client.post("/briefing", json={"query": "Tesla", "ticker": "TSLA"})
    # This may be 200 or 404 depending on live/fallback data, but should not be 422
    assert response.status_code in [200, 404]