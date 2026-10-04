"""
Service layer for Corridor Analysis, concentration trends, and trajectory classifications.
"""

import math
from typing import Optional, List
import pandas as pd

from app.schemas.corridor import (
    CorridorOverviewResponse,
    CorridorRankingItem,
    CorridorConcentrationPoint,
    CorridorTrajectoryPoint,
    CorridorDetailResponse,
)
from app.services.data_service import data_service
from src.dashboard_data import get_top_global_corridors, load_canonical_country_map
from src.advanced_analytics import compute_corridor_concentration_trend


def _safe_float(val: Optional[float], default: Optional[float] = None) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return default
    try:
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return default


class CorridorService:
    """Service handling corridor concentration and trajectory analysis."""

    def get_overview(self, year: int = 2020, top_n: int = 10) -> CorridorOverviewResponse:
        """
        Compute corridor overview metrics, top ranked corridors, and longitudinal concentration trend.
        
        Args:
            year: Census observation round year
            top_n: Number of top ranked corridors to return
            
        Returns:
            CorridorOverviewResponse: Corridor summary and concentration trend.
        """
        df_bilateral = data_service.get_bilateral_corridor_data()

        # 1. Total corridors & top corridor for selected year
        df_yr = df_bilateral[
            (df_bilateral["year"] == year) &
            (~df_bilateral.get("is_aggregate_route", False)) &
            (df_bilateral["origin_code"].notna()) &
            (df_bilateral["destination_code"].notna()) &
            (df_bilateral["origin_code"] != df_bilateral["destination_code"]) &
            (df_bilateral["migrant_stock"] > 0)
        ].sort_values("migrant_stock", ascending=False)

        total_corridors = len(df_yr)
        total_stock = float(df_yr["migrant_stock"].sum()) if not df_yr.empty else 0.0

        if not df_yr.empty:
            top_row = df_yr.iloc[0]
            top_corridor = str(top_row.get("corridor_label", f"{top_row['origin_code']} → {top_row['destination_code']}"))
            top_corridor_stock = float(top_row["migrant_stock"])
            top_10_share = (float(df_yr.iloc[:10]["migrant_stock"].sum()) / total_stock * 100.0) if total_stock > 0 else 0.0
        else:
            top_corridor = "N/A"
            top_corridor_stock = 0.0
            top_10_share = 0.0

        # 2. Top N corridors
        df_top = get_top_global_corridors(df_bilateral, year=year, top_n=top_n)
        top_corridors: List[CorridorRankingItem] = []
        for idx, row in df_top.iterrows():
            stk = float(row["migrant_stock"])
            sh = (stk / total_stock * 100.0) if total_stock > 0 else 0.0
            top_corridors.append(
                CorridorRankingItem(
                    rank=int(row.get("rank", idx + 1)),
                    corridor_label=str(row["corridor_label"]),
                    origin_display_name=str(row["origin_display_name"]),
                    origin_code=str(row["origin_code"]),
                    dest_display_name=str(row["dest_display_name"]),
                    destination_code=str(row["destination_code"]),
                    year=int(row["year"]),
                    migrant_stock=stk,
                    share_of_total=sh,
                )
            )

        # 3. Longitudinal concentration trend across 1990–2020
        df_conc = compute_corridor_concentration_trend(df_bilateral)
        concentration_trend: List[CorridorConcentrationPoint] = []
        for _, row in df_conc.iterrows():
            concentration_trend.append(
                CorridorConcentrationPoint(
                    year=int(row["year"]),
                    total_corridor_stock=float(row["total_corridor_stock"]),
                    active_corridor_count=int(row["active_corridor_count"]),
                    top_10_corridor_share=float(row["top_10_corridor_share"]),
                    top_25_corridor_share=float(row["top_25_corridor_share"]),
                    top_50_corridor_share=float(row["top_50_corridor_share"]),
                    largest_corridor=str(row["largest_corridor"]),
                )
            )

        return CorridorOverviewResponse(
            year=year,
            total_corridors=total_corridors,
            top_corridor=top_corridor,
            top_corridor_stock=top_corridor_stock,
            top_10_share=top_10_share,
            concentration_trend=concentration_trend,
            top_corridors=top_corridors,
        )

    def get_concentration(self) -> List[CorridorConcentrationPoint]:
        """Fetch 1990–2020 corridor concentration trend points."""
        df_bilateral = data_service.get_bilateral_corridor_data()
        df_conc = compute_corridor_concentration_trend(df_bilateral)
        points: List[CorridorConcentrationPoint] = []
        for _, row in df_conc.iterrows():
            points.append(
                CorridorConcentrationPoint(
                    year=int(row["year"]),
                    total_corridor_stock=float(row["total_corridor_stock"]),
                    active_corridor_count=int(row["active_corridor_count"]),
                    top_10_corridor_share=float(row["top_10_corridor_share"]),
                    top_25_corridor_share=float(row["top_25_corridor_share"]),
                    top_50_corridor_share=float(row["top_50_corridor_share"]),
                    largest_corridor=str(row["largest_corridor"]),
                )
            )
        return points

    def get_corridor_detail(
        self, origin_code: str, destination_code: str, year: int = 2020
    ) -> CorridorDetailResponse:
        """
        Compute deep-dive metrics, trajectory, and classification for a bilateral corridor.
        
        Deterministic Classifications:
        - 'Emerging': Stock growth >= +25% over prior census round
        - 'Persistent': Stock >= 500k and growth between -10% and +25%
        - 'Declining': Stock growth <= -10%
        - 'Stable': Stock growth between -10% and +10%
        - 'No Baseline': Earliest census round (1990)
        """
        df_bilateral = data_service.get_bilateral_corridor_data()
        name_map = load_canonical_country_map()

        origin_name = name_map.get(origin_code, origin_code)
        destination_name = name_map.get(destination_code, destination_code)
        corridor_label = f"{origin_name} → {destination_name}"

        # Filter corridor history
        df_pair = df_bilateral[
            (df_bilateral["origin_code"] == origin_code) &
            (df_bilateral["destination_code"] == destination_code) &
            (~df_bilateral.get("is_aggregate_route", False))
        ].sort_values("year")

        history: List[CorridorTrajectoryPoint] = []
        hist_map = {}
        for _, row in df_pair.iterrows():
            yr = int(row["year"])
            stk = float(row["migrant_stock"])
            history.append(CorridorTrajectoryPoint(year=yr, migrant_stock=stk))
            hist_map[yr] = stk

        current_stock = hist_map.get(year, None)

        # 5-Year percentage change calculation
        prev_year = year - 5 if (year - 5) in hist_map else None
        pct_change = None
        if prev_year and prev_year in hist_map:
            prev_stock = hist_map[prev_year]
            if prev_stock > 0 and current_stock is not None:
                pct_change = ((current_stock - prev_stock) / prev_stock) * 100.0

        # Classification rule
        if year == 1990 or pct_change is None:
            classification = "No Baseline (1990 Round)"
        elif pct_change >= 25.0:
            classification = "Emerging (≥ +25% 5yr growth)"
        elif (current_stock or 0) >= 500000 and -10.0 <= pct_change < 25.0:
            classification = "Persistent Major Core (High volume, stable/growing)"
        elif pct_change <= -10.0:
            classification = "Declining (≤ -10% 5yr reduction)"
        else:
            classification = "Stable (-10% to +10%)"

        # Global Rank & Share in current year
        df_yr_all = df_bilateral[
            (df_bilateral["year"] == year) &
            (~df_bilateral.get("is_aggregate_route", False)) &
            (df_bilateral["origin_code"].notna()) &
            (df_bilateral["destination_code"].notna()) &
            (df_bilateral["origin_code"] != df_bilateral["destination_code"]) &
            (df_bilateral["migrant_stock"] > 0)
        ].sort_values("migrant_stock", ascending=False).reset_index(drop=True)

        total_global_stock = float(df_yr_all["migrant_stock"].sum()) if not df_yr_all.empty else 0.0

        match_idx = df_yr_all[
            (df_yr_all["origin_code"] == origin_code) & (df_yr_all["destination_code"] == destination_code)
        ].index

        global_rank = int(match_idx[0] + 1) if len(match_idx) > 0 else None
        share_of_global = ((current_stock / total_global_stock * 100.0) if (current_stock and total_global_stock > 0) else None)

        # Top 10 corridors for context
        df_top10 = df_yr_all.head(10)
        top_corridors: List[CorridorRankingItem] = []
        for idx, row in df_top10.iterrows():
            stk = float(row["migrant_stock"])
            top_corridors.append(
                CorridorRankingItem(
                    rank=int(idx + 1),
                    corridor_label=str(row.get("corridor_label", f"{row['origin_code']} → {row['destination_code']}")),
                    origin_display_name=str(row.get("origin_display_name", row["origin_code"])),
                    origin_code=str(row["origin_code"]),
                    dest_display_name=str(row.get("dest_display_name", row["destination_code"])),
                    destination_code=str(row["destination_code"]),
                    year=year,
                    migrant_stock=stk,
                    share_of_total=(stk / total_global_stock * 100.0) if total_global_stock > 0 else 0.0,
                )
            )

        return CorridorDetailResponse(
            origin_code=origin_code,
            destination_code=destination_code,
            origin_name=origin_name,
            destination_name=destination_name,
            corridor_label=corridor_label,
            year=year,
            current_stock=current_stock,
            global_rank=global_rank,
            share_of_global=share_of_global,
            pct_change_5yr=pct_change,
            classification=classification,
            history=history,
            top_corridors=top_corridors,
        )


corridor_service = CorridorService()
