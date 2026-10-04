"""
Tests for /api/communities endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_communities_overview():
    response = client.get("/api/communities?year=2020&top_n_edges=100")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["num_communities"] >= 2
    assert data["modularity"] > 0.0
    assert len(data["communities"]) == data["num_communities"]
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

    first_comm = data["communities"][0]
    assert "community_id" in first_comm
    assert "community_name" in first_comm
    assert first_comm["size"] > 0
    assert len(first_comm["member_codes"]) == first_comm["size"]


def test_api_community_detail():
    response = client.get("/api/communities/1?year=2020&top_n_edges=100")
    assert response.status_code == 200
    data = response.json()
    assert data["community_id"] == 1
    assert data["size"] > 0
    assert len(data["member_countries"]) == data["size"]


def test_api_communities_invalid_year():
    response = client.get("/api/communities?year=1992")
    assert response.status_code == 400
