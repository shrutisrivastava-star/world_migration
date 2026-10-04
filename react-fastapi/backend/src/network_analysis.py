"""
Advanced Migration Network Analysis Core for the Global Migration Observatory.
Constructs NetworkX graphs, computes centrality metrics, executes community detection,
evaluates bidirectional corridor asymmetry, and computes temporal network dynamics.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config


def build_migration_network(
    bilateral_df: pd.DataFrame,
    year: int,
    min_stock: Optional[float] = None,
    top_n_edges: Optional[int] = None,
    sovereign_only: bool = True,
    directed: bool = True
) -> nx.DiGraph:
    """
    Construct a NetworkX graph representing bilateral migrant-stock relationships for a given UN DESA observation year.
    
    Nodes represent countries/territories.
    Each directed edge Origin → Destination represents the UN DESA estimated migrant stock residing in the
    destination whose origin is the specified origin country, for the selected UN DESA observation year.
    Edge weights represent residing migrant stock (people).
    
    The network represents bilateral migrant-stock relationships. It does NOT represent annual migration flows,
    annual immigration flows, annual emigration flows, or yearly migration movements.
    
    Args:
        bilateral_df: Cleaned bilateral migration DataFrame.
        year: Target UN DESA observation census round year.
        min_stock: Optional minimum bilateral migrant-stock threshold.
        top_n_edges: Optional top N strongest edges to retain.
        sovereign_only: If True, exclude regional and aggregate entities.
        directed: If True, returns a DiGraph; otherwise returns an undirected Graph.
        
    Returns:
        nx.DiGraph or nx.Graph: Constructed NetworkX graph.
    """
    G = nx.DiGraph() if directed else nx.Graph()
    if bilateral_df.empty or "year" not in bilateral_df.columns:
        return G
        
    df_yr = bilateral_df[bilateral_df["year"] == year].copy()
    if df_yr.empty:
        return G
    
    # Filter out aggregates
    if sovereign_only and "is_aggregate_route" in df_yr.columns:
        df_yr = df_yr[~df_yr["is_aggregate_route"]]
        
    # Check essential columns exist
    if "origin_code" not in df_yr.columns or "destination_code" not in df_yr.columns or "migrant_stock" not in df_yr.columns:
        return G
        
    # Remove null codes and self-loops
    df_yr = df_yr[
        df_yr["origin_code"].notna() &
        df_yr["destination_code"].notna() &
        (df_yr["origin_code"] != df_yr["destination_code"]) &
        (df_yr["migrant_stock"] > 0)
    ].copy()
    
    # Apply minimum stock filter if specified
    if min_stock is not None and min_stock > 0:
        df_yr = df_yr[df_yr["migrant_stock"] >= min_stock]
        
    # Sort and take top N edges if specified
    df_yr = df_yr.sort_values("migrant_stock", ascending=False)
    if top_n_edges is not None and top_n_edges > 0:
        df_yr = df_yr.head(top_n_edges)
        
    G = nx.DiGraph() if directed else nx.Graph()
    
    if df_yr.empty:
        return G
        
    # Add nodes with metadata
    for row in df_yr.itertuples(index=False):
        orig_code = str(row.origin_code)
        orig_name = getattr(row, "origin_display_name", str(row.origin_country))
        dest_code = str(row.destination_code)
        dest_name = getattr(row, "dest_display_name", str(row.destination_country))
        stock = float(row.migrant_stock)
        
        if not G.has_node(orig_code):
            G.add_node(orig_code, name=orig_name, iso3=orig_code)
        if not G.has_node(dest_code):
            G.add_node(dest_code, name=dest_name, iso3=dest_code)
            
        orig_share = float(row.origin_corridor_share_pct) if pd.notna(getattr(row, "origin_corridor_share_pct", np.nan)) else 0.0
        dest_share = float(row.dest_corridor_share_pct) if pd.notna(getattr(row, "dest_corridor_share_pct", np.nan)) else 0.0
        
        if G.has_edge(orig_code, dest_code) and not directed:
            # For undirected graph, sum bidirectional weights
            G[orig_code][dest_code]["weight"] += stock
        else:
            G.add_edge(
                orig_code,
                dest_code,
                weight=stock,
                origin_name=orig_name,
                dest_name=dest_name,
                origin_share=orig_share,
                dest_share=dest_share
            )
            
    return G


def calculate_network_metrics(G: nx.DiGraph) -> pd.DataFrame:
    """
    Compute comprehensive network centrality and strength metrics for all nodes in the graph.
    
    Metrics computed:
    - In-Degree & Out-Degree
    - Total Degree Centrality
    - In-Strength (weighted inbound stock) & Out-Strength (weighted outbound stock)
    - Total Weighted Strength
    - Betweenness Centrality
    - PageRank
    
    Args:
        G: NetworkX DiGraph or Graph.
        
    Returns:
        pd.DataFrame: Table of country-level network metrics.
    """
    if len(G) == 0:
        return pd.DataFrame(columns=[
            "country_code", "country_name", "in_degree", "out_degree", "total_degree",
            "in_strength", "out_strength", "total_strength", "degree_centrality",
            "betweenness_centrality", "pagerank"
        ])
        
    is_directed = G.is_directed()
    nodes = list(G.nodes())
    
    # 1. Degree & Strength Calculations
    if is_directed:
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
        total_degrees = {n: in_degrees[n] + out_degrees[n] for n in nodes}
        in_strengths = dict(G.in_degree(weight="weight"))
        out_strengths = dict(G.out_degree(weight="weight"))
        total_strengths = {n: in_strengths[n] + out_strengths[n] for n in nodes}
    else:
        deg = dict(G.degree())
        in_degrees = deg
        out_degrees = deg
        total_degrees = deg
        strength = dict(G.degree(weight="weight"))
        in_strengths = strength
        out_strengths = strength
        total_strengths = strength
        
    # 2. Degree Centrality (Normalized)
    deg_centrality = nx.degree_centrality(G)
    
    # 3. Betweenness Centrality
    try:
        betweenness = nx.betweenness_centrality(G, weight=None, normalized=True)
    except Exception:
        betweenness = {n: 0.0 for n in nodes}
        
    # 4. PageRank
    try:
        pagerank = nx.pagerank(G, weight="weight", alpha=0.85, max_iter=200)
    except Exception:
        try:
            pagerank = nx.pagerank(G, weight=None, alpha=0.85)
        except Exception:
            pagerank = {n: 1.0 / len(nodes) for n in nodes}
            
    records = []
    for n in nodes:
        name = G.nodes[n].get("name", n)
        records.append({
            "country_code": n,
            "country_name": name,
            "in_degree": in_degrees.get(n, 0),
            "out_degree": out_degrees.get(n, 0),
            "total_degree": total_degrees.get(n, 0),
            "in_strength": in_strengths.get(n, 0.0),
            "out_strength": out_strengths.get(n, 0.0),
            "total_strength": total_strengths.get(n, 0.0),
            "degree_centrality": deg_centrality.get(n, 0.0),
            "betweenness_centrality": betweenness.get(n, 0.0),
            "pagerank": pagerank.get(n, 0.0),
        })
        
    df_metrics = pd.DataFrame(records)
    return df_metrics.sort_values("total_strength", ascending=False).reset_index(drop=True)


def get_network_rankings_data(
    metrics_df: pd.DataFrame,
    metric_name: str = "Weighted Strength",
    top_n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Extract top N rankings for a selected network centrality metric.
    
    Args:
        metrics_df: DataFrame generated by calculate_network_metrics.
        metric_name: User-selected metric name.
        top_n: Number of countries to return.
        ascending: Sort order.
        
    Returns:
        pd.DataFrame: Top N ranked countries.
    """
    col_map = {
        "Weighted Degree / Strength": "total_strength",
        "Weighted Strength": "total_strength",
        "Total Strength": "total_strength",
        "In-Strength (Immigrant Stock)": "in_strength",
        "Out-Strength (Emigrant Stock)": "out_strength",
        "Degree Centrality": "degree_centrality",
        "Total Degree": "total_degree",
        "Betweenness Centrality": "betweenness_centrality",
        "Betweenness": "betweenness_centrality",
        "PageRank": "pagerank"
    }
    col = col_map.get(metric_name, "total_strength")
    
    if metrics_df.empty or col not in metrics_df.columns:
        return pd.DataFrame()
        
    df_sorted = metrics_df.sort_values(col, ascending=ascending).head(top_n).copy()
    df_sorted["rank"] = range(1, len(df_sorted) + 1)
    df_sorted["metric_value"] = df_sorted[col]
    return df_sorted


def create_undirected_stock_network(G_dir: nx.DiGraph) -> nx.Graph:
    """
    Construct a separate weighted undirected representation of the directed migrant-stock network
    specifically for algorithms (such as modularity-based community detection) that require an undirected graph.
    
    Transformation Rules:
    1. Each directed edge Origin → Destination represents the UN DESA estimated migrant stock residing in the
       destination whose origin is the specified origin country, for the selected UN DESA observation year.
    2. Where bilateral migrant-stock relationships exist in both directions (u -> v and v -> u), the undirected
       edge weight is computed as the combined bilateral migrant stock: forward_stock + reverse_stock.
    3. Where only a single direction exists (u -> v), the undirected edge weight retains that observed stock.
    4. Node metadata (name, iso3) is preserved.
    
    Args:
        G_dir: Primary directed migration network (DiGraph).
        
    Returns:
        nx.Graph: Derived weighted undirected network.
    """
    G_undir = nx.Graph()
    
    for n, d in G_dir.nodes(data=True):
        G_undir.add_node(n, **d)
        
    for u, v, data in G_dir.edges(data=True):
        w = float(data.get("weight", 0.0))
        if G_undir.has_edge(u, v):
            G_undir[u][v]["weight"] += w
        else:
            G_undir.add_edge(u, v, weight=w)
            
    return G_undir


def detect_network_communities(G: nx.DiGraph) -> Tuple[Dict[str, int], pd.DataFrame, float]:
    """
    Execute community detection on the migration network using modularity optimization.
    
    The primary migration network is directed (Origin -> Destination). For modularity community detection,
    a separate weighted undirected representation is explicitly constructed where reciprocal edge weights
    are combined as (forward_stock + reverse_stock).
    
    Community membership represents empirical clusters generated from observed bilateral migrant-stock
    network structure and does not represent political blocs, cultural regions, or causal migration systems.
    
    Args:
        G: Primary directed NetworkX graph (DiGraph).
        
    Returns:
        Tuple:
            - Dict[str, int]: Node -> Community ID mapping.
            - pd.DataFrame: Community summary table.
            - float: Modularity score.
    """
    if len(G) < 2:
        return {}, pd.DataFrame(), 0.0
        
    G_undir = create_undirected_stock_network(G)
    
    # Try Louvain community detection first
    try:
        communities = list(nx.community.louvain_communities(G_undir, weight="weight", seed=42))
    except Exception:
        try:
            communities = list(nx.community.greedy_modularity_communities(G_undir, weight="weight"))
        except Exception:
            communities = [set(G_undir.nodes())]
            
    # Calculate Modularity
    try:
        modularity = nx.community.modularity(G_undir, communities, weight="weight")
    except Exception:
        modularity = 0.0
        
    node_comm_map = {}
    comm_summary = []
    
    for c_id, comm_nodes in enumerate(communities, start=1):
        for node in comm_nodes:
            node_comm_map[node] = c_id
            
        # Extract member names and top countries by degree
        subG = G.subgraph(comm_nodes)
        sub_degrees = dict(subG.degree(weight="weight"))
        sorted_members = sorted(sub_degrees.items(), key=lambda x: x[1], reverse=True)
        top_member_names = [G.nodes[code].get("name", code) for code, _ in sorted_members[:5]]
        
        comm_summary.append({
            "community_id": c_id,
            "community_name": f"Community {c_id}: {', '.join(top_member_names[:3])}",
            "size": len(comm_nodes),
            "members": sorted([G.nodes[code].get("name", code) for code in comm_nodes]),
            "member_codes": sorted(list(comm_nodes)),
            "top_anchor_countries": ", ".join(top_member_names),
        })
        
    df_summary = pd.DataFrame(comm_summary).sort_values("size", ascending=False).reset_index(drop=True)
    return node_comm_map, df_summary, float(modularity)


def get_bidirectional_corridor_analysis(
    bilateral_df: pd.DataFrame,
    year: int,
    country_a: str,
    country_b: str
) -> Dict[str, Any]:
    """
    Perform deep bidirectional corridor analysis between two countries.
    
    Examines:
    - Forward migrant stock (A -> B)
    - Reverse migrant stock (B -> A)
    - Combined bilateral stock (A <-> B)
    - Directional difference (|A -> B - B -> A|)
    - Directional asymmetry ratio & index
    
    Args:
        bilateral_df: Cleaned bilateral DataFrame.
        year: Selected year.
        country_a: ISO3 code of first country.
        country_b: ISO3 code of second country.
        
    Returns:
        Dict[str, Any]: Bidirectional corridor analysis results.
    """
    df_yr = bilateral_df[bilateral_df["year"] == year]
    
    # A -> B
    row_ab = df_yr[(df_yr["origin_code"] == country_a) & (df_yr["destination_code"] == country_b)]
    stock_ab = float(row_ab["migrant_stock"].values[0]) if not row_ab.empty and pd.notna(row_ab["migrant_stock"].values[0]) else 0.0
    
    # B -> A
    row_ba = df_yr[(df_yr["origin_code"] == country_b) & (df_yr["destination_code"] == country_a)]
    stock_ba = float(row_ba["migrant_stock"].values[0]) if not row_ba.empty and pd.notna(row_ba["migrant_stock"].values[0]) else 0.0
    
    total_bilateral = stock_ab + stock_ba
    diff = abs(stock_ab - stock_ba)
    
    # Asymmetry Index: (A->B - B->A) / (A->B + B->A) in range [-1.0, 1.0]
    if total_bilateral > 0:
        asymmetry_index = (stock_ab - stock_ba) / total_bilateral
        ratio = stock_ab / stock_ba if stock_ba > 0 else np.nan
    else:
        asymmetry_index = 0.0
        ratio = np.nan
        
    if stock_ab > stock_ba:
        dominant_direction = f"{country_a} → {country_b}"
    elif stock_ba > stock_ab:
        dominant_direction = f"{country_b} → {country_a}"
    else:
        dominant_direction = "Symmetric / Equal"
        
    return {
        "year": year,
        "country_a": country_a,
        "country_b": country_b,
        "stock_a_to_b": stock_ab,
        "stock_b_to_a": stock_ba,
        "total_bilateral_stock": total_bilateral,
        "stock_difference": diff,
        "asymmetry_index": asymmetry_index,
        "directional_ratio": ratio,
        "dominant_direction": dominant_direction,
    }


def get_temporal_network_evolution(
    bilateral_df: pd.DataFrame,
    min_stock: Optional[float] = None,
    top_n_edges: Optional[int] = None
) -> pd.DataFrame:
    """
    Analyze temporal evolution of global migration network properties across all UN DESA years (1990–2020).
    
    Args:
        bilateral_df: Cleaned bilateral DataFrame.
        min_stock: Optional threshold.
        top_n_edges: Optional edge cutoff.
        
    Returns:
        pd.DataFrame: Yearly network summary statistics.
    """
    years = sorted(bilateral_df["year"].unique())
    records = []
    
    for yr in years:
        G = build_migration_network(
            bilateral_df,
            year=yr,
            min_stock=min_stock,
            top_n_edges=top_n_edges,
            sovereign_only=True,
            directed=True
        )
        
        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()
        
        if edge_count > 0:
            total_stock = sum(d.get("weight", 0) for _, _, d in G.edges(data=True))
            avg_degree = (2.0 * edge_count) / node_count if node_count > 0 else 0.0
            density = nx.density(G)
            
            # Find largest single corridor
            edges_sorted = sorted(G.edges(data=True), key=lambda x: x[2].get("weight", 0), reverse=True)
            top_e = edges_sorted[0]
            top_corridor_label = f"{top_e[0]} → {top_e[1]} ({top_e[2].get('weight', 0):,.0f})"
        else:
            total_stock = 0.0
            avg_degree = 0.0
            density = 0.0
            top_corridor_label = "None"
            
        records.append({
            "year": yr,
            "node_count": node_count,
            "edge_count": edge_count,
            "total_observed_stock": total_stock,
            "avg_degree": avg_degree,
            "network_density": density,
            "top_corridor": top_corridor_label
        })
        
    return pd.DataFrame(records)


def get_country_centrality_trajectories(
    bilateral_df: pd.DataFrame,
    country_codes: List[str],
    top_n_edges: Optional[int] = None
) -> pd.DataFrame:
    """
    Compute longitudinal centrality trajectories (1990–2020) for a set of selected countries.
    
    Args:
        bilateral_df: Cleaned bilateral DataFrame.
        country_codes: List of country ISO3 codes.
        top_n_edges: Optional edge cutoff for each year's network.
        
    Returns:
        pd.DataFrame: Longitudinal network metrics for selected countries.
    """
    years = sorted(bilateral_df["year"].unique())
    all_metrics = []
    
    for yr in years:
        G = build_migration_network(
            bilateral_df,
            year=yr,
            top_n_edges=top_n_edges,
            sovereign_only=True,
            directed=True
        )
        df_m = calculate_network_metrics(G)
        df_m["year"] = yr
        df_filtered = df_m[df_m["country_code"].isin(country_codes)]
        all_metrics.append(df_filtered)
        
    if all_metrics:
        return pd.concat(all_metrics, ignore_index=True).sort_values(["country_name", "year"])
    return pd.DataFrame()
