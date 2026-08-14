"""
Unit tests for data_cleaning and standardization module.
"""

import numpy as np
import pandas as pd
import pytest

from src.data_cleaning import (
    clean_migration_destination,
    clean_world_bank_data,
)
from src.utils import classify_entity_type, resolve_country_code


def test_resolve_country_code_standard():
    """Test resolution of canonical country names and codes."""
    assert resolve_country_code(country_name="United States of America") == "USA"
    assert resolve_country_code(country_name="United States*") == "USA"
    assert resolve_country_code(country_name="Germany") == "DEU"
    assert resolve_country_code(country_name="India") == "IND"
    assert resolve_country_code(country_name="Viet Nam") == "VNM"
    assert resolve_country_code(country_name="Russian Federation") == "RUS"
    assert resolve_country_code(iso_code="FRA") == "FRA"
    assert resolve_country_code(m49_code=840) == "USA"
    assert resolve_country_code(m49_code=356) == "IND"


def test_resolve_country_code_aggregates():
    """Test that regional aggregate M49 codes are not mapped to sovereign ISO3 codes."""
    assert resolve_country_code(m49_code=900) is None  # World
    assert resolve_country_code(m49_code=954) is None  # Micronesia Region
    assert resolve_country_code(m49_code=910) is None  # Sub-Saharan Africa


def test_classify_entity_type():
    """Test sovereign vs aggregate classification."""
    assert classify_entity_type("USA") == "country"
    assert classify_entity_type("PRI") == "territory"  # Puerto Rico
    assert classify_entity_type("WLD") == "world"
    assert classify_entity_type("HIC") == "income_group"
    assert classify_entity_type("SSA") == "region"
    assert classify_entity_type(None, country_name="Sub-Saharan Africa", m49_code=910) == "region"
    assert classify_entity_type(None, country_name="WORLD", m49_code=900) == "world"


def test_clean_migration_destination_synthetic_sample():
    """Test clean_migration_destination with sample data."""
    sample_raw = pd.DataFrame({
        "Unnamed: 0": [1, 2],
        "Region, development group, country or area": ["United States of America*", "WORLD"],
        "Location code": [840, 900],
        "Notes": [None, None],
        "Type of data": ["B", "G"],
        1990: ["1000", "5000"],
        1995: ["..", "6000"],
        2000: [2000, 7000],
        2005: [2500, 8000],
        2010: [3000, 9000],
        2015: [3500, 10000],
        2020: [4000, 11000],
    })
    
    cleaned = clean_migration_destination(sample_raw)
    assert isinstance(cleaned, pd.DataFrame)
    assert len(cleaned) == 14  # 2 entities * 7 years
    
    usa_1995 = cleaned[(cleaned["country_code"] == "USA") & (cleaned["year"] == 1995)]
    assert len(usa_1995) == 1
    # '..' should be converted to NaN
    assert pd.isna(usa_1995["migrant_stock"].values[0])
    
    usa_2020 = cleaned[(cleaned["country_code"] == "USA") & (cleaned["year"] == 2020)]
    assert usa_2020["migrant_stock"].values[0] == 4000.0


def test_clean_world_bank_data_pivoting():
    """Test pivoting raw World Bank indicators into country-year structure."""
    raw_wb = pd.DataFrame([
        {"indicator_id": "NY.GDP.MKTP.CD", "indicator_name": "GDP", "country_iso2": "US", "country_name": "United States", "country_iso3": "USA", "year": "2020", "value": 2.1e13, "unit": ""},
        {"indicator_id": "SP.POP.TOTL", "indicator_name": "Population", "country_iso2": "US", "country_name": "United States", "country_iso3": "USA", "year": "2020", "value": 3.3e8, "unit": ""},
        {"indicator_id": "NY.GDP.PCAP.CD", "indicator_name": "GDP per capita", "country_iso2": "US", "country_name": "United States", "country_iso3": "USA", "year": "2020", "value": 63000.0, "unit": ""},
        {"indicator_id": "SL.UEM.TOTL.ZS", "indicator_name": "Unemployment", "country_iso2": "US", "country_name": "United States", "country_iso3": "USA", "year": "2020", "value": 8.05, "unit": ""},
    ])
    
    cleaned_wb = clean_world_bank_data(raw_wb)
    assert len(cleaned_wb) == 1
    row = cleaned_wb.iloc[0]
    assert row["country_code"] == "USA"
    assert row["year"] == 2020
    assert row["gdp"] == 2.1e13
    assert row["population"] == 3.3e8
    assert row["gdp_per_capita"] == 63000.0
    assert row["unemployment"] == 8.05
