"""
Tests for GET /api/health endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health():
    """Verify health check endpoint returns 200 OK and expected metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "Global Migration Observatory"
    assert data["version"] == "react-vite"


def test_root_metadata():
    """Verify root endpoint returns project info and link to docs."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "docs" in data
    assert "/api/health" in data["api_endpoints"]
