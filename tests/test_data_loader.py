"""
Unit tests for data_loader module.
"""

from pathlib import Path
import pytest
import pandas as pd

from src.config import config
from src.data_loader import (
    load_processed_data,
    load_raw_migration_destination,
    load_raw_migration_bilateral,
    load_world_bank_data,
)


def test_processed_data_loader_csv():
    """Test loading a processed CSV dataset."""
    df = load_processed_data("migration_destination_cleaned.csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "country_code" in df.columns
    assert "year" in df.columns
    assert "migrant_stock" in df.columns


def test_processed_data_loader_parquet():
    """Test loading a processed Parquet dataset."""
    df = load_processed_data("migration_bilateral_cleaned.parquet")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "origin_code" in df.columns
    assert "destination_code" in df.columns
    assert "migrant_stock" in df.columns


def test_load_processed_data_nonexistent_raises_error():
    """Test that requesting a nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_processed_data("non_existent_dataset_12345.csv")


def test_load_raw_destination_migration():
    """Test loading raw destination UN DESA data."""
    df = load_raw_migration_destination()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    # Must contain 1990 and 2020 columns
    assert 1990 in df.columns or "1990" in df.columns
    assert 2020 in df.columns or "2020" in df.columns


def test_load_world_bank_cached_data():
    """Test loading cached World Bank indicator data."""
    df_wb = load_world_bank_data(use_cache=True)
    assert isinstance(df_wb, pd.DataFrame)
    assert not df_wb.empty
    assert "indicator_id" in df_wb.columns
    assert "country_iso3" in df_wb.columns
    assert "value" in df_wb.columns
