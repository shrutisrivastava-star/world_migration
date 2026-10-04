"""
Service layer for Bilateral Routes & Corridors queries.
"""

import math
from typing import Optional
from app.schemas.routes import RouteResponse, RouteHistoryPoint, CorridorItem
from app.services.data_service import data_service
from src.dashboard_data import get_top_global_corridors, get_filtered_corridors, load_canonical_country_map


def _safe_float(val: Optional[float]) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


class RoutesService:
    """Service handling bilateral routes and top corridors."""

    def get_routes(
        self,
        year: int = 2020,
        origin_code: Optional[str] = None,
        destination_code: Optional[str] = None,
        top_n: int = 20,
    ) -> RouteResponse:
        """
        Query route metrics, history, and top corridors.
        
        Args:
            year: Selected census round year
            origin_code: Optional origin ISO3
            destination_code: Optional destination ISO3
            top_n: Number of top corridors to return
            
        Returns:
            RouteResponse: Route data, historical trajectory, and top corridors list.
        """
        df_bilateral = data_service.get_bilateral_corridor_data()
        name_map = load_canonical_country_map()

        origin_name = name_map.get(origin_code, origin_code) if origin_code else None
        destination_name = name_map.get(destination_code, destination_code) if destination_code else None
        corridor_label = f"{origin_name} → {destination_name}" if (origin_name and destination_name) else None

        # Fetch top corridors for the year (filtered or global)
        if (origin_code and origin_code != "All") or (destination_code and destination_code != "All"):
            df_corridors = get_filtered_corridors(
                df_bilateral,
                year=year,
                origin_code=origin_code,
                dest_code=destination_code,
                top_n=top_n,
            )
        else:
            df_corridors = get_top_global_corridors(df_bilateral, year=year, top_n=top_n)

        top_corridors = []
        for _, row in df_corridors.iterrows():
            top_corridors.append(
                CorridorItem(
                    rank=int(row["rank"]) if "rank" in row and pd_notna(row["rank"]) else None,
                    corridor_label=str(row["corridor_label"]),
                    origin_display_name=str(row["origin_display_name"]),
                    origin_code=str(row["origin_code"]),
                    dest_display_name=str(row["dest_display_name"]),
                    destination_code=str(row["destination_code"]),
                    year=int(row["year"]),
                    migrant_stock=float(row["migrant_stock"]),
                    origin_corridor_share_pct=_safe_float(row.get("origin_corridor_share_pct")),
                    dest_corridor_share_pct=_safe_float(row.get("dest_corridor_share_pct")),
                )
            )

        # If specific origin and destination provided, calculate 1990–2020 history
        history = []
        current_stock = None

        if origin_code and destination_code and origin_code != "All" and destination_code != "All":
            df_pair = df_bilateral[
                (df_bilateral["origin_code"] == origin_code) &
                (df_bilateral["destination_code"] == destination_code) &
                (~df_bilateral.get("is_aggregate_route", False))
            ].sort_values("year")

            for _, row in df_pair.iterrows():
                yr = int(row["year"])
                stk = float(row["migrant_stock"])
                if yr == year:
                    current_stock = stk
                history.append(
                    RouteHistoryPoint(
                        year=yr,
                        migrant_stock=stk,
                        origin_corridor_share_pct=_safe_float(row.get("origin_corridor_share_pct")),
                        dest_corridor_share_pct=_safe_float(row.get("dest_corridor_share_pct")),
                    )
                )

        return RouteResponse(
            year=year,
            origin_code=origin_code,
            destination_code=destination_code,
            origin_name=origin_name,
            destination_name=destination_name,
            corridor_label=corridor_label,
            current_stock=current_stock,
            history=history,
            top_corridors=top_corridors,
        )


def pd_notna(val) -> bool:
    return val is not None and not (isinstance(val, float) and math.isnan(val))


routes_service = RoutesService()
