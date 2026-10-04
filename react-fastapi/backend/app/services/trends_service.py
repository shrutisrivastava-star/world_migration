"""
Service layer for Longitudinal Trends queries.
"""

import math
from typing import List, Optional
from app.schemas.trends import (
    GlobalTrendResponse,
    GlobalTrendPoint,
    CountryTrendResponse,
    CountryTrendPoint,
)
from app.services.data_service import data_service
from src.dashboard_data import get_global_trend_data, get_country_trend_data


def _safe_float(val: Optional[float]) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


class TrendsService:
    """Service handling longitudinal trend time series."""

    def get_global_trend(self) -> GlobalTrendResponse:
        """
        Fetch global quinquennial migrant stock trajectory across 1990–2020.
        
        Returns:
            GlobalTrendResponse: 7 quinquennial observations.
        """
        df_merged = data_service.get_country_socioeconomic_data()
        df_global = get_global_trend_data(df_merged)

        points = []
        for _, row in df_global.iterrows():
            points.append(
                GlobalTrendPoint(
                    year=int(row["year"]),
                    total_migrant_stock=float(row["total_migrant_stock"]),
                    country_count=int(row["country_count"]),
                    total_population=float(row["total_population"]),
                    migrant_stock_pct_population=float(row["migrant_stock_pct_population"]),
                )
            )

        return GlobalTrendResponse(points=points)

    def get_country_trends(
        self, country_codes: List[str], metric_name: str = "Migrant Stock"
    ) -> CountryTrendResponse:
        """
        Fetch multi-country comparative time series.
        
        Args:
            country_codes: List of ISO3 codes (e.g. ['USA', 'IND', 'DEU'])
            metric_name: Selected metric name
            
        Returns:
            CountryTrendResponse: Formatted time series points.
        """
        df_merged = data_service.get_country_socioeconomic_data()
        df_trends = get_country_trend_data(
            df_merged, country_codes=country_codes, metric_name=metric_name
        )

        points = []
        for _, row in df_trends.iterrows():
            points.append(
                CountryTrendPoint(
                    display_name=str(row["display_name"]),
                    country_code=str(row["country_code"]),
                    year=int(row["year"]),
                    metric_value=_safe_float(row.get("metric_value")),
                    metric_label=str(row.get("metric_label", metric_name)),
                )
            )

        return CountryTrendResponse(
            metric_name=metric_name,
            countries=country_codes,
            points=points,
        )


trends_service = TrendsService()
