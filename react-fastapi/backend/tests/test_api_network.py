"""
Tests for /api/network endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_network_default():
    response = client.get("/api/network?year=2020&top_n_edges=100")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["top_n_edges"] == 100
    assert data["node_count"] > 20
    assert data["edge_count"] <= 100
    assert data["total_observed_stock"] > 50000000
    assert len(data["nodes"]) == data["node_count"]
    assert len(data["edges"]) == data["edge_count"]
    assert len(data["top_hubs"]) > 0

    first_node = data["nodes"][0]
    assert "country_code" in first_node
    assert "country_name" in first_node
    assert "x" in first_node
    assert "y" in first_node
    assert "circ_x" in first_node
    assert "circ_y" in first_node
    assert "total_strength" in first_node
    assert "betweenness_centrality" in first_node
    assert "pagerank" in first_node


def test_api_network_invalid_year():
    response = client.get("/api/network?year=1991")
    assert response.status_code == 400


def test_api_network_min_stock():
    response = client.get("/api/network?year=2020&min_stock=500000&top_n_edges=50")
    assert response.status_code == 200
    data = response.json()
    assert data["edge_count"] <= 50
