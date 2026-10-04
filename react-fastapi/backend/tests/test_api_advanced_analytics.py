"""
Tests for /api/analytics endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_analytics_overview():
    response = client.get("/api/analytics/overview?year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["destination_hhi"] > 0
    assert data["top_10_destination_share"] > 0
    assert data["active_destinations"] > 50
    assert data["total_insights"] > 0
    assert len(data["top_insights"]) > 0


def test_api_analytics_concentration():
    response = client.get("/api/analytics/concentration?year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert "destination" in data
    assert "origin" in data
    assert data["destination"]["hhi"] > 0
    assert data["origin"]["origin_hhi"] > 0
    assert len(data["destination"]["top_destinations"]) > 0


def test_api_analytics_correlations():
    response = client.get("/api/analytics/correlations?year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert len(data["correlations"]) >= 4
    first_pair = data["correlations"][0]
    assert "pair_name" in first_pair
    assert "spearman_rho" in first_pair
    assert "pearson_r" in first_pair


def test_api_analytics_scatter():
    response = client.get(
        "/api/analytics/scatter?year=2020&x_metric=gdp_per_capita&y_metric=migrant_stock_pct_population&log_x=true&log_y=false"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert len(data["points"]) > 50
    assert "stats" in data
    assert "spearman_rho" in data["stats"]


def test_api_analytics_outliers_iqr():
    response = client.get("/api/analytics/outliers?year=2020&metric=migrant_stock&method=IQR&threshold=1.5")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["method"] == "IQR"
    assert data["outlier_count"] > 0
    assert len(data["outliers"]) == data["outlier_count"]


def test_api_analytics_outliers_zscore():
    response = client.get("/api/analytics/outliers?year=2020&metric=migrant_stock&method=Z-Score&threshold=2.5")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["method"] == "Z-Score"
    assert "mean" in data["summary"]
    assert "std" in data["summary"]


def test_api_analytics_compare():
    response = client.get("/api/analytics/compare?year=2020&countries=USA,IND,DEU")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert len(data["countries"]) == 3
    assert len(data["absolute_comparison"]) == 3
    assert len(data["normalized_comparison"]) == 3
    assert len(data["trajectories"]) == 3


def test_api_analytics_compare_validation_errors():
    # Less than 2 countries
    res_single = client.get("/api/analytics/compare?year=2020&countries=USA")
    assert res_single.status_code == 400

    # More than 5 countries
    res_many = client.get("/api/analytics/compare?year=2020&countries=USA,IND,DEU,FRA,GBR,CAN")
    assert res_many.status_code == 400


def test_api_analytics_insights():
    response = client.get("/api/analytics/insights?year=2020")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2020
    assert data["total_insights"] > 0
    assert len(data["categories"]) > 3
    assert len(data["insights"]) == data["total_insights"]


def test_api_analytics_invalid_year():
    response = client.get("/api/analytics/overview?year=1993")
    assert response.status_code == 400
