"""
Unit and integration tests for NetworkX-based migration network analysis module.
"""

import networkx as nx
import numpy as np
import pandas as pd
import pytest

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


@pytest.fixture
def synthetic_bilateral_df():
    return pd.DataFrame([
        # Year 2020 Sovereign Corridors
        {"origin_country": "Mexico", "origin_code": "MEX", "origin_display_name": "Mexico", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "Mexico → United States", "year": 2020, "migrant_stock": 10000000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 90.0, "dest_corridor_share_pct": 20.0},
        {"origin_country": "United States", "origin_code": "USA", "origin_display_name": "United States", "destination_country": "Mexico", "destination_code": "MEX", "dest_display_name": "Mexico", "corridor_label": "United States → Mexico", "year": 2020, "migrant_stock": 1000000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 30.0, "dest_corridor_share_pct": 80.0},
        {"origin_country": "India", "origin_code": "IND", "origin_display_name": "India", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "India → United States", "year": 2020, "migrant_stock": 2500000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 15.0, "dest_corridor_share_pct": 5.0},
        {"origin_country": "India", "origin_code": "IND", "origin_display_name": "India", "destination_country": "UAE", "destination_code": "ARE", "dest_display_name": "United Arab Emirates", "corridor_label": "India → United Arab Emirates", "year": 2020, "migrant_stock": 3500000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 21.0, "dest_corridor_share_pct": 40.0},
        {"origin_country": "Germany", "origin_code": "DEU", "origin_display_name": "Germany", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "Germany → United States", "year": 2020, "migrant_stock": 600000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 15.0, "dest_corridor_share_pct": 1.2},
        {"origin_country": "Poland", "origin_code": "POL", "origin_display_name": "Poland", "destination_country": "Germany", "destination_code": "DEU", "dest_display_name": "Germany", "corridor_label": "Poland → Germany", "year": 2020, "migrant_stock": 1500000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 40.0, "dest_corridor_share_pct": 10.0},
        
        # Self-loop and Aggregate to be filtered
        {"origin_country": "United States", "origin_code": "USA", "origin_display_name": "United States", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "USA → USA", "year": 2020, "migrant_stock": 50000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 1.0, "dest_corridor_share_pct": 1.0},
        {"origin_country": "World", "origin_code": None, "origin_display_name": "World", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "World → United States", "year": 2020, "migrant_stock": 50000000.0, "is_aggregate_route": True, "origin_corridor_share_pct": None, "dest_corridor_share_pct": None},

        # Year 2015 Corridors
        {"origin_country": "Mexico", "origin_code": "MEX", "origin_display_name": "Mexico", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "Mexico → United States", "year": 2015, "migrant_stock": 9000000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 88.0, "dest_corridor_share_pct": 20.0},
        {"origin_country": "India", "origin_code": "IND", "origin_display_name": "India", "destination_country": "United States", "destination_code": "USA", "dest_display_name": "United States", "corridor_label": "India → United States", "year": 2015, "migrant_stock": 2000000.0, "is_aggregate_route": False, "origin_corridor_share_pct": 14.0, "dest_corridor_share_pct": 4.5},
    ])


def test_build_migration_network_basic(synthetic_bilateral_df):
    """Test directed graph construction, aggregate removal, and self-loop exclusion."""
    G = build_migration_network(synthetic_bilateral_df, year=2020, sovereign_only=True, directed=True)
    assert isinstance(G, nx.DiGraph)
    # Self loop (USA->USA) and World aggregate must be excluded
    assert not G.has_edge("USA", "USA")
    assert not G.has_node("None")
    assert G.has_edge("MEX", "USA")
    assert G["MEX"]["USA"]["weight"] == 10000000.0
    assert set(G.nodes()) == {"MEX", "USA", "IND", "ARE", "DEU", "POL"}


def test_build_migration_network_min_stock_filter(synthetic_bilateral_df):
    """Test graph construction with minimum migrant stock threshold."""
    G = build_migration_network(synthetic_bilateral_df, year=2020, min_stock=2000000.0)
    # Only MEX->USA (10M), IND->USA (2.5M), and IND->ARE (3.5M) meet threshold >= 2M
    assert G.number_of_edges() == 3
    assert G.has_edge("MEX", "USA")
    assert G.has_edge("IND", "USA")
    assert G.has_edge("IND", "ARE")
    assert not G.has_edge("DEU", "USA")  # 600k < 2M


def test_build_migration_network_top_n_edges(synthetic_bilateral_df):
    """Test retaining only the top N strongest edges."""
    G = build_migration_network(synthetic_bilateral_df, year=2020, top_n_edges=2)
    assert G.number_of_edges() == 2
    # Top 2 edges are MEX->USA (10M) and IND->ARE (3.5M)
    assert G.has_edge("MEX", "USA")
    assert G.has_edge("IND", "ARE")


def test_calculate_network_metrics(synthetic_bilateral_df):
    """Test degree, strength, betweenness, and PageRank calculations."""
    G = build_migration_network(synthetic_bilateral_df, year=2020)
    df_metrics = calculate_network_metrics(G)
    assert not df_metrics.empty
    assert "country_code" in df_metrics.columns
    assert "total_strength" in df_metrics.columns
    assert "betweenness_centrality" in df_metrics.columns
    assert "pagerank" in df_metrics.columns
    
    # USA in-strength: MEX(10M) + IND(2.5M) + DEU(0.6M) = 13.1M
    usa_row = df_metrics[df_metrics["country_code"] == "USA"].iloc[0]
    assert usa_row["in_strength"] == 13100000.0
    assert usa_row["out_strength"] == 1000000.0  # USA->MEX (1M)
    assert usa_row["total_strength"] == 14100000.0
    assert usa_row["in_degree"] == 3  # MEX, IND, DEU


def test_get_network_rankings_data(synthetic_bilateral_df):
    """Test ranking extraction by centrality metrics."""
    G = build_migration_network(synthetic_bilateral_df, year=2020)
    df_metrics = calculate_network_metrics(G)
    
    rank_df = get_network_rankings_data(df_metrics, metric_name="Weighted Strength", top_n=3)
    assert len(rank_df) == 3
    assert rank_df.iloc[0]["country_code"] == "USA"
    assert rank_df.iloc[0]["rank"] == 1


def test_create_undirected_stock_network(synthetic_bilateral_df):
    """Test explicit weighted undirected graph transformation with reciprocal weight combining."""
    G_dir = build_migration_network(synthetic_bilateral_df, year=2020)
    assert G_dir.is_directed()
    
    G_undir = create_undirected_stock_network(G_dir)
    assert not G_undir.is_directed()
    
    # Check that reciprocal edges MEX->USA (10M) and USA->MEX (1M) are combined to 11M
    assert G_undir.has_edge("MEX", "USA")
    assert G_undir["MEX"]["USA"]["weight"] == 11000000.0
    
    # Check that single directional edge POL->DEU (1.5M) is preserved as 1.5M
    assert G_undir.has_edge("POL", "DEU")
    assert G_undir["POL"]["DEU"]["weight"] == 1500000.0
    
    # Check node metadata preservation
    assert G_undir.nodes["USA"]["name"] == "United States"


def test_detect_network_communities(synthetic_bilateral_df):
    """Test modularity community detection."""
    G = build_migration_network(synthetic_bilateral_df, year=2020)
    node_map, summary_df, modularity = detect_network_communities(G)
    assert isinstance(node_map, dict)
    assert len(node_map) == len(G.nodes())
    assert isinstance(summary_df, pd.DataFrame)
    assert not summary_df.empty
    assert modularity >= -1.0 and modularity <= 1.0


def test_bidirectional_corridor_analysis(synthetic_bilateral_df):
    """Test bilateral asymmetry between USA and MEX."""
    result = get_bidirectional_corridor_analysis(synthetic_bilateral_df, year=2020, country_a="MEX", country_b="USA")
    assert result["stock_a_to_b"] == 10000000.0  # MEX -> USA
    assert result["stock_b_to_a"] == 1000000.0   # USA -> MEX
    assert result["total_bilateral_stock"] == 11000000.0
    assert result["stock_difference"] == 9000000.0
    # Asymmetry: (10M - 1M) / 11M = 9/11 ~ 0.8181
    assert np.isclose(result["asymmetry_index"], 9.0 / 11.0, atol=0.01)
    assert result["dominant_direction"] == "MEX → USA"


def test_temporal_network_evolution(synthetic_bilateral_df):
    """Test longitudinal network metrics."""
    df_temp = get_temporal_network_evolution(synthetic_bilateral_df)
    assert len(df_temp) == 2  # 2015 and 2020
    assert "node_count" in df_temp.columns
    assert "edge_count" in df_temp.columns
    assert "network_density" in df_temp.columns


def test_get_country_centrality_trajectories(synthetic_bilateral_df):
    """Test trajectory of metrics for a selected country across years."""
    df_traj = get_country_centrality_trajectories(synthetic_bilateral_df, country_codes=["USA", "MEX"])
    assert not df_traj.empty
    assert set(df_traj["country_code"]) == {"USA", "MEX"}
    assert set(df_traj["year"]) == {2015, 2020}


def test_network_visualization_safety(synthetic_bilateral_df):
    """Test that Plotly graph constructors execute safely without throwing exceptions."""
    G = build_migration_network(synthetic_bilateral_df, year=2020)
    df_metrics = calculate_network_metrics(G)
    
    # 2D Plot
    fig_2d = create_network_2d_plot(G, df_metrics, is_dark_mode=False)
    assert fig_2d is not None
    
    # Dark Mode 2D Plot
    fig_2d_dark = create_network_2d_plot(G, df_metrics, is_dark_mode=True)
    assert fig_2d_dark is not None
    
    # Geo Map
    fig_geo = create_geographic_network_map(G, is_dark_mode=False, top_n_edges=5)
    assert fig_geo is not None
    
    # Community plot
    node_map, _, _ = detect_network_communities(G)
    fig_comm = create_community_graph_plot(G, node_map, is_dark_mode=True)
    assert fig_comm is not None


def test_empty_graph_safety():
    """Test robustness with empty network."""
    empty_df = pd.DataFrame(columns=["origin_code", "destination_code", "year", "migrant_stock", "is_aggregate_route"])
    G = build_migration_network(empty_df, year=2020)
    assert G.number_of_nodes() == 0
    df_m = calculate_network_metrics(G)
    assert df_m.empty
    fig = create_network_2d_plot(G, df_m)
    assert fig is not None
