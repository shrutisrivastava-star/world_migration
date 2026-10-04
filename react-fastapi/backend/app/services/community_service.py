"""
Service layer for Community Detection and Cluster breakdowns.
"""

import math
from typing import Optional, List, Dict
import networkx as nx
import pandas as pd

from app.schemas.community import (
    CommunitiesResponse,
    CommunityItem,
    CommunityNode,
    CommunityEdge,
    CommunityDetailResponse,
)
from app.services.data_service import data_service
from src.network_analysis import (
    build_migration_network,
    calculate_network_metrics,
    detect_network_communities,
)
from src.dashboard_data import load_canonical_country_map


def _safe_float(val: Optional[float], default: float = 0.0) -> float:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return default
    try:
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return default


class CommunityService:
    """Service handling modularity-based community detection queries."""

    def get_communities(self, year: int = 2020, top_n_edges: int = 150) -> CommunitiesResponse:
        """
        Execute community detection on the bilateral migration stock graph.
        
        Args:
            year: Census observation round year
            top_n_edges: Number of edges to include in graph for community partitioning
            
        Returns:
            CommunitiesResponse: Detected communities list, modularity score, and 2D node coordinates.
        """
        df_bilateral = data_service.get_bilateral_corridor_data()
        name_map = load_canonical_country_map()

        G = build_migration_network(
            df_bilateral,
            year=year,
            top_n_edges=top_n_edges,
            sovereign_only=True,
            directed=True,
        )

        if len(G) < 2:
            return CommunitiesResponse(
                year=year,
                num_communities=0,
                modularity=0.0,
                largest_community_size=0,
                largest_community_share=0.0,
                communities=[],
                nodes=[],
                edges=[],
            )

        node_comm_map, df_summary, modularity = detect_network_communities(G)
        df_metrics = calculate_network_metrics(G)
        metrics_lookup = df_metrics.set_index("country_code").to_dict(orient="index") if not df_metrics.empty else {}

        # 2D coordinates for visualization
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=60)

        # Compute total stock represented in graph
        total_graph_stock = sum(d.get("weight", 0.0) for _, _, d in G.edges(data=True))

        # Build community items
        communities: List[CommunityItem] = []
        for _, row in df_summary.iterrows():
            c_id = int(row["community_id"])
            m_codes = list(row.get("member_codes", []))
            
            # Compute total migrant stock associated with this community's members
            comm_stock = sum(
                metrics_lookup.get(c, {}).get("in_strength", 0.0) for c in m_codes
            )
            share_pct = (comm_stock / total_graph_stock * 100.0) if total_graph_stock > 0 else 0.0

            communities.append(
                CommunityItem(
                    community_id=c_id,
                    community_name=str(row["community_name"]),
                    size=int(row["size"]),
                    total_migrant_stock=_safe_float(comm_stock),
                    share_pct=_safe_float(share_pct),
                    top_anchor_countries=str(row["top_anchor_countries"]),
                    member_codes=m_codes,
                    members=[name_map.get(code, code) for code in m_codes],
                )
            )

        # Build nodes
        nodes: List[CommunityNode] = []
        for n in G.nodes():
            c_name = name_map.get(n, G.nodes[n].get("name", n))
            comm_id = node_comm_map.get(n, 1)
            m = metrics_lookup.get(n, {})
            x, y = pos.get(n, (0.0, 0.0))

            nodes.append(
                CommunityNode(
                    country_code=n,
                    country_name=c_name,
                    community_id=int(comm_id),
                    total_strength=_safe_float(m.get("total_strength")),
                    in_strength=_safe_float(m.get("in_strength")),
                    out_strength=_safe_float(m.get("out_strength")),
                    total_degree=int(m.get("total_degree", G.degree(n))),
                    x=float(x),
                    y=float(y),
                )
            )

        # Build edges
        edges: List[CommunityEdge] = []
        for u, v, data in G.edges(data=True):
            x0, y0 = pos.get(u, (0.0, 0.0))
            x1, y1 = pos.get(v, (0.0, 0.0))
            edges.append(
                CommunityEdge(
                    origin_code=u,
                    destination_code=v,
                    weight=_safe_float(data.get("weight", 0.0)),
                    x0=float(x0),
                    y0=float(y0),
                    x1=float(x1),
                    y1=float(y1),
                )
            )

        largest_size = communities[0].size if communities else 0
        largest_share = communities[0].share_pct if communities else 0.0

        return CommunitiesResponse(
            year=year,
            num_communities=len(communities),
            modularity=_safe_float(modularity),
            largest_community_size=largest_size,
            largest_community_share=largest_share,
            communities=communities,
            nodes=nodes,
            edges=edges,
        )

    def get_community_detail(
        self, community_id: int, year: int = 2020, top_n_edges: int = 150
    ) -> CommunityDetailResponse:
        """
        Retrieve member breakdown, top hubs, and internal bilateral corridors for a community.
        """
        all_comm = self.get_communities(year=year, top_n_edges=top_n_edges)
        target = next((c for c in all_comm.communities if c.community_id == community_id), None)

        if not target:
            # Fallback to first community if ID not found
            target = all_comm.communities[0] if all_comm.communities else None

        if not target:
            return CommunityDetailResponse(
                community_id=community_id,
                community_name=f"Community {community_id}",
                size=0,
                total_migrant_stock=0.0,
                share_pct=0.0,
                member_countries=[],
                member_codes=[],
                top_hubs=[],
                internal_corridors=[],
            )

        member_set = set(target.member_codes)
        top_hubs = [n for n in all_comm.nodes if n.country_code in member_set]
        top_hubs.sort(key=lambda x: x.total_strength, reverse=True)

        # Extract internal corridors within this community
        df_bilateral = data_service.get_bilateral_corridor_data()
        name_map = load_canonical_country_map()

        df_internal = df_bilateral[
            (df_bilateral["year"] == year) &
            (df_bilateral["origin_code"].isin(member_set)) &
            (df_bilateral["destination_code"].isin(member_set)) &
            (~df_bilateral.get("is_aggregate_route", False)) &
            (df_bilateral["migrant_stock"] > 0)
        ].sort_values("migrant_stock", ascending=False).head(10)

        internal_corrs = []
        for idx, row in df_internal.iterrows():
            orig = str(row["origin_code"])
            dest = str(row["destination_code"])
            internal_corrs.append({
                "rank": len(internal_corrs) + 1,
                "corridor_label": f"{name_map.get(orig, orig)} → {name_map.get(dest, dest)}",
                "origin_name": name_map.get(orig, orig),
                "origin_code": orig,
                "dest_name": name_map.get(dest, dest),
                "destination_code": dest,
                "migrant_stock": float(row["migrant_stock"]),
            })

        return CommunityDetailResponse(
            community_id=target.community_id,
            community_name=target.community_name,
            size=target.size,
            total_migrant_stock=target.total_migrant_stock,
            share_pct=target.share_pct,
            member_countries=target.members,
            member_codes=target.member_codes,
            top_hubs=top_hubs[:10],
            internal_corridors=internal_corrs,
        )


community_service = CommunityService()
