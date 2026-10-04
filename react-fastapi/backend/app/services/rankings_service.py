"""
Service layer for Country Rankings queries.
"""

import math
from typing import Optional
from app.schemas.rankings import RankingsResponse, RankingItem
from app.services.data_service import data_service
from src.dashboard_data import get_rankings_data


def _safe_float(val: Optional[float]) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


class RankingsService:
    """Service handling country rankings."""

    def get_rankings(
        self,
        year: int,
        metric_name: str = "Migrant Stock",
        top_n: int = 10,
        ascending: bool = False,
    ) -> RankingsResponse:
        """
        Compute ranked list of sovereign countries.
        
        Args:
            year: Census round year (1990–2020)
            metric_name: Metric to rank by
            top_n: Number of countries to return
            ascending: Sort order (False for highest first)
            
        Returns:
            RankingsResponse: Ordered list of country rankings.
        """
        df_merged = data_service.get_country_socioeconomic_data()
        df_rank = get_rankings_data(
            df_merged,
            year=year,
            metric_name=metric_name,
            top_n=top_n,
            ascending=ascending,
        )

        rankings = []
        for _, row in df_rank.iterrows():
            rankings.append(
                RankingItem(
                    rank=int(row["rank"]),
                    display_name=str(row["display_name"]),
                    country_code=str(row["country_code"]),
                    year=int(row["year"]),
                    metric_value=_safe_float(row.get("metric_value")),
                    metric_label=str(row.get("metric_label", metric_name)),
                    migrant_stock=_safe_float(row.get("migrant_stock")),
                    population=_safe_float(row.get("population")),
                    migrant_stock_pct_population=_safe_float(row.get("migrant_stock_pct_population")),
                    stock_change_5yr=_safe_float(row.get("stock_change_5yr")),
                    stock_growth_pct_5yr=_safe_float(row.get("stock_growth_pct_5yr")),
                    gdp_per_capita=_safe_float(row.get("gdp_per_capita")),
                )
            )

        return RankingsResponse(
            year=year,
            metric_name=metric_name,
            top_n=top_n,
            ascending=ascending,
            rankings=rankings,
        )


rankings_service = RankingsService()
