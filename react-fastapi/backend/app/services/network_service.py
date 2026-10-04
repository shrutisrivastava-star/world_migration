"""
Service layer for Migration Network graph construction, centrality metrics, and 2D layouts.
"""

import math
from typing import Optional, List
import networkx as nx
import pandas as pd

from app.schemas.network import NetworkOverviewResponse, NetworkNode, NetworkEdge
from app.services.data_service import data_service
from src.network_analysis import build_migration_network, calculate_network_metrics


def _safe_float(val: Optional[float], default: float = 0.0) -> float:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return default
    try:
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return default


class NetworkService:
    """Service handling migration network graph queries and layouts."""

    def get_network(
        self,
        year: int = 2020,
        top_n_edges: int = 100,
        min_stock: Optional[float] = None,
    ) -> NetworkOverviewResponse:
        """
        Build migration stock network and compute centrality metrics and 2D layouts.
        
        Args:
            year: Census observation round year
            top_n_edges: Number of strongest bilateral corridors to retain in graph
            min_stock: Optional minimum bilateral migrant stock threshold
            
        Returns:
            NetworkOverviewResponse: Graph nodes, edges, summary stats, and hub rankings.
        """
        df_bilateral = data_service.get_bilateral_corridor_data()

        G = build_migration_network(
            df_bilateral,
            year=year,
            min_stock=min_stock,
            top_n_edges=top_n_edges,
            sovereign_only=True,
            directed=True,
        )

        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()

        if node_count == 0 or edge_count == 0:
            return NetworkOverviewResponse(
                year=year,
                top_n_edges=top_n_edges,
                node_count=0,
                edge_count=0,
                total_observed_stock=0.0,
                network_density=0.0,
                nodes=[],
                edges=[],
                top_hubs=[],
            )

        # 1. Compute node centralities & metrics
        df_metrics = calculate_network_metrics(G)
        metric_lookup = df_metrics.set_index("country_code").to_dict(orient="index") if not df_metrics.empty else {}

        # 2. Compute deterministic layouts (Spring & Circular)
        pos_spring = nx.spring_layout(G, seed=42, k=0.45, iterations=60)
        pos_circ = nx.circular_layout(G)

        # 3. Build Nodes
        nodes: List[NetworkNode] = []
        for n in G.nodes():
            c_name = G.nodes[n].get("name", n)
            m = metric_lookup.get(n, {})
            sx, sy = pos_spring.get(n, (0.0, 0.0))
            cx, cy = pos_circ.get(n, (0.0, 0.0))

            nodes.append(
                NetworkNode(
                    country_code=n,
                    country_name=c_name,
                    in_degree=int(m.get("in_degree", G.in_degree(n))),
                    out_degree=int(m.get("out_degree", G.out_degree(n))),
                    total_degree=int(m.get("total_degree", G.degree(n))),
                    in_strength=_safe_float(m.get("in_strength")),
                    out_strength=_safe_float(m.get("out_strength")),
                    total_strength=_safe_float(m.get("total_strength")),
                    degree_centrality=_safe_float(m.get("degree_centrality")),
                    betweenness_centrality=_safe_float(m.get("betweenness_centrality")),
                    pagerank=_safe_float(m.get("pagerank")),
                    x=float(sx),
                    y=float(sy),
                    circ_x=float(cx),
                    circ_y=float(cy),
                )
            )

        # 4. Build Edges
        edges: List[NetworkEdge] = []
        total_observed_stock = 0.0

        for u, v, data in G.edges(data=True):
            w = _safe_float(data.get("weight", 0.0))
            total_observed_stock += w
            u_name = data.get("origin_name", G.nodes[u].get("name", u))
            v_name = data.get("dest_name", G.nodes[v].get("name", v))
            
            x0, y0 = pos_spring.get(u, (0.0, 0.0))
            x1, y1 = pos_spring.get(v, (0.0, 0.0))
            cx0, cy0 = pos_circ.get(u, (0.0, 0.0))
            cx1, cy1 = pos_circ.get(v, (0.0, 0.0))

            orig_sh = _safe_float(data.get("origin_share")) if "origin_share" in data else None
            dest_sh = _safe_float(data.get("dest_share")) if "dest_share" in data else None

            edges.append(
                NetworkEdge(
                    origin_code=u,
                    origin_name=u_name,
                    destination_code=v,
                    destination_name=v_name,
                    migrant_stock=w,
                    origin_share=orig_sh,
                    dest_share=dest_sh,
                    x0=float(x0),
                    y0=float(y0),
                    x1=float(x1),
                    y1=float(y1),
                    circ_x0=float(cx0),
                    circ_y0=float(cy0),
                    circ_x1=float(cx1),
                    circ_y1=float(cy1),
                )
            )

        # Sort top hubs by total strength
        top_hubs = sorted(nodes, key=lambda node: node.total_strength, reverse=True)[:15]
        density = float(nx.density(G)) if node_count > 1 else 0.0

        return NetworkOverviewResponse(
            year=year,
            top_n_edges=top_n_edges,
            node_count=node_count,
            edge_count=edge_count,
            total_observed_stock=total_observed_stock,
            network_density=density,
            nodes=nodes,
            edges=edges,
            top_hubs=top_hubs,
        )


network_service = NetworkService()
