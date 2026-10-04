"""
Pydantic schemas for country entity and reference endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CountryItem(BaseModel):
    """Country or aggregate geographic entity item."""
    country_code: Optional[str] = Field(None, description="ISO3 alpha-3 country code or null for unmapped regions")
    display_name: str = Field(..., description="Clean canonical country display name")
    country_name: str = Field(..., description="Original UN DESA or World Bank country name")
    is_aggregate: bool = Field(False, description="Whether entity is a regional aggregate (True) or sovereign state (False)")


class CountriesResponse(BaseModel):
    """List of available country entities."""
    total: int = Field(..., description="Total number of entities returned")
    countries: List[CountryItem] = Field(..., description="List of country entities")
