"""
Feature engineering module for the Global Migration Observatory.
Calculates scientifically valid derived metrics from migrant stock and socioeconomic data.

CRITICAL METHODOLOGICAL DISTINCTION:
Migrant Stock is the estimated number of international migrants residing in a country
at a specific mid-year point in time. It is NOT annual migration flow.
Derived metrics must strictly reflect stock quantities and proportions.
"""

import logging
from typing import Optional
import numpy as np
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_migrant_stock_pct_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate international migrant stock as a percentage of the total population.
    
    Formula: (migrant_stock / population) * 100
    
    Args:
        df: DataFrame containing 'migrant_stock' and 'population'.
        
    Returns:
        pd.DataFrame: DataFrame with new column 'migrant_stock_pct_population'.
    """
    result = df.copy()
    
    if "migrant_stock" not in result.columns or "population" not in result.columns:
        logger.warning("Columns 'migrant_stock' or 'population' missing. Cannot calculate stock % of population.")
        return result
        
    # Valid non-zero population
    valid_mask = (result["population"].notna()) & (result["population"] > 0) & (result["migrant_stock"].notna())
    
    result["migrant_stock_pct_population"] = np.nan
    result.loc[valid_mask, "migrant_stock_pct_population"] = (
        (result.loc[valid_mask, "migrant_stock"] / result.loc[valid_mask, "population"]) * 100.0
    ).round(4)
    
    logger.info("Computed 'migrant_stock_pct_population'.")
    return result


def compute_period_stock_change(
    df: pd.DataFrame,
    id_col: str = "country_code",
    year_col: str = "year",
    value_col: str = "migrant_stock"
) -> pd.DataFrame:
    """
    Calculate 5-year intercensal change in migrant stock.
    
    NOTE ON TERMINOLOGY:
    Intercensal stock difference is NOT annual migration flow. It reflects net cumulative
    change in residing foreign-born population between UN 5-year estimation rounds.
    
    Args:
        df: DataFrame sorted by entity and year.
        id_col: Entity identifier column.
        year_col: Year column.
        value_col: Column to compute change for.
        
    Returns:
        pd.DataFrame: DataFrame with 'stock_change_5yr' and 'stock_growth_pct_5yr'.
    """
    result = df.copy()
    
    if id_col not in result.columns or year_col not in result.columns or value_col not in result.columns:
        logger.warning(f"Required columns ({id_col}, {year_col}, {value_col}) missing for period change computation.")
        return result
        
    result = result.sort_values([id_col, year_col]).reset_index(drop=True)
    
    # Calculate difference grouped by country
    result["stock_change_5yr"] = result.groupby(id_col)[value_col].diff()
    
    # Calculate percentage change
    prev_stock = result.groupby(id_col)[value_col].shift(1)
    valid_pct_mask = (prev_stock.notna()) & (prev_stock > 0) & (result["stock_change_5yr"].notna())
    
    result["stock_growth_pct_5yr"] = np.nan
    result.loc[valid_pct_mask, "stock_growth_pct_5yr"] = (
        (result.loc[valid_pct_mask, "stock_change_5yr"] / prev_stock.loc[valid_pct_mask]) * 100.0
    ).round(2)
    
    logger.info("Computed 'stock_change_5yr' and 'stock_growth_pct_5yr'.")
    return result


def compute_corridor_shares(df_bilateral: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate bilateral corridor shares relative to total origin emigration stock and destination immigration stock.
    
    Definitions:
    - origin_corridor_share_pct: (corridor_stock / total_emigrants_abroad_from_origin) * 100
      (What percentage of migrants from origin X reside in destination Y in given year)
    - dest_corridor_share_pct: (corridor_stock / total_immigrants_in_destination) * 100
      (What percentage of migrants in destination Y originated from origin X in given year)
      
    Args:
        df_bilateral: Bilateral migration DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with origin and destination corridor shares.
    """
    result = df_bilateral.copy()
    
    req_cols = ["origin_code", "destination_code", "year", "migrant_stock"]
    if not all(c in result.columns for c in req_cols):
        logger.warning(f"Missing required columns for corridor share computation in: {list(result.columns)}")
        return result
        
    # Total emigrants from origin per year (excluding self-origin if any)
    origin_totals = (
        result[result["migrant_stock"].notna()]
        .groupby(["origin_code", "year"])["migrant_stock"]
        .sum()
        .reset_index()
        .rename(columns={"migrant_stock": "origin_total_emigrant_stock"})
    )
    
    # Total immigrants in destination per year
    dest_totals = (
        result[result["migrant_stock"].notna()]
        .groupby(["destination_code", "year"])["migrant_stock"]
        .sum()
        .reset_index()
        .rename(columns={"migrant_stock": "dest_total_immigrant_stock"})
    )
    
    result = pd.merge(result, origin_totals, on=["origin_code", "year"], how="left")
    result = pd.merge(result, dest_totals, on=["destination_code", "year"], how="left")
    
    # Origin Corridor Share %
    valid_orig = (result["origin_total_emigrant_stock"].notna()) & (result["origin_total_emigrant_stock"] > 0)
    result["origin_corridor_share_pct"] = np.nan
    result.loc[valid_orig, "origin_corridor_share_pct"] = (
        (result.loc[valid_orig, "migrant_stock"] / result.loc[valid_orig, "origin_total_emigrant_stock"]) * 100.0
    ).round(3)
    
    # Destination Corridor Share %
    valid_dest = (result["dest_total_immigrant_stock"].notna()) & (result["dest_total_immigrant_stock"] > 0)
    result["dest_corridor_share_pct"] = np.nan
    result.loc[valid_dest, "dest_corridor_share_pct"] = (
        (result.loc[valid_dest, "migrant_stock"] / result.loc[valid_dest, "dest_total_immigrant_stock"]) * 100.0
    ).round(3)
    
    logger.info("Computed bilateral corridor shares.")
    return result


def compute_country_rankings(df: pd.DataFrame, metric_col: str = "migrant_stock") -> pd.DataFrame:
    """
    Calculate annual global country rankings for sovereign states for a specified metric.
    
    Args:
        df: Country-year DataFrame.
        metric_col: Metric to rank on (e.g. 'migrant_stock' or 'migrant_stock_pct_population').
        
    Returns:
        pd.DataFrame: DataFrame with added rank column.
    """
    result = df.copy()
    
    if metric_col not in result.columns or "year" not in result.columns:
        return result
        
    rank_col_name = f"{metric_col}_global_rank"
    
    # Rank only non-aggregate sovereign countries/territories
    is_sovereign = ~result["is_aggregate"] if "is_aggregate" in result.columns else pd.Series(True, index=result.index)
    
    result[rank_col_name] = np.nan
    
    for yr in result["year"].unique():
        yr_mask = (result["year"] == yr) & is_sovereign & (result[metric_col].notna())
        if yr_mask.any():
            result.loc[yr_mask, rank_col_name] = (
                result.loc[yr_mask, metric_col].rank(ascending=False, method="min").astype(int)
            )
            
    logger.info(f"Computed '{rank_col_name}'.")
    return result
