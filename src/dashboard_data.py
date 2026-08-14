"""
Dashboard Data Access & Analytical Helper Layer for the Global Migration Observatory.
Provides clean, cached, and performant data transformations for Streamlit visualizations.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config
from src.data_loader import load_processed_data


METRIC_COLUMN_MAP = {
    "Migrant Stock": "migrant_stock",
    "Migrant Stock % of Population": "migrant_stock_pct_population",
    "5-Year Stock Change": "stock_change_5yr",
    "5-Year Stock Growth %": "stock_growth_pct_5yr",
}

METRIC_LABELS = {
    "migrant_stock": "Migrant Stock (People)",
    "migrant_stock_pct_population": "Migrant Stock % of Population",
    "stock_change_5yr": "5-Year Absolute Stock Change",
    "stock_growth_pct_5yr": "5-Year Stock Growth Rate (%)",
}


def load_canonical_country_map() -> Dict[str, str]:
    """Load ISO3 -> canonical country name dictionary."""
    try:
        df_ref = load_processed_data("country_reference.csv")
        return dict(zip(df_ref["iso3"], df_ref["name"]))
    except Exception:
        return {}


def prepare_country_socioeconomic_data() -> pd.DataFrame:
    """
    Load and clean the merged country socioeconomic dataset with canonical names.
    
    Returns:
        pd.DataFrame: Cleaned country socioeconomic dataset.
    """
    df = load_processed_data("migration_country_socioeconomic.csv")
    name_map = load_canonical_country_map()
    
    # Standardize country display names
    def _clean_name(row):
        code = str(row["country_code"]) if pd.notna(row["country_code"]) else ""
        if code in name_map:
            return name_map[code]
        raw_name = str(row["country"]) if pd.notna(row["country"]) else ""
        return raw_name.replace("*", "").strip()
        
    df["display_name"] = df.apply(_clean_name, axis=1)
    return df


def prepare_bilateral_corridor_data() -> pd.DataFrame:
    """
    Load and clean the bilateral corridor dataset with canonical names.
    
    Returns:
        pd.DataFrame: Cleaned bilateral corridor dataset.
    """
    df = load_processed_data("migration_bilateral_cleaned.parquet")
    name_map = load_canonical_country_map()
    
    def _clean_orig(row):
        code = str(row["origin_code"]) if pd.notna(row["origin_code"]) else ""
        if code in name_map:
            return name_map[code]
        raw = str(row["origin_country"]) if pd.notna(row["origin_country"]) else ""
        return raw.replace("*", "").strip()
        
    def _clean_dest(row):
        code = str(row["destination_code"]) if pd.notna(row["destination_code"]) else ""
        if code in name_map:
            return name_map[code]
        raw = str(row["destination_country"]) if pd.notna(row["destination_country"]) else ""
        return raw.replace("*", "").strip()
        
    df["origin_display_name"] = df.apply(_clean_orig, axis=1)
    df["dest_display_name"] = df.apply(_clean_dest, axis=1)
    df["corridor_label"] = df["origin_display_name"] + " → " + df["dest_display_name"]
    return df


def get_overview_kpis(
    df_merged: pd.DataFrame,
    df_bilateral: pd.DataFrame,
    year: int
) -> Dict[str, Any]:
    """
    Calculate executive overview KPIs for a selected year from actual datasets.
    
    Args:
        df_merged: Cleaned country socioeconomic DataFrame.
        df_bilateral: Cleaned bilateral DataFrame.
        year: Target census round year (e.g. 2020).
        
    Returns:
        Dict[str, Any]: Dynamic KPI metrics.
    """
    # Filter to non-aggregates for sovereign state stats
    df_yr_sovereign = df_merged[(df_merged["year"] == year) & (~df_merged["is_aggregate"])].copy()
    
    total_migrant_stock = float(df_yr_sovereign["migrant_stock"].sum(skipna=True))
    num_countries = int(df_yr_sovereign["country_code"].nunique())
    
    # Top destination by stock
    top_stock_row = df_yr_sovereign.sort_values("migrant_stock", ascending=False).iloc[0] if not df_yr_sovereign.empty else None
    top_dest_name = top_stock_row["display_name"] if top_stock_row is not None else "N/A"
    top_dest_stock = float(top_stock_row["migrant_stock"]) if top_stock_row is not None else 0.0
    
    # Top destination by share of population
    df_share = df_yr_sovereign[df_yr_sovereign["migrant_stock_pct_population"].notna()]
    top_share_row = df_share.sort_values("migrant_stock_pct_population", ascending=False).iloc[0] if not df_share.empty else None
    top_share_name = top_share_row["display_name"] if top_share_row is not None else "N/A"
    top_share_pct = float(top_share_row["migrant_stock_pct_population"]) if top_share_row is not None else 0.0
    
    # Number of active bilateral corridors (> 0 migrants between sovereign entities)
    df_b_yr = df_bilateral[
        (df_bilateral["year"] == year) &
        (~df_bilateral["is_aggregate_route"]) &
        (df_bilateral["migrant_stock"] > 0)
    ]
    num_corridors = int(len(df_b_yr))
    
    return {
        "year": year,
        "total_migrant_stock": total_migrant_stock,
        "num_countries": num_countries,
        "top_destination_name": top_dest_name,
        "top_destination_stock": top_dest_stock,
        "top_share_name": top_share_name,
        "top_share_pct": top_share_pct,
        "num_corridors": num_corridors,
    }


def get_map_data(
    df_merged: pd.DataFrame,
    year: int,
    metric_name: str = "Migrant Stock"
) -> pd.DataFrame:
    """
    Extract and format country-level data for the Plotly choropleth world map.
    
    Args:
        df_merged: Merged country socioeconomic DataFrame.
        year: Selected year.
        metric_name: User-selected metric display name.
        
    Returns:
        pd.DataFrame: Formatted DataFrame for choropleth mapping.
    """
    col_name = METRIC_COLUMN_MAP.get(metric_name, "migrant_stock")
    
    df_yr = df_merged[
        (df_merged["year"] == year) &
        (~df_merged["is_aggregate"]) &
        (df_merged["country_code"].notna())
    ].copy()
    
    df_yr["metric_value"] = df_yr[col_name]
    df_yr["metric_label"] = METRIC_LABELS.get(col_name, metric_name)
    
    cols = [
        "display_name", "country_code", "year", "metric_value",
        "migrant_stock", "population", "migrant_stock_pct_population",
        "stock_change_5yr", "stock_growth_pct_5yr", "migrant_stock_global_rank"
    ]
    existing = [c for c in cols if c in df_yr.columns]
    return df_yr[existing].copy()


def get_global_trend_data(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate global total migrant stock trajectory across 1990–2020.
    
    Args:
        df_merged: Merged country socioeconomic DataFrame.
        
    Returns:
        pd.DataFrame: Year-by-year global total migrant stock.
    """
    df_sovereign = df_merged[~df_merged["is_aggregate"]].copy()
    global_trend = df_sovereign.groupby("year", as_index=False).agg(
        total_migrant_stock=("migrant_stock", "sum"),
        country_count=("country_code", "nunique"),
        total_population=("population", "sum")
    )
    global_trend["migrant_stock_pct_population"] = (
        (global_trend["total_migrant_stock"] / global_trend["total_population"]) * 100
    )
    return global_trend.sort_values("year")


def get_country_trend_data(
    df_merged: pd.DataFrame,
    country_codes: List[str],
    metric_name: str = "Migrant Stock"
) -> pd.DataFrame:
    """
    Extract multi-country time series for trend comparisons.
    
    Args:
        df_merged: Merged country socioeconomic DataFrame.
        country_codes: List of ISO3 codes to compare.
        metric_name: Selected metric name.
        
    Returns:
        pd.DataFrame: Cleaned time series DataFrame.
    """
    col_name = METRIC_COLUMN_MAP.get(metric_name, "migrant_stock")
    
    df_filtered = df_merged[
        (df_merged["country_code"].isin(country_codes)) &
        (~df_merged["is_aggregate"])
    ].copy()
    
    df_filtered["metric_value"] = df_filtered[col_name]
    df_filtered["metric_label"] = METRIC_LABELS.get(col_name, metric_name)
    return df_filtered.sort_values(["display_name", "year"])


def get_rankings_data(
    df_merged: pd.DataFrame,
    year: int,
    metric_name: str = "Migrant Stock",
    top_n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Generate dynamic country rankings for a given metric and year.
    
    Args:
        df_merged: Merged country socioeconomic DataFrame.
        year: Selected year.
        metric_name: Selected metric.
        top_n: Top N entities to return (e.g. 10, 25, 50).
        ascending: Sort order (False = highest first).
        
    Returns:
        pd.DataFrame: Top N ranked countries with rank index.
    """
    col_name = METRIC_COLUMN_MAP.get(metric_name, "migrant_stock")
    
    df_yr = df_merged[
        (df_merged["year"] == year) &
        (~df_merged["is_aggregate"]) &
        (df_merged[col_name].notna())
    ].copy()
    
    df_sorted = df_yr.sort_values(col_name, ascending=ascending).head(top_n).copy()
    df_sorted["rank"] = range(1, len(df_sorted) + 1)
    df_sorted["metric_value"] = df_sorted[col_name]
    
    cols = [
        "rank", "display_name", "country_code", "year", "metric_value",
        "migrant_stock", "population", "migrant_stock_pct_population",
        "stock_change_5yr", "stock_growth_pct_5yr", "gdp_per_capita"
    ]
    existing = [c for c in cols if c in df_sorted.columns]
    return df_sorted[existing].copy()


def get_top_global_corridors(
    df_bilateral: pd.DataFrame,
    year: int,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Retrieve top N bilateral migration stock corridors globally for a selected year.
    
    Args:
        df_bilateral: Cleaned bilateral DataFrame.
        year: Selected year.
        top_n: Number of corridors to return.
        
    Returns:
        pd.DataFrame: Top N bilateral corridors.
    """
    df_yr = df_bilateral[
        (df_bilateral["year"] == year) &
        (~df_bilateral["is_aggregate_route"]) &
        (df_bilateral["origin_code"].notna()) &
        (df_bilateral["destination_code"].notna()) &
        (df_bilateral["origin_code"] != df_bilateral["destination_code"]) &
        (df_bilateral["migrant_stock"] > 0)
    ].copy()
    
    df_sorted = df_yr.sort_values("migrant_stock", ascending=False).head(top_n).copy()
    df_sorted["rank"] = range(1, len(df_sorted) + 1)
    
    cols = [
        "rank", "corridor_label", "origin_display_name", "origin_code",
        "dest_display_name", "destination_code", "year", "migrant_stock",
        "origin_corridor_share_pct", "dest_corridor_share_pct"
    ]
    existing = [c for c in cols if c in df_sorted.columns]
    return df_sorted[existing].copy()


def get_filtered_corridors(
    df_bilateral: pd.DataFrame,
    year: int,
    origin_code: Optional[str] = None,
    dest_code: Optional[str] = None,
    top_n: int = 20
) -> pd.DataFrame:
    """
    Filter bilateral migration stock corridors by origin and/or destination.
    
    Args:
        df_bilateral: Cleaned bilateral DataFrame.
        year: Selected year.
        origin_code: Optional origin ISO3 code.
        dest_code: Optional destination ISO3 code.
        top_n: Max rows to return.
        
    Returns:
        pd.DataFrame: Filtered bilateral corridor records.
    """
    df_yr = df_bilateral[
        (df_bilateral["year"] == year) &
        (~df_bilateral["is_aggregate_route"]) &
        (df_bilateral["origin_code"].notna()) &
        (df_bilateral["destination_code"].notna()) &
        (df_bilateral["origin_code"] != df_bilateral["destination_code"])
    ].copy()
    
    if origin_code and origin_code != "All":
        df_yr = df_yr[df_yr["origin_code"] == origin_code]
        
    if dest_code and dest_code != "All":
        df_yr = df_yr[df_yr["destination_code"] == dest_code]
        
    df_sorted = df_yr.sort_values("migrant_stock", ascending=False).head(top_n).copy()
    if not df_sorted.empty:
        df_sorted["rank"] = range(1, len(df_sorted) + 1)
        
    cols = [
        "rank", "corridor_label", "origin_display_name", "origin_code",
        "dest_display_name", "destination_code", "year", "migrant_stock",
        "origin_corridor_share_pct", "dest_corridor_share_pct"
    ]
    existing = [c for c in cols if c in df_sorted.columns]
    return df_sorted[existing].copy()


def get_country_profile_data(
    df_merged: pd.DataFrame,
    df_bilateral: pd.DataFrame,
    country_code: str,
    year: int
) -> Dict[str, Any]:
    """
    Extract comprehensive country profile metrics, time series, and corridor networks.
    
    Args:
        df_merged: Merged country socioeconomic DataFrame.
        df_bilateral: Cleaned bilateral DataFrame.
        country_code: Selected ISO3 country code.
        year: Selected reference year.
        
    Returns:
        Dict[str, Any]: Country profile summary data.
    """
    # Country history across all years
    df_history = df_merged[
        (df_merged["country_code"] == country_code) &
        (~df_merged["is_aggregate"])
    ].sort_values("year").copy()
    
    current_row = df_history[df_history["year"] == year]
    curr_data = current_row.iloc[0].to_dict() if not current_row.empty else {}
    
    # Inbound corridors (origin -> this country as destination)
    inbound_df = df_bilateral[
        (df_bilateral["destination_code"] == country_code) &
        (df_bilateral["year"] == year) &
        (~df_bilateral["is_aggregate_route"]) &
        (df_bilateral["origin_code"] != country_code) &
        (df_bilateral["migrant_stock"] > 0)
    ].sort_values("migrant_stock", ascending=False).head(10).copy()
    
    # Outbound corridors (this country as origin -> destination)
    outbound_df = df_bilateral[
        (df_bilateral["origin_code"] == country_code) &
        (df_bilateral["year"] == year) &
        (~df_bilateral["is_aggregate_route"]) &
        (df_bilateral["destination_code"] != country_code) &
        (df_bilateral["migrant_stock"] > 0)
    ].sort_values("migrant_stock", ascending=False).head(10).copy()
    
    return {
        "country_code": country_code,
        "country_name": curr_data.get("display_name", country_code),
        "year": year,
        "current_stats": curr_data,
        "history_df": df_history,
        "inbound_corridors": inbound_df,
        "outbound_corridors": outbound_df,
    }
