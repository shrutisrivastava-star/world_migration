"""
Configuration management module for the Global Migration Observatory.
Loads settings from config.yaml and provides typed access and path resolvers.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


# Determine project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from config.yaml.
    
    Args:
        config_path: Path to configuration file. Defaults to PROJECT_ROOT / "config.yaml".
        
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    path = config_path or CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


class AppConfig:
    """Class wrapper providing convenient typed access to project configuration."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self._raw = config_dict or load_config()
        self.project_root = PROJECT_ROOT
        
        # Paths
        paths = self._raw.get("paths", {})
        self.raw_migration_dir = self.project_root / paths.get("raw_migration", "data/raw/migration")
        self.raw_world_bank_dir = self.project_root / paths.get("raw_world_bank", "data/raw/world_bank")
        self.processed_dir = self.project_root / paths.get("processed", "data/processed")
        self.reports_dir = self.project_root / paths.get("reports", "data/reports")
        
        # Migration settings
        mig = self._raw.get("migration_data", {})
        self.migration_source = mig.get("source", "UN DESA Population Division")
        self.migration_dataset_name = mig.get("dataset_name", "International Migrant Stock 2020")
        self.migration_revision_year = mig.get("revision_year", 2020)
        self.migration_years: List[int] = mig.get("time_horizon", [1990, 1995, 2000, 2005, 2010, 2015, 2020])
        self.min_year: int = mig.get("min_year", 1990)
        self.max_year: int = mig.get("max_year", 2020)
        self.data_type_definition = mig.get("data_type_definition", "Migrant Stock (mid-year estimates)")
        
        dest_file = mig.get("destination_file", {})
        self.destination_filename = dest_file.get("filename", "undesa_pd_2020_ims_stock_by_sex_and_destination.xlsx")
        self.destination_url = dest_file.get("url", "")
        self.destination_sheet = dest_file.get("sheet_name", "Table 1")
        self.destination_header_row = dest_file.get("header_row", 10)
        
        bilateral_file = mig.get("bilateral_file", {})
        self.bilateral_filename = bilateral_file.get("filename", "undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx")
        self.bilateral_url = bilateral_file.get("url", "")
        self.bilateral_sheet = bilateral_file.get("sheet_name", "Table 1")
        self.bilateral_header_row = bilateral_file.get("header_row", 10)
        
        # World Bank settings
        wb = self._raw.get("world_bank_data", {})
        self.wb_source = wb.get("source", "World Bank WDI")
        self.wb_api_base_url = wb.get("api_base_url", "https://api.worldbank.org/v2")
        self.wb_api_timeout = wb.get("api_timeout_seconds", 30)
        self.wb_date_range = wb.get("date_range", "1990:2020")
        self.wb_per_page = wb.get("per_page", 10000)
        self.wb_indicators: Dict[str, Dict[str, str]] = wb.get("indicators", {})
        
        # Output filenames
        outputs = self._raw.get("output_files", {})
        self.out_migration_destination = self.processed_dir / outputs.get("migration_destination", "migration_destination_cleaned.csv")
        self.out_migration_bilateral = self.processed_dir / outputs.get("migration_bilateral", "migration_bilateral_cleaned.parquet")
        self.out_world_bank = self.processed_dir / outputs.get("world_bank", "world_bank_cleaned.csv")
        self.out_merged = self.processed_dir / outputs.get("merged_country_socioeconomic", "migration_country_socioeconomic.csv")
        self.out_country_reference = self.processed_dir / outputs.get("country_reference", "country_reference.csv")
        self.out_quality_report_csv = self.reports_dir / outputs.get("quality_report_csv", "data_quality_report.csv")
        self.out_quality_report_md = self.reports_dir / outputs.get("quality_report_summary", "data_quality_summary.md")

    def ensure_directories(self) -> None:
        """Ensure all required project directories exist."""
        for directory in [
            self.raw_migration_dir,
            self.raw_world_bank_dir,
            self.processed_dir,
            self.reports_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Global default configuration instance
config = AppConfig()
