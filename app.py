"""
Global Migration Observatory — Phase 5 Advanced Migration Analytics & Data Storytelling
An empirical, academic-grade data platform integrating UN DESA 2020 International Migrant Stock
and World Bank WDI indicators with NetworkX network analytics, community detection, concentration (HHI),
socioeconomic bivariate correlations, transparent outlier detection, multi-country comparisons,
and rule-based automated data storytelling.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.advanced_analytics import (
    classify_stock_changes,
    compute_corridor_concentration_trend,
    compute_corridor_trajectories,
    compute_destination_concentration,
    compute_longitudinal_concentration_trend,
    compute_multicountry_comparison,
    compute_origin_concentration,
    compute_socioeconomic_correlations,
    detect_migration_anomalies,
    get_bivariate_scatter_data,
    get_top_growth_and_declining_countries,
)
from src.config import config
from src.dashboard_data import (
    METRIC_COLUMN_MAP,
    METRIC_LABELS,
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
from src.insight_engine import (
    generate_all_insights,
    generate_change_insights,
    generate_concentration_insights,
    generate_corridor_insights,
    generate_global_insights,
    generate_network_insights,
    generate_socioeconomic_insights,
)
from src.network_analysis import (
    build_migration_network,
    calculate_network_metrics,
    create_undirected_stock_network,
    detect_network_communities,
    get_bidirectional_corridor_analysis,
    get_country_centrality_trajectories,
    get_network_rankings_data,
    get_temporal_network_evolution,
)
from src.network_visualization import (
    create_community_graph_plot,
    create_geographic_network_map,
    create_network_2d_plot,
)
from src.ui_components import (
    render_correlation_badge,
    render_insight_card,
    render_kpi_card,
    render_masthead,
    render_scientific_alert,
    render_section_title,
    render_sidebar_header,
    render_warning_callout,
)
from src.ui_theme import apply_ui_theme, get_plotly_layout, get_theme_colors


# =============================================================================
# STREAMLIT PAGE CONFIG & THEME INITIALIZATION
# =============================================================================

st.set_page_config(
    page_title="Global Migration Observatory",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Theme Management
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

# Apply universal UI styling
apply_ui_theme(st.session_state["theme_mode"])
theme_mode = st.session_state["theme_mode"]
is_dark = (theme_mode == "Dark")
plotly_tmpl = "plotly_dark" if is_dark else "plotly_white"
theme_colors = get_theme_colors(theme_mode)


# =============================================================================
# CACHED DATA LOADERS & COMPUTATIONS
# =============================================================================

@st.cache_data(show_spinner="Loading Global Migration datasets...")
def load_cached_datasets():
    df_country = prepare_country_socioeconomic_data()
    df_bilat = prepare_bilateral_corridor_data()
    return df_country, df_bilat


@st.cache_data(show_spinner="Computing network centrality metrics...")
def get_cached_network_and_metrics(year: int, min_stock: Optional[float], top_n_edges: Optional[int]):
    G = build_migration_network(
        df_bilat,
        year=year,
        min_stock=min_stock,
        top_n_edges=top_n_edges,
        sovereign_only=True,
        directed=True
    )
    df_metrics = calculate_network_metrics(G)
    return G, df_metrics


@st.cache_data(show_spinner="Detecting modularity communities...")
def get_cached_communities(year: int, min_stock: Optional[float], top_n_edges: Optional[int]):
    G = build_migration_network(
        df_bilat,
        year=year,
        min_stock=min_stock,
        top_n_edges=top_n_edges,
        sovereign_only=True,
        directed=True
    )
    node_map, summary_df, mod = detect_network_communities(G)
    return G, node_map, summary_df, mod


@st.cache_data(show_spinner="Computing temporal network evolution...")
def get_cached_temporal_evolution(min_stock: Optional[float], top_n_edges: Optional[int]):
    return get_temporal_network_evolution(df_bilat, min_stock=min_stock, top_n_edges=top_n_edges)


@st.cache_data(show_spinner="Computing concentration trends...")
def get_cached_concentration_trend():
    return compute_longitudinal_concentration_trend(df_country, df_bilat)


@st.cache_data(show_spinner="Computing corridor concentration trends...")
def get_cached_corridor_concentration_trend():
    return compute_corridor_concentration_trend(df_bilat)


try:
    df_country, df_bilat = load_cached_datasets()
    data_loaded = True
except Exception as exc:
    data_loaded = False
    st.error(f"Error loading processed datasets: {exc}")
    st.info("Run `python run_pipeline.py` to regenerate the processed datasets.")


if data_loaded:
    AVAILABLE_YEARS = sorted(df_country["year"].unique().tolist())
    SOVEREIGN_COUNTRIES = (
        df_country[~df_country["is_aggregate"]]
        [["country_code", "display_name"]]
        .drop_duplicates()
        .sort_values("display_name")
    )
    COUNTRY_DICT = dict(zip(SOVEREIGN_COUNTRIES["display_name"], SOVEREIGN_COUNTRIES["country_code"]))
    CODE_TO_NAME = dict(zip(SOVEREIGN_COUNTRIES["country_code"], SOVEREIGN_COUNTRIES["display_name"]))

    # =============================================================================
    # SIDEBAR CONTROLS & GROUPED NAVIGATION
    # =============================================================================
    render_sidebar_header(theme_mode)

    # Theme Switcher in Sidebar
    theme_col1, theme_col2 = st.sidebar.columns([1, 1])
    with theme_col1:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state["theme_mode"] = "Light"
            st.rerun()
    with theme_col2:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state["theme_mode"] = "Dark"
            st.rerun()

    st.sidebar.markdown("---")

    # Grouped Navigation Options
    st.sidebar.markdown(f"<p style='font-size: 0.75rem; font-weight: 700; color: {theme_colors['text_muted']}; text-transform: uppercase; letter-spacing: 0.08em; margin: 0.5rem 0 0.25rem 0;'>Navigation</p>", unsafe_allow_html=True)
    
    NAV_OPTIONS = [
        "🏠 Overview",
        "🌍 Global Map",
        "📈 Trends",
        "🏆 Rankings",
        "🔀 Route Explorer",
        "🌎 Country Explorer",
        "🕸️ Migration Network",
        "🔗 Corridor Analysis",
        "🌐 Communities",
        "📊 Advanced Analytics",
        "⚖️ Country Comparison",
        "💡 Migration Insights",
        "ℹ️ Methodology",
    ]

    page = st.sidebar.radio(
        "Navigation Options",
        NAV_OPTIONS,
        index=0,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"<p style='font-size: 0.75rem; font-weight: 700; color: {theme_colors['text_muted']}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.2rem;'>Scientific Principle</p>", unsafe_allow_html=True)
    st.sidebar.caption(
        "**Migrant Stock ≠ Migration Flow**. Data represents the estimated residing foreign-born population at mid-year (UN DESA 2020 Revision)."
    )

    # Masthead Header Banner
    render_masthead(theme_mode)

    # =============================================================================
    # PAGE 1: 🏠 OVERVIEW
    # =============================================================================
    if page == "🏠 Overview":
        render_section_title("🏠 Executive Overview Dashboard", "Global summary of international migrant stock and distribution")
        
        col_ctrl, _ = st.columns([2, 4])
        with col_ctrl:
            selected_year = st.selectbox(
                "Select Census Estimation Year",
                AVAILABLE_YEARS,
                index=len(AVAILABLE_YEARS) - 1,
                key="overview_year"
            )
            
        kpis = get_overview_kpis(df_country, df_bilat, year=selected_year)
        
        # KPI Row
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(render_kpi_card("Total Global Migrant Stock", f"{kpis['total_migrant_stock']:,.0f}", f"Estimated in {selected_year}", theme_mode), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Global Migrant Share", f"{kpis['global_migrant_pct']:.2f}%", "Share of world population", theme_mode), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Countries / Entities", f"{kpis['num_countries']}", "Reporting sovereign nations", theme_mode), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi_card("Top Destination", f"{kpis['top_destination_name']}", f"{kpis['top_destination_stock']:,.0f} migrants", theme_mode), unsafe_allow_html=True)
        with k5:
            st.markdown(render_kpi_card("Bilateral Corridors", f"{kpis['num_corridors']:,}", "Active non-zero pairs", theme_mode), unsafe_allow_html=True)

        render_scientific_alert(
            "<b>Scientific Principle</b>: <b>Migrant stock</b> represents the estimated cumulative count of foreign-born individuals living in a destination country at mid-year. It is <b>NOT</b> an annual flow rate. Intercensal differences between 5-year rounds reflect net cumulative changes including births, deaths, naturalizations, return migration, and boundary adjustments.",
            theme_mode
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Overview Visualizations
        ov_col1, ov_col2 = st.columns([3, 2])
        with ov_col1:
            render_section_title("Global Migrant Stock Growth (1990–2020)")
            trend_df = get_global_trend_data(df_country)
            fig_trend = px.area(
                trend_df,
                x="year",
                y="total_migrant_stock",
                title="Global Residing Migrant Stock (Quinquennial Census Rounds)",
                labels={"year": "Census Round", "total_migrant_stock": "Migrant Stock (People)"},
                template=plotly_tmpl
            )
            fig_trend.update_layout(**get_plotly_layout(theme_mode, "Global Residing Migrant Stock (Quinquennial Census Rounds)", height=380))
            fig_trend.update_traces(line=dict(color=theme_colors["accent_blue"], width=3), fillcolor="rgba(2, 132, 199, 0.15)" if not is_dark else "rgba(56, 189, 248, 0.15)")
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with ov_col2:
            render_section_title(f"Top 10 Destination Countries ({selected_year})")
            top10_df = get_rankings_data(df_country, year=selected_year, metric_name="Migrant Stock", top_n=10)
            fig_bar = px.bar(
                top10_df.sort_values("metric_value", ascending=True),
                x="metric_value",
                y="display_name",
                orientation="h",
                title=f"Top 10 Hosts in {selected_year}",
                labels={"metric_value": "Migrant Stock", "display_name": "Country"},
                template=plotly_tmpl
            )
            fig_bar.update_layout(**get_plotly_layout(theme_mode, f"Top 10 Hosts in {selected_year}", height=380))
            fig_bar.update_traces(marker_color=theme_colors["accent_blue"])
            st.plotly_chart(fig_bar, use_container_width=True)

        # Download Table
        render_section_title("Top 10 Destinations Summary Table")
        overview_table = top10_df[["rank", "display_name", "country_code", "metric_value", "migrant_stock_pct_population", "population"]].rename(columns={
            "rank": "Rank", "display_name": "Country", "country_code": "ISO3",
            "metric_value": "Migrant Stock", "migrant_stock_pct_population": "Migrant % of Pop", "population": "Total Population"
        })
        st.dataframe(
            overview_table.style.format({
                "Migrant Stock": "{:,.0f}", "Migrant % of Pop": "{:.2f}%", "Total Population": "{:,.0f}"
            }),
            use_container_width=True,
            height=280
        )
        st.download_button(
            label="📥 Download Overview Data CSV",
            data=overview_table.to_csv(index=False).encode("utf-8"),
            file_name=f"migration_overview_{selected_year}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 2: 🌍 GLOBAL MAP
    # =============================================================================
    elif page == "🌍 Global Map":
        render_section_title("🌍 Global Migration Choropleth Map", "Interactive world map displaying country-level migrant stock and demographic intensities")
        
        m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
        with m_col1:
            map_year = st.selectbox("Select Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="map_year")
        with m_col2:
            map_metric = st.selectbox("Select Display Metric", list(METRIC_COLUMN_MAP.keys()), index=0, key="map_metric")
        with m_col3:
            map_proj = st.selectbox("Map Projection", ["natural earth", "equirectangular", "orthographic", "robinson", "mercator"], index=0, key="map_proj")

        map_df = get_map_data(df_country, year=map_year, metric_name=map_metric)
        color_scale = "Blues" if not is_dark else "Viridis"
        
        fig_map = px.choropleth(
            map_df,
            locations="country_code",
            color="metric_value",
            hover_name="display_name",
            hover_data={
                "country_code": True,
                "metric_value": ":,.2f" if "pct" in map_metric.lower() or "%" in map_metric else ":,.0f",
                "population": ":,.0f",
                "gdp_per_capita": ":$,.0f"
            },
            labels={"metric_value": map_metric, "country_code": "ISO3"},
            color_continuous_scale=color_scale,
            projection=map_proj,
            template=plotly_tmpl
        )
        fig_map.update_layout(
            **get_plotly_layout(theme_mode, f"Global Distribution: {map_metric} ({map_year})", height=540)
        )
        fig_map.update_geos(
            showcoastlines=True, coastlinecolor=theme_colors["map_coastline"],
            showland=True, landcolor=theme_colors["map_land"],
            showocean=True, oceancolor=theme_colors["map_ocean"],
            showframe=False
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # Map Data Table
        render_section_title(f"Data Records for {map_metric} ({map_year})")
        display_map_df = map_df[["display_name", "country_code", "metric_value", "population", "gdp_per_capita"]].dropna(subset=["metric_value"]).sort_values("metric_value", ascending=False)
        st.dataframe(
            display_map_df.rename(columns={
                "display_name": "Country", "country_code": "ISO3", "metric_value": map_metric,
                "population": "Total Population", "gdp_per_capita": "GDP per Capita (USD)"
            }).style.format({
                map_metric: "{:,.2f}%" if "pct" in map_metric.lower() or "%" in map_metric else "{:,.0f}",
                "Total Population": "{:,.0f}",
                "GDP per Capita (USD)": "${:,.0f}"
            }),
            use_container_width=True,
            height=280
        )
        st.download_button(
            label="📥 Download Map Data CSV",
            data=display_map_df.to_csv(index=False).encode("utf-8"),
            file_name=f"migration_map_{map_metric}_{map_year}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 3: 📈 TRENDS
    # =============================================================================
    elif page == "📈 Trends":
        render_section_title("📈 Longitudinal Migration Trends (1990–2020)", "Multi-round time-series trajectories for global totals and individual countries")
        
        t_tabs = st.tabs(["🌐 Global Trajectory", "🔍 Country Comparison Trends"])
        with t_tabs[0]:
            glob_trend = get_global_trend_data(df_country)
            fig_g_trend = go.Figure()
            fig_g_trend.add_trace(go.Scatter(
                x=glob_trend["year"],
                y=glob_trend["total_migrant_stock"],
                mode="lines+markers",
                name="Total Migrant Stock",
                line=dict(color=theme_colors["accent_blue"], width=3),
                marker=dict(size=8)
            ))
            fig_g_trend.update_layout(**get_plotly_layout(theme_mode, "Total Residing Migrant Stock Worldwide (1990–2020)", height=420))
            st.plotly_chart(fig_g_trend, use_container_width=True)

        with t_tabs[1]:
            t_col1, t_col2 = st.columns([3, 1])
            with t_col1:
                selected_trend_countries = st.multiselect(
                    "Select Countries to Compare Trends",
                    list(COUNTRY_DICT.keys()),
                    default=["United States of America", "Germany", "United Kingdom", "Canada", "India"] if "United States of America" in COUNTRY_DICT else list(COUNTRY_DICT.keys())[:5],
                    key="trend_countries"
                )
            with t_col2:
                trend_metric = st.selectbox(
                    "Select Trend Metric",
                    ["Migrant Stock", "Migrant Stock % of Population", "GDP per Capita"],
                    index=0,
                    key="trend_metric_select"
                )

            selected_codes = [COUNTRY_DICT[c] for c in selected_trend_countries if c in COUNTRY_DICT]
            trend_data = get_country_trend_data(df_country, country_codes=selected_codes, metric_name=trend_metric)
            if not trend_data.empty:
                metric_lbl = trend_data["metric_label"].iloc[0] if "metric_label" in trend_data.columns else trend_metric
                fig_c_trend = px.line(
                    trend_data,
                    x="year",
                    y="metric_value",
                    color="display_name",
                    markers=True,
                    title=f"Comparative Historical Trajectories: {trend_metric}",
                    labels={"year": "Census Round", "metric_value": metric_lbl, "display_name": "Country"},
                    template=plotly_tmpl
                )
                fig_c_trend.update_layout(**get_plotly_layout(theme_mode, f"Comparative Historical Trajectories: {trend_metric}", height=440))
                st.plotly_chart(fig_c_trend, use_container_width=True)

                table_trend = trend_data[["year", "display_name", "country_code", "metric_value"]].pivot(index="display_name", columns="year", values="metric_value").reset_index()
                st.dataframe(table_trend, use_container_width=True)
                st.download_button(
                    label="📥 Download Trend Data CSV",
                    data=table_trend.to_csv(index=False).encode("utf-8"),
                    file_name=f"migration_trends_{METRIC_COLUMN_MAP.get(trend_metric, 'metric')}.csv",
                    mime="text/csv"
                )

    # =============================================================================
    # PAGE 4: 🏆 RANKINGS
    # =============================================================================
    elif page == "🏆 Rankings":
        render_section_title("🏆 Global Country Rankings", "Ranked leaderboards by migrant stock, demographic intensity, and 5-year growth")
        
        r_col1, r_col2, r_col3 = st.columns([2, 2, 2])
        with r_col1:
            rank_year = st.selectbox("Select Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="rank_year")
        with r_col2:
            rank_metric = st.selectbox("Select Ranking Metric", list(METRIC_COLUMN_MAP.keys()), index=0, key="rank_metric")
        with r_col3:
            rank_top_n = st.slider("Number of Countries (Top N)", min_value=10, max_value=50, value=20, step=5, key="rank_top_n")

        rank_df = get_rankings_data(df_country, year=rank_year, metric_name=rank_metric, top_n=rank_top_n)
        
        if not rank_df.empty:
            fig_rank = px.bar(
                rank_df.sort_values("metric_value", ascending=True),
                x="metric_value",
                y="display_name",
                orientation="h",
                title=f"Top {rank_top_n} Nations by {rank_metric} ({rank_year})",
                labels={"metric_value": rank_metric, "display_name": "Country"},
                template=plotly_tmpl
            )
            fig_rank.update_layout(**get_plotly_layout(theme_mode, f"Top {rank_top_n} Nations by {rank_metric} ({rank_year})", height=500))
            fig_rank.update_traces(marker_color=theme_colors["accent_blue"])
            st.plotly_chart(fig_rank, use_container_width=True)

            render_section_title("Rankings Full Table")
            display_rank = rank_df[["rank", "display_name", "country_code", "metric_value", "population", "gdp_per_capita"]].rename(columns={
                "rank": "Rank", "display_name": "Country", "country_code": "ISO3",
                "metric_value": rank_metric, "population": "Total Population", "gdp_per_capita": "GDP per Capita (USD)"
            })
            st.dataframe(
                display_rank.style.format({
                    rank_metric: "{:,.2f}%" if "pct" in rank_metric.lower() or "%" in rank_metric else "{:,.0f}",
                    "Total Population": "{:,.0f}",
                    "GDP per Capita (USD)": "${:,.0f}"
                }),
                use_container_width=True,
                height=320
            )
            st.download_button(
                label="📥 Download Rankings CSV",
                data=display_rank.to_csv(index=False).encode("utf-8"),
                file_name=f"migration_rankings_{rank_metric}_{rank_year}.csv",
                mime="text/csv"
            )

    # =============================================================================
    # PAGE 5: 🔀 ROUTE EXPLORER
    # =============================================================================
    elif page == "🔀 Route Explorer":
        render_section_title("🔀 Bilateral Corridor Route Explorer", "Explore origin-to-destination bilateral migrant-stock pairs")
        
        render_scientific_alert(
            "<b>Corridor Stock Definition</b>: A bilateral corridor estimate represents the number of individuals born in the <b>Origin Country</b> residing in the <b>Destination Country</b> at mid-year. Corridor shares reflect the portion of total bilateral migrant stock, <b>not</b> annual flow rates.",
            theme_mode
        )

        rc1, rc2, rc3 = st.columns([2, 2, 2])
        with rc1:
            route_year = st.selectbox("Census Round Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="route_year")
        with rc2:
            filter_origin = st.selectbox("Filter Origin Country", ["All Origins"] + list(COUNTRY_DICT.keys()), index=0, key="filter_origin")
        with rc3:
            filter_dest = st.selectbox("Filter Destination Country", ["All Destinations"] + list(COUNTRY_DICT.keys()), index=0, key="filter_dest")

        orig_code = COUNTRY_DICT.get(filter_origin, None) if filter_origin != "All Origins" else None
        dest_code = COUNTRY_DICT.get(filter_dest, None) if filter_dest != "All Destinations" else None

        if orig_code is None and dest_code is None:
            corridor_df = get_top_global_corridors(df_bilat, year=route_year, top_n=25)
            chart_title = f"Top 25 Global Migration Corridors ({route_year})"
        else:
            corridor_df = get_filtered_corridors(df_bilat, year=route_year, origin_code=orig_code, destination_code=dest_code, top_n=25)
            chart_title = f"Filtered Corridors: {filter_origin} → {filter_dest} ({route_year})"

        if not corridor_df.empty:
            fig_corridor = px.bar(
                corridor_df.sort_values("migrant_stock", ascending=True).tail(20),
                x="migrant_stock",
                y="corridor_label",
                orientation="h",
                title=chart_title,
                labels={"migrant_stock": "Residing Migrant Stock", "corridor_label": "Bilateral Corridor"},
                template=plotly_tmpl
            )
            fig_corridor.update_layout(**get_plotly_layout(theme_mode, chart_title, height=480))
            fig_corridor.update_traces(marker_color=theme_colors["accent_teal"])
            st.plotly_chart(fig_corridor, use_container_width=True)

            render_section_title("Corridor Detail Records")
            display_routes = corridor_df[[
                "rank", "corridor_label", "origin_display_name", "dest_display_name",
                "migrant_stock", "origin_corridor_share_pct", "dest_corridor_share_pct"
            ]].rename(columns={
                "rank": "Rank", "corridor_label": "Corridor", "origin_display_name": "Origin",
                "dest_display_name": "Destination", "migrant_stock": "Migrant Stock",
                "origin_corridor_share_pct": "Origin Emigrant Share %", "dest_corridor_share_pct": "Dest Immigrant Share %"
            })
            st.dataframe(
                display_routes.style.format({
                    "Migrant Stock": "{:,.0f}", "Origin Emigrant Share %": "{:.2f}%", "Dest Immigrant Share %": "{:.2f}%"
                }),
                use_container_width=True,
                height=300
            )
            st.download_button(
                label="📥 Download Corridor Data CSV",
                data=display_routes.to_csv(index=False).encode("utf-8"),
                file_name=f"migration_corridors_{route_year}.csv",
                mime="text/csv"
            )

    # =============================================================================
    # PAGE 6: 🌎 COUNTRY EXPLORER
    # =============================================================================
    elif page == "🌎 Country Explorer":
        render_section_title("🌎 Individual Country Profile & Diaspora Intelligence", "In-depth bilateral inbound and outbound stock profile for any sovereign entity")
        
        c_prof1, c_prof2 = st.columns([3, 2])
        with c_prof1:
            selected_country_name = st.selectbox(
                "Select Country to Inspect",
                list(COUNTRY_DICT.keys()),
                index=list(COUNTRY_DICT.keys()).index("United States of America") if "United States of America" in COUNTRY_DICT else 0,
                key="prof_country"
            )
        with c_prof2:
            prof_year = st.selectbox("Census Observation Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="prof_year")

        sel_code = COUNTRY_DICT[selected_country_name]
        profile = get_country_profile_data(df_country, df_bilat, country_code=sel_code, year=prof_year)
        
        # Country KPI Row
        cp1, cp2, cp3, cp4 = st.columns(4)
        with cp1:
            st.markdown(render_kpi_card("Residing Immigrant Stock", f"{profile['immigrant_stock']:,.0f}", f"Inbound stock ({prof_year})", theme_mode), unsafe_allow_html=True)
        with cp2:
            st.markdown(render_kpi_card("Migrant % of Population", f"{profile['migrant_pct_population']:.2f}%", f"Total Pop: {profile['total_population']:,.0f}", theme_mode), unsafe_allow_html=True)
        with cp3:
            st.markdown(render_kpi_card("Emigrant Stock Abroad", f"{profile['emigrant_stock']:,.0f}", f"Living abroad ({prof_year})", theme_mode), unsafe_allow_html=True)
        with cp4:
            st.markdown(render_kpi_card("Net Migrant Stock Balance", f"{profile['net_migrant_stock']:+,.0f}", "Immigrant minus Emigrant Stock", theme_mode), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Inbound and Outbound Corridors
        in_col, out_col = st.columns(2)
        with in_col:
            render_section_title(f"Top 10 Inbound Origins (Migrants in {selected_country_name})")
            if not profile["top_inbound_origins"].empty:
                fig_in = px.bar(
                    profile["top_inbound_origins"].sort_values("migrant_stock", ascending=True),
                    x="migrant_stock",
                    y="origin_display_name",
                    orientation="h",
                    title=f"Origins of Migrants Residing in {selected_country_name}",
                    labels={"migrant_stock": "Residing Migrants", "origin_display_name": "Origin Country"},
                    template=plotly_tmpl
                )
                fig_in.update_layout(**get_plotly_layout(theme_mode, f"Origins of Migrants Residing in {selected_country_name}", height=380))
                fig_in.update_traces(marker_color=theme_colors["accent_blue"])
                st.plotly_chart(fig_in, use_container_width=True)

        with out_col:
            render_section_title(f"Top 10 Outbound Destinations (Diaspora from {selected_country_name})")
            if not profile["top_outbound_destinations"].empty:
                fig_out = px.bar(
                    profile["top_outbound_destinations"].sort_values("migrant_stock", ascending=True),
                    x="migrant_stock",
                    y="dest_display_name",
                    orientation="h",
                    title=f"Destinations of Migrants Born in {selected_country_name}",
                    labels={"migrant_stock": "Diaspora Stock", "dest_display_name": "Destination Country"},
                    template=plotly_tmpl
                )
                fig_out.update_layout(**get_plotly_layout(theme_mode, f"Destinations of Migrants Born in {selected_country_name}", height=380))
                fig_out.update_traces(marker_color=theme_colors["accent_amber"])
                st.plotly_chart(fig_out, use_container_width=True)

        # Historical Trajectory Table
        render_section_title(f"Historical Demographic & Socioeconomic Records (1990–2020)")
        history_df = profile["history_df"][["year", "migrant_stock", "migrant_stock_pct_population", "population", "gdp_per_capita", "unemployment"]].rename(columns={
            "year": "Year", "migrant_stock": "Migrant Stock", "migrant_stock_pct_population": "Migrant % Pop",
            "population": "Population", "gdp_per_capita": "GDP per Capita", "unemployment": "Unemployment %"
        })
        st.dataframe(
            history_df.style.format({
                "Migrant Stock": "{:,.0f}", "Migrant % Pop": "{:.2f}%", "Population": "{:,.0f}",
                "GDP per Capita": "${:,.0f}", "Unemployment %": "{:.2f}%"
            }),
            use_container_width=True,
            height=280
        )
        st.caption("Descriptive macroeconomic indicators from World Bank WDI. These values describe economic context and do not establish causal relationships.")

    # =============================================================================
    # PAGE 7: 🕸️ MIGRATION NETWORK
    # =============================================================================
    elif page == "🕸️ Migration Network":
        render_section_title("🕸️ Global Migration Stock Network Analysis", "Network graph modeling bilateral migrant stock with centrality metrics and geographic flows")
        
        render_scientific_alert(
            "<b>Scientific Definition</b>: Each directed edge Origin → Destination represents the UN DESA estimated migrant stock residing in the destination whose origin is the specified origin country, for the selected UN DESA observation year. The network represents bilateral migrant-stock relationships. It does <b>NOT</b> represent annual migration flows, annual immigration flows, annual emigration flows, or yearly migration movements.",
            theme_mode
        )

        net_c1, net_c2, net_c3 = st.columns([2, 2, 2])
        with net_c1:
            net_year = st.selectbox("Select Network Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="net_yr")
        with net_c2:
            net_min_stock = st.selectbox("Min Corridor Stock Filter", [None, 50000, 100000, 250000, 500000, 1000000], index=3, format_func=lambda x: "All Corridors" if x is None else f"≥ {x:,.0f} migrants", key="net_stock")
        with net_c3:
            net_top_edges = st.selectbox("Top N Global Corridors", [None, 50, 100, 200, 300], index=2, format_func=lambda x: "All Edges" if x is None else f"Top {x} Corridors", key="net_edges")

        G, df_metrics = get_cached_network_and_metrics(net_year, net_min_stock, net_top_edges)

        # Network KPIs
        nk1, nk2, nk3, nk4 = st.columns(4)
        with nk1:
            st.markdown(render_kpi_card("Connected Nodes (Countries)", f"{G.number_of_nodes():,}", f"Active entities in {net_year}", theme_mode), unsafe_allow_html=True)
        with nk2:
            st.markdown(render_kpi_card("Directed Corridors (Edges)", f"{G.number_of_edges():,}", f"Bilateral connections", theme_mode), unsafe_allow_html=True)
        with nk3:
            total_net_stock = sum(d["weight"] for _, _, d in G.edges(data=True)) if G.number_of_edges() > 0 else 0
            st.markdown(render_kpi_card("Network Total Migrant Stock", f"{total_net_stock:,.0f}", "Sum of included corridors", theme_mode), unsafe_allow_html=True)
        with nk4:
            density = nx.density(G) if G.number_of_nodes() > 1 else 0
            st.markdown(render_kpi_card("Network Graph Density", f"{density:.4f}", "Edge saturation ratio", theme_mode), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Visualizations Tabs
        net_tabs = st.tabs(["🌐 Geographic Network Map", "🕸️ 2D Force-Directed Layout", "🏆 Centrality Leaderboards"])
        with net_tabs[0]:
            fig_geo = create_geographic_network_map(
                G,
                is_dark_mode=is_dark,
                title=f"Geographic Bilateral Migrant-Stock Network ({net_year})"
            )
            st.plotly_chart(fig_geo, use_container_width=True)

        with net_tabs[1]:
            layout_algo = st.radio("Graph Layout Algorithm", ["spring", "circular"], horizontal=True, index=0)
            fig_2d = create_network_2d_plot(
                G,
                metrics_df=df_metrics,
                layout_type=layout_algo,
                is_dark_mode=is_dark,
                title=f"2D Force-Directed Migration Network ({net_year})"
            )
            st.plotly_chart(fig_2d, use_container_width=True)

        with net_tabs[2]:
            render_section_title("Centrality & Hub Rankings")
            df_rank_net = df_metrics[[
                "country_name", "country_code", "in_strength", "out_strength",
                "total_strength", "pagerank", "betweenness_centrality", "total_degree"
            ]].rename(columns={
                "country_name": "Country", "country_code": "ISO3",
                "in_strength": "Inbound Residing Stock", "out_strength": "Outbound Diaspora Stock",
                "total_strength": "Total Weighted Strength", "pagerank": "PageRank Centrality",
                "betweenness_centrality": "Betweenness Centrality", "total_degree": "Degree"
            }).sort_values("Total Weighted Strength", ascending=False)

            st.dataframe(
                df_rank_net.style.format({
                    "Inbound Residing Stock": "{:,.0f}", "Outbound Diaspora Stock": "{:,.0f}",
                    "Total Weighted Strength": "{:,.0f}", "PageRank Centrality": "{:.4f}",
                    "Betweenness Centrality": "{:.4f}", "Degree": "{:,.0f}"
                }),
                use_container_width=True,
                height=340
            )
            st.download_button(
                label="📥 Download Centrality Metrics CSV",
                data=df_rank_net.to_csv(index=False).encode("utf-8"),
                file_name=f"migration_network_centrality_{net_year}.csv",
                mime="text/csv"
            )

    # =============================================================================
    # PAGE 8: 🔗 CORRIDOR ANALYSIS
    # =============================================================================
    elif page == "🔗 Corridor Analysis":
        render_section_title("🔗 Advanced Bilateral Corridor & Asymmetry Analytics", "Directional asymmetry, reciprocal balances, and corridor concentration")
        
        c_tabs = st.tabs(["⚖️ Country-Pair Asymmetry", "🎯 Corridor Concentration (HHI)", "📋 Top 50 Global Corridors"])
        with c_tabs[0]:
            asym_col1, asym_col2, asym_col3 = st.columns([2, 2, 2])
            with asym_col1:
                asym_year = st.selectbox("Census Observation Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="asym_yr")
            with asym_col2:
                c_a = st.selectbox("Country A", list(COUNTRY_DICT.keys()), index=list(COUNTRY_DICT.keys()).index("Mexico") if "Mexico" in COUNTRY_DICT else 0, key="asym_ca")
            with asym_col3:
                c_b = st.selectbox("Country B", list(COUNTRY_DICT.keys()), index=list(COUNTRY_DICT.keys()).index("United States of America") if "United States of America" in COUNTRY_DICT else 1, key="asym_cb")

            code_a = COUNTRY_DICT[c_a]
            code_b = COUNTRY_DICT[c_b]
            asym_res = get_bidirectional_corridor_analysis(df_bilat, country_a=code_a, country_b=code_b, year=asym_year)

            ak1, ak2, ak3, ak4 = st.columns(4)
            with ak1:
                st.markdown(render_kpi_card(f"{c_a} → {c_b} Stock", f"{asym_res['stock_a_to_b']:,.0f}", f"Born in {c_a}, residing in {c_b}", theme_mode), unsafe_allow_html=True)
            with ak2:
                st.markdown(render_kpi_card(f"{c_b} → {c_a} Stock", f"{asym_res['stock_b_to_a']:,.0f}", f"Born in {c_b}, residing in {c_a}", theme_mode), unsafe_allow_html=True)
            with ak3:
                st.markdown(render_kpi_card("Combined Bilateral Stock", f"{asym_res['total_bilateral_stock']:,.0f}", "Total mutual stock", theme_mode), unsafe_allow_html=True)
            with ak4:
                st.markdown(render_kpi_card("Directional Asymmetry Index", f"{asym_res['asymmetry_index']:+.3f}", f"Dominant: {asym_res['dominant_direction']}", theme_mode), unsafe_allow_html=True)

            st.markdown(f"**Dominant Direction**: `{asym_res['dominant_direction']}` | **Directional Ratio**: `{asym_res['directional_ratio']:.1f}:1`")

        with c_tabs[1]:
            render_section_title("Destination Concentration for a Given Origin Country")
            conc_c1, conc_c2 = st.columns([3, 2])
            with conc_c1:
                conc_country = st.selectbox("Select Origin Country", list(COUNTRY_DICT.keys()), index=0, key="conc_orig")
            with conc_c2:
                conc_year = st.selectbox("Select Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="conc_yr")

            c_code = COUNTRY_DICT[conc_country]
            emig_df = df_bilat[
                (df_bilat["origin_code"] == c_code) &
                (df_bilat["year"] == conc_year) &
                (~df_bilat["is_aggregate_route"]) &
                (df_bilat["destination_code"] != c_code) &
                (df_bilat["migrant_stock"] > 0)
            ].copy()
            
            if not emig_df.empty:
                tot_emig = emig_df["migrant_stock"].sum()
                emig_df["share"] = (emig_df["migrant_stock"] / tot_emig) * 100
                hhi_emig = sum((emig_df["share"] / 100) ** 2) * 10000
                
                ck1, ck2 = st.columns(2)
                with ck1:
                    st.markdown(render_kpi_card("Total Emigrant Stock Abroad", f"{tot_emig:,.0f}", f"Born in {conc_country}", theme_mode), unsafe_allow_html=True)
                with ck2:
                    st.markdown(render_kpi_card("Emigrant Destination HHI", f"{hhi_emig:,.0f}", "Max 10,000 (Monopoly)", theme_mode), unsafe_allow_html=True)

                fig_conc = px.pie(
                    emig_df.head(8),
                    values="migrant_stock",
                    names="dest_display_name",
                    title=f"Emigrant Stock Concentration: Top Destinations for {conc_country} ({conc_year})",
                    template=plotly_tmpl
                )
                fig_conc.update_layout(**get_plotly_layout(theme_mode, f"Emigrant Stock Concentration: Top Destinations for {conc_country} ({conc_year})", height=400))
                st.plotly_chart(fig_conc, use_container_width=True)

        with c_tabs[2]:
            render_section_title("Top 50 Global Corridors Full Table")
            top_c_all = get_top_global_corridors(df_bilat, year=AVAILABLE_YEARS[-1], top_n=50)
            st.dataframe(
                top_c_all.rename(columns={
                    "rank": "Rank", "corridor_label": "Corridor", "origin_display_name": "Origin",
                    "origin_code": "Origin ISO3", "dest_display_name": "Destination", "destination_code": "Dest ISO3",
                    "migrant_stock": "Migrant Stock", "origin_corridor_share_pct": "Origin Emigrant Share %",
                    "dest_corridor_share_pct": "Dest Immigrant Share %"
                }).style.format({
                    "Migrant Stock": "{:,.0f}", "Origin Emigrant Share %": "{:.2f}%", "Dest Immigrant Share %": "{:.2f}%"
                }),
                use_container_width=True,
                height=380
            )
            st.download_button(
                label="📥 Download Top 50 Corridors CSV",
                data=top_c_all.to_csv(index=False).encode("utf-8"),
                file_name=f"top_50_global_corridors_{AVAILABLE_YEARS[-1]}.csv",
                mime="text/csv"
            )

    # =============================================================================
    # PAGE 9: 🌐 COMMUNITIES
    # =============================================================================
    elif page == "🌐 Communities":
        render_section_title("🌐 Migration Stock Network Communities", "Modularity community detection on the weighted migrant-stock network")
        
        render_scientific_alert(
            "<b>Community Detection Principle</b>: Community detection is performed on a derived weighted undirected representation of the bilateral migrant-stock network, where undirected edge weights equal combined bilateral migrant stock ($S_{A \\to B} + S_{B \\to A}$). Communities represent <b>empirical clusters generated from the observed migrant-stock network structure</b> and do not represent geopolitical regions, political blocs, cultural regions, or causal migration systems.",
            theme_mode
        )

        comm_c1, comm_c2 = st.columns([2, 2])
        with comm_c1:
            comm_year = st.selectbox("Community Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="comm_yr")
        with comm_c2:
            comm_edges_cutoff = st.selectbox("Graph Edge Density (Top N Edges)", [50, 100, 200, 300], index=1, key="comm_e")

        G_comm, node_comm_map, df_comm_summary, modularity_score = get_cached_communities(
            year=comm_year,
            min_stock=None,
            top_n_edges=comm_edges_cutoff
        )

        st.markdown(f"**Modularity Score**: `{modularity_score:.4f}` (Values &gt; 0.3 indicate strong community cluster structure)")
        
        fig_comm = create_community_graph_plot(
            G_comm,
            node_comm_map,
            is_dark_mode=is_dark,
            title=f"Detected Migration Network Communities ({comm_year}) — {len(df_comm_summary)} Clusters"
        )
        st.plotly_chart(fig_comm, use_container_width=True)

        render_section_title("📋 Community Clusters Summary")
        st.dataframe(
            df_comm_summary[[
                "community_id", "community_name", "size", "top_anchor_countries"
            ]].rename(columns={
                "community_id": "ID", "community_name": "Cluster Name",
                "size": "Member Count", "top_anchor_countries": "Key Anchor Nations"
            }),
            use_container_width=True,
            height=250
        )

        st.download_button(
            label="📥 Download Community Membership CSV",
            data=pd.DataFrame([
                {"country_code": k, "country_name": CODE_TO_NAME.get(k, k), "community_id": v}
                for k, v in node_comm_map.items()
            ]).to_csv(index=False).encode("utf-8"),
            file_name=f"migration_communities_{comm_year}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 10: 📊 ADVANCED ANALYTICS (PHASE 5)
    # =============================================================================
    elif page == "📊 Advanced Analytics":
        render_section_title("📊 Advanced Migration Analytics", "Statistical concentration indices, growth classifications, socioeconomic correlations, and anomaly detection")

        adv_tabs = st.tabs([
            "🌐 Geographic Concentration (HHI)",
            "📈 Migration Change & Growth",
            "🔬 Socioeconomic Relationships",
            "⚠️ Outlier & Anomaly Detection"
        ])

        # TAB 1: CONCENTRATION
        with adv_tabs[0]:
            render_section_title("Global Destination & Origin Concentration (1990–2020)")
            conc_trend_df = get_cached_concentration_trend()

            hhi_c1, hhi_c2, hhi_c3, hhi_c4 = st.columns(4)
            latest_dest_conc = compute_destination_concentration(df_country, year=AVAILABLE_YEARS[-1])
            latest_orig_conc = compute_origin_concentration(df_bilat, year=AVAILABLE_YEARS[-1])

            with hhi_c1:
                st.markdown(render_kpi_card("Destination HHI (2020)", f"{latest_dest_conc['hhi']:,.0f}", latest_dest_conc["hhi_category"], theme_mode), unsafe_allow_html=True)
            with hhi_c2:
                st.markdown(render_kpi_card("Top 10 Destination Share", f"{latest_dest_conc['top_10_share']:.1f}%", "Hosted by top 10 nations", theme_mode), unsafe_allow_html=True)
            with hhi_c3:
                st.markdown(render_kpi_card("Origin HHI (2020)", f"{latest_orig_conc['origin_hhi']:,.0f}", "Origin diaspora concentration", theme_mode), unsafe_allow_html=True)
            with hhi_c4:
                st.markdown(render_kpi_card("Top 10 Origin Share", f"{latest_orig_conc['top_10_origin_share']:.1f}%", "Originated in top 10 nations", theme_mode), unsafe_allow_html=True)

            # HHI Trend Chart
            fig_hhi = go.Figure()
            fig_hhi.add_trace(go.Scatter(
                x=conc_trend_df["year"], y=conc_trend_df["dest_hhi"],
                mode="lines+markers", name="Destination HHI",
                line=dict(color=theme_colors["accent_blue"], width=3), marker=dict(size=8)
            ))
            fig_hhi.add_trace(go.Scatter(
                x=conc_trend_df["year"], y=conc_trend_df["orig_hhi"],
                mode="lines+markers", name="Origin HHI",
                line=dict(color=theme_colors["accent_amber"], width=3), marker=dict(size=8)
            ))
            fig_hhi.add_hline(y=1000, line_dash="dash", line_color="gray", annotation_text="Unconcentrated (< 1,000)")
            fig_hhi.add_hline(y=1800, line_dash="dash", line_color="orange", annotation_text="Moderately Concentrated (1,000–1,800)")
            fig_hhi.update_layout(**get_plotly_layout(theme_mode, "Herfindahl-Hirschman Index (HHI) Evolution (1990–2020)", height=420))
            st.plotly_chart(fig_hhi, use_container_width=True)

            # Top Shares Trend
            fig_shares = px.line(
                conc_trend_df,
                x="year",
                y=["dest_top_5_share", "dest_top_10_share", "dest_top_25_share"],
                markers=True,
                title="Top 5, Top 10, and Top 25 Destination Shares of Global Migrant Stock (%)",
                labels={"year": "Census Year", "value": "Share of Global Migrant Stock (%)", "variable": "Metric Tier"},
                template=plotly_tmpl
            )
            fig_shares.update_layout(**get_plotly_layout(theme_mode, "Top Destination Shares of Global Migrant Stock (%)", height=380))
            st.plotly_chart(fig_shares, use_container_width=True)

            st.download_button(
                label="📥 Download Concentration Trends CSV",
                data=conc_trend_df.to_csv(index=False).encode("utf-8"),
                file_name="migration_concentration_trends_1990_2020.csv",
                mime="text/csv"
            )

        # TAB 2: MIGRATION CHANGE
        with adv_tabs[1]:
            render_section_title("5-Year Intercensal Growth & Change Classifications")
            
            chg_year = st.selectbox("Select Target Census Round", AVAILABLE_YEARS[1:], index=len(AVAILABLE_YEARS)-2, key="chg_year")
            df_classified = classify_stock_changes(df_country, year=chg_year)
            top_changes = get_top_growth_and_declining_countries(df_country, year=chg_year, top_n=10)

            # Classification Breakdown Chart
            cat_counts = df_classified["change_category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig_cat = px.bar(
                cat_counts,
                x="Category", y="Count",
                title=f"Country Distribution by 5-Year Growth Category ({chg_year - 5} → {chg_year})",
                template=plotly_tmpl
            )
            fig_cat.update_layout(**get_plotly_layout(theme_mode, f"Growth Category Distribution ({chg_year - 5} → {chg_year})", height=360))
            fig_cat.update_traces(marker_color=theme_colors["accent_blue"])
            st.plotly_chart(fig_cat, use_container_width=True)

            # Fastest Growth & Largest Absolute Adjustments
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                render_section_title(f"Fastest Percentage Growth (≥ 10k stock)")
                st.dataframe(
                    top_changes["fastest_growth_pct"][["display_name", "country_code", "migrant_stock", "stock_growth_pct_5yr"]].rename(columns={
                        "display_name": "Country", "country_code": "ISO3", "migrant_stock": "Migrant Stock", "stock_growth_pct_5yr": "5-Yr Growth %"
                    }).style.format({
                        "Migrant Stock": "{:,.0f}", "5-Yr Growth %": "{:+.1f}%"
                    }),
                    use_container_width=True,
                    height=280
                )
            with g_col2:
                render_section_title(f"Largest Absolute Stock Increases")
                st.dataframe(
                    top_changes["largest_increase_abs"][["display_name", "country_code", "stock_change_5yr", "migrant_stock"]].rename(columns={
                        "display_name": "Country", "country_code": "ISO3", "stock_change_5yr": "5-Yr Net Increase", "migrant_stock": "Migrant Stock"
                    }).style.format({
                        "5-Yr Net Increase": "{:+,.0f}", "Migrant Stock": "{:,.0f}"
                    }),
                    use_container_width=True,
                    height=280
                )

            st.download_button(
                label="📥 Download Growth Classification CSV",
                data=df_classified.to_csv(index=False).encode("utf-8"),
                file_name=f"migration_change_classification_{chg_year}.csv",
                mime="text/csv"
            )

        # TAB 3: SOCIOECONOMIC RELATIONSHIPS
        with adv_tabs[2]:
            render_section_title("Socioeconomic Bivariate Relationship Engine", "Observational correlations between macroeconomic context and migrant stock")

            render_warning_callout(
                "<b>Correlation ≠ Causation Advisory</b>: Empirical associations between World Bank economic indicators (e.g. GDP per capita, unemployment) and migrant stock describe macroeconomic context and do NOT establish causal mechanisms or individual behavioral drivers.",
                theme_mode
            )

            s_col1, s_col2, s_col3, s_col4 = st.columns([2, 2, 2, 2])
            with s_col1:
                soc_year = st.selectbox("Select Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="soc_year")
            with s_col2:
                x_axis_choice = st.selectbox(
                    "X-Axis Indicator",
                    ["GDP per Capita", "Total GDP", "Total Population", "Unemployment Rate"],
                    index=0,
                    key="x_axis_choice"
                )
            with s_col3:
                y_axis_choice = st.selectbox(
                    "Y-Axis Indicator",
                    ["Migrant Stock % of Population", "Total Migrant Stock"],
                    index=0,
                    key="y_axis_choice"
                )
            with s_col4:
                use_log_x = st.checkbox("Log10 X-Axis", value=True, key="log_x")
                use_log_y = st.checkbox("Log10 Y-Axis", value=False, key="log_y")

            col_map = {
                "GDP per Capita": "gdp_per_capita", "Total GDP": "gdp", "Total Population": "population",
                "Unemployment Rate": "unemployment", "Migrant Stock % of Population": "migrant_stock_pct_population",
                "Total Migrant Stock": "migrant_stock"
            }

            x_col = col_map[x_axis_choice]
            y_col = col_map[y_axis_choice]

            scatter_df, stats_dict = get_bivariate_scatter_data(
                df_country, x_metric_col=x_col, y_metric_col=y_col, year=soc_year,
                log_scale_x=use_log_x, log_scale_y=use_log_y
            )

            # Correlation Summary Table
            _, df_metrics_soc = get_cached_network_and_metrics(soc_year, min_stock=None, top_n_edges=None)
            corr_df = compute_socioeconomic_correlations(df_country, year=soc_year, df_net_metrics=df_metrics_soc)
            
            st.dataframe(
                corr_df[[
                    "pair_name", "sample_size", "spearman_rho", "spearman_p_value",
                    "pearson_r", "pearson_p_value", "relationship_strength", "statistical_significance"
                ]].rename(columns={
                    "pair_name": "Indicator Pair", "sample_size": "N", "spearman_rho": "Spearman ρ",
                    "spearman_p_value": "Spearman p", "pearson_r": "Pearson r", "pearson_p_value": "Pearson p",
                    "relationship_strength": "Empirical Strength", "statistical_significance": "Significance"
                }).style.format({
                    "Spearman ρ": "{:+.3f}", "Spearman p": "{:.4g}", "Pearson r": "{:+.3f}", "Pearson p": "{:.4g}"
                }),
                use_container_width=True,
                height=220
            )

            if not scatter_df.empty:
                fig_scatter = px.scatter(
                    scatter_df,
                    x="plot_x",
                    y="plot_y",
                    hover_name="display_name",
                    hover_data={"country_code": True, "migrant_stock": ":,.0f", "population": ":,.0f", "gdp_per_capita": ":$,.0f"},
                    title=f"Bivariate Relationship: {x_axis_choice} vs. {y_axis_choice} ({soc_year}) [N={stats_dict.get('n', 0)}]",
                    labels={"plot_x": f"{x_axis_choice} {'(Log10)' if use_log_x else ''}", "plot_y": f"{y_axis_choice} {'(Log10)' if use_log_y else ''}"},
                    template=plotly_tmpl
                )
                
                # Add regression line
                if "slope" in stats_dict and pd.notna(stats_dict["slope"]):
                    x_line = np.linspace(scatter_df["plot_x"].min(), scatter_df["plot_x"].max(), 50)
                    y_line = stats_dict["slope"] * x_line + stats_dict["intercept"]
                    fig_scatter.add_trace(go.Scatter(
                        x=x_line, y=y_line, mode="lines",
                        name=f"OLS Fit (ρ = {stats_dict.get('spearman_rho', 0):+.2f})",
                        line=dict(color=theme_colors["accent_blue"], width=2, dash="dash")
                    ))
                    
                fig_scatter.update_layout(**get_plotly_layout(theme_mode, f"{x_axis_choice} vs. {y_axis_choice} ({soc_year})", height=480))
                fig_scatter.update_traces(marker=dict(size=9, opacity=0.8, line=dict(width=1, color=theme_colors["card_border"])))
                st.plotly_chart(fig_scatter, use_container_width=True)

                st.download_button(
                    label="📥 Download Scatter Data CSV",
                    data=scatter_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"bivariate_scatter_{x_col}_{y_col}_{soc_year}.csv",
                    mime="text/csv"
                )

        # TAB 4: ANOMALY DETECTION
        with adv_tabs[3]:
            render_section_title("Statistical Outlier & Anomaly Identification", "Detection of unusual distribution patterns across migrant stock and demographic shares")
            
            anom_c1, anom_c2, anom_c3 = st.columns([2, 2, 2])
            with anom_c1:
                anom_year = st.selectbox("Census Observation Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="anom_year")
            with anom_c2:
                anom_metric_choice = st.selectbox(
                    "Target Metric",
                    ["Migrant Stock % of Population", "Total Migrant Stock", "5-Year Stock Growth (%)"],
                    index=0,
                    key="anom_metric"
                )
            with anom_c3:
                anom_method = st.selectbox("Detection Method", ["IQR", "Z-Score"], index=0, key="anom_method")

            target_metric_col = "migrant_stock_pct_population" if "Population" in anom_metric_choice else ("migrant_stock" if "Total" in anom_metric_choice else "stock_growth_pct_5yr")
            threshold_val = 1.5 if anom_method == "IQR" else 2.5
            
            outliers_df, dist_summary = detect_migration_anomalies(
                df_country, metric_col=target_metric_col, year=anom_year, method=anom_method, threshold=threshold_val
            )

            # Summary metrics
            as1, as2, as3, as4 = st.columns(4)
            with as1:
                st.markdown(render_kpi_card("Method", f"{dist_summary.get('method', 'N/A')}", f"Threshold: {threshold_val}", theme_mode), unsafe_allow_html=True)
            with as2:
                st.markdown(render_kpi_card("Lower Bound", f"{dist_summary.get('lower_bound', 0):,.2f}", "Normal range floor", theme_mode), unsafe_allow_html=True)
            with as3:
                st.markdown(render_kpi_card("Upper Bound", f"{dist_summary.get('upper_bound', 0):,.2f}", "Normal range ceiling", theme_mode), unsafe_allow_html=True)
            with as4:
                st.markdown(render_kpi_card("Detected Anomalies", f"{len(outliers_df)}", f"Nations beyond threshold", theme_mode), unsafe_allow_html=True)

            render_scientific_alert(
                f"<b>Analytical Interpretation</b>: {len(outliers_df)} observations exceed the {anom_method} statistical threshold for <i>{anom_metric_choice}</i> in {anom_year}. In demographic analysis, anomalies frequently represent specialized demographic contexts (e.g. Gulf Cooperation Council labor-importing states, microstates, or sudden humanitarian refugee host nations) rather than reporting errors.",
                theme_mode
            )

            if not outliers_df.empty:
                st.dataframe(
                    outliers_df[[
                        "display_name", "country_code", target_metric_col, "outlier_type", "population", "gdp_per_capita"
                    ]].rename(columns={
                        "display_name": "Country", "country_code": "ISO3", target_metric_col: anom_metric_choice,
                        "outlier_type": "Anomaly Classification", "population": "Population", "gdp_per_capita": "GDP per Capita"
                    }).style.format({
                        anom_metric_choice: "{:,.2f}%" if "%" in anom_metric_choice else "{:,.0f}",
                        "Population": "{:,.0f}",
                        "GDP per Capita": "${:,.0f}"
                    }),
                    use_container_width=True,
                    height=300
                )
                st.download_button(
                    label="📥 Download Detected Outliers CSV",
                    data=outliers_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"migration_outliers_{target_metric_col}_{anom_year}.csv",
                    mime="text/csv"
                )

    # =============================================================================
    # PAGE 11: ⚖️ COUNTRY COMPARISON (PHASE 5)
    # =============================================================================
    elif page == "⚖️ Country Comparison":
        render_section_title("⚖️ Multi-Country Comparative Profiler", "Cross-national comparative analysis across demographic, economic, and network dimensions")

        cmp_c1, cmp_c2 = st.columns([3, 2])
        with cmp_c1:
            default_countries = ["United States of America", "Germany", "India", "United Arab Emirates"]
            valid_defaults = [c for c in default_countries if c in COUNTRY_DICT]
            comp_selected_names = st.multiselect(
                "Select 2 to 5 Countries for Comparative Profiling",
                list(COUNTRY_DICT.keys()),
                default=valid_defaults if len(valid_defaults) >= 2 else list(COUNTRY_DICT.keys())[:3],
                max_selections=5,
                key="comp_countries"
            )
        with cmp_c2:
            comp_year = st.selectbox("Census Observation Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="comp_year")

        if len(comp_selected_names) >= 2:
            comp_codes = [COUNTRY_DICT[c] for c in comp_selected_names if c in COUNTRY_DICT]
            _, df_metrics_comp = get_cached_network_and_metrics(comp_year, min_stock=None, top_n_edges=None)

            abs_df, norm_df = compute_multicountry_comparison(
                df_country, country_codes=comp_codes, year=comp_year, df_net_metrics=df_metrics_comp
            )

            # Absolute Values Table
            render_section_title("1. Absolute Indicator Comparison Matrix")
            st.dataframe(
                abs_df.rename(columns={"country_name": "Country", "country_code": "ISO3"}).style.format({
                    "Total Migrant Stock (People)": "{:,.0f}",
                    "Migrant Stock % of Population": "{:.2f}%",
                    "5-Year Stock Growth (%)": "{:+.1f}%",
                    "GDP per Capita (USD)": "${:,.0f}",
                    "Total Population": "{:,.0f}",
                    "Unemployment Rate (%)": "{:.2f}%",
                    "Network Weighted Strength": "{:,.0f}",
                    "Network Degree Centrality": "{:,.0f}",
                    "PageRank Score": "{:.4f}"
                }),
                use_container_width=True
            )

            # Normalized Relative Score Chart
            render_section_title("2. Normalized Relative Comparison Scores [0–100]")
            render_warning_callout(
                "<b>Normalized Scoring Methodology</b>: Scores represent min-max relative normalization across all global sovereign entities for that census year ($0 = \\text{global minimum}, 100 = \\text{global maximum}$). These values are comparative scores and do not represent original units.",
                theme_mode
            )

            norm_melted = norm_df.melt(id_vars=["country_name", "country_code"], var_name="Indicator", value_name="Normalized Score")
            fig_norm = px.bar(
                norm_melted,
                x="Indicator",
                y="Normalized Score",
                color="country_name",
                barmode="group",
                title=f"Normalized Multi-Country Comparison ({comp_year})",
                labels={"Normalized Score": "Relative Scale [0–100]", "country_name": "Country"},
                template=plotly_tmpl
            )
            fig_norm.update_layout(**get_plotly_layout(theme_mode, f"Normalized Relative Profile ({comp_year})", height=420))
            st.plotly_chart(fig_norm, use_container_width=True)

            # Historical Multi-Line Trajectory
            render_section_title("3. Historical Longitudinal Trajectories (1990–2020)")
            comp_hist_metric = st.selectbox(
                "Select Trajectory Metric",
                ["Migrant Stock", "Migrant Stock % of Population", "GDP per Capita", "Population", "5-Year Stock Growth %"],
                index=0,
                key="comp_hist_m"
            )
            comp_traj_df = get_country_trend_data(df_country, country_codes=comp_codes, metric_name=comp_hist_metric)

            if not comp_traj_df.empty:
                metric_lbl = comp_traj_df["metric_label"].iloc[0] if "metric_label" in comp_traj_df.columns else comp_hist_metric
                fig_comp_traj = px.line(
                    comp_traj_df,
                    x="year",
                    y="metric_value",
                    color="display_name",
                    markers=True,
                    title=f"Comparative Trajectory: {comp_hist_metric} (1990–2020)",
                    labels={"year": "Census Year", "metric_value": metric_lbl, "display_name": "Country"},
                    template=plotly_tmpl
                )
                fig_comp_traj.update_layout(**get_plotly_layout(theme_mode, f"Comparative Trajectory: {comp_hist_metric}", height=400))
                st.plotly_chart(fig_comp_traj, use_container_width=True)

            st.download_button(
                label="📥 Download Country Comparison CSV",
                data=abs_df.to_csv(index=False).encode("utf-8"),
                file_name=f"country_comparison_{comp_year}.csv",
                mime="text/csv"
            )
        else:
            st.info("Please select at least 2 countries to generate comparative analytics.")

    # =============================================================================
    # PAGE 12: 💡 MIGRATION INSIGHTS (PHASE 5)
    # =============================================================================
    elif page == "💡 Migration Insights":
        render_section_title("💡 Automated Migration Data Storytelling", "Deterministic, data-driven analytical insights derived directly from UN DESA & World Bank datasets")

        ins_c1, ins_c2 = st.columns([2, 2])
        with ins_c1:
            ins_year = st.selectbox("Select Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="ins_year")
        with ins_c2:
            ins_cat_filter = st.selectbox(
                "Filter Insight Category",
                ["All Categories", "Global Trend", "Concentration", "Fastest Growth", "Largest Changes", "Major Corridors", "Socioeconomic Associations", "Network Structure"],
                index=0,
                key="ins_cat"
            )

        _, df_metrics_ins = get_cached_network_and_metrics(ins_year, min_stock=None, top_n_edges=None)
        insights = generate_all_insights(df_country, df_bilat, year=ins_year, df_net_metrics=df_metrics_ins)

        if ins_cat_filter != "All Categories":
            insights = [i for i in insights if i["category"] == ins_cat_filter]

        render_scientific_alert(
            "<b>Deterministic Generation Principle</b>: All narrative insights are generated deterministically from underlying calculations across the verified UN DESA and World Bank datasets. No statistical mechanisms or causal relationships are fabricated.",
            theme_mode
        )

        for ins in insights:
            render_insight_card(
                category=ins["category"],
                title=ins["title"],
                message=ins["message"],
                badge_text=ins.get("badge", None),
                theme_mode=theme_mode
            )

        # Tabular View & Download
        render_section_title("Summary Table of Generated Insights")
        insights_df = pd.DataFrame(insights)
        if not insights_df.empty:
            st.dataframe(
                insights_df[["category", "title", "message", "badge"]].rename(columns={
                    "category": "Category", "title": "Headline", "message": "Analytical Summary", "badge": "Key Metric"
                }),
                use_container_width=True,
                height=260
            )
            st.download_button(
                label="📥 Download Generated Insights CSV",
                data=insights_df.to_csv(index=False).encode("utf-8"),
                file_name=f"migration_insights_{ins_year}.csv",
                mime="text/csv"
            )

    # =============================================================================
    # PAGE 13: ℹ️ METHODOLOGY
    # =============================================================================
    elif page == "ℹ️ Methodology":
        render_section_title("ℹ️ Data Sources, Methodological Standards & Limitations")
        
        st.markdown("""
        #### 1. Authoritative Data Sources
        - **UN DESA International Migrant Stock (2020 Revision)**:
          - Published by the United Nations Department of Economic and Social Affairs (Population Division).
          - Mid-year estimates across 7 quinquennial census rounds: **1990, 1995, 2000, 2005, 2010, 2015, 2020**.
          - Based on official national censuses, population registers, and nationally representative surveys.
        - **World Bank World Development Indicators (WDI)**:
          - Midyear Total Population (`SP.POP.TOTL`)
          - Current GDP in USD (`NY.GDP.MKTP.CD`)
          - GDP per Capita in USD (`NY.GDP.PCAP.CD`)
          - Total Unemployment (% of total labor force, ILO modeled) (`SL.UEM.TOTL.ZS`)

        ---

        #### 2. Fundamental Scientific Distinction: Migrant Stock vs. Migration Flow
        
        | Dimension | International Migrant Stock (This Platform) | Annual Migration Flow |
        | :--- | :--- | :--- |
        | **Concept** | Estimated total number of foreign-born individuals residing in a destination country at mid-year. | Number of individuals crossing national borders during a specific period. |
        | **Measurement** | Cumulative census snapshot at time $t$. | Rate of flow (moves / entries per calendar year). |
        | **Components of Change** | Reflects net immigration, mortality among migrants, return migration, naturalizations, and boundary changes. | Gross border admissions / departures only. |
        | **Time Granularity** | Quinquennial rounds (1990, 1995, 2000, 2005, 2010, 2015, 2020). | Annual or monthly border registry counts. |

        > [!IMPORTANT]
        > **5-Year Stock Differences $\\neq$ Migration Flows**: The difference in migrant stock between two census rounds represents the **net intercensal stock change**, not the total number of people who migrated during that 5-year window.

        ---

        #### 3. Network Metrics & Mathematical Formulations
        1. **In-Degree & Out-Degree**:
           - $\\text{In-Degree}(v) = |\\{u \\mid (u, v) \\in E\\}|$ (Count of origin countries sending migrants to $v$)
           - $\\text{Out-Degree}(u) = |\\{v \\mid (u, v) \\in E\\}|$ (Count of destination countries hosting migrants from $u$)
        2. **Weighted Strength**:
           - $\\text{In-Strength}(v) = \\sum_{u} W(u, v)$ (Total foreign-born stock residing in $v$)
           - $\\text{Out-Strength}(u) = \\sum_{v} W(u, v)$ (Total diaspora/emigrant stock living abroad from $u$)
        3. **Betweenness Centrality**:
           - $C_B(v) = \\sum_{s \\neq v \\neq t} \\frac{\\sigma_{st}(v)}{\\sigma_{st}}$ (Frequency with which country $v$ sits on shortest network paths)
        4. **Bidirectional Asymmetry Index**:
           - $\\text{Asymmetry Index}_{A \\leftrightarrow B} = \\frac{S_{A \\to B} - S_{B \\to A}}{S_{A \\to B} + S_{B \\to A}} \\in [-1, 1]$
        5. **Community Detection (Modularity)**:
           - $Q = \\frac{1}{2m} \\sum_{i,j} \\left[ A_{ij} - \\frac{k_i k_j}{2m} \\right] \\delta(c_i, c_j)$

        ---

        #### 4. Advanced Analytics & Statistical Formulations
        1. **Herfindahl-Hirschman Index (HHI)**:
           - $\\text{HHI} = \\sum_{i=1}^{N} s_i^2$, where $s_i = \\left( \\frac{S_i}{S_{\\text{total}}} \\right) \\times 100$.
           - Benchmarks: $\\text{HHI} < 1000$ (Unconcentrated), $1000 \\le \\text{HHI} \\le 1800$ (Moderately Concentrated), $\\text{HHI} > 1800$ (Highly Concentrated).
        2. **Bivariate Correlation (Pearson & Spearman)**:
           - Pearson: $r = \\frac{\\sum (x_i - \\bar{x})(y_i - \\bar{y})}{\\sqrt{\\sum (x_i - \\bar{x})^2 \\sum (y_i - \\bar{y})^2}}$ (Linear association)
           - Spearman: $\\rho = 1 - \\frac{6 \\sum d_i^2}{n(n^2 - 1)}$ (Monotonic rank association)
           - **Correlation $\\neq$ Causation**: Observational cross-sectional macroeconomic correlations do not establish causal mechanisms.
        3. **Statistical Outlier Detection (IQR & Z-Score)**:
           - $\\text{IQR} = Q_3 - Q_1$, Outliers beyond $[Q_1 - k \\cdot \\text{IQR}, Q_3 + k \\cdot \\text{IQR}]$.
           - $Z = \\frac{x - \\mu}{\\sigma}$, Outliers where $|Z| > \\text{threshold}$.
        4. **Min-Max Normalization**:
           - $x_{\\text{norm}} = \\frac{x - x_{\\text{min}}}{x_{\\text{max}} - x_{\\text{min}}} \\times 100 \\in [0, 100]$.
        """)
