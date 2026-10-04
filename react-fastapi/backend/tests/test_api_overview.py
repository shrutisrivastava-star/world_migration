"""
Tests for GET /api/overview endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_overview_default_year():
    """Verify overview default query returns 2020 calculated KPIs."""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["total_migrant_stock"] > 200_000_000.0
    assert data["total_population"] > 5_000_000_000.0
    assert 2.0 < data["global_migrant_pct"] < 5.0
    assert data["num_countries"] > 150
    assert "United States" in data["top_destination_name"]
    assert data["top_destination_stock"] > 40_000_000.0
    assert data["top_share_pct"] > 50.0  # UAE / Qatar / etc.
    assert data["num_corridors"] > 1000


@pytest.mark.parametrize("census_year", [1990, 1995, 2000, 2005, 2010, 2015, 2020])
def test_api_overview_all_census_years(census_year):
    """Verify overview endpoint returns valid calculations for all UN DESA census rounds."""
    response = client.get(f"/api/overview?year={census_year}")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == census_year
    assert data["total_migrant_stock"] > 0
    assert data["total_population"] > 0
    assert 1.0 < data["global_migrant_pct"] < 10.0
    assert data["num_countries"] > 150
    assert data["num_corridors"] > 1000


def test_api_overview_invalid_year():
    """Verify invalid year returns 400 Bad Request."""
    response = client.get("/api/overview?year=1999")
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "Invalid census observation year" in detail


def test_api_overview_malformed_year():
    """Verify non-integer year returns 422 Unprocessable Entity."""
    response = client.get("/api/overview?year=invalid_year")
    assert response.status_code == 422
