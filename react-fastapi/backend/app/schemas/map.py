"""
Pydantic schemas for Global Choropleth Map endpoint.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MapCountryRecord(BaseModel):
    """Country-level record for choropleth mapping."""
    country_code: str = Field(..., description="ISO3 alpha-3 country code")
    display_name: str = Field(..., description="Canonical country display name")
    year: int = Field(..., description="Census observation round year")
    metric_value: Optional[float] = Field(None, description="Resolved numeric value for the requested metric")
    metric_label: str = Field(..., description="Display label for the metric")
    migrant_stock: Optional[float] = Field(None, description="Total international migrant stock count")
    population: Optional[float] = Field(None, description="Total population count")
    migrant_stock_pct_population: Optional[float] = Field(None, description="Migrant stock as % of population")
    stock_change_5yr: Optional[float] = Field(None, description="5-year absolute stock change")
    stock_growth_pct_5yr: Optional[float] = Field(None, description="5-year percentage growth")
    migrant_stock_global_rank: Optional[float] = Field(None, description="Global rank by migrant stock")
    gdp_per_capita: Optional[float] = Field(None, description="GDP per capita in current USD")
    gdp: Optional[float] = Field(None, description="Total GDP in current USD")
    unemployment: Optional[float] = Field(None, description="Total unemployment rate (%)")


class MapDataResponse(BaseModel):
    """Full choropleth map response payload."""
    year: int = Field(..., description="Target census observation round year")
    metric_name: str = Field(..., description="Selected metric name")
    total_countries: int = Field(..., description="Number of country records returned")
    data: List[MapCountryRecord] = Field(..., description="List of sovereign country map records")
