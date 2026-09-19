"""
Integration test for verifying that all dashboard data queries across all pages,
years, and metrics execute without error on the actual processed datasets.
"""

import pandas as pd
import numpy as np
import pytest

from src.dashboard_data import (
    METRIC_COLUMN_MAP,
    get_country_profile_data,
    get_country_trend_data,
    get_filtered_corridors,
    get_global_trend_data,
    get_map_data,
    get_overview_kpis,
    get_rankings_data,
    get_top_global_corridors,
    prepare_bilateral_corridor_data,
    prepare_country_socioeconomic_data,
)


@pytest.fixture(scope="module")
def loaded_datasets():
    df_c = prepare_country_socioeconomic_data()
    df_b = prepare_bilateral_corridor_data()
    return df_c, df_b


def test_all_years_overview_kpis(loaded_datasets):
    df_c, df_b = loaded_datasets
    years = sorted(df_c["year"].unique())
    for yr in years:
        kpi = get_overview_kpis(df_c, df_b, year=yr)
        assert kpi["year"] == yr
        assert kpi["total_migrant_stock"] > 0
        assert kpi["num_countries"] > 150
        assert kpi["top_destination_stock"] > 0
        assert kpi["num_corridors"] > 1000
        assert "global_migrant_pct" in kpi
        assert 1.0 < kpi["global_migrant_pct"] < 10.0


def test_all_map_metrics_and_years(loaded_datasets):
    df_c, _ = loaded_datasets
    years = sorted(df_c["year"].unique())
    metrics = list(METRIC_COLUMN_MAP.keys())
    
    for yr in years:
        for m in metrics:
            map_df = get_map_data(df_c, year=yr, metric_name=m)
            assert not map_df.empty
            assert "country_code" in map_df.columns
            assert "metric_value" in map_df.columns
            assert "population" in map_df.columns
            assert "gdp_per_capita" in map_df.columns


def test_all_rankings_metrics_and_years(loaded_datasets):
    df_c, _ = loaded_datasets
    years = sorted(df_c["year"].unique())
    metrics = ["Migrant Stock", "Migrant Stock % of Population", "5-Year Stock Change", "5-Year Stock Growth %"]
    
    for yr in years:
        for m in metrics:
            rank_df = get_rankings_data(df_c, year=yr, metric_name=m, top_n=25)
            # 1990 is the base year, so 5-year change metrics are NaN in 1990
            if yr == 1990 and ("Change" in m or "Growth" in m):
                assert len(rank_df) == 0
            else:
                assert len(rank_df) > 0
                assert "rank" in rank_df.columns
                assert "metric_value" in rank_df.columns


def test_top_global_corridors_all_years(loaded_datasets):
    _, df_b = loaded_datasets
    years = sorted(df_b["year"].unique())
    for yr in years:
        corridors = get_top_global_corridors(df_b, year=yr, top_n=25)
        assert len(corridors) == 25
        assert "migrant_stock" in corridors.columns
        # Top 1 corridor in 2020 is MEX -> USA
        if yr == 2020:
            top_1 = corridors.iloc[0]
            assert top_1["origin_code"] == "MEX"
            assert top_1["destination_code"] == "USA"


def test_country_profile_major_countries(loaded_datasets):
    df_c, df_b = loaded_datasets
    test_iso3s = ["USA", "IND", "DEU", "CHN", "GBR", "ARE", "MEX", "CAN"]
    for code in test_iso3s:
        profile = get_country_profile_data(df_c, df_b, country_code=code, year=2020)
        assert profile["country_code"] == code
        assert not profile["history_df"].empty
        assert len(profile["history_df"]) == 7  # 7 census rounds 1990-2020
        assert "immigrant_stock" in profile
        assert "migrant_stock" in profile
        assert profile["immigrant_stock"] > 0
        assert "emigrant_stock" in profile
        assert "net_migrant_stock" in profile
        assert "top_inbound_origins" in profile
        assert "top_outbound_destinations" in profile
