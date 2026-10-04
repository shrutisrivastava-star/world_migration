"""
Pydantic schemas for Longitudinal Trends endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GlobalTrendPoint(BaseModel):
    """Global aggregate demographic data point for a census round."""
    year: int = Field(..., description="Census observation round year")
    total_migrant_stock: float = Field(..., description="Global total international migrant stock")
    country_count: int = Field(..., description="Number of sovereign nations with records")
    total_population: float = Field(..., description="Global total sovereign population")
    migrant_stock_pct_population: float = Field(..., description="Migrant stock as % of world population")


class GlobalTrendResponse(BaseModel):
    """Global longitudinal trend response."""
    points: List[GlobalTrendPoint] = Field(..., description="Quinquennial data points from 1990 to 2020")


class CountryTrendPoint(BaseModel):
    """Single country temporal observation."""
    display_name: str = Field(..., description="Country display name")
    country_code: str = Field(..., description="ISO3 country code")
    year: int = Field(..., description="Census observation round year")
    metric_value: Optional[float] = Field(None, description="Numeric metric value for the year")
    metric_label: str = Field(..., description="Display label for the metric")


class CountryTrendResponse(BaseModel):
    """Multi-country comparative trend response."""
    metric_name: str = Field(..., description="Selected metric name")
    countries: List[str] = Field(..., description="List of ISO3 codes queried")
    points: List[CountryTrendPoint] = Field(..., description="Longitudinal observations for selected countries")
