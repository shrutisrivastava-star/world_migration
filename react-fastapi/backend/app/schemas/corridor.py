"""
Pydantic schemas for Corridor Analysis & Concentration endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CorridorRankingItem(BaseModel):
    """Ranked bilateral migration corridor record."""
    rank: int = Field(..., description="Corridor rank (1-indexed)")
    corridor_label: str = Field(..., description="Corridor string formatted as 'Origin → Destination'")
    origin_display_name: str = Field(..., description="Origin country display name")
    origin_code: str = Field(..., description="Origin ISO3 code")
    dest_display_name: str = Field(..., description="Destination country display name")
    destination_code: str = Field(..., description="Destination ISO3 code")
    year: int = Field(..., description="Census observation round year")
    migrant_stock: float = Field(..., description="Estimated bilateral migrant stock count")
    share_of_total: float = Field(..., description="Share of global bilateral stock (%)")


class CorridorConcentrationPoint(BaseModel):
    """Longitudinal corridor concentration shares for a census round."""
    year: int = Field(..., description="Census observation round year")
    total_corridor_stock: float = Field(..., description="Total bilateral migrant stock across all corridors")
    active_corridor_count: int = Field(..., description="Number of active bilateral corridors (> 0 stock)")
    top_10_corridor_share: float = Field(..., description="Share of total stock in top 10 corridors (%)")
    top_25_corridor_share: float = Field(..., description="Share of total stock in top 25 corridors (%)")
    top_50_corridor_share: float = Field(..., description="Share of total stock in top 50 corridors (%)")
    largest_corridor: str = Field(..., description="Single largest global corridor label")


class CorridorTrajectoryPoint(BaseModel):
    """Historical stock for a bilateral corridor at a census round."""
    year: int = Field(..., description="Census round year")
    migrant_stock: float = Field(..., description="Bilateral migrant stock count")


class CorridorDetailResponse(BaseModel):
    """Comprehensive detail and trajectory for a single bilateral corridor."""
    origin_code: str = Field(..., description="Origin ISO3 code")
    destination_code: str = Field(..., description="Destination ISO3 code")
    origin_name: str = Field(..., description="Origin country display name")
    destination_name: str = Field(..., description="Destination country display name")
    corridor_label: str = Field(..., description="Corridor label formatted as 'Origin → Destination'")
    year: int = Field(..., description="Selected census round year")
    current_stock: Optional[float] = Field(None, description="Migrant stock count for the selected year")
    global_rank: Optional[int] = Field(None, description="Global ranking among all bilateral corridors")
    share_of_global: Optional[float] = Field(None, description="Share of global bilateral migrant stock (%)")
    pct_change_5yr: Optional[float] = Field(None, description="5-year percentage stock growth (%)")
    classification: str = Field(..., description="Deterministic trajectory classification ('Emerging', 'Persistent', 'Declining', 'Stable', 'No Baseline')")
    history: List[CorridorTrajectoryPoint] = Field(default_factory=list, description="1990–2020 longitudinal trajectory")
    top_corridors: List[CorridorRankingItem] = Field(default_factory=list, description="Top comparative global corridors")


class CorridorOverviewResponse(BaseModel):
    """Corridor analysis overview response payload."""
    year: int = Field(..., description="Selected census round year")
    total_corridors: int = Field(..., description="Total active bilateral corridors count")
    top_corridor: str = Field(..., description="Single largest corridor name")
    top_corridor_stock: float = Field(..., description="Migrant stock in the top corridor")
    top_10_share: float = Field(..., description="Percentage of global stock in top 10 corridors (%)")
    concentration_trend: List[CorridorConcentrationPoint] = Field(default_factory=list, description="1990–2020 concentration trend points")
    top_corridors: List[CorridorRankingItem] = Field(default_factory=list, description="Top ranked corridors for selected year")
