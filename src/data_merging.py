"""
Data merging module for the Global Migration Observatory.
Combines UN DESA migration datasets with World Bank socioeconomic indicators
using standardized ISO3 country codes and years.
"""

import logging
from typing import Optional, Tuple
import pandas as pd

from src.config import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def merge_country_level(df_mig_dest: pd.DataFrame, df_wb: pd.DataFrame) -> pd.DataFrame:
    """
    Merge destination-level migrant stock with World Bank socioeconomic indicators.
    
    Join Key: (country_code, year)
    
    Args:
        df_mig_dest: Cleaned UN DESA destination migrant stock DataFrame.
        df_wb: Cleaned World Bank country-year socioeconomic DataFrame.
        
    Returns:
        pd.DataFrame: Merged country-year DataFrame with migration and economic fields.
    """
    logger.info("Merging destination migrant stock with World Bank socioeconomic data...")
    
    # Prepare migration side
    mig_cols = ["country", "country_code", "year", "migrant_stock", "entity_type", "is_aggregate"]
    mig_subset = df_mig_dest[[c for c in mig_cols if c in df_mig_dest.columns]].copy()
    
    # Prepare World Bank side
    wb_cols = ["country_code", "year", "gdp", "gdp_per_capita", "population", "unemployment"]
    wb_subset = df_wb[[c for c in wb_cols if c in df_wb.columns]].copy()
    
    # Join on (country_code, year)
    merged = pd.merge(
        mig_subset,
        wb_subset,
        on=["country_code", "year"],
        how="inner"
    )
    
    # Ensure sorted order
    merged = merged.sort_values(["country_code", "year"]).reset_index(drop=True)
    
    match_rate = len(merged) / len(mig_subset) * 100 if len(mig_subset) > 0 else 0.0
    logger.info(
        f"Country-level merge completed: {len(merged):,} records merged "
        f"({match_rate:.1f}% match of migration destination records)."
    )
    return merged


def merge_route_level(df_bilateral: pd.DataFrame, df_wb: pd.DataFrame) -> pd.DataFrame:
    """
    Merge bilateral migration corridors with World Bank socioeconomic indicators.
    
    Distinctly attaches origin socioeconomic variables (origin_gdp, origin_population, etc.)
    and destination socioeconomic variables (destination_gdp, destination_population, etc.).
    
    Args:
        df_bilateral: Cleaned UN DESA bilateral migrant stock DataFrame.
        df_wb: Cleaned World Bank country-year socioeconomic DataFrame.
        
    Returns:
        pd.DataFrame: Merged route-level DataFrame with distinct origin and destination metrics.
    """
    logger.info("Merging bilateral migration corridors with origin and destination socioeconomic indicators...")
    
    wb_indicators = ["gdp", "gdp_per_capita", "population", "unemployment"]
    
    # Prepare origin WB data
    wb_origin = df_wb[["country_code", "year"] + [c for c in wb_indicators if c in df_wb.columns]].copy()
    wb_origin = wb_origin.rename(columns={
        "country_code": "origin_code",
        "gdp": "origin_gdp",
        "gdp_per_capita": "origin_gdp_per_capita",
        "population": "origin_population",
        "unemployment": "origin_unemployment",
    })
    
    # Prepare destination WB data
    wb_dest = df_wb[["country_code", "year"] + [c for c in wb_indicators if c in df_wb.columns]].copy()
    wb_dest = wb_dest.rename(columns={
        "country_code": "destination_code",
        "gdp": "destination_gdp",
        "gdp_per_capita": "destination_gdp_per_capita",
        "population": "destination_population",
        "unemployment": "destination_unemployment",
    })
    
    # Merge origin WB indicators
    merged = pd.merge(
        df_bilateral,
        wb_origin,
        on=["origin_code", "year"],
        how="left"
    )
    
    # Merge destination WB indicators
    merged = pd.merge(
        merged,
        wb_dest,
        on=["destination_code", "year"],
        how="left"
    )
    
    logger.info(f"Route-level merge completed: {len(merged):,} corridor records.")
    return merged
