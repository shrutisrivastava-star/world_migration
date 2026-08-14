"""
Unit tests for data_validation module.
"""

import pandas as pd
import pytest

from src.data_validation import DataValidator


def test_validator_destination_valid():
    """Test validation on a well-formed destination DataFrame."""
    df = pd.DataFrame({
        "country": ["United States", "Germany"],
        "country_code": ["USA", "DEU"],
        "year": [2020, 2020],
        "migrant_stock": [50000000.0, 15000000.0],
        "is_aggregate": [False, False],
    })
    
    validator = DataValidator()
    passed = validator.validate_destination_migration(df)
    assert passed is True
    report_df = validator.generate_report_dataframe()
    assert (report_df["status"] == "PASS").all()


def test_validator_catches_negative_stock():
    """Test that validator catches invalid negative stock values."""
    df = pd.DataFrame({
        "country": ["Invalid Country"],
        "country_code": ["USA"],
        "year": [2020],
        "migrant_stock": [-100.0],  # Negative value
        "is_aggregate": [False],
    })
    
    validator = DataValidator()
    passed = validator.validate_destination_migration(df)
    assert passed is False
    
    report_df = validator.generate_report_dataframe()
    neg_check = report_df[report_df["check_name"] == "Non-Negative Migrant Stock"]
    assert len(neg_check) == 1
    assert neg_check.iloc[0]["status"] == "FAIL"


def test_validator_catches_duplicate_keys():
    """Test that validator catches duplicate (country_code, year) pairs."""
    df = pd.DataFrame({
        "country": ["United States", "United States Duplicate"],
        "country_code": ["USA", "USA"],
        "year": [2020, 2020],
        "migrant_stock": [50000000.0, 50000000.0],
        "is_aggregate": [False, False],
    })
    
    validator = DataValidator()
    passed = validator.validate_destination_migration(df)
    assert passed is False
    
    report_df = validator.generate_report_dataframe()
    dup_check = report_df[report_df["check_name"] == "Unique Primary Key (country_code, year)"]
    assert dup_check.iloc[0]["status"] == "FAIL"


def test_validator_catches_invalid_unemployment():
    """Test that validator catches out-of-range unemployment rate (> 100%)."""
    df = pd.DataFrame({
        "country": ["Country X"],
        "country_code": ["USA"],
        "year": [2020],
        "gdp": [1e12],
        "gdp_per_capita": [50000.0],
        "population": [1e7],
        "unemployment": [150.0],  # Invalid percentage
    })
    
    validator = DataValidator()
    passed = validator.validate_world_bank_data(df)
    assert passed is False
    
    report_df = validator.generate_report_dataframe()
    uem_check = report_df[report_df["check_name"] == "Unemployment Percentage Range [0-100%]"]
    assert uem_check.iloc[0]["status"] == "FAIL"
