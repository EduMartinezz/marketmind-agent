from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_briefing_empty_query():
    response = client.post("/briefing", json={"query": "   "})
    assert response.status_code == 400