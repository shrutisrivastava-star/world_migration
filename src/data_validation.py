"""
Data validation module for the Global Migration Observatory.
Performs schema, type, range, constraint, duplicate, and completeness checks across datasets.
Generates comprehensive machine-readable and human-readable data quality reports.
"""

from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.config import config
from src.utils import get_iso3_lookup_maps


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ValidationCheckResult:
    """Represents the outcome of a single validation rule."""
    dataset_name: str
    check_name: str
    passed: bool
    details: str
    severity: str = "ERROR"  # 'ERROR', 'WARNING', or 'INFO'


def _df_to_markdown_table(df: pd.DataFrame) -> str:
    """Format DataFrame as a Markdown table without external dependencies."""
    if df.empty:
        return "_No data available._"
    
    headers = [str(c) for c in df.columns]
    col_widths = [max(len(h), 4) for h in headers]
    
    rows_data = []
    for _, row in df.iterrows():
        row_str = [str(v) if pd.notna(v) else "" for v in row.values]
        rows_data.append(row_str)
        for i, val in enumerate(row_str):
            col_widths[i] = max(col_widths[i], len(val))
            
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    separator_line = "|-" + "-|-".join("-" * col_widths[i] for i in range(len(headers))) + "-|"
    
    table_lines = [header_line, separator_line]
    for row in rows_data:
        table_lines.append("| " + " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(row)) + " |")
        
    return "\n".join(table_lines)


class DataValidator:
    """Performs validation checks across raw, cleaned, and merged datasets."""

    def __init__(self):
        _, _, self.valid_iso3 = get_iso3_lookup_maps()
        self.results: List[ValidationCheckResult] = []
        self.dataset_profiles: List[Dict[str, Any]] = []

    def validate_destination_migration(self, df: pd.DataFrame) -> bool:
        """Validate destination migration dataset."""
        ds_name = "UN DESA Destination Migrant Stock"
        all_passed = True
        
        # 1. Required columns
        required_cols = ["country", "country_code", "year", "migrant_stock", "is_aggregate"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        passed = len(missing_cols) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Required Columns Exist",
            passed=passed,
            details=f"Missing: {missing_cols}" if not passed else "All required columns present."
        ))
        if not passed:
            all_passed = False
            
        # 2. Year range
        valid_years = set(config.migration_years)
        actual_years = set(df["year"].dropna().unique())
        invalid_years = actual_years - valid_years
        passed = len(invalid_years) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Valid Year Range",
            passed=passed,
            details=f"Unexpected years: {invalid_years}" if not passed else f"Valid years: {sorted(list(actual_years))}"
        ))
        if not passed:
            all_passed = False

        # 3. Country Codes
        non_null_codes = df["country_code"].dropna()
        sovereign_df = df[~df["is_aggregate"]]
        sovereign_invalid = [c for c in sovereign_df["country_code"].dropna() if c not in self.valid_iso3]
        passed = len(sovereign_invalid) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Sovereign ISO3 Country Codes",
            passed=passed,
            details=f"{len(sovereign_invalid)} invalid sovereign ISO3 codes found" if not passed else "All sovereign country codes are valid ISO3."
        ))
        if not passed:
            all_passed = False

        # 4. Non-negative Migrant Stock
        neg_stocks = df[df["migrant_stock"] < 0]
        passed = len(neg_stocks) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Non-Negative Migrant Stock",
            passed=passed,
            details=f"Found {len(neg_stocks)} negative migrant stock records" if not passed else "All migrant stock values are non-negative."
        ))
        if not passed:
            all_passed = False

        # 5. Duplicate Keys (country_code + year)
        valid_rows = df.dropna(subset=["country_code", "year"])
        dups = valid_rows[valid_rows.duplicated(subset=["country_code", "year"], keep=False)]
        passed = len(dups) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Unique Primary Key (country_code, year)",
            passed=passed,
            details=f"Found {len(dups)} duplicate (country_code, year) rows" if not passed else "Primary keys are unique."
        ))
        if not passed:
            all_passed = False

        # Profile
        self._profile_dataset(df, ds_name, ["migrant_stock"])
        return all_passed

    def validate_bilateral_migration(self, df: pd.DataFrame) -> bool:
        """Validate bilateral migration dataset."""
        ds_name = "UN DESA Bilateral Migrant Stock"
        all_passed = True
        
        # 1. Required columns
        required_cols = ["origin_country", "origin_code", "destination_country", "destination_code", "year", "migrant_stock"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        passed = len(missing_cols) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Required Columns Exist",
            passed=passed,
            details=f"Missing: {missing_cols}" if not passed else "All required columns present."
        ))
        if not passed:
            all_passed = False

        # 2. Non-negative Migrant Stock
        neg_stocks = df[df["migrant_stock"] < 0]
        passed = len(neg_stocks) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Non-Negative Migrant Stock",
            passed=passed,
            details=f"Found {len(neg_stocks)} negative corridor records" if not passed else "All bilateral migrant stock values are non-negative."
        ))
        if not passed:
            all_passed = False

        # 3. Duplicate Corridors (origin_code + destination_code + year)
        valid_rows = df.dropna(subset=["origin_code", "destination_code", "year"])
        dups = valid_rows[valid_rows.duplicated(subset=["origin_code", "destination_code", "year"], keep=False)]
        passed = len(dups) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Unique Corridor Key (origin, dest, year)",
            passed=passed,
            details=f"Found {len(dups)} duplicate corridor rows" if not passed else "Corridor primary keys are unique."
        ))
        if not passed:
            all_passed = False

        # Profile
        self._profile_dataset(df, ds_name, ["migrant_stock"])
        return all_passed

    def validate_world_bank_data(self, df: pd.DataFrame) -> bool:
        """Validate cleaned World Bank socioeconomic dataset."""
        ds_name = "World Bank Socioeconomic Indicators"
        all_passed = True
        
        # 1. Required columns
        required_cols = ["country", "country_code", "year", "gdp", "gdp_per_capita", "population", "unemployment"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        passed = len(missing_cols) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Required Columns Exist",
            passed=passed,
            details=f"Missing: {missing_cols}" if not passed else "All indicator columns present."
        ))
        if not passed:
            all_passed = False

        # 2. Non-negative Population & GDP per capita
        neg_pop = df[df["population"] < 0]
        neg_gdp_pc = df[df["gdp_per_capita"] < 0]
        passed = len(neg_pop) == 0 and len(neg_gdp_pc) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Non-Negative Population & GDP/Capita",
            passed=passed,
            details=f"Negative pop: {len(neg_pop)}, negative gdp_per_capita: {len(neg_gdp_pc)}" if not passed else "Values are strictly non-negative."
        ))
        if not passed:
            all_passed = False

        # 3. Unemployment range [0, 100]
        invalid_uem = df[(df["unemployment"] < 0) | (df["unemployment"] > 100)]
        passed = len(invalid_uem) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Unemployment Percentage Range [0-100%]",
            passed=passed,
            details=f"Found {len(invalid_uem)} out-of-range unemployment records" if not passed else "All unemployment rates within 0-100%."
        ))
        if not passed:
            all_passed = False

        # 4. Duplicate Primary Key
        dups = df[df.duplicated(subset=["country_code", "year"], keep=False)]
        passed = len(dups) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Unique Primary Key (country_code, year)",
            passed=passed,
            details=f"Found {len(dups)} duplicate (country_code, year) rows" if not passed else "Primary keys are unique."
        ))
        if not passed:
            all_passed = False

        # Profile
        self._profile_dataset(df, ds_name, ["gdp", "gdp_per_capita", "population", "unemployment"])
        return all_passed

    def validate_merged_dataset(self, df: pd.DataFrame) -> bool:
        """Validate merged country-level migration and socioeconomic dataset."""
        ds_name = "Merged Country Socioeconomic Dataset"
        all_passed = True
        
        # 1. Required merged columns
        required_cols = ["country", "country_code", "year", "migrant_stock", "population", "gdp", "gdp_per_capita", "unemployment"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        passed = len(missing_cols) == 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Required Merged Columns Exist",
            passed=passed,
            details=f"Missing: {missing_cols}" if not passed else "All merged fields present."
        ))
        if not passed:
            all_passed = False

        # 2. Check overlap coverage
        has_stock = df["migrant_stock"].notna()
        has_pop = df["population"].notna()
        overlap_count = (has_stock & has_pop).sum()
        passed = overlap_count > 0
        self.results.append(ValidationCheckResult(
            dataset_name=ds_name,
            check_name="Migration & Population Overlap",
            passed=passed,
            details=f"{overlap_count:,} records have both migrant stock and population."
        ))
        if not passed:
            all_passed = False

        # Profile
        self._profile_dataset(df, ds_name, ["migrant_stock", "population", "gdp", "gdp_per_capita", "unemployment"])
        return all_passed

    def _profile_dataset(self, df: pd.DataFrame, dataset_name: str, key_numeric_cols: List[str]) -> None:
        """Generate summary dimensions and missingness profile for a dataset."""
        total_rows = len(df)
        total_cols = len(df.columns)
        
        country_col = "country_code" if "country_code" in df.columns else ("destination_code" if "destination_code" in df.columns else None)
        unique_countries = df[country_col].nunique() if country_col else 0
        
        year_col = "year" if "year" in df.columns else None
        years_list = sorted(df[year_col].dropna().unique().tolist()) if year_col else []
        min_year = years_list[0] if years_list else None
        max_year = years_list[-1] if years_list else None
        
        missing_summary = {}
        for col in key_numeric_cols:
            if col in df.columns:
                null_count = int(df[col].isna().sum())
                null_pct = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
                missing_summary[f"missing_{col}_count"] = null_count
                missing_summary[f"missing_{col}_pct"] = null_pct
                
        profile = {
            "dataset_name": dataset_name,
            "total_rows": total_rows,
            "total_columns": total_cols,
            "unique_countries": unique_countries,
            "min_year": min_year,
            "max_year": max_year,
            "years_covered": ", ".join(str(y) for y in years_list),
            **missing_summary
        }
        self.dataset_profiles.append(profile)

    def generate_report_dataframe(self) -> pd.DataFrame:
        """Return all validation check outcomes as a DataFrame."""
        rows = []
        for r in self.results:
            rows.append({
                "dataset_name": r.dataset_name,
                "check_name": r.check_name,
                "status": "PASS" if r.passed else "FAIL",
                "severity": r.severity,
                "details": r.details,
            })
        return pd.DataFrame(rows)

    def generate_profile_dataframe(self) -> pd.DataFrame:
        """Return dataset profiling summary as a DataFrame."""
        return pd.DataFrame(self.dataset_profiles)

    def save_reports(self) -> Tuple[Path, Path]:
        """Save data quality reports to reports directory in CSV and Markdown."""
        config.ensure_directories()
        df_checks = self.generate_report_dataframe()
        df_profiles = self.generate_profile_dataframe()
        
        csv_path = config.out_quality_report_csv
        md_path = config.out_quality_report_md
        
        # Save CSV
        df_checks.to_csv(csv_path, index=False)
        logger.info(f"Saved validation checks report to: {csv_path}")
        
        # Build Markdown Summary
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks
        
        md_content = [
            "# Global Migration Observatory - Data Quality & Validation Report",
            "",
            f"**Phase**: Phase 1 Foundation & Data Ingestion  ",
            f"**Status**: {'✅ ALL CHECKS PASSED' if failed_checks == 0 else f'⚠️ {failed_checks} CHECKS FAILED'}  ",
            f"**Summary**: {passed_checks}/{total_checks} validation checks passed.  ",
            "",
            "---",
            "",
            "## 1. Dataset Dimensions & Coverage",
            "",
            _df_to_markdown_table(df_profiles),
            "",
            "---",
            "",
            "## 2. Validation Check Results",
            "",
            _df_to_markdown_table(df_checks),
            "",
            "---",
            "",
            "## 3. Data Integrity & Methodological Notes",
            "",
            "- **Migrant Stock vs Flow**: Migrant stock represents the estimated number of foreign-born / foreign citizens residing in a country at mid-year. It is **NOT** annual migration flow.",
            "- **Zero Fabrication**: No values were synthetically generated, imputed arbitrarily, or replaced with placeholders.",
            "- **Aggregates Handling**: Regional and income group aggregates are cleanly categorized and flagged (`is_aggregate`) to prevent distorting sovereign country comparisons.",
            "- **Country Resolution**: ISO 3166-1 alpha-3 codes are enforced as the primary merge key across UN DESA and World Bank sources.",
            "",
        ]
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))
            
        logger.info(f"Saved markdown quality report summary to: {md_path}")
        return csv_path, md_path
