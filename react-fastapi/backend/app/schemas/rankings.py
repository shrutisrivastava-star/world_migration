"""
Pydantic schemas for Country Rankings endpoint.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RankingItem(BaseModel):
    """Ranked country entry."""
    rank: int = Field(..., description="Rank position (1-indexed)")
    display_name: str = Field(..., description="Canonical country display name")
    country_code: str = Field(..., description="ISO3 country code")
    year: int = Field(..., description="Census observation round year")
    metric_value: Optional[float] = Field(None, description="Resolved metric value")
    metric_label: str = Field(..., description="Display label for the ranking metric")
    migrant_stock: Optional[float] = Field(None, description="Total international migrant stock")
    population: Optional[float] = Field(None, description="Total population count")
    migrant_stock_pct_population: Optional[float] = Field(None, description="Migrant stock as % of population")
    stock_change_5yr: Optional[float] = Field(None, description="5-year absolute change in migrant stock")
    stock_growth_pct_5yr: Optional[float] = Field(None, description="5-year percentage growth")
    gdp_per_capita: Optional[float] = Field(None, description="GDP per capita in USD")


class RankingsResponse(BaseModel):
    """Full country rankings response payload."""
    year: int = Field(..., description="Census round year")
    metric_name: str = Field(..., description="Ranking metric name")
    top_n: int = Field(..., description="Number of top ranked countries requested")
    ascending: bool = Field(..., description="Sort order: False for highest first, True for lowest")
    rankings: List[RankingItem] = Field(..., description="List of ranked sovereign country records")
