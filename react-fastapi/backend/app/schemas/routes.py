"""
Pydantic schemas for Bilateral Routes & Corridors endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CorridorItem(BaseModel):
    """Bilateral migration corridor entry."""
    rank: Optional[int] = Field(None, description="Rank position")
    corridor_label: str = Field(..., description="Corridor text formatted as 'Origin → Destination'")
    origin_display_name: str = Field(..., description="Canonical origin country name")
    origin_code: str = Field(..., description="Origin ISO3 code")
    dest_display_name: str = Field(..., description="Canonical destination country name")
    destination_code: str = Field(..., description="Destination ISO3 code")
    year: int = Field(..., description="Census observation round year")
    migrant_stock: float = Field(..., description="Estimated migrant stock residing in destination from origin")
    origin_corridor_share_pct: Optional[float] = Field(None, description="% of origin's total emigrant diaspora")
    dest_corridor_share_pct: Optional[float] = Field(None, description="% of destination's total foreign-born stock")


class RouteHistoryPoint(BaseModel):
    """Historical bilateral migrant stock data point across census rounds."""
    year: int = Field(..., description="Census round year")
    migrant_stock: float = Field(..., description="Bilateral migrant stock count")
    origin_corridor_share_pct: Optional[float] = Field(None, description="Share of total outbound emigrants (%)")
    dest_corridor_share_pct: Optional[float] = Field(None, description="Share of total inbound immigrants (%)")


class RouteResponse(BaseModel):
    """Bilateral route query response payload."""
    year: int = Field(..., description="Selected census round year")
    origin_code: Optional[str] = Field(None, description="Origin ISO3 code")
    destination_code: Optional[str] = Field(None, description="Destination ISO3 code")
    origin_name: Optional[str] = Field(None, description="Origin country display name")
    destination_name: Optional[str] = Field(None, description="Destination country display name")
    corridor_label: Optional[str] = Field(None, description="Route label")
    current_stock: Optional[float] = Field(None, description="Migrant stock count for the selected year")
    history: List[RouteHistoryPoint] = Field(default_factory=list, description="Historical 1990–2020 trajectory")
    top_corridors: List[CorridorItem] = Field(default_factory=list, description="Top bilateral corridors for the year")
