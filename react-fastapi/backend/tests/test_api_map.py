"""
Tests for /api/map endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_map_default():
    response = client.get("/api/map?year=2020&metric=Migrant+Stock")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["metric_name"] == "Migrant Stock"
    assert data["total_countries"] > 150
    assert len(data["data"]) > 0

    first = data["data"][0]
    assert "country_code" in first
    assert "display_name" in first
    assert "metric_value" in first
    assert "migrant_stock" in first


def test_api_map_other_metrics():
    for metric in ["Migrant Stock % of Population", "GDP per Capita", "Population"]:
        response = client.get(f"/api/map?year=2020&metric={metric}")
        assert response.status_code == 200
        data = response.json()
        assert data["metric_name"] == metric


def test_api_map_invalid_year():
    response = client.get("/api/map?year=1999")
    assert response.status_code == 400
