"""
Tests for /api/corridors endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_corridors_overview():
    response = client.get("/api/corridors/overview?year=2020&top_n=10")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["total_corridors"] > 10000
    assert "Mexico" in data["top_corridor"] or "United States" in data["top_corridor"]
    assert data["top_corridor_stock"] > 10000000
    assert len(data["top_corridors"]) == 10
    assert len(data["concentration_trend"]) == 7  # 1990 to 2020


def test_api_corridors_concentration():
    response = client.get("/api/corridors/concentration")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    years = [d["year"] for d in data]
    assert years == [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    assert data[-1]["top_10_corridor_share"] > 0


def test_api_corridors_detail_mex_usa():
    response = client.get("/api/corridors/detail?origin=MEX&destination=USA&year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["origin_code"] == "MEX"
    assert data["destination_code"] == "USA"
    assert data["current_stock"] > 10000000
    assert data["global_rank"] == 1
    assert "Persistent" in data["classification"] or "Emerging" in data["classification"]
    assert len(data["history"]) == 7


def test_api_corridors_invalid_year():
    response = client.get("/api/corridors/overview?year=1999")
    assert response.status_code == 400
