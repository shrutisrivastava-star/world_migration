"""
Tests for /api/country/{country_code} endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_country_profile_usa():
    response = client.get("/api/country/USA?year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == "USA"
    assert "United States" in data["country_name"]
    assert data["immigrant_stock"] > 40000000
    assert len(data["history"]) == 7
    assert len(data["top_inbound_origins"]) > 0
    assert len(data["top_outbound_destinations"]) > 0


def test_api_country_profile_india():
    response = client.get("/api/country/IND?year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == "IND"
    assert data["emigrant_stock"] > 15000000  # India is top diaspora origin
    assert data["net_migrant_stock"] < 0      # Net origin nation


def test_api_country_invalid_year():
    response = client.get("/api/country/USA?year=1800")
    assert response.status_code == 400
