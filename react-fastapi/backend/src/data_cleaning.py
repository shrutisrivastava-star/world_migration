"""
Data cleaning and standardization module for the Global Migration Observatory.
Transforms raw UN DESA and World Bank datasets into tidy, standardized, and validated schemas.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.config import config
from src.utils import classify_entity_type, resolve_country_code


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_migration_destination(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and reshape the UN DESA destination migrant stock dataset (Table 1).
    
    Transforms wide year columns (1990, 1995, 2000, 2005, 2010, 2015, 2020) into long tidy format,
    standardizes ISO3 country codes and entity classifications, and cleans missing markers.
    
    Args:
        df_raw: Raw DataFrame loaded from UN DESA destination Table 1.
        
    Returns:
        pd.DataFrame: Cleaned destination migrant stock DataFrame.
    """
    logger.info("Cleaning UN DESA destination migrant stock dataset...")
    df = df_raw.copy()
    
    # Identify key columns
    loc_col = None
    name_col = None
    type_col = None
    
    for col in df.columns:
        col_str = str(col).strip()
        if "location code" in col_str.lower():
            loc_col = col
        elif "region" in col_str.lower() or "country or area" in col_str.lower():
            name_col = col
        elif "type of data" in col_str.lower():
            type_col = col
            
    if not loc_col or not name_col:
        raise ValueError(f"Could not locate required Location Code or Country Name columns in: {list(df.columns)}")
        
    year_cols = [y for y in config.migration_years if y in df.columns]
    if not year_cols:
        raise ValueError(f"No configured migration year columns found in DataFrame: {list(df.columns)}")
        
    id_vars = [name_col, loc_col]
    if type_col:
        id_vars.append(type_col)
        
    # Unpivot wide year columns to tidy long format
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="year",
        value_name="migrant_stock"
    )
    
    # Rename standard columns
    rename_map = {
        name_col: "country",
        loc_col: "m49_code",
    }
    if type_col:
        rename_map[type_col] = "data_type"
    df_long = df_long.rename(columns=rename_map)
    
    # Clean Year column
    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype(int)
    
    # Clean Migrant Stock: Convert '..' or strings to NaN, convert valid numbers to float
    df_long["migrant_stock"] = pd.to_numeric(
        df_long["migrant_stock"].astype(str).str.replace("..", "", regex=False).str.strip(),
        errors="coerce"
    )
    
    # Clean M49 code
    df_long["m49_code"] = pd.to_numeric(df_long["m49_code"], errors="coerce")
    
    # Resolve ISO3 country codes and entity classification
    def _resolve_row(row):
        c_name = str(row["country"]) if pd.notna(row["country"]) else ""
        m49 = int(row["m49_code"]) if pd.notna(row["m49_code"]) else None
        iso3 = resolve_country_code(country_name=c_name, m49_code=m49)
        entity_type = classify_entity_type(iso3, country_name=c_name, m49_code=m49)
        return pd.Series([iso3, entity_type])
        
    resolved_info = df_long.apply(_resolve_row, axis=1)
    df_long["country_code"] = resolved_info[0]
    df_long["entity_type"] = resolved_info[1]
    df_long["is_aggregate"] = df_long["entity_type"].isin(["region", "income_group", "world", "aggregate"])
    
    # Drop rows without any entity name or valid year
    df_long = df_long.dropna(subset=["country", "year"])
    
    # Ensure standard column order
    cols_order = [
        "country", "country_code", "year", "migrant_stock",
        "m49_code", "data_type", "entity_type", "is_aggregate"
    ]
    existing_cols = [c for c in cols_order if c in df_long.columns]
    df_cleaned = df_long[existing_cols].copy()
    
    logger.info(f"Cleaned destination dataset: {len(df_cleaned)} records ({df_cleaned['country_code'].nunique()} unique country codes).")
    return df_cleaned


def clean_migration_bilateral(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and reshape the UN DESA bilateral migrant stock matrix (Table 1).
    
    Transforms wide year columns into long tidy bilateral corridors:
    [origin_country, origin_code, destination_country, destination_code, year, migrant_stock].
    
    Args:
        df_raw: Raw DataFrame loaded from UN DESA bilateral Table 1.
        
    Returns:
        pd.DataFrame: Cleaned bilateral migrant stock DataFrame.
    """
    logger.info("Cleaning UN DESA bilateral migrant stock dataset...")
    df = df_raw.copy()
    
    dest_name_col = None
    dest_loc_col = None
    orig_name_col = None
    orig_loc_col = None
    
    for col in df.columns:
        col_str = str(col).strip().lower()
        if "destination" in col_str:
            if "location code" in col_str:
                dest_loc_col = col
            elif "region" in col_str or "country" in col_str:
                dest_name_col = col
        elif "origin" in col_str:
            if "location code" in col_str:
                orig_loc_col = col
            elif "region" in col_str or "country" in col_str:
                orig_name_col = col
                
    if not dest_name_col or not orig_name_col or not dest_loc_col or not orig_loc_col:
        raise ValueError(
            f"Could not identify bilateral origin/destination columns in: {list(df.columns)}"
        )
        
    year_cols = [y for y in config.migration_years if y in df.columns]
    
    id_vars = [dest_name_col, dest_loc_col, orig_name_col, orig_loc_col]
    
    # Unpivot wide year columns to tidy long format
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="year",
        value_name="migrant_stock"
    )
    
    df_long = df_long.rename(columns={
        dest_name_col: "destination_country",
        dest_loc_col: "destination_m49",
        orig_name_col: "origin_country",
        orig_loc_col: "origin_m49",
    })
    
    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype(int)
    
    # Clean Migrant Stock
    df_long["migrant_stock"] = pd.to_numeric(
        df_long["migrant_stock"].astype(str).str.replace("..", "", regex=False).str.strip(),
        errors="coerce"
    )
    
    # Fast resolution of unique entities
    dest_m49 = pd.to_numeric(df_long["destination_m49"], errors="coerce")
    orig_m49 = pd.to_numeric(df_long["origin_m49"], errors="coerce")
    df_long["destination_m49_clean"] = dest_m49
    df_long["origin_m49_clean"] = orig_m49

    unique_d = df_long[["destination_country", "destination_m49_clean"]].drop_duplicates()
    dest_code_map = {
        (row.destination_country, row.destination_m49_clean): resolve_country_code(country_name=row.destination_country, m49_code=row.destination_m49_clean)
        for row in unique_d.itertuples(index=False)
    }
    dest_type_map = {
        (row.destination_country, row.destination_m49_clean): classify_entity_type(dest_code_map.get((row.destination_country, row.destination_m49_clean)), country_name=row.destination_country, m49_code=row.destination_m49_clean)
        for row in unique_d.itertuples(index=False)
    }

    unique_o = df_long[["origin_country", "origin_m49_clean"]].drop_duplicates()
    orig_code_map = {
        (row.origin_country, row.origin_m49_clean): resolve_country_code(country_name=row.origin_country, m49_code=row.origin_m49_clean)
        for row in unique_o.itertuples(index=False)
    }
    orig_type_map = {
        (row.origin_country, row.origin_m49_clean): classify_entity_type(orig_code_map.get((row.origin_country, row.origin_m49_clean)), country_name=row.origin_country, m49_code=row.origin_m49_clean)
        for row in unique_o.itertuples(index=False)
    }

    df_long["destination_code"] = [
        dest_code_map.get((n, m))
        for n, m in zip(df_long["destination_country"], df_long["destination_m49_clean"])
    ]
    df_long["origin_code"] = [
        orig_code_map.get((n, m))
        for n, m in zip(df_long["origin_country"], df_long["origin_m49_clean"])
    ]

    df_long["destination_entity_type"] = [
        dest_type_map.get((n, m), "unknown")
        for n, m in zip(df_long["destination_country"], df_long["destination_m49_clean"])
    ]
    df_long["origin_entity_type"] = [
        orig_type_map.get((n, m), "unknown")
        for n, m in zip(df_long["origin_country"], df_long["origin_m49_clean"])
    ]

    df_long["is_aggregate_route"] = (
        df_long["destination_entity_type"].isin(["region", "income_group", "world", "aggregate"]) |
        df_long["origin_entity_type"].isin(["region", "income_group", "world", "aggregate"])
    )
    
    cols_order = [
        "origin_country", "origin_code", "destination_country", "destination_code",
        "year", "migrant_stock", "origin_entity_type", "destination_entity_type", "is_aggregate_route"
    ]
    df_cleaned = df_long[cols_order].copy()
    
    logger.info(f"Cleaned bilateral dataset: {len(df_cleaned)} records.")
    return df_cleaned


def clean_world_bank_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform raw World Bank records into a tidy country-year wide format.
    
    Pivots indicators:
    - NY.GDP.MKTP.CD -> gdp
    - NY.GDP.PCAP.CD -> gdp_per_capita
    - SP.POP.TOTL -> population
    - SL.UEM.TOTL.ZS -> unemployment
    
    Args:
        df_raw: Raw combined World Bank indicators DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned World Bank DataFrame structured by [country, country_code, year, indicators...].
    """
    logger.info("Cleaning World Bank socioeconomic dataset...")
    df = df_raw.copy()
    
    # Filter years
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df[(df["year"] >= config.min_year) & (df["year"] <= config.max_year)]
    
    # Standardize country code
    df["country_code"] = [
        resolve_country_code(country_name=name, iso_code=iso3)
        for name, iso3 in zip(df["country_name"], df["country_iso3"])
    ]
    
    # Map indicator IDs to clean short column names
    code_to_short = {
        code: meta["short_name"]
        for code, meta in config.wb_indicators.items()
    }
    df["indicator_short"] = df["indicator_id"].map(code_to_short)
    
    # Drop rows where indicator is unmapped or value is missing
    df = df.dropna(subset=["indicator_short", "country_code"])
    
    # Pivot into country-year structure
    pivot_df = df.pivot_table(
        index=["country_name", "country_code", "year"],
        columns="indicator_short",
        values="value",
        aggfunc="first"
    ).reset_index()
    
    pivot_df = pivot_df.rename(columns={"country_name": "country"})
    
    # Classify entities
    pivot_df["entity_type"] = [
        classify_entity_type(code, country_name=name)
        for code, name in zip(pivot_df["country_code"], pivot_df["country"])
    ]
    pivot_df["is_aggregate"] = pivot_df["entity_type"].isin(["region", "income_group", "world", "aggregate"])
    
    # Ensure expected indicator columns exist
    for short_name in ["gdp", "gdp_per_capita", "population", "unemployment"]:
        if short_name not in pivot_df.columns:
            pivot_df[short_name] = np.nan
            
    cols_order = [
        "country", "country_code", "year",
        "gdp", "gdp_per_capita", "population", "unemployment",
        "entity_type", "is_aggregate"
    ]
    df_cleaned = pivot_df[cols_order].sort_values(["country_code", "year"]).reset_index(drop=True)
    
    logger.info(f"Cleaned World Bank dataset: {len(df_cleaned)} records ({df_cleaned['country_code'].nunique()} unique country codes).")
    return df_cleaned
