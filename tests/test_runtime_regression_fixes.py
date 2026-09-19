"""
Dedicated test suite verifying the resolution of all reported runtime regressions:
1. Overview KPI 'global_migrant_pct'
2. Global Map hover data 'gdp_per_capita'
3. Country Explorer profile 'immigrant_stock' and supporting schema
4. Migration Network create_network_2d_plot signature with explicit and optional metrics_df
5. Country Comparison historical trajectory schema contract and Plotly rendering with metric_value
6. Route Explorer destination_code parameter support and multi-filter safety
"""

import numpy as np
import pandas as pd
import plotly.express as px
import pytest

from src.dashboard_data import (
    METRIC_COLUMN_MAP,
    METRIC_LABELS,
    get_country_profile_data,
    get_country_trend_data,
    get_filtered_corridors,
    get_map_data,
    get_overview_kpis,
    get_top_global_corridors,
    prepare_bilateral_corridor_data,
    prepare_country_socioeconomic_data,
)
from src.network_analysis import build_migration_network, calculate_network_metrics
from src.network_visualization import create_network_2d_plot
from src.ui_components import render_kpi_card


@pytest.fixture(scope="module")
def prod_datasets():
    df_c = prepare_country_socioeconomic_data()
    df_b = prepare_bilateral_corridor_data()
    return df_c, df_b


def test_regression_1_overview_kpi_global_migrant_pct(prod_datasets):
    """Verify get_overview_kpis returns valid global_migrant_pct across all census rounds."""
    df_c, df_b = prod_datasets
    for yr in [1990, 1995, 2000, 2005, 2010, 2015, 2020]:
        kpis = get_overview_kpis(df_c, df_b, year=yr)
        assert "global_migrant_pct" in kpis
        assert isinstance(kpis["global_migrant_pct"], float)
        assert 2.0 < kpis["global_migrant_pct"] < 5.0
        # Check UI card rendering
        html = render_kpi_card("Global Migrant Share", f"{kpis['global_migrant_pct']:.2f}%", "Share of world pop", "Light")
        assert len(html) > 0


def test_regression_2_map_hover_data_gdp_per_capita(prod_datasets):
    """Verify get_map_data returns gdp_per_capita and all Plotly hover requirements."""
    df_c, _ = prod_datasets
    for yr in [1990, 2000, 2020]:
        for metric in list(METRIC_COLUMN_MAP.keys()):
            map_df = get_map_data(df_c, year=yr, metric_name=metric)
            assert "gdp_per_capita" in map_df.columns
            assert "population" in map_df.columns
            assert "metric_value" in map_df.columns
            
            # Verify Plotly choropleth constructor executes with hover_data dictionary
            fig_map = px.choropleth(
                map_df,
                locations="country_code",
                color="metric_value",
                hover_name="display_name",
                hover_data={
                    "country_code": True,
                    "metric_value": ":,.2f" if "pct" in metric.lower() or "%" in metric else ":,.0f",
                    "population": ":,.0f",
                    "gdp_per_capita": ":$,.0f"
                },
                labels={"metric_value": metric, "country_code": "ISO3"},
                color_continuous_scale="Blues"
            )
            assert fig_map is not None


def test_regression_3_country_explorer_immigrant_stock_schema(prod_datasets):
    """Verify get_country_profile_data returns immigrant_stock, migrant_stock, emigrant_stock, and net_migrant_stock."""
    df_c, df_b = prod_datasets
    for code in ["USA", "MEX", "DEU", "IND", "ARE"]:
        for yr in [2000, 2020]:
            profile = get_country_profile_data(df_c, df_b, country_code=code, year=yr)
            assert "immigrant_stock" in profile
            assert "migrant_stock" in profile
            assert profile["immigrant_stock"] == profile["migrant_stock"]
            assert "total_population" in profile
            assert "migrant_pct_population" in profile
            assert "emigrant_stock" in profile
            assert "net_migrant_stock" in profile
            assert "top_inbound_origins" in profile
            assert "top_outbound_destinations" in profile
            
            # Verify KPI card formatting
            c1 = render_kpi_card("Residing Immigrant Stock", f"{profile['immigrant_stock']:,.0f}", f"Inbound stock ({yr})", "Dark")
            c2 = render_kpi_card("Migrant % of Population", f"{profile['migrant_pct_population']:.2f}%", "Total Pop", "Light")
            c3 = render_kpi_card("Emigrant Stock Abroad", f"{profile['emigrant_stock']:,.0f}", f"Living abroad ({yr})", "Dark")
            c4 = render_kpi_card("Net Migrant Stock Balance", f"{profile['net_migrant_stock']:+,.0f}", "Balance", "Light")
            assert len(c1) > 0 and len(c2) > 0 and len(c3) > 0 and len(c4) > 0


def test_regression_4_network_2d_plot_signature_and_theming(prod_datasets):
    """Verify create_network_2d_plot works both with explicit metrics_df and with omitted metrics_df."""
    _, df_b = prod_datasets
    G = build_migration_network(df_b, year=2020, min_stock=100000)
    df_metrics = calculate_network_metrics(G)
    
    # 1. With explicit metrics_df (Light theme)
    fig_explicit_light = create_network_2d_plot(
        G,
        metrics_df=df_metrics,
        layout_type="Spring",
        is_dark_mode=False,
        title="Network Light"
    )
    assert fig_explicit_light is not None
    
    # 2. With explicit metrics_df (Dark theme)
    fig_explicit_dark = create_network_2d_plot(
        G,
        metrics_df=df_metrics,
        layout_type="Circular",
        is_dark_mode=True,
        title="Network Dark"
    )
    assert fig_explicit_dark is not None
    
    # 3. With omitted metrics_df (Auto-calculated fallback)
    fig_auto = create_network_2d_plot(
        G,
        layout_type="Spring",
        is_dark_mode=True
    )
    assert fig_auto is not None


def test_regression_5_country_comparison_trajectory_contract(prod_datasets):
    """Verify Country Comparison multi-country trajectories with 2 and 5 countries across metrics."""
    df_c, _ = prod_datasets
    test_country_groups = [
        ["USA", "MEX"],
        ["USA", "DEU", "IND", "CAN", "ARE"]
    ]
    test_metrics = [
        "Migrant Stock",
        "Migrant Stock % of Population",
        "GDP per Capita",
        "Population",
        "5-Year Stock Growth %"
    ]
    
    for c_group in test_country_groups:
        for m_name in test_metrics:
            comp_traj_df = get_country_trend_data(df_c, country_codes=c_group, metric_name=m_name)
            assert not comp_traj_df.empty
            
            # Verify exact schema contract
            expected_columns = {"display_name", "country_code", "year", "metric_value", "metric_label"}
            assert set(comp_traj_df.columns) == expected_columns
            assert len(comp_traj_df["country_code"].unique()) == len(c_group)
            
            # Verify Plotly line plot renders cleanly using metric_value
            metric_lbl = comp_traj_df["metric_label"].iloc[0] if "metric_label" in comp_traj_df.columns else m_name
            fig = px.line(
                comp_traj_df,
                x="year",
                y="metric_value",
                color="display_name",
                markers=True,
                title=f"Comparative Trajectory: {m_name} (1990–2020)",
                labels={"year": "Census Year", "metric_value": metric_lbl, "display_name": "Country"}
            )
            assert fig is not None


def test_regression_6_route_explorer_filtering_and_empty_safety(prod_datasets):
    """Verify Route Explorer caller contract with destination_code, origin_code, pairwise, and empty cases."""
    _, df_b = prod_datasets
    
    # 1. Origin only with destination_code=None
    res_orig = get_filtered_corridors(df_b, year=2020, origin_code="MEX", destination_code=None, top_n=25)
    assert not res_orig.empty
    assert all(res_orig["origin_code"] == "MEX")
    assert "rank" in res_orig.columns
    assert "corridor_label" in res_orig.columns

    # 2. Destination only with origin_code=None and destination_code="USA"
    res_dest = get_filtered_corridors(df_b, year=2020, origin_code=None, destination_code="USA", top_n=25)
    assert not res_dest.empty
    assert all(res_dest["destination_code"] == "USA")

    # 3. Origin + Destination pair
    res_pair = get_filtered_corridors(df_b, year=2020, origin_code="MEX", destination_code="USA", top_n=25)
    assert not res_pair.empty
    assert len(res_pair) == 1
    assert res_pair.iloc[0]["origin_code"] == "MEX"
    assert res_pair.iloc[0]["destination_code"] == "USA"

    # 4. No matching pair handles gracefully
    res_empty = get_filtered_corridors(df_b, year=2020, origin_code="MEX", destination_code="MEX", top_n=25)
    assert res_empty.empty
