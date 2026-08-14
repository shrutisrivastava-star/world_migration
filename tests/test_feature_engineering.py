"""
Unit tests for feature_engineering module.
"""

import numpy as np
import pandas as pd
import pytest

from src.feature_engineering import (
    compute_corridor_shares,
    compute_country_rankings,
    compute_migrant_stock_pct_population,
    compute_period_stock_change,
)


def test_compute_migrant_stock_pct_population():
    """Test calculation of migrant stock as % of total population."""
    df = pd.DataFrame({
        "country_code": ["USA", "DEU", "QAT"],
        "migrant_stock": [50_000_000.0, 15_000_000.0, 2_000_000.0],
        "population": [330_000_000.0, 83_000_000.0, 2_800_000.0],
    })
    
    result = compute_migrant_stock_pct_population(df)
    assert "migrant_stock_pct_population" in result.columns
    # USA: (50M / 330M) * 100 = 15.1515%
    assert np.isclose(result.loc[0, "migrant_stock_pct_population"], 15.1515, atol=0.01)
    # QAT: (2M / 2.8M) * 100 = 71.4286%
    assert np.isclose(result.loc[2, "migrant_stock_pct_population"], 71.4286, atol=0.01)


def test_compute_period_stock_change():
    """Test calculation of 5-year intercensal stock change and growth rate."""
    df = pd.DataFrame({
        "country_code": ["USA", "USA", "USA"],
        "year": [2010, 2015, 2020],
        "migrant_stock": [40_000_000.0, 45_000_000.0, 50_000_000.0],
    })
    
    result = compute_period_stock_change(df, id_col="country_code", year_col="year", value_col="migrant_stock")
    assert "stock_change_5yr" in result.columns
    assert "stock_growth_pct_5yr" in result.columns
    
    # 2010: change is NaN (first year)
    assert pd.isna(result.loc[0, "stock_change_5yr"])
    # 2015: change is +5,000,000, growth is (5M/40M)*100 = 12.5%
    assert result.loc[1, "stock_change_5yr"] == 5_000_000.0
    assert result.loc[1, "stock_growth_pct_5yr"] == 12.5
    # 2020: change is +5,000,000, growth is (5M/45M)*100 = 11.11%
    assert result.loc[2, "stock_change_5yr"] == 5_000_000.0
    assert np.isclose(result.loc[2, "stock_growth_pct_5yr"], 11.11, atol=0.01)


def test_compute_corridor_shares():
    """Test bilateral origin and destination corridor share calculation."""
    df_bilat = pd.DataFrame({
        "origin_code": ["MEX", "MEX", "IND", "IND"],
        "destination_code": ["USA", "CAN", "USA", "ARE"],
        "year": [2020, 2020, 2020, 2020],
        "migrant_stock": [10_000_000.0, 100_000.0, 2_500_000.0, 3_500_000.0],
    })
    
    result = compute_corridor_shares(df_bilat)
    assert "origin_corridor_share_pct" in result.columns
    assert "dest_corridor_share_pct" in result.columns
    
    # Total MEX emigrants: 10M + 100k = 10.1M
    # MEX -> USA share: (10M / 10.1M) * 100 = 99.01%
    mex_usa = result[(result["origin_code"] == "MEX") & (result["destination_code"] == "USA")]
    assert np.isclose(mex_usa["origin_corridor_share_pct"].values[0], 99.01, atol=0.1)
    
    # Total USA immigrants in this table: 10M (from MEX) + 2.5M (from IND) = 12.5M
    # MEX share of USA immigrants: (10M / 12.5M) * 100 = 80.0%
    assert np.isclose(mex_usa["dest_corridor_share_pct"].values[0], 80.0, atol=0.1)


def test_compute_country_rankings():
    """Test country ranking by migrant stock per year."""
    df = pd.DataFrame({
        "country_code": ["USA", "DEU", "FRA", "USA", "DEU", "FRA"],
        "year": [2015, 2015, 2015, 2020, 2020, 2020],
        "migrant_stock": [45_000_000.0, 12_000_000.0, 7_000_000.0, 50_000_000.0, 15_000_000.0, 8_000_000.0],
        "is_aggregate": [False, False, False, False, False, False],
    })
    
    ranked = compute_country_rankings(df, metric_col="migrant_stock")
    assert "migrant_stock_global_rank" in ranked.columns
    
    # In 2020: USA should be Rank 1, DEU Rank 2, FRA Rank 3
    usa_2020 = ranked[(ranked["country_code"] == "USA") & (ranked["year"] == 2020)]
    deu_2020 = ranked[(ranked["country_code"] == "DEU") & (ranked["year"] == 2020)]
    assert usa_2020["migrant_stock_global_rank"].values[0] == 1
    assert deu_2020["migrant_stock_global_rank"].values[0] == 2
