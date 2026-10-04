"""
End-to-end data pipeline orchestrator for the Global Migration Observatory.
Executes the full workflow:
RAW DATA -> INGESTION -> CLEANING -> VALIDATION -> MERGING -> FEATURE ENGINEERING -> PROCESSED EXPORT & REPORTING
"""

import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.config import config
from src.data_cleaning import (
    clean_migration_bilateral,
    clean_migration_destination,
    clean_world_bank_data,
)
from src.data_loader import (
    ensure_un_desa_data_downloaded,
    load_raw_migration_bilateral,
    load_raw_migration_destination,
    load_world_bank_data,
)
from src.data_merging import merge_country_level, merge_route_level
from src.data_validation import DataValidator
from src.feature_engineering import (
    compute_corridor_shares,
    compute_country_rankings,
    compute_migrant_stock_pct_population,
    compute_period_stock_change,
)
from src.utils import build_country_reference_df


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(force_download: bool = False, use_cache: bool = True) -> Dict[str, Any]:
    """
    Execute the Phase 1 Foundation Data Pipeline.
    
    Args:
        force_download: If True, forces redownload of UN DESA Excel files.
        use_cache: If True, uses cached World Bank API queries.
        
    Returns:
        Dict[str, Any]: Comprehensive pipeline execution summary.
    """
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("STARTING GLOBAL MIGRATION OBSERVATORY - PHASE 1 DATA PIPELINE")
    logger.info("=" * 70)
    
    # 0. Setup directories
    config.ensure_directories()
    
    # 1. Download / Verify Raw Data
    logger.info("Step 1: Checking and acquiring raw datasets...")
    ensure_un_desa_data_downloaded(force=force_download)
    
    # 2. Ingestion
    logger.info("Step 2: Loading raw datasets...")
    raw_dest_df = load_raw_migration_destination()
    raw_bilat_df = load_raw_migration_bilateral()
    raw_wb_df = load_world_bank_data(use_cache=use_cache)
    
    # 3. Cleaning & Standardization
    logger.info("Step 3: Cleaning and standardizing datasets...")
    df_dest_cleaned = clean_migration_destination(raw_dest_df)
    df_bilat_cleaned = clean_migration_bilateral(raw_bilat_df)
    df_wb_cleaned = clean_world_bank_data(raw_wb_df)
    df_country_ref = build_country_reference_df()
    
    # 4. Merging
    logger.info("Step 4: Merging migration and socioeconomic datasets...")
    df_merged_country = merge_country_level(df_dest_cleaned, df_wb_cleaned)
    df_merged_bilat = merge_route_level(df_bilat_cleaned, df_wb_cleaned)
    
    # 5. Feature Engineering
    logger.info("Step 5: Computing scientifically valid derived features...")
    # Country-level features
    df_merged_country = compute_migrant_stock_pct_population(df_merged_country)
    df_merged_country = compute_period_stock_change(df_merged_country, id_col="country_code", year_col="year", value_col="migrant_stock")
    df_merged_country = compute_country_rankings(df_merged_country, metric_col="migrant_stock")
    df_merged_country = compute_country_rankings(df_merged_country, metric_col="migrant_stock_pct_population")
    
    # Also add period growth to destination dataset
    df_dest_cleaned = compute_period_stock_change(df_dest_cleaned, id_col="country_code", year_col="year", value_col="migrant_stock")
    df_dest_cleaned = compute_country_rankings(df_dest_cleaned, metric_col="migrant_stock")
    
    # Route-level corridor shares
    df_merged_bilat = compute_corridor_shares(df_merged_bilat)
    
    # 6. Data Validation
    logger.info("Step 6: Executing data validation rules and generating reports...")
    validator = DataValidator()
    validator.validate_destination_migration(df_dest_cleaned)
    validator.validate_bilateral_migration(df_bilat_cleaned)
    validator.validate_world_bank_data(df_wb_cleaned)
    validator.validate_merged_dataset(df_merged_country)
    
    csv_report_path, md_report_path = validator.save_reports()
    
    # 7. Export Processed Datasets
    logger.info("Step 7: Saving processed datasets to data/processed/...")
    df_dest_cleaned.to_csv(config.out_migration_destination, index=False)
    df_merged_bilat.to_parquet(config.out_migration_bilateral, index=False, engine="pyarrow")
    df_wb_cleaned.to_csv(config.out_world_bank, index=False)
    df_merged_country.to_csv(config.out_merged, index=False)
    df_country_ref.to_csv(config.out_country_reference, index=False)
    
    elapsed = time.time() - start_time
    logger.info("=" * 70)
    logger.info(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS")
    logger.info(f"Destination cleaned records: {len(df_dest_cleaned):,}")
    logger.info(f"Bilateral cleaned corridors: {len(df_merged_bilat):,}")
    logger.info(f"World Bank cleaned records: {len(df_wb_cleaned):,}")
    logger.info(f"Merged country-economic records: {len(df_merged_country):,}")
    logger.info(f"Saved reports: {csv_report_path.name}, {md_report_path.name}")
    logger.info("=" * 70)
    
    return {
        "status": "SUCCESS",
        "elapsed_seconds": round(elapsed, 2),
        "destination_records": len(df_dest_cleaned),
        "bilateral_records": len(df_merged_bilat),
        "world_bank_records": len(df_wb_cleaned),
        "merged_country_records": len(df_merged_country),
        "country_reference_count": len(df_country_ref),
        "validation_summary": validator.generate_report_dataframe().to_dict(orient="records"),
        "profiles": validator.generate_profile_dataframe().to_dict(orient="records"),
        "files_generated": {
            "migration_destination": str(config.out_migration_destination),
            "migration_bilateral": str(config.out_migration_bilateral),
            "world_bank": str(config.out_world_bank),
            "merged_country": str(config.out_merged),
            "country_reference": str(config.out_country_reference),
            "quality_report_csv": str(csv_report_path),
            "quality_report_md": str(md_report_path),
        }
    }


if __name__ == "__main__":
    run_pipeline()
