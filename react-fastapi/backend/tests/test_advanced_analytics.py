"""
Unit and integration test suite for Phase 5 Advanced Migration Analytics & Insight Engine.
Validates concentration metrics, HHI calculations, socioeconomic correlations,
transparent anomaly detection, growth classifications, multi-country comparisons,
migration dependence / share metrics, and rule-based insight generation.
"""

import numpy as np
import pandas as pd
import pytest

from src.advanced_analytics import (
    classify_stock_changes,
    compute_corridor_concentration_trend,
    compute_corridor_trajectories,
    compute_destination_concentration,
    compute_longitudinal_concentration_trend,
    compute_migration_dependence,
    compute_multicountry_comparison,
    compute_origin_concentration,
    compute_socioeconomic_correlations,
    detect_migration_anomalies,
    get_bivariate_scatter_data,
    get_top_growth_and_declining_countries,
)
from src.dashboard_data import (
    prepare_bilateral_corridor_data,
    prepare_country_socioeconomic_data,
)
from src.insight_engine import (
    generate_all_insights,
    generate_change_insights,
    generate_concentration_insights,
    generate_corridor_insights,
    generate_global_insights,
    generate_socioeconomic_insights,
)
from src.network_analysis import build_migration_network, calculate_network_metrics


@pytest.fixture(scope="module")
def real_datasets():
    df_c = prepare_country_socioeconomic_data()
    df_b = prepare_bilateral_corridor_data()
    G_2020 = build_migration_network(df_b, year=2020)
    net_metrics_2020 = calculate_network_metrics(G_2020)
    return df_c, df_b, net_metrics_2020


def test_destination_concentration_calculation(real_datasets):
    df_c, _, _ = real_datasets
    for yr in [1990, 2000, 2010, 2020]:
        conc = compute_destination_concentration(df_c, year=yr)
        assert conc["year"] == yr
        assert conc["total_migrant_stock"] > 0
        assert conc["num_countries"] > 150
        assert 0.0 < conc["top_5_share"] < 100.0
        assert 0.0 < conc["top_10_share"] < 100.0
        assert 0.0 < conc["top_25_share"] < 100.0
        assert conc["top_5_share"] < conc["top_10_share"] < conc["top_25_share"]
        # HHI must be within [0, 10000]
        assert 0.0 <= conc["hhi"] <= 10000.0
        assert len(conc["top_destinations"]) > 0


def test_origin_concentration_calculation(real_datasets):
    _, df_b, _ = real_datasets
    for yr in [1990, 2000, 2010, 2020]:
        orig = compute_origin_concentration(df_b, year=yr)
        assert orig["year"] == yr
        assert orig["total_emigrant_stock"] > 0
        assert orig["num_origins"] > 150
        assert 0.0 < orig["top_5_origin_share"] < 100.0
        assert 0.0 <= orig["origin_hhi"] <= 10000.0
        assert len(orig["top_origins"]) > 0


def test_longitudinal_concentration_trend(real_datasets):
    df_c, df_b, _ = real_datasets
    trend_df = compute_longitudinal_concentration_trend(df_c, df_b)
    assert not trend_df.empty
    assert len(trend_df) == 7  # 1990 to 2020 quinquennial rounds
    assert "dest_hhi" in trend_df.columns
    assert "orig_hhi" in trend_df.columns
    assert "dest_top_10_share" in trend_df.columns


def test_migration_dependence_calculation(real_datasets):
    df_c, df_b, _ = real_datasets
    dep_df = compute_migration_dependence(df_c, df_b, year=2020)
    assert not dep_df.empty
    assert "country_code" in dep_df.columns
    assert "top_origin_share_pct" in dep_df.columns
    assert "origin_concentration_hhi" in dep_df.columns
    # Check top destination (USA)
    usa_row = dep_df[dep_df["country_code"] == "USA"]
    assert not usa_row.empty
    assert usa_row.iloc[0]["top_origin_code"] == "MEX"
    assert usa_row.iloc[0]["top_origin_share_pct"] > 15.0


def test_corridor_concentration_trend(real_datasets):
    _, df_b, _ = real_datasets
    corr_trend = compute_corridor_concentration_trend(df_b)
    assert not corr_trend.empty
    assert len(corr_trend) == 7
    assert "top_10_corridor_share" in corr_trend.columns
    assert "top_25_corridor_share" in corr_trend.columns
    assert "top_50_corridor_share" in corr_trend.columns
    for _, row in corr_trend.iterrows():
        assert row["top_10_corridor_share"] < row["top_25_corridor_share"] < row["top_50_corridor_share"]


def test_corridor_trajectories(real_datasets):
    _, df_b, _ = real_datasets
    trajs = compute_corridor_trajectories(df_b, top_n=10)
    assert not trajs.empty
    assert "corridor_label" in trajs.columns
    assert "migrant_stock" in trajs.columns
    mex_usa = trajs[trajs["corridor_label"].str.contains("Mexico") | (trajs["origin_code"] == "MEX")]
    assert not mex_usa.empty


def test_socioeconomic_correlations(real_datasets):
    df_c, _, net_metrics_2020 = real_datasets
    corr_df = compute_socioeconomic_correlations(df_c, year=2020, df_net_metrics=net_metrics_2020)
    assert not corr_df.empty
    assert len(corr_df) >= 4
    for _, row in corr_df.iterrows():
        if pd.notna(row["pearson_r"]):
            assert -1.0 <= row["pearson_r"] <= 1.0
            assert 0.0 <= row["pearson_p_value"] <= 1.0
        if pd.notna(row["spearman_rho"]):
            assert -1.0 <= row["spearman_rho"] <= 1.0
            assert 0.0 <= row["spearman_p_value"] <= 1.0


def test_bivariate_scatter_data(real_datasets):
    df_c, _, _ = real_datasets
    scatter_df, stats_dict = get_bivariate_scatter_data(
        df_c,
        x_metric_col="gdp_per_capita",
        y_metric_col="migrant_stock_pct_population",
        year=2020,
        log_scale_x=True
    )
    assert not scatter_df.empty
    assert "plot_x" in scatter_df.columns
    assert "plot_y" in scatter_df.columns
    assert "pearson_r" in stats_dict
    assert "spearman_rho" in stats_dict


def test_classify_stock_changes(real_datasets):
    df_c, _, _ = real_datasets
    classified_df = classify_stock_changes(df_c, year=2020)
    assert "change_category" in classified_df.columns
    categories = classified_df["change_category"].unique()
    assert any("Increase" in str(c) or "Stable" in str(c) or "Decrease" in str(c) for c in categories)


def test_get_top_growth_and_declining_countries(real_datasets):
    df_c, _, _ = real_datasets
    changes = get_top_growth_and_declining_countries(df_c, year=2020, top_n=5)
    assert "fastest_growth_pct" in changes
    assert "largest_increase_abs" in changes
    assert "largest_decrease_abs" in changes
    assert len(changes["largest_increase_abs"]) == 5
    assert len(changes["largest_decrease_abs"]) == 5


def test_detect_migration_anomalies_iqr(real_datasets):
    df_c, _, _ = real_datasets
    outliers, summary = detect_migration_anomalies(
        df_c,
        metric_col="migrant_stock_pct_population",
        year=2020,
        method="IQR",
        threshold=1.5
    )
    assert not outliers.empty
    assert "outlier_type" in outliers.columns
    assert summary["method"] == "IQR"
    assert summary["iqr"] > 0
    assert summary["upper_bound"] > summary["q3"]


def test_detect_migration_anomalies_zscore(real_datasets):
    df_c, _, _ = real_datasets
    outliers, summary = detect_migration_anomalies(
        df_c,
        metric_col="migrant_stock",
        year=2020,
        method="Z-Score",
        threshold=2.5
    )
    assert not outliers.empty
    assert "z_score" in outliers.columns
    assert summary["method"] == "Z-Score"
    assert summary["threshold"] == 2.5
    assert any(outliers["country_code"] == "USA")


def test_multicountry_comparison(real_datasets):
    df_c, _, net_metrics_2020 = real_datasets
    test_countries = ["USA", "DEU", "IND", "ARE"]
    abs_df, norm_df = compute_multicountry_comparison(
        df_c,
        country_codes=test_countries,
        year=2020,
        df_net_metrics=net_metrics_2020
    )
    assert len(abs_df) == 4
    assert len(norm_df) == 4
    assert "Total Migrant Stock (People)" in abs_df.columns
    assert "Total Migrant Stock (People)" in norm_df.columns
    # Normalized scores must be within [0, 100]
    for col in norm_df.columns:
        if col not in ["country_code", "country_name"]:
            valid_scores = norm_df[col].dropna()
            if not valid_scores.empty:
                assert (valid_scores >= 0.0).all()
                assert (valid_scores <= 100.0).all()


def test_insight_engine_generation(real_datasets):
    df_c, df_b, net_metrics_2020 = real_datasets
    insights = generate_all_insights(df_c, df_b, year=2020, df_net_metrics=net_metrics_2020)
    assert len(insights) >= 5
    categories = [ins["category"] for ins in insights]
    assert "Global Trend" in categories
    assert "Concentration" in categories
    assert "Major Corridors" in categories
    assert "Socioeconomic Associations" in categories
    
    for ins in insights:
        assert "title" in ins and len(ins["title"]) > 0
        assert "message" in ins and len(ins["message"]) > 0
        assert ins["year"] == 2020


def test_advanced_analytics_empty_dataframe_safety():
    empty_c = pd.DataFrame(columns=["year", "country_code", "display_name", "migrant_stock", "is_aggregate"])
    empty_b = pd.DataFrame(columns=["year", "origin_code", "destination_code", "migrant_stock", "is_aggregate_route"])
    
    conc = compute_destination_concentration(empty_c, year=2020)
    assert conc["total_migrant_stock"] == 0.0
    assert conc["hhi"] == 0.0
    
    orig = compute_origin_concentration(empty_b, year=2020)
    assert orig["total_emigrant_stock"] == 0.0

    dep = compute_migration_dependence(empty_c, empty_b, year=2020)
    assert dep.empty
    
    corr = compute_socioeconomic_correlations(empty_c, year=2020)
    assert corr.empty
    
    outliers, _ = detect_migration_anomalies(empty_c, "migrant_stock", year=2020)
    assert outliers.empty
    
    insights = generate_all_insights(empty_c, empty_b, year=2020)
    assert isinstance(insights, list)
