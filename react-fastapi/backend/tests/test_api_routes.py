"""
Tests for /api/routes endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_routes_top_global():
    response = client.get("/api/routes?year=2020&top_n=10")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert len(data["top_corridors"]) == 10
    first = data["top_corridors"][0]
    assert "origin_code" in first
    assert "destination_code" in first
    assert first["migrant_stock"] > 0


def test_api_routes_specific_pair():
    response = client.get("/api/routes?year=2020&origin=MEX&destination=USA")
    assert response.status_code == 200
    data = response.json()
    assert data["origin_code"] == "MEX"
    assert data["destination_code"] == "USA"
    assert data["current_stock"] is not None
    assert data["current_stock"] > 10000000  # Mexico -> USA is > 10M in 2020
    assert len(data["history"]) == 7  # 1990 to 2020


def test_api_routes_invalid_year():
    response = client.get("/api/routes?year=1993")
    assert response.status_code == 400
