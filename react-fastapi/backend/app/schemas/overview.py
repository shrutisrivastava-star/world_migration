"""
Pydantic schemas for executive overview KPI endpoints.
"""

from pydantic import BaseModel, Field


class OverviewKPIsResponse(BaseModel):
    """Executive KPI summary schema for a selected census round year."""
    year: int = Field(..., description="Target census round year (e.g. 2020)")
    total_migrant_stock: float = Field(..., description="Global total international migrant stock (sovereign states)")
    total_population: float = Field(..., description="Global total population across sovereign states")
    global_migrant_pct: float = Field(..., description="Migrants as a percentage of global population")
    num_countries: int = Field(..., description="Number of sovereign nations with available data")
    top_destination_name: str = Field(..., description="Top destination country by residing migrant stock")
    top_destination_stock: float = Field(..., description="Migrant stock of top destination country")
    top_share_name: str = Field(..., description="Country with highest migrant stock as % of population")
    top_share_pct: float = Field(..., description="Highest migrant percentage of population")
    num_corridors: int = Field(..., description="Number of active bilateral corridors with > 0 migrants")
