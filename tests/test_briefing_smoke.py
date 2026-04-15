from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "MarketMind Agent is running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_empty_query():
    response = client.post("/briefing", json={"query": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty."