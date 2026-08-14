"""
Global Migration Observatory — Phase 3 UI Polish
A professional, empirical data dashboard integrating UN DESA 2020 International Migrant Stock
and World Bank WDI indicators with NetworkX network analytics, community detection,
geographic corridor maps, centrality rankings, and universal Light/Dark theming.
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
    render_kpi_card,
    render_masthead,
    render_scientific_alert,
    render_section_title,
    render_sidebar_header,
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

    # Grouped Navigation
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
        "ℹ️ Methodology",
        "⚙️ Settings",
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
            st.markdown(render_kpi_card("Total Migrant Stock", f"{kpis['total_migrant_stock']:,.0f}", f"Sovereign totals in {selected_year}", theme_mode), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Countries & Areas", f"{kpis['num_countries']}", "Sovereign entities tracked", theme_mode), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Top Destination", kpis['top_destination_name'], f"{kpis['top_destination_stock']:,.0f} foreign-born", theme_mode), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi_card("Top Share of Pop.", kpis['top_share_name'], f"{kpis['top_share_pct']:.1f}% of national pop.", theme_mode), unsafe_allow_html=True)
        with k5:
            st.markdown(render_kpi_card("Active Corridors", f"{kpis['num_corridors']:,}", "Origin-Destination pairs > 0", theme_mode), unsafe_allow_html=True)

        render_scientific_alert(
            "<b>Scientific Principle</b>: <b>Migrant stock</b> represents the estimated cumulative count of foreign-born individuals living in a destination country at mid-year. It is <b>NOT</b> an annual flow rate. Intercensal differences between 5-year rounds reflect net cumulative changes including births, deaths, naturalizations, return migration, and boundary adjustments.",
            theme_mode
        )

        # Overview Visualizations
        c_left, c_right = st.columns(2)
        
        with c_left:
            render_section_title("Global Migrant Stock Trajectory", "1990–2020 longitudinal aggregate")
            df_gt = get_global_trend_data(df_country)
            fig_gt = px.line(
                df_gt,
                x="year",
                y="total_migrant_stock",
                markers=True,
                labels={"year": "Census Round", "total_migrant_stock": "Total Migrant Stock (People)"},
                template=plotly_tmpl
            )
            fig_gt.update_traces(line=dict(color=theme_colors["accent_blue"], width=3), marker=dict(size=8))
            fig_gt.update_layout(**get_plotly_layout(theme_mode, "", height=350))
            st.plotly_chart(fig_gt, use_container_width=True)

        with c_right:
            render_section_title(f"Top 10 Destinations by Migrant Stock", f"Census Round {selected_year}")
            top10_dest = get_rankings_data(df_country, year=selected_year, metric_name="Migrant Stock", top_n=10)
            fig_top10 = px.bar(
                top10_dest,
                x="migrant_stock",
                y="display_name",
                orientation="h",
                color="migrant_stock_pct_population",
                color_continuous_scale="Blues",
                labels={
                    "migrant_stock": "Migrant Stock",
                    "display_name": "Country",
                    "migrant_stock_pct_population": "Stock % Pop."
                },
                template=plotly_tmpl
            )
            fig_top10.update_layout(**get_plotly_layout(theme_mode, "", height=350))
            fig_top10.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_top10, use_container_width=True)

        # Underlying Data Table & Download
        render_section_title(f"📋 Summary Data Table ({selected_year})", "Filterable sovereign dataset")
        overview_table = df_country[
            (df_country["year"] == selected_year) & (~df_country["is_aggregate"])
        ][[
            "display_name", "country_code", "year", "migrant_stock",
            "population", "migrant_stock_pct_population", "stock_change_5yr",
            "stock_growth_pct_5yr", "gdp_per_capita", "migrant_stock_global_rank"
        ]].sort_values("migrant_stock", ascending=False).rename(columns={
            "display_name": "Country",
            "country_code": "ISO3",
            "year": "Year",
            "migrant_stock": "Migrant Stock",
            "population": "Population",
            "migrant_stock_pct_population": "Stock % of Pop",
            "stock_change_5yr": "5-Yr Stock Change",
            "stock_growth_pct_5yr": "5-Yr Stock Growth %",
            "gdp_per_capita": "GDP per Capita (USD)",
            "migrant_stock_global_rank": "Global Rank"
        })
        
        st.dataframe(
            overview_table.style.format({
                "Migrant Stock": "{:,.0f}",
                "Population": "{:,.0f}",
                "Stock % of Pop": "{:.2f}%",
                "5-Yr Stock Change": "{:+,.0f}",
                "5-Yr Stock Growth %": "{:+.2f}%",
                "GDP per Capita (USD)": "${:,.0f}",
                "Global Rank": "{:.0f}"
            }, na_rep="—"),
            use_container_width=True,
            height=320
        )
        
        st.download_button(
            label=f"📥 Download Overview Data ({selected_year}) as CSV",
            data=overview_table.to_csv(index=False).encode("utf-8"),
            file_name=f"migration_overview_{selected_year}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 2: 🌍 GLOBAL MAP
    # =============================================================================
    elif page == "🌍 Global Map":
        render_section_title("🌍 Global Migrant Stock Choropleth Map", "Spatial distribution of migrant stock and demographic shares")
        
        m_c1, m_c2 = st.columns([3, 2])
        with m_c1:
            selected_metric = st.selectbox(
                "Select Map Metric",
                list(METRIC_COLUMN_MAP.keys()),
                index=0,
                key="map_metric"
            )
        with m_c2:
            selected_year = st.selectbox(
                "Select Census Year",
                AVAILABLE_YEARS,
                index=len(AVAILABLE_YEARS) - 1,
                key="map_year"
            )

        if selected_year == 1990 and ("Change" in selected_metric or "Growth" in selected_metric):
            st.info("ℹ️ **Baseline Year Notice**: 5-year intercensal stock change and growth rate are calculated relative to the previous 5-year round (available for 1995–2020). For the 1990 baseline round, please select **Migrant Stock** or **Migrant Stock % of Population**.")

        map_df = get_map_data(df_country, year=selected_year, metric_name=selected_metric)
        
        # Color Scale Customization based on metric
        if "Growth" in selected_metric or "Change" in selected_metric:
            color_scale = "Tealrose"
            midpoint = 0.0
        elif "% of Population" in selected_metric:
            color_scale = "Viridis"
            midpoint = None
        else:
            color_scale = "Blues"
            midpoint = None

        fig_map = px.choropleth(
            map_df,
            locations="country_code",
            color="metric_value",
            hover_name="display_name",
            hover_data={
                "country_code": True,
                "year": True,
                "metric_value": ":,.2f" if "%" in selected_metric else ":,.0f",
                "migrant_stock": ":,.0f",
                "population": ":,.0f",
                "migrant_stock_pct_population": ":.2f",
                "migrant_stock_global_rank": ":.0f"
            },
            color_continuous_scale=color_scale,
            color_continuous_midpoint=midpoint,
            labels={
                "metric_value": selected_metric,
                "country_code": "ISO3 Code",
                "year": "Year",
                "migrant_stock": "Total Migrant Stock",
                "population": "Population",
                "migrant_stock_pct_population": "Stock % of Pop",
                "migrant_stock_global_rank": "Global Rank"
            },
            title=f"Global {selected_metric} by Country ({selected_year})",
            template=plotly_tmpl
        )
        
        fig_map.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor=theme_colors["map_coastline"],
                landcolor=theme_colors["map_land"],
                oceancolor=theme_colors["map_ocean"],
                showocean=True,
                projection_type="natural earth"
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=540,
            font=dict(family="'Inter', sans-serif")
        )
        
        st.plotly_chart(fig_map, use_container_width=True)

        render_section_title(f"📋 Country-Level Map Data ({selected_year})")
        display_map_df = map_df[[
            "display_name", "country_code", "year", "metric_value",
            "migrant_stock", "population", "migrant_stock_pct_population",
            "stock_change_5yr", "stock_growth_pct_5yr", "migrant_stock_global_rank"
        ]].sort_values("metric_value", ascending=False).rename(columns={
            "display_name": "Country",
            "country_code": "ISO3",
            "year": "Year",
            "metric_value": f"Selected Metric ({selected_metric})",
            "migrant_stock": "Migrant Stock",
            "population": "Population",
            "migrant_stock_pct_population": "Stock % Pop",
            "stock_change_5yr": "5-Yr Stock Change",
            "stock_growth_pct_5yr": "5-Yr Stock Growth %",
            "migrant_stock_global_rank": "Global Rank"
        })

        st.dataframe(
            display_map_df.style.format({
                f"Selected Metric ({selected_metric})": "{:,.2f}" if "%" in selected_metric else "{:,.0f}",
                "Migrant Stock": "{:,.0f}",
                "Population": "{:,.0f}",
                "Stock % Pop": "{:.2f}%",
                "5-Yr Stock Change": "{:+,.0f}",
                "5-Yr Stock Growth %": "{:+.2f}%",
                "Global Rank": "{:.0f}"
            }, na_rep="—"),
            use_container_width=True,
            height=300
        )

        st.download_button(
            label="📥 Download Map Data as CSV",
            data=display_map_df.to_csv(index=False).encode("utf-8"),
            file_name=f"map_data_{selected_metric.lower().replace(' ', '_')}_{selected_year}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 3: 📈 TRENDS
    # =============================================================================
    elif page == "📈 Trends":
        render_section_title("📈 Long-Term Migration Stock Trajectories", "Longitudinal trajectories across 1990–2020 census rounds")
        
        render_scientific_alert(
            "<b>Stock Differences Note</b>: Changes in migrant stock between 5-year census rounds reflect net cumulative demographic changes. They are not annual border-crossing counts.",
            theme_mode
        )
        
        # Visualization 1: Global Aggregate Trend
        render_section_title("1. Global Aggregated Migrant Stock (1990–2020)")
        df_gt = get_global_trend_data(df_country)
        
        fig_gt = go.Figure()
        fig_gt.add_trace(go.Scatter(
            x=df_gt["year"],
            y=df_gt["total_migrant_stock"],
            mode="lines+markers",
            name="Total Global Migrant Stock",
            line=dict(color=theme_colors["accent_blue"], width=3),
            marker=dict(size=8)
        ))
        fig_gt.update_layout(
            **get_plotly_layout(theme_mode, "Global Residing Migrant Stock Across 5-Year UN Census Rounds", height=350)
        )
        st.plotly_chart(fig_gt, use_container_width=True)

        st.markdown("---")
        
        # Visualization 2: Multi-Country Comparison
        render_section_title("2. Multi-Country Trend Comparison")
        
        t_c1, t_c2 = st.columns([3, 2])
        with t_c1:
            default_countries = ["United States of America", "Germany", "India", "Canada", "United Arab Emirates", "United Kingdom"]
            valid_defaults = [c for c in default_countries if c in COUNTRY_DICT]
            selected_country_names = st.multiselect(
                "Select Countries to Compare",
                options=list(COUNTRY_DICT.keys()),
                default=valid_defaults if valid_defaults else list(COUNTRY_DICT.keys())[:5],
                key="trend_countries"
            )
        with t_c2:
            trend_metric = st.selectbox(
                "Comparison Metric",
                list(METRIC_COLUMN_MAP.keys()),
                index=0,
                key="trend_metric"
            )

        if selected_country_names:
            selected_codes = [COUNTRY_DICT[c] for c in selected_country_names]
            trend_df = get_country_trend_data(df_country, country_codes=selected_codes, metric_name=trend_metric)
            
            fig_ct = px.line(
                trend_df,
                x="year",
                y="metric_value",
                color="display_name",
                markers=True,
                labels={
                    "year": "Census Year",
                    "metric_value": trend_metric,
                    "display_name": "Country"
                },
                title=f"Comparative Trajectories: {trend_metric} (1990–2020)",
                template=plotly_tmpl
            )
            fig_ct.update_layout(**get_plotly_layout(theme_mode, f"Comparative Trajectories: {trend_metric} (1990–2020)", height=450))
            st.plotly_chart(fig_ct, use_container_width=True)

            # Data Table
            render_section_title("📋 Comparative Trend Data")
            table_trend = trend_df[[
                "display_name", "country_code", "year", "metric_value",
                "migrant_stock", "population", "migrant_stock_pct_population"
            ]].rename(columns={
                "display_name": "Country",
                "country_code": "ISO3",
                "year": "Year",
                "metric_value": f"Selected Metric ({trend_metric})",
                "migrant_stock": "Migrant Stock",
                "population": "Population",
                "migrant_stock_pct_population": "Stock % of Pop"
            })
            
            st.dataframe(
                table_trend.style.format({
                    f"Selected Metric ({trend_metric})": "{:,.2f}" if "%" in trend_metric else "{:,.0f}",
                    "Migrant Stock": "{:,.0f}",
                    "Population": "{:,.0f}",
                    "Stock % of Pop": "{:.2f}%"
                }, na_rep="—"),
                use_container_width=True,
                height=260
            )

            st.download_button(
                label="📥 Download Trend Data as CSV",
                data=table_trend.to_csv(index=False).encode("utf-8"),
                file_name=f"migration_trends_{trend_metric.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Select at least one country above to display trend comparisons.")

    # =============================================================================
    # PAGE 4: 🏆 RANKINGS
    # =============================================================================
    elif page == "🏆 Rankings":
        render_section_title("🏆 Country Rankings & Distribution", "Quinquennial ranking leaderboards by demographic indicators")
        
        r_c1, r_c2, r_c3, r_c4 = st.columns([3, 2, 2, 2])
        with r_c1:
            rank_metric = st.selectbox(
                "Ranking Metric",
                list(METRIC_COLUMN_MAP.keys()),
                index=0,
                key="rank_metric"
            )
        with r_c2:
            rank_year = st.selectbox(
                "Census Year",
                AVAILABLE_YEARS,
                index=len(AVAILABLE_YEARS) - 1,
                key="rank_year"
            )
        with r_c3:
            rank_top_n = st.selectbox(
                "Top N Entities",
                [10, 25, 50],
                index=0,
                key="rank_top_n"
            )
        with r_c4:
            sort_order = st.radio(
                "Order",
                ["Highest First", "Lowest First"],
                index=0,
                key="rank_order"
            )

        if rank_year == 1990 and ("Change" in rank_metric or "Growth" in rank_metric):
            st.info("ℹ️ **Baseline Year Notice**: 5-year intercensal stock change and growth rate are calculated relative to the previous 5-year round (available for 1995–2020). For the 1990 baseline round, please select **Total Migrant Stock** or **Migrant Stock % of Population**.")

        df_rank = get_rankings_data(
            df_country,
            year=rank_year,
            metric_name=rank_metric,
            top_n=rank_top_n,
            ascending=(sort_order == "Lowest First")
        )

        # Bar chart
        fig_rank = px.bar(
            df_rank,
            x="metric_value",
            y="display_name",
            orientation="h",
            text="metric_value",
            labels={
                "metric_value": rank_metric,
                "display_name": "Country"
            },
            title=f"Top {rank_top_n} Countries by {rank_metric} ({rank_year}) — {sort_order}",
            template=plotly_tmpl,
            color="metric_value",
            color_continuous_scale="Blues" if sort_order == "Highest First" else "Teal"
        )
        
        fmt = "%{text:,.2f}%" if "%" in rank_metric else "%{text:,.0f}"
        fig_rank.update_traces(texttemplate=fmt, textposition="outside")
        fig_rank.update_layout(**get_plotly_layout(theme_mode, f"Top {rank_top_n} Countries by {rank_metric} ({rank_year}) — {sort_order}", height=max(380, len(df_rank) * 26)))
        fig_rank.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_rank, use_container_width=True)

        # Rankings Table
        render_section_title(f"📋 Full Ranking Data Table ({rank_year})")
        display_rank = df_rank[[
            "rank", "display_name", "country_code", "year", "metric_value",
            "migrant_stock", "population", "migrant_stock_pct_population",
            "stock_change_5yr", "stock_growth_pct_5yr", "gdp_per_capita"
        ]].rename(columns={
            "rank": "Rank",
            "display_name": "Country",
            "country_code": "ISO3",
            "year": "Year",
            "metric_value": f"Rank Metric ({rank_metric})",
            "migrant_stock": "Migrant Stock",
            "population": "Population",
            "migrant_stock_pct_population": "Stock % Pop",
            "stock_change_5yr": "5-Yr Stock Change",
            "stock_growth_pct_5yr": "5-Yr Stock Growth %",
            "gdp_per_capita": "GDP per Capita (USD)"
        })

        st.dataframe(
            display_rank.style.format({
                f"Rank Metric ({rank_metric})": "{:,.2f}" if "%" in rank_metric else "{:,.0f}",
                "Migrant Stock": "{:,.0f}",
                "Population": "{:,.0f}",
                "Stock % Pop": "{:.2f}%",
                "5-Yr Stock Change": "{:+,.0f}",
                "5-Yr Stock Growth %": "{:+.2f}%",
                "GDP per Capita (USD)": "${:,.0f}"
            }, na_rep="—"),
            use_container_width=True,
            height=320
        )

        st.download_button(
            label="📥 Download Rankings as CSV",
            data=display_rank.to_csv(index=False).encode("utf-8"),
            file_name=f"rankings_{rank_metric.lower().replace(' ', '_')}_{rank_year}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 5: 🔀 ROUTE EXPLORER
    # =============================================================================
    elif page == "🔀 Route Explorer":
        render_section_title("🔀 Bilateral Migrant Stock Corridor Explorer", "Bilateral corridor stocks and origin/destination shares")
        
        render_scientific_alert(
            "<b>Corridor Stock Definition</b>: A bilateral corridor estimate represents the number of individuals born in the <b>Origin Country</b> residing in the <b>Destination Country</b> at mid-year. Corridor shares reflect the portion of total bilateral migrant stock, <b>not</b> annual flow rates.",
            theme_mode
        )
        
        # Section A: Global Top Corridors
        render_section_title("1. Top Global Bilateral Corridors")
        
        gt_c1, gt_c2 = st.columns([2, 2])
        with gt_c1:
            corridor_year = st.selectbox(
                "Select Corridor Census Year",
                AVAILABLE_YEARS,
                index=len(AVAILABLE_YEARS) - 1,
                key="corridor_year"
            )
        with gt_c2:
            top_corridor_n = st.selectbox(
                "Top N Global Corridors",
                [10, 25, 50],
                index=0,
                key="top_corridor_n"
            )

        top_corridors_df = get_top_global_corridors(df_bilat, year=corridor_year, top_n=top_corridor_n)
        
        fig_corridors = px.bar(
            top_corridors_df,
            x="migrant_stock",
            y="corridor_label",
            orientation="h",
            text="migrant_stock",
            labels={
                "migrant_stock": "Migrant Stock (People)",
                "corridor_label": "Bilateral Corridor (Origin → Destination)"
            },
            title=f"Top {top_corridor_n} Global Bilateral Corridors ({corridor_year})",
            template=plotly_tmpl,
            color="migrant_stock",
            color_continuous_scale="Blues"
        )
        fig_corridors.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_corridors.update_layout(**get_plotly_layout(theme_mode, f"Top {top_corridor_n} Global Bilateral Corridors ({corridor_year})", height=max(360, len(top_corridors_df) * 28)))
        fig_corridors.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_corridors, use_container_width=True)

        st.markdown("---")
        
        # Section B: Interactive Corridor Query
        render_section_title("2. Search & Filter Bilateral Corridors")
        
        f_c1, f_c2, f_c3 = st.columns([3, 3, 2])
        with f_c1:
            orig_selection = st.selectbox(
                "Origin Country (Emigrants)",
                ["All"] + list(COUNTRY_DICT.keys()),
                index=0,
                key="route_orig"
            )
        with f_c2:
            dest_selection = st.selectbox(
                "Destination Country (Immigrants)",
                ["All"] + list(COUNTRY_DICT.keys()),
                index=0,
                key="route_dest"
            )
        with f_c3:
            custom_top_n = st.selectbox(
                "Max Corridors Displayed",
                [10, 20, 50, 100],
                index=1,
                key="route_top_n"
            )

        orig_code = COUNTRY_DICT.get(orig_selection) if orig_selection != "All" else None
        dest_code = COUNTRY_DICT.get(dest_selection) if dest_selection != "All" else None

        filtered_routes = get_filtered_corridors(
            df_bilat,
            year=corridor_year,
            origin_code=orig_code,
            dest_code=dest_code,
            top_n=custom_top_n
        )

        if not filtered_routes.empty:
            if orig_code and dest_code:
                single_r = filtered_routes.iloc[0]
                rk1, rk2, rk3 = st.columns(3)
                with rk1:
                    st.markdown(render_kpi_card("Corridor Migrant Stock", f"{single_r['migrant_stock']:,.0f}", f"{single_r['corridor_label']} ({corridor_year})", theme_mode), unsafe_allow_html=True)
                with rk2:
                    st.markdown(render_kpi_card("Origin Emigrant Share", f"{single_r['origin_corridor_share_pct']:.2f}%", f"Share of {orig_selection}'s emigrants", theme_mode), unsafe_allow_html=True)
                with rk3:
                    st.markdown(render_kpi_card("Dest. Immigrant Share", f"{single_r['dest_corridor_share_pct']:.2f}%", f"Share of {dest_selection}'s immigrants", theme_mode), unsafe_allow_html=True)

            render_section_title(f"📋 Matching Corridors ({corridor_year})")
            display_routes = filtered_routes[[
                "rank", "corridor_label", "origin_display_name", "origin_code",
                "dest_display_name", "destination_code", "year", "migrant_stock",
                "origin_corridor_share_pct", "dest_corridor_share_pct"
            ]].rename(columns={
                "rank": "Rank",
                "corridor_label": "Bilateral Corridor",
                "origin_display_name": "Origin",
                "origin_code": "Origin ISO3",
                "dest_display_name": "Destination",
                "destination_code": "Dest ISO3",
                "year": "Year",
                "migrant_stock": "Migrant Stock",
                "origin_corridor_share_pct": "Origin Emigrant Share %",
                "dest_corridor_share_pct": "Dest Immigrant Share %"
            })

            st.dataframe(
                display_routes.style.format({
                    "Migrant Stock": "{:,.0f}",
                    "Origin Emigrant Share %": "{:.2f}%",
                    "Dest Immigrant Share %": "{:.2f}%"
                }, na_rep="—"),
                use_container_width=True,
                height=300
            )

            st.download_button(
                label="📥 Download Corridor Data as CSV",
                data=display_routes.to_csv(index=False).encode("utf-8"),
                file_name=f"corridors_{corridor_year}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No bilateral corridors found matching the selected filters.")

    # =============================================================================
    # PAGE 6: 🌎 COUNTRY EXPLORER
    # =============================================================================
    elif page == "🌎 Country Explorer":
        render_section_title("🌎 Individual Country Profile Explorer", "Detailed demographic, economic, and network profile")
        
        ce_c1, ce_c2 = st.columns([3, 2])
        with ce_c1:
            selected_country_name = st.selectbox(
                "Select Country",
                options=list(COUNTRY_DICT.keys()),
                index=0,
                key="profile_country"
            )
        with ce_c2:
            selected_country_year = st.selectbox(
                "Snapshot Reference Year",
                AVAILABLE_YEARS,
                index=len(AVAILABLE_YEARS) - 1,
                key="profile_year"
            )

        country_code = COUNTRY_DICT[selected_country_name]
        profile = get_country_profile_data(df_country, df_bilat, country_code=country_code, year=selected_country_year)
        stats = profile["current_stats"]

        # Metric Banner
        m_val = stats.get("migrant_stock", np.nan)
        s_val = stats.get("migrant_stock_pct_population", np.nan)
        r_val = stats.get("migrant_stock_global_rank", np.nan)
        pop_val = stats.get("population", np.nan)
        gdp_val = stats.get("gdp_per_capita", np.nan)

        m_str = f"{m_val:,.0f}" if pd.notna(m_val) else "N/A"
        s_str = f"{s_val:.2f}%" if pd.notna(s_val) else "N/A"
        r_str = f"#{r_val:.0f}" if pd.notna(r_val) else "N/A"
        pop_str = f"{pop_val:,.0f}" if pd.notna(pop_val) else "N/A"
        gdp_str = f"${gdp_val:,.0f}" if pd.notna(gdp_val) else "N/A"

        p1, p2, p3, p4, p5 = st.columns(5)
        with p1:
            st.markdown(render_kpi_card("Migrant Stock", m_str, f"Foreign-born in {selected_country_year}", theme_mode), unsafe_allow_html=True)
        with p2:
            st.markdown(render_kpi_card("Stock % Pop.", s_str, "Share of resident pop.", theme_mode), unsafe_allow_html=True)
        with p3:
            st.markdown(render_kpi_card("Global Rank", r_str, f"By stock in {selected_country_year}", theme_mode), unsafe_allow_html=True)
        with p4:
            st.markdown(render_kpi_card("Total Population", pop_str, "World Bank midyear", theme_mode), unsafe_allow_html=True)
        with p5:
            st.markdown(render_kpi_card("GDP per Capita", gdp_str, "Current US$", theme_mode), unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        # 5 Analytic Tabs (Extended with Network Profile)
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Stock Trajectory (1990–2020)",
            "🔀 Inbound & Outbound Corridors",
            "🕸️ Network Centrality Profile",
            "🏆 Global Rank History",
            "📊 Socioeconomic Indicators"
        ])

        with tab1:
            render_section_title(f"Migrant Stock Trajectory: {selected_country_name}")
            history_df = profile["history_df"]
            if not history_df.empty:
                fig_p1 = px.line(
                    history_df,
                    x="year",
                    y="migrant_stock",
                    markers=True,
                    labels={"year": "Census Year", "migrant_stock": "Migrant Stock (People)"},
                    title=f"Total Residing Migrant Stock (1990–2020)",
                    template=plotly_tmpl
                )
                fig_p1.update_traces(line=dict(color=theme_colors["accent_blue"], width=3), marker=dict(size=8))
                fig_p1.update_layout(**get_plotly_layout(theme_mode, f"Total Residing Migrant Stock: {selected_country_name}", height=380))
                st.plotly_chart(fig_p1, use_container_width=True)
            else:
                st.info("No historical data available for this country.")

        with tab2:
            render_section_title(f"Top Bilateral Corridors ({selected_country_year})")
            in_df = profile["inbound_corridors"]
            out_df = profile["outbound_corridors"]
            
            c_in, c_out = st.columns(2)
            with c_in:
                st.markdown(f"**Top Inbound Origins** (Foreign-born residing in {selected_country_name}):")
                if not in_df.empty:
                    fig_in = px.bar(
                        in_df,
                        x="migrant_stock",
                        y="origin_display_name",
                        orientation="h",
                        labels={"migrant_stock": "Migrant Stock", "origin_display_name": "Origin Country"},
                        template=plotly_tmpl,
                        color="dest_corridor_share_pct",
                        color_continuous_scale="Blues"
                    )
                    fig_in.update_layout(**get_plotly_layout(theme_mode, "", height=320))
                    fig_in.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig_in, use_container_width=True)
                else:
                    st.caption("No inbound corridor records available.")
                    
            with c_out:
                st.markdown(f"**Top Outbound Destinations** (Emigrants from {selected_country_name}):")
                if not out_df.empty:
                    fig_out = px.bar(
                        out_df,
                        x="migrant_stock",
                        y="dest_display_name",
                        orientation="h",
                        labels={"migrant_stock": "Migrant Stock", "dest_display_name": "Destination Country"},
                        template=plotly_tmpl,
                        color="origin_corridor_share_pct",
                        color_continuous_scale="Teal"
                    )
                    fig_out.update_layout(**get_plotly_layout(theme_mode, "", height=320))
                    fig_out.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig_out, use_container_width=True)
                else:
                    st.caption("No outbound corridor records available.")

        with tab3:
            render_section_title(f"🕸️ Network Profile: {selected_country_name} ({selected_country_year})")
            G_full, df_net_m = get_cached_network_and_metrics(year=selected_country_year, min_stock=None, top_n_edges=None)
            c_net = df_net_m[df_net_m["country_code"] == country_code]
            
            if not c_net.empty:
                c_row = c_net.iloc[0]
                nc1, nc2, nc3, nc4 = st.columns(4)
                with nc1:
                    st.metric("Total Degree (Connections)", f"{c_row['total_degree']:,}", f"In: {c_row['in_degree']} | Out: {c_row['out_degree']}")
                with nc2:
                    st.metric("Weighted Network Strength", f"{c_row['total_strength']:,.0f}", f"In: {c_row['in_strength']:,.0f}")
                with nc3:
                    st.metric("Betweenness Centrality", f"{c_row['betweenness_centrality']:.4f}")
                with nc4:
                    st.metric("PageRank Score", f"{c_row['pagerank']:.4f}")
                    
                st.markdown("---")
                st.markdown(f"**Ego Network (Neighborhood Subgraph for {selected_country_name})**:")
                if G_full.has_node(country_code):
                    # Extract 1-hop ego network
                    ego_nodes = list(G_full.predecessors(country_code)) + list(G_full.successors(country_code)) + [country_code]
                    ego_subG = G_full.subgraph(ego_nodes)
                    fig_ego = create_network_2d_plot(
                        ego_subG,
                        df_net_m[df_net_m["country_code"].isin(ego_nodes)],
                        layout_type="Spring",
                        is_dark_mode=is_dark,
                        title=f"{selected_country_name} Network Neighborhood ({selected_country_year})"
                    )
                    st.plotly_chart(fig_ego, use_container_width=True)
            else:
                st.info("Country is not connected in the selected year network.")

        with tab4:
            render_section_title("Global Migrant Stock Rank Trajectory (1990–2020)")
            history_df = profile["history_df"]
            if not history_df.empty and "migrant_stock_global_rank" in history_df.columns:
                fig_rank_hist = px.line(
                    history_df,
                    x="year",
                    y="migrant_stock_global_rank",
                    markers=True,
                    labels={"year": "Census Year", "migrant_stock_global_rank": "Global Rank (1 = Highest)"},
                    title=f"Global Rank Position Over Time",
                    template=plotly_tmpl
                )
                fig_rank_hist.update_traces(line=dict(color=theme_colors["accent_amber"], width=3), marker=dict(size=8))
                fig_rank_hist.update_layout(**get_plotly_layout(theme_mode, f"Global Rank Position Over Time: {selected_country_name}", height=350))
                fig_rank_hist.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_rank_hist, use_container_width=True)

        with tab5:
            render_section_title(f"Macroeconomic Indicators ({selected_country_name})")
            st.caption("Descriptive macroeconomic indicators from World Bank WDI. These values describe economic context and do not establish causal relationships.")
            if not history_df.empty:
                econ_table = history_df[[
                    "year", "population", "gdp", "gdp_per_capita", "unemployment", "migrant_stock", "migrant_stock_pct_population"
                ]].rename(columns={
                    "year": "Year",
                    "population": "Population",
                    "gdp": "Total GDP (USD)",
                    "gdp_per_capita": "GDP per Capita (USD)",
                    "unemployment": "Unemployment Rate (%)",
                    "migrant_stock": "Migrant Stock",
                    "migrant_stock_pct_population": "Stock % of Pop"
                })
                st.dataframe(
                    econ_table.style.format({
                        "Population": "{:,.0f}",
                        "Total GDP (USD)": "${:,.0f}",
                        "GDP per Capita (USD)": "${:,.0f}",
                        "Unemployment Rate (%)": "{:.2f}%",
                        "Migrant Stock": "{:,.0f}",
                        "Stock % of Pop": "{:.2f}%"
                    }, na_rep="—"),
                    use_container_width=True,
                    height=280
                )

        # Complete Country History Table
        render_section_title(f"📋 Complete Country History: {selected_country_name}")
        st.dataframe(
            history_df[[
                "display_name", "country_code", "year", "migrant_stock",
                "population", "migrant_stock_pct_population", "stock_change_5yr",
                "stock_growth_pct_5yr", "gdp_per_capita", "unemployment", "migrant_stock_global_rank"
            ]].style.format({
                "migrant_stock": "{:,.0f}",
                "population": "{:,.0f}",
                "migrant_stock_pct_population": "{:.2f}%",
                "stock_change_5yr": "{:+,.0f}",
                "stock_growth_pct_5yr": "{:+.2f}%",
                "gdp_per_capita": "${:,.0f}",
                "unemployment": "{:.2f}%",
                "migrant_stock_global_rank": "{:.0f}"
            }, na_rep="—"),
            use_container_width=True,
            height=260
        )

        st.download_button(
            label=f"📥 Download {selected_country_name} Profile Data as CSV",
            data=history_df.to_csv(index=False).encode("utf-8"),
            file_name=f"country_profile_{country_code}.csv",
            mime="text/csv"
        )

    # =============================================================================
    # PAGE 7: 🕸️ MIGRATION NETWORK
    # =============================================================================
    elif page == "🕸️ Migration Network":
        render_section_title("🕸️ Global Bilateral Migrant-Stock Network", "Network topology, centrality analysis, and spatial arcs")
        
        render_scientific_alert(
            "<b>Scientific Definition</b>: Each directed edge Origin → Destination represents the UN DESA estimated migrant stock residing in the destination whose origin is the specified origin country, for the selected UN DESA observation year. The network represents bilateral migrant-stock relationships. It does <b>NOT</b> represent annual migration flows, annual immigration flows, annual emigration flows, or yearly migration movements.",
            theme_mode
        )
        
        net_tabs = st.tabs([
            "🌐 Interactive 2D Network",
            "🗺️ Geographic Network Map",
            "🏆 Network Centrality Rankings",
            "📈 Longitudinal Network Evolution",
            "📊 Country Centrality Comparison"
        ])
        
        # Controls Header
        nc1, nc2, nc3 = st.columns([2, 2, 2])
        with nc1:
            net_year = st.selectbox("Network Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="net_yr")
        with nc2:
            top_edges = st.selectbox("Top N Strongest Edges", [25, 50, 100, 250, 500], index=2, key="net_top_e")
        with nc3:
            min_stock_thresh = st.selectbox("Minimum Stock Threshold", [0, 50000, 100000, 500000, 1000000], index=0, key="net_min_s")

        G_curr, df_metrics = get_cached_network_and_metrics(year=net_year, min_stock=min_stock_thresh, top_n_edges=top_edges)

        # TAB 1: 2D NETWORK GRAPH
        with net_tabs[0]:
            render_section_title(f"2D Force-Directed Graph ({net_year})", f"Filtered to Top {top_edges} strongest bilateral corridors")
            g_c1, g_c2, g_c3 = st.columns([2, 2, 2])
            with g_c1:
                layout_choice = st.selectbox("Layout Algorithm", ["Spring", "Circular", "Kamada-Kawai"], index=0, key="net_layout")
            with g_c2:
                node_size_choice = st.selectbox("Node Size Metric", ["Weighted Strength", "Total Degree", "Betweenness Centrality", "PageRank"], index=0, key="net_size")
            with g_c3:
                node_color_choice = st.selectbox("Node Color Metric", ["Weighted Strength", "Total Degree", "Betweenness Centrality", "PageRank"], index=0, key="net_color")

            fig_2d = create_network_2d_plot(
                G_curr,
                df_metrics,
                layout_type=layout_choice,
                node_size_metric=node_size_choice,
                node_color_metric=node_color_choice,
                is_dark_mode=is_dark,
                title=f"Global Migrant-Stock Network ({net_year}) — Top {top_edges} Edges"
            )
            st.plotly_chart(fig_2d, use_container_width=True)

        # TAB 2: GEOGRAPHIC NETWORK MAP
        with net_tabs[1]:
            render_section_title(f"Geographic Migration Arcs ({net_year})", "Spatial arcs between origin and destination centroids")
            fig_geo_net = create_geographic_network_map(
                G_curr,
                is_dark_mode=is_dark,
                top_n_edges=top_edges,
                title=f"Geographic Migrant Stock Corridors ({net_year})"
            )
            st.plotly_chart(fig_geo_net, use_container_width=True)

        # TAB 3: CENTRALITY RANKINGS
        with net_tabs[2]:
            render_section_title(f"Network Centrality Rankings ({net_year})")
            rk_c1, rk_c2 = st.columns([3, 2])
            with rk_c1:
                rank_metric_net = st.selectbox("Centrality Metric", ["Weighted Strength", "In-Strength", "Out-Strength", "Total Degree", "Betweenness Centrality", "PageRank"], index=0, key="net_rank_metric")
            with rk_c2:
                rank_n_net = st.selectbox("Top N Countries", [10, 25, 50], index=0, key="net_rank_n")

            df_rank_net = get_network_rankings_data(df_metrics, metric_name=rank_metric_net, top_n=rank_n_net)
            
            if not df_rank_net.empty:
                fig_rank_n = px.bar(
                    df_rank_net,
                    x="metric_value",
                    y="country_name",
                    orientation="h",
                    text="metric_value",
                    labels={"metric_value": rank_metric_net, "country_name": "Country"},
                    title=f"Top {rank_n_net} Countries by {rank_metric_net} ({net_year})",
                    template=plotly_tmpl,
                    color="metric_value",
                    color_continuous_scale="Blues"
                )
                fmt_str = "%{text:.4f}" if "Centrality" in rank_metric_net or "PageRank" in rank_metric_net else "%{text:,.0f}"
                fig_rank_n.update_traces(texttemplate=fmt_str, textposition="outside")
                fig_rank_n.update_layout(**get_plotly_layout(theme_mode, f"Top {rank_n_net} Countries by {rank_metric_net} ({net_year})", height=max(360, len(df_rank_net)*28)))
                fig_rank_n.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_rank_n, use_container_width=True)

                # Data Table
                render_section_title("Centrality Data Table")
                st.dataframe(
                    df_rank_net[[
                        "rank", "country_name", "country_code", "total_strength",
                        "in_strength", "out_strength", "total_degree", "betweenness_centrality", "pagerank"
                    ]].rename(columns={
                        "rank": "Rank", "country_name": "Country", "country_code": "ISO3",
                        "total_strength": "Total Strength", "in_strength": "In-Strength", "out_strength": "Out-Strength",
                        "total_degree": "Degree", "betweenness_centrality": "Betweenness", "pagerank": "PageRank"
                    }).style.format({
                        "Total Strength": "{:,.0f}", "In-Strength": "{:,.0f}", "Out-Strength": "{:,.0f}",
                        "Degree": "{:,.0f}", "Betweenness": "{:.4f}", "PageRank": "{:.4f}"
                    }),
                    use_container_width=True,
                    height=280
                )

                st.download_button(
                    label="📥 Download Centrality Rankings CSV",
                    data=df_rank_net.to_csv(index=False).encode("utf-8"),
                    file_name=f"centrality_rankings_{net_year}.csv",
                    mime="text/csv"
                )

        # TAB 4: TEMPORAL EVOLUTION
        with net_tabs[3]:
            render_section_title("Longitudinal Network Evolution (1990–2020)")
            df_temp_net = get_cached_temporal_evolution(min_stock=min_stock_thresh, top_n_edges=top_edges)
            
            tp1, tp2 = st.columns(2)
            with tp1:
                fig_nodes_edges = px.line(
                    df_temp_net,
                    x="year",
                    y=["node_count", "edge_count"],
                    markers=True,
                    title="Active Network Nodes & Edges (1990–2020)",
                    labels={"year": "Year", "value": "Count", "variable": "Network Element"},
                    template=plotly_tmpl
                )
                fig_nodes_edges.update_layout(**get_plotly_layout(theme_mode, "Active Network Nodes & Edges (1990–2020)", height=350))
                st.plotly_chart(fig_nodes_edges, use_container_width=True)
            with tp2:
                fig_dens = px.line(
                    df_temp_net,
                    x="year",
                    y="network_density",
                    markers=True,
                    title="Global Network Density Over Time",
                    labels={"year": "Year", "network_density": "Network Density"},
                    template=plotly_tmpl
                )
                fig_dens.update_traces(line=dict(color=theme_colors["accent_teal"], width=3))
                fig_dens.update_layout(**get_plotly_layout(theme_mode, "Global Network Density Over Time", height=350))
                st.plotly_chart(fig_dens, use_container_width=True)

            st.dataframe(
                df_temp_net.rename(columns={
                    "year": "Census Year", "node_count": "Nodes", "edge_count": "Edges",
                    "total_observed_stock": "Total Observed Stock", "avg_degree": "Average Degree",
                    "network_density": "Density", "top_corridor": "Largest Bilateral Corridor"
                }).style.format({
                    "Nodes": "{:,}", "Edges": "{:,}", "Total Observed Stock": "{:,.0f}",
                    "Average Degree": "{:.2f}", "Density": "{:.4f}"
                }),
                use_container_width=True
            )

        # TAB 5: COUNTRY CENTRALITY TRAJECTORY
        with net_tabs[4]:
            render_section_title("Compare Longitudinal Centrality Across Countries")
            cmp_c1, cmp_c2 = st.columns([3, 2])
            with cmp_c1:
                comp_countries = st.multiselect(
                    "Select Countries to Compare",
                    options=list(COUNTRY_DICT.keys()),
                    default=["United States of America", "India", "Germany", "United Arab Emirates", "China"],
                    key="net_comp_c"
                )
            with cmp_c2:
                comp_metric_choice = st.selectbox(
                    "Longitudinal Centrality Metric",
                    ["total_strength", "in_strength", "out_strength", "betweenness_centrality", "pagerank"],
                    index=0,
                    key="net_comp_m"
                )

            if comp_countries:
                comp_codes = [COUNTRY_DICT[c] for c in comp_countries]
                df_traj = get_country_centrality_trajectories(df_bilat, country_codes=comp_codes, top_n_edges=top_edges)
                
                if not df_traj.empty:
                    fig_traj = px.line(
                        df_traj,
                        x="year",
                        y=comp_metric_choice,
                        color="country_name",
                        markers=True,
                        title=f"Centrality Trajectories: {comp_metric_choice.replace('_', ' ').title()} (1990–2020)",
                        labels={"year": "Year", comp_metric_choice: comp_metric_choice.replace('_', ' ').title(), "country_name": "Country"},
                        template=plotly_tmpl
                    )
                    fig_traj.update_layout(**get_plotly_layout(theme_mode, f"Centrality Trajectories: {comp_metric_choice.replace('_', ' ').title()} (1990–2020)", height=420))
                    st.plotly_chart(fig_traj, use_container_width=True)

    # =============================================================================
    # PAGE 8: 🔗 CORRIDOR ANALYSIS
    # =============================================================================
    elif page == "🔗 Corridor Analysis":
        render_section_title("🔗 Advanced Corridor Analytics & Bidirectional Asymmetry", "Bilateral asymmetry and portfolio concentration")
        
        c_tabs = st.tabs([
            "⚖️ Bidirectional Asymmetry Analyzer",
            "📊 Origin & Destination Concentration",
            "🌐 Global Top Corridors"
        ])

        with c_tabs[0]:
            render_section_title("1. Bidirectional Country Pair Analysis", "Directional bilateral migrant stock between two sovereign nations")
            
            b_c1, b_c2, b_c3 = st.columns([3, 3, 2])
            with b_c1:
                b_orig = st.selectbox("Country A", options=list(COUNTRY_DICT.keys()), index=list(COUNTRY_DICT.keys()).index("India") if "India" in COUNTRY_DICT else 0, key="bi_a")
            with b_c2:
                b_dest = st.selectbox("Country B", options=list(COUNTRY_DICT.keys()), index=list(COUNTRY_DICT.keys()).index("United Arab Emirates") if "United Arab Emirates" in COUNTRY_DICT else 1, key="bi_b")
            with b_c3:
                b_year = st.selectbox("Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="bi_yr")

            code_a = COUNTRY_DICT[b_orig]
            code_b = COUNTRY_DICT[b_dest]

            if code_a != code_b:
                bi_res = get_bidirectional_corridor_analysis(df_bilat, year=b_year, country_a=code_a, country_b=code_b)
                
                # Asymmetry KPI Cards
                ak1, ak2, ak3, ak4 = st.columns(4)
                with ak1:
                    st.markdown(render_kpi_card(f"{b_orig} → {b_dest}", f"{bi_res['stock_a_to_b']:,.0f}", f"Born in {b_orig} living in {b_dest}", theme_mode), unsafe_allow_html=True)
                with ak2:
                    st.markdown(render_kpi_card(f"{b_dest} → {b_orig}", f"{bi_res['stock_b_to_a']:,.0f}", f"Born in {b_dest} living in {b_orig}", theme_mode), unsafe_allow_html=True)
                with ak3:
                    st.markdown(render_kpi_card("Combined Bilateral Stock", f"{bi_res['total_bilateral_stock']:,.0f}", "Total two-way residing stock", theme_mode), unsafe_allow_html=True)
                with ak4:
                    st.markdown(render_kpi_card("Directional Asymmetry", f"{bi_res['asymmetry_index']:+.2f}", "Range: [-1.0, +1.0]", theme_mode), unsafe_allow_html=True)

                render_scientific_alert(
                    f"<b>Asymmetry Interpretation</b>: Dominant corridor direction is <b>{bi_res['dominant_direction']}</b> with a stock difference of <b>{bi_res['stock_difference']:,.0f}</b> people.",
                    theme_mode
                )

                # Bar comparison
                bi_chart_df = pd.DataFrame([
                    {"Direction": f"{b_orig} → {b_dest}", "Migrant Stock": bi_res["stock_a_to_b"]},
                    {"Direction": f"{b_dest} → {b_orig}", "Migrant Stock": bi_res["stock_b_to_a"]}
                ])
                fig_bi = px.bar(
                    bi_chart_df,
                    x="Direction",
                    y="Migrant Stock",
                    color="Direction",
                    color_discrete_sequence=[theme_colors["accent_blue"], theme_colors["accent_teal"]],
                    title=f"Bidirectional Stock Comparison ({b_year})",
                    template=plotly_tmpl
                )
                fig_bi.update_layout(**get_plotly_layout(theme_mode, f"Bidirectional Stock Comparison ({b_year})", height=350))
                st.plotly_chart(fig_bi, use_container_width=True)
            else:
                st.warning("Please select two distinct countries to analyze bidirectional asymmetry.")

        with c_tabs[1]:
            render_section_title("2. Corridor Concentration (Herfindahl Index)")
            st.caption("Measures how concentrated a country's emigrant stock or immigrant stock is across partner countries.")
            
            conc_c1, conc_c2 = st.columns([3, 2])
            with conc_c1:
                conc_country = st.selectbox("Select Country for Concentration Audit", options=list(COUNTRY_DICT.keys()), index=0, key="conc_c")
            with conc_c2:
                conc_year = st.selectbox("Census Year", AVAILABLE_YEARS, index=len(AVAILABLE_YEARS)-1, key="conc_yr")

            c_code = COUNTRY_DICT[conc_country]
            
            # Compute emigrant destination concentration
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
                    st.metric("Total Emigrant Stock Abroad", f"{tot_emig:,.0f}")
                with ck2:
                    st.metric("Emigrant Destination Concentration (HHI)", f"{hhi_emig:,.0f}", "Max 10,000 (Monopoly)")

                fig_conc = px.pie(
                    emig_df.head(8),
                    values="migrant_stock",
                    names="dest_display_name",
                    title=f"Emigrant Stock Concentration: Top Destinations for {conc_country} ({conc_year})",
                    template=plotly_tmpl
                )
                fig_conc.update_layout(**get_plotly_layout(theme_mode, f"Emigrant Stock Concentration: Top Destinations for {conc_country} ({conc_year})", height=400))
                st.plotly_chart(fig_conc, use_container_width=True)
            else:
                st.info("No outbound corridor data available for this selection.")

        with c_tabs[2]:
            render_section_title("3. Top Global Corridors Full Table")
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
        
        # Plot community clusters
        fig_comm = create_community_graph_plot(
            G_comm,
            node_comm_map,
            is_dark_mode=is_dark,
            title=f"Detected Migration Network Communities ({comm_year}) — {len(df_comm_summary)} Clusters"
        )
        st.plotly_chart(fig_comm, use_container_width=True)

        # Community Summary Table & Drill-down
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

        # Detailed Member Inspector
        render_section_title("🔍 Inspect Community Members")
        selected_comm_id = st.selectbox(
            "Select Community ID to Inspect",
            df_comm_summary["community_id"].tolist() if not df_comm_summary.empty else [1]
        )
        
        selected_row = df_comm_summary[df_comm_summary["community_id"] == selected_comm_id]
        if not selected_row.empty:
            members_list = selected_row.iloc[0]["members"]
            st.markdown(f"**Member Countries ({len(members_list)} total)**:")
            st.write(", ".join(members_list))

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
    # PAGE 10: ℹ️ METHODOLOGY
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
        """)

    # =============================================================================
    # PAGE 11: ⚙️ SETTINGS
    # =============================================================================
    elif page == "⚙️ Settings":
        render_section_title("⚙️ Application Settings & Theme")
        
        st.markdown("#### Visual Appearance")
        chosen_theme = st.radio(
            "Select Interface Theme",
            ["Light", "Dark"],
            index=1 if is_dark else 0,
            key="settings_theme"
        )
        if chosen_theme != st.session_state["theme_mode"]:
            st.session_state["theme_mode"] = chosen_theme
            st.rerun()
            
        st.markdown("---")
        render_section_title("Cache Management")
        if st.button("🧹 Clear Streamlit Cache"):
            st.cache_data.clear()
            st.success("Cache cleared successfully! Reloading...")
            st.rerun()
