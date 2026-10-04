"""
Tests for GET /api/countries endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_countries():
    """Verify countries endpoint returns non-empty list of valid entities."""
    response = client.get("/api/countries")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "countries" in data
    assert data["total"] > 150
    assert len(data["countries"]) == data["total"]

    # Verify item structure
    first = data["countries"][0]
    assert "display_name" in first
    assert "country_name" in first
    assert "is_aggregate" in first


def test_api_countries_sovereign_only():
    """Verify sovereign_only filter excludes regional aggregates."""
    response = client.get("/api/countries?sovereign_only=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 150
    # Every item must have is_aggregate = False and valid country_code
    for item in data["countries"]:
        assert item["is_aggregate"] is False
        assert item["country_code"] is not None
        assert len(item["country_code"]) == 3
