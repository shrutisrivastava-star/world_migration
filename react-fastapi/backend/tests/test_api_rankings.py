"""
Tests for /api/rankings endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_rankings_default():
    response = client.get("/api/rankings?year=2020&metric=Migrant+Stock&top_n=10")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["metric_name"] == "Migrant Stock"
    assert data["top_n"] == 10
    assert len(data["rankings"]) == 10
    assert data["rankings"][0]["rank"] == 1
    # Top destination by stock in 2020 is USA
    assert data["rankings"][0]["country_code"] == "USA"


def test_api_rankings_pct_pop():
    response = client.get("/api/rankings?year=2020&metric=Migrant+Stock+%25+of+Population&top_n=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["rankings"]) == 5
    assert data["rankings"][0]["metric_value"] > 50  # Top share countries have > 50%


def test_api_rankings_invalid_year():
    response = client.get("/api/rankings?year=1991")
    assert response.status_code == 400
