"""
Countries Service module.
Handles queries for available country entities, regional aggregates, and ISO mappings.
"""

from typing import List
import pandas as pd
from app.services.data_service import data_service
from app.schemas.countries import CountryItem, CountriesResponse


class CountriesService:
    """Service for querying country metadata and lists."""

    def get_all_countries(self, sovereign_only: bool = False) -> CountriesResponse:
        """
        Retrieve all distinct countries / entities in the observatory.
        
        Args:
            sovereign_only: If True, returns only sovereign states.
            
        Returns:
            CountriesResponse: Structured country response list.
        """
        df = data_service.get_country_socioeconomic_data()
        
        # Deduplicate by country_code and country name
        entities_df = df[["country_code", "country", "display_name", "is_aggregate"]].drop_duplicates()
        
        if sovereign_only:
            entities_df = entities_df[~entities_df["is_aggregate"] & entities_df["country_code"].notna()]
            
        # Sort by display_name
        entities_df = entities_df.sort_values("display_name")
        
        items: List[CountryItem] = []
        for _, row in entities_df.iterrows():
            code = str(row["country_code"]) if pd.notna(row["country_code"]) else None
            items.append(
                CountryItem(
                    country_code=code,
                    display_name=str(row["display_name"]),
                    country_name=str(row["country"]),
                    is_aggregate=bool(row["is_aggregate"]),
                )
            )
            
        return CountriesResponse(
            total=len(items),
            countries=items
        )


countries_service = CountriesService()
