"""
Service layer for Global Choropleth Map queries.
"""

import math
from typing import Optional
from app.schemas.map import MapDataResponse, MapCountryRecord
from app.services.data_service import data_service
from src.dashboard_data import get_map_data, METRIC_COLUMN_MAP


def _safe_float(val: Optional[float]) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


class MapService:
    """Service handling choropleth map queries."""

    def get_map(self, year: int, metric_name: str = "Migrant Stock") -> MapDataResponse:
        """
        Fetch country records for choropleth world map.
        
        Args:
            year: Census round year (1990–2020)
            metric_name: Selected metric name
            
        Returns:
            MapDataResponse: Formatted payload of sovereign country records.
        """
        df_merged = data_service.get_country_socioeconomic_data()
        df_map = get_map_data(df_merged, year=year, metric_name=metric_name)

        records = []
        for _, row in df_map.iterrows():
            records.append(
                MapCountryRecord(
                    country_code=str(row["country_code"]),
                    display_name=str(row["display_name"]),
                    year=int(row["year"]),
                    metric_value=_safe_float(row.get("metric_value")),
                    metric_label=str(row.get("metric_label", metric_name)),
                    migrant_stock=_safe_float(row.get("migrant_stock")),
                    population=_safe_float(row.get("population")),
                    migrant_stock_pct_population=_safe_float(row.get("migrant_stock_pct_population")),
                    stock_change_5yr=_safe_float(row.get("stock_change_5yr")),
                    stock_growth_pct_5yr=_safe_float(row.get("stock_growth_pct_5yr")),
                    migrant_stock_global_rank=_safe_float(row.get("migrant_stock_global_rank")),
                    gdp_per_capita=_safe_float(row.get("gdp_per_capita")),
                    gdp=_safe_float(row.get("gdp")),
                    unemployment=_safe_float(row.get("unemployment")),
                )
            )

        return MapDataResponse(
            year=year,
            metric_name=metric_name,
            total_countries=len(records),
            data=records,
        )


map_service = MapService()
