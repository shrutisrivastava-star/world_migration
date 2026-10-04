"""
Tests for GET /api/years endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_years():
    """Verify years endpoint returns all 7 official UN DESA observation years."""
    response = client.get("/api/years")
    assert response.status_code == 200
    data = response.json()
    assert "years" in data
    expected_years = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    assert data["years"] == expected_years
    assert len(data["years"]) == 7
