"""
Pydantic schemas for Community Detection endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CommunityNode(BaseModel):
    """Country node with assigned modularity community ID and coordinates."""
    country_code: str = Field(..., description="ISO3 country code")
    country_name: str = Field(..., description="Canonical country display name")
    community_id: int = Field(..., description="Assigned network-structural community cluster ID (1-indexed)")
    total_strength: float = Field(..., description="Total weighted degree (inbound + outbound migrant stock)")
    in_strength: float = Field(..., description="Inbound foreign-born migrant stock")
    out_strength: float = Field(..., description="Outbound emigrant diaspora stock")
    total_degree: int = Field(..., description="Total unweighted connections count")
    x: float = Field(..., description="2D Spring cluster X coordinate")
    y: float = Field(..., description="2D Spring cluster Y coordinate")


class CommunityEdge(BaseModel):
    """Corridor edge within or between communities."""
    origin_code: str = Field(..., description="Origin ISO3 code")
    destination_code: str = Field(..., description="Destination ISO3 code")
    weight: float = Field(..., description="Migrant stock weight")
    x0: float = Field(..., description="Origin X")
    y0: float = Field(..., description="Origin Y")
    x1: float = Field(..., description="Destination X")
    y1: float = Field(..., description="Destination Y")


class CommunityItem(BaseModel):
    """Summary of a detected network-structural migration community cluster."""
    community_id: int = Field(..., description="Community ID (1-indexed)")
    community_name: str = Field(..., description="Generated descriptive community title")
    size: int = Field(..., description="Number of sovereign country members")
    total_migrant_stock: float = Field(..., description="Total migrant stock residing in member countries")
    share_pct: float = Field(..., description="Share of global migrant stock (%)")
    top_anchor_countries: str = Field(..., description="Comma-separated leading anchor nations by network strength")
    member_codes: List[str] = Field(default_factory=list, description="List of member country ISO3 codes")
    members: List[str] = Field(default_factory=list, description="List of member country display names")


class CommunitiesResponse(BaseModel):
    """Full community detection partition response payload."""
    year: int = Field(..., description="Selected census round year")
    num_communities: int = Field(..., description="Total number of detected structural communities")
    modularity: float = Field(..., description="Modularity score of the graph partition")
    largest_community_size: int = Field(..., description="Member count of the largest community")
    largest_community_share: float = Field(..., description="Global migrant-stock share of the largest community (%)")
    communities: List[CommunityItem] = Field(..., description="Summary list of all detected communities")
    nodes: List[CommunityNode] = Field(..., description="Nodes with coordinates and community colors")
    edges: List[CommunityEdge] = Field(..., description="Top network edges for visualization")


class CommunityDetailResponse(BaseModel):
    """In-depth breakdown of a single selected community cluster."""
    community_id: int = Field(..., description="Community cluster ID")
    community_name: str = Field(..., description="Community name")
    size: int = Field(..., description="Number of member countries")
    total_migrant_stock: float = Field(..., description="Total migrant stock within community")
    share_pct: float = Field(..., description="Share of global migrant stock (%)")
    member_countries: List[str] = Field(default_factory=list, description="List of member country names")
    member_codes: List[str] = Field(default_factory=list, description="List of member country ISO3 codes")
    top_hubs: List[CommunityNode] = Field(default_factory=list, description="Leading network hubs in this community")
    internal_corridors: List[dict] = Field(default_factory=list, description="Top bilateral corridors inside this community")
