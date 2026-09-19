"""
Network and Spatial Visualization Engine for the Global Migration Observatory.
Provides interactive 2D graph visualizations, geographic corridor network maps,
and community cluster network charts adhering to universal Light/Dark theming.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui_theme import get_theme_colors


# Approximate Centroid Coordinates (Lat, Lon) for ISO-3 Sovereign Nations & Major Territories
COUNTRY_CENTROIDS: Dict[str, Tuple[float, float]] = {
    "AFG": (33.9391, 67.7100), "ALB": (41.1533, 20.1683), "DZA": (28.0339, 1.6596),
    "AND": (42.5063, 1.5218), "AGO": (-11.2027, 17.8739), "ARG": (-38.4161, -63.6167),
    "ARM": (40.0691, 45.0382), "AUS": (-25.2744, 133.7751), "AUT": (47.5162, 14.5501),
    "AZE": (40.1431, 47.5769), "BHS": (25.0343, -77.3963), "BHR": (26.0667, 50.5577),
    "BGD": (23.6850, 90.3563), "BRB": (13.1939, -59.5432), "BLR": (53.7098, 27.9534),
    "BEL": (50.5039, 4.4699), "BLZ": (17.1899, -88.4976), "BEN": (9.3077, 2.3158),
    "BTN": (27.5142, 90.4336), "BOL": (-16.2902, -63.5887), "BIH": (43.9159, 17.6791),
    "BWA": (-22.3285, 24.6849), "BRA": (-14.2350, -51.9253), "BRN": (4.5353, 114.7277),
    "BGR": (42.7339, 25.4858), "BFA": (12.2383, -1.5616), "BDI": (-3.3731, 29.9189),
    "KHM": (12.5657, 104.9910), "CMR": (7.3697, 12.3547), "CAN": (56.1304, -106.3468),
    "CPV": (16.0022, -24.0131), "CAF": (6.6111, 20.9394), "TCD": (15.4542, 18.7322),
    "CHL": (-35.6751, -71.5430), "CHN": (35.8617, 104.1954), "COL": (4.5709, -74.2973),
    "COM": (-11.8750, 43.8722), "COG": (-0.2280, 15.8277), "COD": (-4.0383, 21.7587),
    "CRI": (9.7489, -83.7534), "CIV": (7.5400, -5.5471), "HRV": (45.1000, 15.2000),
    "CUB": (21.5218, -77.7812), "CYP": (35.1264, 33.4299), "CZE": (49.8175, 15.4730),
    "DNK": (56.2639, 9.5018), "DJI": (11.8251, 42.5903), "DOM": (18.7357, -70.1627),
    "ECU": (-1.8312, -78.1834), "EGY": (26.8206, 30.8025), "SLV": (13.7942, -88.8965),
    "GNQ": (1.6508, 10.2679), "ERI": (15.1794, 39.7823), "EST": (58.5953, 25.0136),
    "SWZ": (-26.5225, 31.4659), "ETH": (9.1450, 40.4897), "FJI": (-17.7134, 178.0650),
    "FIN": (61.9241, 25.7482), "FRA": (46.2276, 2.2137), "GAB": (-0.8037, 11.6094),
    "GMB": (13.4432, -15.3101), "GEO": (42.3154, 43.3569), "DEU": (51.1657, 10.4515),
    "GHA": (7.9465, -1.0232), "GRC": (39.0742, 21.8243), "GTM": (15.7835, -90.2308),
    "GIN": (9.9456, -9.6966), "GNB": (11.8037, -15.1804), "GUY": (4.8604, -58.9302),
    "HTI": (18.9712, -72.2852), "HND": (15.2000, -86.2419), "HKG": (22.3193, 114.1694),
    "HUN": (47.1625, 19.5033), "ISL": (64.9631, -19.0208), "IND": (20.5937, 78.9629),
    "IDN": (-0.7893, 113.9213), "IRN": (32.4279, 53.6880), "IRQ": (33.2232, 43.6793),
    "IRL": (53.1424, -7.6921), "ISR": (31.0461, 34.8516), "ITA": (41.8719, 12.5674),
    "JAM": (18.1096, -77.2975), "JPN": (36.2048, 138.2529), "JOR": (30.5852, 36.2384),
    "KAZ": (48.0196, 66.9237), "KEN": (-0.0236, 37.9062), "KWT": (29.3117, 47.4818),
    "KGZ": (41.2044, 74.7661), "LAO": (19.8563, 102.4955), "LVA": (56.8796, 24.6032),
    "LBN": (33.8547, 35.8623), "LSO": (-29.6099, 28.2336), "LBR": (6.4281, -9.4295),
    "LBY": (26.3351, 17.2283), "LTU": (55.1694, 23.8813), "LUX": (49.8153, 6.1296),
    "MDG": (-18.7669, 46.8691), "MWI": (-13.2543, 34.3015), "MYS": (4.2105, 101.9758),
    "MDV": (3.2028, 73.2207), "MLI": (17.5707, -3.9962), "MLT": (35.9375, 14.3754),
    "MRT": (21.0079, -10.9408), "MUS": (-20.3484, 57.5522), "MEX": (23.6345, -102.5528),
    "MDA": (47.4116, 28.3699), "MCO": (43.7384, 7.4246), "MNG": (46.8625, 103.8467),
    "MNE": (42.7087, 19.3744), "MAR": (31.7917, -7.0926), "MOZ": (-18.6657, 35.5296),
    "MMR": (21.9162, 95.9560), "NAM": (-22.9576, 18.4904), "NPL": (28.3949, 84.1240),
    "NLD": (52.1326, 5.2913), "NZL": (-40.9006, 174.8860), "NIC": (12.8654, -85.2072),
    "NER": (17.6078, 8.0817), "NGA": (9.0820, 8.6753), "MKD": (41.6086, 21.7453),
    "NOR": (60.4720, 8.4689), "OMN": (21.4735, 55.9754), "PAK": (30.3753, 69.3451),
    "PAN": (8.5379, -80.7821), "PNG": (-6.3150, 143.9555), "PRY": (-23.4425, -58.4438),
    "PER": (-9.1900, -75.0152), "PHL": (12.8797, 121.7740), "POL": (51.9194, 19.1451),
    "PRT": (39.3999, -8.2245), "PRI": (18.2208, -66.5901), "QAT": (25.3548, 51.1839),
    "ROU": (45.9432, 24.9668), "RUS": (61.5240, 105.3188), "RWA": (-1.9403, 29.8739),
    "SAU": (23.8859, 45.0792), "SEN": (14.4974, -14.4524), "SRB": (44.0165, 21.0059),
    "SLE": (8.4606, -11.7799), "SGP": (1.3521, 103.8198), "SVK": (48.6690, 19.6990),
    "SVN": (46.1512, 14.9955), "SOM": (5.1521, 46.1996), "ZAF": (-30.5595, 22.9375),
    "KOR": (35.9078, 127.7669), "SSD": (6.8770, 31.3070), "ESP": (40.4637, -3.7492),
    "LKA": (7.8731, 80.7718), "SDN": (12.8628, 30.2176), "SUR": (3.9193, -56.0278),
    "SWE": (60.1282, 18.6435), "CHE": (46.8182, 8.2275), "SYR": (34.8021, 38.9968),
    "TWN": (23.6978, 120.9605), "TJK": (38.8610, 71.2761), "TZA": (-6.3690, 34.8888),
    "THA": (15.8700, 100.9925), "TLS": (-8.8742, 125.7275), "TGO": (8.6195, 0.8248),
    "TTO": (10.6918, -61.2225), "TUN": (33.8869, 9.5375), "TUR": (38.9637, 35.2433),
    "TKM": (38.9697, 59.5563), "UGA": (1.3733, 32.2903), "UKR": (48.3794, 31.1656),
    "ARE": (23.4241, 53.8478), "GBR": (55.3781, -3.4360), "USA": (37.0902, -95.7129),
    "URY": (-32.5228, -55.7658), "UZB": (41.3775, 64.5853), "VEN": (6.4238, -66.5897),
    "VNM": (14.0583, 108.2772), "PSE": (31.9522, 35.2332), "YEM": (15.5527, 48.5164),
    "ZMB": (-13.1339, 27.8493), "ZWE": (-19.0154, 29.1549)
}


def create_network_2d_plot(
    G: nx.DiGraph,
    metrics_df: Optional[pd.DataFrame] = None,
    layout_type: str = "Spring",
    node_size_metric: str = "Weighted Strength",
    node_color_metric: str = "Weighted Strength",
    is_dark_mode: bool = False,
    title: str = "Interactive Migration Stock Network"
) -> go.Figure:
    """
    Generate an interactive 2D network visualization using Plotly graph objects.
    
    Nodes represent countries sized and colored by network centrality/strength.
    Edges represent bilateral migrant-stock relationships with thickness proportional to weight.
    
    Args:
        G: NetworkX DiGraph or Graph.
        metrics_df: Country network metrics DataFrame (optional, calculated from G if omitted).
        layout_type: 'Spring', 'Circular', or 'Kamada-Kawai'.
        node_size_metric: Metric for node scaling.
        node_color_metric: Metric for node coloring.
        is_dark_mode: Boolean indicating if dark theme is active.
        title: Plot title.
        
    Returns:
        go.Figure: Interactive Plotly network figure.
    """
    colors = get_theme_colors("Dark" if is_dark_mode else "Light")
    
    if len(G) == 0:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            template=colors["plotly_template"],
            annotations=[dict(text="No active network nodes for the selected filter threshold.", showarrow=False)]
        )
        return fig

    if metrics_df is None or (isinstance(metrics_df, pd.DataFrame) and metrics_df.empty):
        from src.network_analysis import calculate_network_metrics
        metrics_df = calculate_network_metrics(G)

    # 1. Compute 2D node coordinates
    if layout_type == "Circular":
        pos = nx.circular_layout(G)
    elif layout_type == "Kamada-Kawai":
        try:
            pos = nx.kamada_kawai_layout(G, weight=None)
        except Exception:
            pos = nx.spring_layout(G, seed=42, k=0.35)
    else:
        pos = nx.spring_layout(G, seed=42, k=0.45, iterations=50)

    # 2. Extract edge lines and hover data
    edge_x = []
    edge_y = []
    edge_hover_x = []
    edge_hover_y = []
    edge_hover_text = []
    
    max_weight = max([d.get("weight", 1) for _, _, d in G.edges(data=True)]) if G.number_of_edges() > 0 else 1.0

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Midpoint for hover tooltip
        w = data.get("weight", 0)
        u_name = data.get("origin_name", u)
        v_name = data.get("dest_name", v)
        edge_hover_x.append((x0 + x1) / 2.0)
        edge_hover_y.append((y0 + y1) / 2.0)
        edge_hover_text.append(f"Corridor: {u_name} → {v_name}<br>Migrant Stock: {w:,.0f}")

    # Edge trace (lines)
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.0, color=colors["node_edge_color"]),
        hoverinfo="none",
        mode="lines"
    )

    # Edge midpoint hover trace
    edge_midpoint_trace = go.Scatter(
        x=edge_hover_x,
        y=edge_hover_y,
        mode="markers",
        hoverinfo="text",
        text=edge_hover_text,
        marker=dict(size=4, color="rgba(0,0,0,0)"),
        showlegend=False
    )

    # 3. Build Node Traces
    node_x = []
    node_y = []
    node_text = []
    node_sizes = []
    node_colors = []
    
    metric_lookup = metrics_df.set_index("country_code").to_dict(orient="index") if not metrics_df.empty else {}
    
    col_map = {
        "Weighted Strength": "total_strength",
        "Total Strength": "total_strength",
        "In-Strength": "in_strength",
        "Out-Strength": "out_strength",
        "Total Degree": "total_degree",
        "Degree Centrality": "degree_centrality",
        "Betweenness": "betweenness_centrality",
        "Betweenness Centrality": "betweenness_centrality",
        "PageRank": "pagerank"
    }
    size_col = col_map.get(node_size_metric, "total_strength")
    color_col = col_map.get(node_color_metric, "total_strength")

    # Determine size scaling bounds
    raw_sizes = [metric_lookup.get(n, {}).get(size_col, 1) for n in G.nodes()]
    min_s, max_s = (min(raw_sizes), max(raw_sizes)) if raw_sizes else (1, 1)

    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        
        m_info = metric_lookup.get(n, {})
        c_name = G.nodes[n].get("name", n)
        val_size = m_info.get(size_col, 0)
        val_color = m_info.get(color_col, 0)
        
        # Dynamic size scaling between 8px and 32px
        if max_s > min_s:
            scaled_size = 9 + 23 * ((val_size - min_s) / (max_s - min_s))
        else:
            scaled_size = 14
        node_sizes.append(scaled_size)
        node_colors.append(val_color)
        
        # Hover info
        deg = m_info.get("total_degree", G.degree(n))
        strength = m_info.get("total_strength", 0)
        bw = m_info.get("betweenness_centrality", 0)
        pr = m_info.get("pagerank", 0)
        
        hover = (
            f"<b>{c_name} ({n})</b><br>"
            f"Total Degree: {deg}<br>"
            f"Weighted Strength: {strength:,.0f}<br>"
            f"Betweenness: {bw:.4f}<br>"
            f"PageRank: {pr:.4f}"
        )
        node_text.append(hover)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[n for n in G.nodes()],
        textposition="top center",
        textfont=dict(size=9, color=colors["text_primary"]),
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale="Viridis" if is_dark_mode else "Blues",
            color=node_colors,
            size=node_sizes,
            colorbar=dict(
                thickness=12,
                title=dict(text=node_color_metric, side="top", font=dict(color=colors["text_primary"], size=11, family="Inter, sans-serif")),
                tickfont=dict(color=colors["text_primary"], size=10, family="Inter, sans-serif"),
                xanchor="left"
            ),
            line=dict(width=1.5, color=colors["card_bg"])
        )
    )

    fig = go.Figure(data=[edge_trace, edge_midpoint_trace, node_trace])
    fig.update_layout(
        title=title,
        template=colors["plotly_template"],
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=560,
        font=dict(family="Inter, sans-serif", color=colors["text_primary"])
    )
    return fig


def create_geographic_network_map(
    G: nx.DiGraph,
    is_dark_mode: bool = False,
    top_n_edges: int = 50,
    title: str = "Global Geographic Migration Corridors"
) -> go.Figure:
    """
    Generate an interactive geographic network map displaying bilateral migrant stock arcs across world coordinates.
    
    Args:
        G: NetworkX DiGraph.
        is_dark_mode: Theme flag.
        top_n_edges: Number of strongest corridors to draw.
        title: Plot title.
        
    Returns:
        go.Figure: Plotly Scattergeo figure.
    """
    colors = get_theme_colors("Dark" if is_dark_mode else "Light")
    
    if len(G) == 0:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            template=colors["plotly_template"],
            annotations=[dict(text="No active network nodes for the selected threshold.", showarrow=False)]
        )
        return fig

    # Filter top N edges by weight
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2].get("weight", 0), reverse=True)[:top_n_edges]
    
    edge_traces = []
    max_w = max([d.get("weight", 1) for _, _, d in sorted_edges]) if sorted_edges else 1.0

    # Draw individual curved geodesic arcs
    for u, v, data in sorted_edges:
        if u in COUNTRY_CENTROIDS and v in COUNTRY_CENTROIDS:
            lat0, lon0 = COUNTRY_CENTROIDS[u]
            lat1, lon1 = COUNTRY_CENTROIDS[v]
            w = data.get("weight", 0)
            u_name = data.get("origin_name", u)
            v_name = data.get("dest_name", v)
            
            # Line thickness scaled between 1.0 and 4.5
            lw = 1.0 + 3.5 * (w / max_w)
            arc_color = "rgba(56, 189, 248, 0.65)" if is_dark_mode else "rgba(2, 132, 199, 0.55)"

            edge_traces.append(go.Scattergeo(
                lon=[lon0, lon1],
                lat=[lat0, lat1],
                mode="lines",
                line=dict(width=lw, color=arc_color),
                hoverinfo="text",
                text=f"{u_name} → {v_name}<br>Bilateral Stock: {w:,.0f}",
                showlegend=False
            ))

    # Node markers at country centroids
    node_lats = []
    node_lons = []
    node_hover = []
    node_labels = []
    
    for n in G.nodes():
        if n in COUNTRY_CENTROIDS:
            lat, lon = COUNTRY_CENTROIDS[n]
            node_lats.append(lat)
            node_lons.append(lon)
            c_name = G.nodes[n].get("name", n)
            in_w = sum(d.get("weight", 0) for _, _, d in G.in_edges(n, data=True))
            out_w = sum(d.get("weight", 0) for _, _, d in G.out_edges(n, data=True))
            node_hover.append(f"<b>{c_name} ({n})</b><br>In-Stock (Immigrants): {in_w:,.0f}<br>Out-Stock (Emigrants): {out_w:,.0f}")
            node_labels.append(n)

    node_trace = go.Scattergeo(
        lon=node_lons,
        lat=node_lats,
        text=node_labels,
        hoverinfo="text",
        hovertext=node_hover,
        mode="markers+text",
        textposition="top center",
        textfont=dict(size=8, color=colors["text_primary"]),
        marker=dict(
            size=6,
            color=colors["accent_teal"] if is_dark_mode else colors["accent_blue"],
            line=dict(width=1, color=colors["card_bg"])
        ),
        showlegend=False
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title=title,
        template=colors["plotly_template"],
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor=colors["map_land"],
            showocean=True,
            oceancolor=colors["map_ocean"],
            showcoastlines=True,
            coastlinecolor=colors["map_coastline"],
            showcountries=True,
            countrycolor=colors["map_coastline"],
            showframe=False
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=540,
        font=dict(family="Inter, sans-serif", color=colors["text_primary"])
    )
    return fig


def create_community_graph_plot(
    G: nx.DiGraph,
    node_comm_map: Dict[str, int],
    is_dark_mode: bool = False,
    title: str = "Migration Stock Community Clusters"
) -> go.Figure:
    """
    Generate a 2D network graph grouping and coloring countries by detected modularity community.
    
    Args:
        G: NetworkX graph.
        node_comm_map: Mapping from node ISO3 to community ID.
        is_dark_mode: Theme flag.
        title: Plot title.
        
    Returns:
        go.Figure: Plotly Community network graph.
    """
    colors = get_theme_colors("Dark" if is_dark_mode else "Light")
    
    if len(G) == 0 or not node_comm_map:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            template=colors["plotly_template"],
            annotations=[dict(text="No community partition available for the current graph.", showarrow=False)]
        )
        return fig

    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=60)
    
    # 1. Edge Traces
    edge_x = []
    edge_y = []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.8, color=colors["node_edge_color"]),
        hoverinfo="none",
        mode="lines"
    )

    # 2. Node Traces (group by community for discrete coloring)
    unique_comms = sorted(list(set(node_comm_map.values())))
    palette = px.colors.qualitative.Plotly if len(unique_comms) <= 10 else px.colors.qualitative.Alphabet
    
    comm_traces = [edge_trace]
    
    for idx, c_id in enumerate(unique_comms):
        c_nodes = [n for n in G.nodes() if node_comm_map.get(n) == c_id]
        if not c_nodes:
            continue
            
        c_color = palette[idx % len(palette)]
        nx_coords = [pos[n][0] for n in c_nodes]
        ny_coords = [pos[n][1] for n in c_nodes]
        n_names = [f"<b>{G.nodes[n].get('name', n)} ({n})</b><br>Community ID: {c_id}" for n in c_nodes]
        
        trace = go.Scatter(
            x=nx_coords,
            y=ny_coords,
            mode="markers+text",
            text=[n for n in c_nodes],
            textposition="top center",
            textfont=dict(size=8, color=colors["text_primary"]),
            hoverinfo="text",
            hovertext=n_names,
            name=f"Community {c_id} ({len(c_nodes)} countries)",
            marker=dict(
                size=12,
                color=c_color,
                line=dict(width=1.5, color=colors["card_bg"])
            )
        )
        comm_traces.append(trace)

    fig = go.Figure(data=comm_traces)
    fig.update_layout(
        title=title,
        template=colors["plotly_template"],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color=colors["text_primary"], size=10, family="Inter, sans-serif")
        ),
        hovermode="closest",
        margin=dict(b=40, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=560,
        font=dict(family="Inter, sans-serif", color=colors["text_primary"])
    )
    return fig
