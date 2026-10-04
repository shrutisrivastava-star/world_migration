"""
Pydantic schemas for Country Explorer profile endpoint.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CountryHistoryPoint(BaseModel):
    """Historical socioeconomic record for a country."""
    year: int = Field(..., description="Census observation round year")
    migrant_stock: Optional[float] = Field(None, description="Total foreign-born population residing in country")
    population: Optional[float] = Field(None, description="Total population")
    migrant_stock_pct_population: Optional[float] = Field(None, description="Migrant stock as % of population")
    stock_change_5yr: Optional[float] = Field(None, description="5-year absolute stock change")
    stock_growth_pct_5yr: Optional[float] = Field(None, description="5-year percentage growth")
    gdp_per_capita: Optional[float] = Field(None, description="GDP per capita (USD)")
    gdp: Optional[float] = Field(None, description="Total GDP (USD)")
    unemployment: Optional[float] = Field(None, description="Unemployment rate (%)")


class CountryCorridorItem(BaseModel):
    """Corridor breakdown item (inbound origin or outbound diaspora destination)."""
    rank: Optional[int] = Field(None, description="Rank position (1-10)")
    country_code: str = Field(..., description="Partner country ISO3 code")
    country_name: str = Field(..., description="Partner country display name")
    migrant_stock: float = Field(..., description="Bilateral migrant stock count")
    share_pct: Optional[float] = Field(None, description="Share percentage of total inbound/outbound stock")


class CountryProfileResponse(BaseModel):
    """Comprehensive country demographic dossier."""
    country_code: str = Field(..., description="Selected country ISO3 code")
    country_name: str = Field(..., description="Canonical country display name")
    year: int = Field(..., description="Census observation round year")
    immigrant_stock: float = Field(..., description="Total foreign-born residing in this country (inbound)")
    migrant_stock: float = Field(..., description="Synonym for immigrant_stock")
    total_population: float = Field(..., description="Total national population")
    migrant_pct_population: float = Field(..., description="Immigrant stock as % of population")
    emigrant_stock: float = Field(..., description="Total national diaspora residing abroad (outbound)")
    net_migrant_stock: float = Field(..., description="Net balance = immigrant_stock - emigrant_stock")
    gdp_per_capita: Optional[float] = Field(None, description="GDP per capita in USD")
    unemployment: Optional[float] = Field(None, description="Unemployment rate (%)")
    history: List[CountryHistoryPoint] = Field(default_factory=list, description="1990–2020 longitudinal history")
    top_inbound_origins: List[CountryCorridorItem] = Field(default_factory=list, description="Top 10 origins supplying foreign-born residents")
    top_outbound_destinations: List[CountryCorridorItem] = Field(default_factory=list, description="Top 10 destination hosts for national diaspora")
