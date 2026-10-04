"""
Pydantic schemas for Migration Network analysis endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class NetworkNode(BaseModel):
    """Country node in the migration stock graph."""
    country_code: str = Field(..., description="ISO3 alpha-3 country code")
    country_name: str = Field(..., description="Canonical country display name")
    in_degree: int = Field(..., description="Number of inbound origin corridors")
    out_degree: int = Field(..., description="Number of outbound destination corridors")
    total_degree: int = Field(..., description="Total degree (in + out)")
    in_strength: float = Field(..., description="Total inbound foreign-born migrant stock")
    out_strength: float = Field(..., description="Total outbound emigrant diaspora stock")
    total_strength: float = Field(..., description="Total weighted degree (inbound + outbound)")
    degree_centrality: float = Field(..., description="Normalized degree centrality")
    betweenness_centrality: float = Field(..., description="Betweenness centrality")
    pagerank: float = Field(..., description="Weighted PageRank score")
    x: float = Field(..., description="Force-directed Spring layout 2D X coordinate")
    y: float = Field(..., description="Force-directed Spring layout 2D Y coordinate")
    circ_x: float = Field(..., description="Circular layout 2D X coordinate")
    circ_y: float = Field(..., description="Circular layout 2D Y coordinate")


class NetworkEdge(BaseModel):
    """Bilateral migration stock edge between origin and destination."""
    origin_code: str = Field(..., description="Origin ISO3 code")
    origin_name: str = Field(..., description="Origin country display name")
    destination_code: str = Field(..., description="Destination ISO3 code")
    destination_name: str = Field(..., description="Destination country display name")
    migrant_stock: float = Field(..., description="Estimated mid-year migrant stock")
    origin_share: Optional[float] = Field(None, description="Share of origin's total diaspora (%)")
    dest_share: Optional[float] = Field(None, description="Share of destination's total foreign-born (%)")
    x0: float = Field(..., description="Origin Spring X")
    y0: float = Field(..., description="Origin Spring Y")
    x1: float = Field(..., description="Destination Spring X")
    y1: float = Field(..., description="Destination Spring Y")
    circ_x0: float = Field(..., description="Origin Circular X")
    circ_y0: float = Field(..., description="Origin Circular Y")
    circ_x1: float = Field(..., description="Destination Circular X")
    circ_y1: float = Field(..., description="Destination Circular Y")


class NetworkOverviewResponse(BaseModel):
    """Full migration stock network graph response payload."""
    year: int = Field(..., description="Census observation round year")
    top_n_edges: int = Field(..., description="Top N bilateral corridors filter threshold")
    node_count: int = Field(..., description="Total number of nodes (countries)")
    edge_count: int = Field(..., description="Total number of edges (corridors)")
    total_observed_stock: float = Field(..., description="Total migrant stock represented in graph")
    network_density: float = Field(..., description="Directed graph density")
    nodes: List[NetworkNode] = Field(..., description="List of country nodes with metrics and coordinates")
    edges: List[NetworkEdge] = Field(..., description="List of bilateral corridors with coordinates")
    top_hubs: List[NetworkNode] = Field(..., description="Top ranked network hubs by weighted strength")
