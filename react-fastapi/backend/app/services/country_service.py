"""
Service layer for Country Explorer profile dossiers.
"""

import math
from typing import Optional
from app.schemas.country import (
    CountryProfileResponse,
    CountryHistoryPoint,
    CountryCorridorItem,
)
from app.services.data_service import data_service
from src.dashboard_data import get_country_profile_data, load_canonical_country_map


def _safe_float(val: Optional[float]) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


class CountryService:
    """Service handling country profile queries."""

    def get_profile(self, country_code: str, year: int = 2020) -> CountryProfileResponse:
        """
        Generate detailed demographic profile dossier for a country.
        
        Args:
            country_code: Country ISO3 alpha-3 code (e.g. 'USA')
            year: Selected census round year
            
        Returns:
            CountryProfileResponse: Full country profile payload.
        """
        df_merged = data_service.get_country_socioeconomic_data()
        df_bilateral = data_service.get_bilateral_corridor_data()
        name_map = load_canonical_country_map()

        res = get_country_profile_data(
            df_merged=df_merged,
            df_bilateral=df_bilateral,
            country_code=country_code,
            year=year,
        )

        curr_stats = res.get("current_stats", {})
        df_history = res.get("history_df")
        inbound_df = res.get("inbound_corridors")
        outbound_df = res.get("outbound_corridors")

        # Parse longitudinal history
        history_points = []
        if df_history is not None and not df_history.empty:
            for _, row in df_history.iterrows():
                history_points.append(
                    CountryHistoryPoint(
                        year=int(row["year"]),
                        migrant_stock=_safe_float(row.get("migrant_stock")),
                        population=_safe_float(row.get("population")),
                        migrant_stock_pct_population=_safe_float(row.get("migrant_stock_pct_population")),
                        stock_change_5yr=_safe_float(row.get("stock_change_5yr")),
                        stock_growth_pct_5yr=_safe_float(row.get("stock_growth_pct_5yr")),
                        gdp_per_capita=_safe_float(row.get("gdp_per_capita")),
                        gdp=_safe_float(row.get("gdp")),
                        unemployment=_safe_float(row.get("unemployment")),
                    )
                )

        # Parse top inbound origins
        inbound_items = []
        if inbound_df is not None and not inbound_df.empty:
            rank = 1
            for _, row in inbound_df.iterrows():
                o_code = str(row["origin_code"])
                inbound_items.append(
                    CountryCorridorItem(
                        rank=rank,
                        country_code=o_code,
                        country_name=name_map.get(o_code, str(row.get("origin_display_name", o_code))),
                        migrant_stock=float(row["migrant_stock"]),
                        share_pct=_safe_float(row.get("dest_corridor_share_pct")),
                    )
                )
                rank += 1

        # Parse top outbound destinations
        outbound_items = []
        if outbound_df is not None and not outbound_df.empty:
            rank = 1
            for _, row in outbound_df.iterrows():
                d_code = str(row["destination_code"])
                outbound_items.append(
                    CountryCorridorItem(
                        rank=rank,
                        country_code=d_code,
                        country_name=name_map.get(d_code, str(row.get("dest_display_name", d_code))),
                        migrant_stock=float(row["migrant_stock"]),
                        share_pct=_safe_float(row.get("origin_corridor_share_pct")),
                    )
                )
                rank += 1

        country_name = name_map.get(country_code, curr_stats.get("display_name", country_code))

        return CountryProfileResponse(
            country_code=country_code,
            country_name=country_name,
            year=year,
            immigrant_stock=float(res.get("immigrant_stock", 0.0)),
            migrant_stock=float(res.get("immigrant_stock", 0.0)),
            total_population=float(res.get("total_population", 0.0)),
            migrant_pct_population=float(res.get("migrant_pct_population", 0.0)),
            emigrant_stock=float(res.get("emigrant_stock", 0.0)),
            net_migrant_stock=float(res.get("net_migrant_stock", 0.0)),
            gdp_per_capita=_safe_float(curr_stats.get("gdp_per_capita")),
            unemployment=_safe_float(curr_stats.get("unemployment")),
            history=history_points,
            top_inbound_origins=inbound_items,
            top_outbound_destinations=outbound_items,
        )


country_service = CountryService()
