"""
Tests for /api/trends endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_global_trends():
    response = client.get("/api/trends/global")
    assert response.status_code == 200
    data = response.json()
    assert "points" in data
    points = data["points"]
    assert len(points) == 7  # 1990, 1995, 2000, 2005, 2010, 2015, 2020
    years = [p["year"] for p in points]
    assert years == [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    # Check 2020 total stock is strictly ~279M
    assert points[-1]["total_migrant_stock"] > 250000000


def test_api_country_trends():
    response = client.get("/api/trends/countries?countries=USA,IND,DEU&metric=Migrant+Stock")
    assert response.status_code == 200
    data = response.json()
    assert data["metric_name"] == "Migrant Stock"
    assert len(data["points"]) > 0
    codes = {p["country_code"] for p in data["points"]}
    assert "USA" in codes or "IND" in codes


def test_api_country_trends_empty():
    response = client.get("/api/trends/countries?countries=")
    assert response.status_code == 400
