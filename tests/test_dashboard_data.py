"""
Unit tests for dashboard_data module.
Validates overview KPIs, map data formatting, country profiles, trends, rankings, and corridor filters.
"""

import pandas as pd
import numpy as np
import pytest

from src.dashboard_data import (
    get_overview_kpis,
    get_map_data,
    get_global_trend_data,
    get_country_trend_data,
    get_rankings_data,
    get_top_global_corridors,
    get_filtered_corridors,
    get_country_profile_data,
    prepare_country_socioeconomic_data,
    prepare_bilateral_corridor_data,
)


@pytest.fixture
def sample_merged_df():
    return pd.DataFrame([
        {"country": "United States", "country_code": "USA", "display_name": "United States", "year": 2015, "migrant_stock": 45000000.0, "is_aggregate": False, "population": 320000000.0, "migrant_stock_pct_population": 14.06, "stock_change_5yr": 5000000.0, "stock_growth_pct_5yr": 12.5, "gdp_per_capita": 56000.0, "unemployment": 5.28},
        {"country": "United States", "country_code": "USA", "display_name": "United States", "year": 2020, "migrant_stock": 50000000.0, "is_aggregate": False, "population": 330000000.0, "migrant_stock_pct_population": 15.15, "stock_change_5yr": 5000000.0, "stock_growth_pct_5yr": 11.11, "gdp_per_capita": 63000.0, "unemployment": 8.05},
        {"country": "Germany", "country_code": "DEU", "display_name": "Germany", "year": 2015, "migrant_stock": 12000000.0, "is_aggregate": False, "population": 82000000.0, "migrant_stock_pct_population": 14.63, "stock_change_5yr": 2000000.0, "stock_growth_pct_5yr": 20.0, "gdp_per_capita": 41000.0, "unemployment": 4.62},
        {"country": "Germany", "country_code": "DEU", "display_name": "Germany", "year": 2020, "migrant_stock": 15000000.0, "is_aggregate": False, "population": 83000000.0, "migrant_stock_pct_population": 18.07, "stock_change_5yr": 3000000.0, "stock_growth_pct_5yr": 25.0, "gdp_per_capita": 46000.0, "unemployment": 3.81},
        {"country": "World", "country_code": "WLD", "display_name": "World", "year": 2020, "migrant_stock": 280000000.0, "is_aggregate": True, "population": 7800000000.0, "migrant_stock_pct_population": 3.58, "stock_change_5yr": 30000000.0, "stock_growth_pct_5yr": 12.0, "gdp_per_capita": 11000.0, "unemployment": 6.5},
    ])


@pytest.fixture
def sample_bilateral_df():
    return pd.DataFrame([
        {"origin_country": "Mexico", "origin_code": "MEX", "origin_display_name": "Mexico", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "Mexico → United States", "year": 2020, "migrant_stock": 10000000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 90.0, "dest_corridor_share_pct": 20.0},
        {"origin_country": "India", "origin_code": "IND", "origin_display_name": "India", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "India → United States", "year": 2020, "migrant_stock": 2500000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 15.0, "dest_corridor_share_pct": 5.0},
        {"origin_country": "India", "origin_code": "IND", "origin_display_name": "India", "destination_country": "UAE", "destination_code": "ARE", "dest_display_name": "United Arab Emirates", "corridor_label": "India → United Arab Emirates", "year": 2020, "migrant_stock": 3500000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 21.0, "dest_corridor_share_pct": 40.0},
        {"origin_country": "World", "origin_code": None, "origin_display_name": "World", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "World → United States", "year": 2020, "migrant_stock": 50000000.0, "is_aggregate_route": True, "origin_corridor_share_pct": None, "dest_corridor_share_pct": None},
    ])


def test_overview_kpis(sample_merged_df, sample_bilateral_df):
    """Test dynamic overview KPI computation including global_migrant_pct."""
    kpis = get_overview_kpis(sample_merged_df, sample_bilateral_df, year=2020)
    assert kpis["year"] == 2020
    # Sovereign sum: 50M (USA) + 15M (DEU) = 65M (excluding World)
    assert kpis["total_migrant_stock"] == 65000000.0
    assert kpis["total_population"] == 413000000.0  # 330M + 83M
    assert "global_migrant_pct" in kpis
    expected_pct = (65000000.0 / 413000000.0) * 100.0
    assert np.isclose(kpis["global_migrant_pct"], expected_pct, atol=0.01)
    assert kpis["num_countries"] == 2
    assert kpis["top_destination_name"] == "United States"
    assert kpis["top_destination_stock"] == 50000000.0
    assert kpis["top_share_name"] == "Germany"  # 18.07% > 15.15%
    assert np.isclose(kpis["top_share_pct"], 18.07, atol=0.01)
    assert kpis["num_corridors"] == 3  # 3 sovereign non-aggregate corridors


def test_get_map_data(sample_merged_df):
    """Test map data formatting, metric resolution, and hover columns including gdp_per_capita."""
    map_df = get_map_data(sample_merged_df, year=2020, metric_name="Migrant Stock")
    assert len(map_df) == 2  # Sovereign only
    assert "USA" in map_df["country_code"].values
    assert "DEU" in map_df["country_code"].values
    assert "WLD" not in map_df["country_code"].values
    assert map_df.loc[map_df["country_code"] == "USA", "metric_value"].values[0] == 50000000.0
    # Verify all expected hover columns exist
    for col in ["country_code", "metric_value", "population", "gdp_per_capita", "migrant_stock_pct_population"]:
        assert col in map_df.columns
    assert map_df.loc[map_df["country_code"] == "USA", "gdp_per_capita"].values[0] == 63000.0


def test_get_global_trend_data(sample_merged_df):
    """Test global trend aggregation."""
    trend = get_global_trend_data(sample_merged_df)
    assert len(trend) == 2  # 2015, 2020
    stock_2015 = trend[trend["year"] == 2015]["total_migrant_stock"].values[0]
    assert stock_2015 == 57000000.0  # 45M + 12M


def test_get_country_trend_data(sample_merged_df):
    """Test multi-country trend extraction."""
    trends = get_country_trend_data(sample_merged_df, country_codes=["USA", "DEU"], metric_name="Migrant Stock % of Population")
    assert len(trends) == 4
    assert set(trends["country_code"]) == {"USA", "DEU"}


def test_get_rankings_data(sample_merged_df):
    """Test ranking data generation."""
    ranks = get_rankings_data(sample_merged_df, year=2020, metric_name="Migrant Stock", top_n=10)
    assert len(ranks) == 2
    assert ranks.iloc[0]["country_code"] == "USA"
    assert ranks.iloc[0]["rank"] == 1
    assert ranks.iloc[1]["country_code"] == "DEU"
    assert ranks.iloc[1]["rank"] == 2


def test_get_top_global_corridors(sample_bilateral_df):
    """Test top bilateral corridors ranking."""
    top_c = get_top_global_corridors(sample_bilateral_df, year=2020, top_n=2)
    assert len(top_c) == 2
    assert top_c.iloc[0]["origin_code"] == "MEX"
    assert top_c.iloc[0]["destination_code"] == "USA"
    assert top_c.iloc[0]["migrant_stock"] == 10000000.0


def test_get_filtered_corridors_by_origin(sample_bilateral_df):
    """Test corridor filtering by origin."""
    filtered = get_filtered_corridors(sample_bilateral_df, year=2020, origin_code="IND")
    assert len(filtered) == 2
    assert all(filtered["origin_code"] == "IND")


def test_get_filtered_corridors_by_destination_and_pair(sample_bilateral_df):
    """Test corridor filtering by destination_code, dest_code, and combined pair."""
    # Test destination_code keyword parameter
    filtered_dest = get_filtered_corridors(sample_bilateral_df, year=2020, destination_code="USA")
    assert len(filtered_dest) == 2
    assert all(filtered_dest["destination_code"] == "USA")

    # Test dest_code legacy keyword parameter
    filtered_dest_legacy = get_filtered_corridors(sample_bilateral_df, year=2020, dest_code="ARE")
    assert len(filtered_dest_legacy) == 1
    assert filtered_dest_legacy.iloc[0]["destination_code"] == "ARE"

    # Test pair (origin + destination)
    filtered_pair = get_filtered_corridors(sample_bilateral_df, year=2020, origin_code="MEX", destination_code="USA")
    assert len(filtered_pair) == 1
    assert filtered_pair.iloc[0]["origin_code"] == "MEX"
    assert filtered_pair.iloc[0]["destination_code"] == "USA"

    # Test no-match returns empty dataframe safely
    no_match = get_filtered_corridors(sample_bilateral_df, year=2020, origin_code="NONEXISTENT")
    assert no_match.empty


def test_get_country_profile_data(sample_merged_df, sample_bilateral_df):
    """Test country profile data compilation and schema contract."""
    profile = get_country_profile_data(sample_merged_df, sample_bilateral_df, country_code="USA", year=2020)
    assert profile["country_code"] == "USA"
    assert profile["country_name"] == "United States"
    assert "immigrant_stock" in profile
    assert "migrant_stock" in profile
    assert profile["immigrant_stock"] == 50000000.0
    assert profile["migrant_stock"] == 50000000.0
    assert profile["total_population"] == 330000000.0
    assert np.isclose(profile["migrant_pct_population"], 15.15, atol=0.01)
    assert "emigrant_stock" in profile
    assert "net_migrant_stock" in profile
    assert "top_inbound_origins" in profile
    assert "top_outbound_destinations" in profile
    assert len(profile["history_df"]) == 2
    assert len(profile["inbound_corridors"]) == 2  # MEX -> USA, IND -> USA
    assert len(profile["outbound_corridors"]) == 0
