"""
Data loader module for the Global Migration Observatory.
Handles downloading and ingestion of UN DESA International Migrant Stock datasets
and World Bank World Development Indicators via API and local caching.
"""

import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import pandas as pd
import requests

from src.config import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def download_file(url: str, destination_path: Path, chunk_size: int = 65536) -> Path:
    """
    Download a remote file with streaming and progress logging.
    
    Args:
        url: Remote file URL.
        destination_path: Local destination Path.
        chunk_size: Stream chunk size in bytes.
        
    Returns:
        Path: Path to downloaded file.
    """
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading from {url} to {destination_path}...")
    headers = {"User-Agent": "Global-Migration-Observatory/1.0 (Research Pipeline)"}
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=90)
        response.raise_for_status()
        
        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    
        logger.info(f"Successfully downloaded: {destination_path} ({destination_path.stat().st_size:,} bytes)")
        return destination_path
    except Exception as e:
        if destination_path.exists():
            destination_path.unlink()  # Clean up partial download
        logger.error(f"Failed to download from {url}: {e}")
        raise RuntimeError(
            f"Could not download dataset from {url}.\n"
            f"Please download the file manually and place it at:\n{destination_path.resolve()}"
        ) from e


def ensure_un_desa_data_downloaded(force: bool = False) -> Dict[str, Path]:
    """
    Ensure that the official UN DESA 2020 revision datasets are present in data/raw/migration.
    Downloads them if missing.
    
    Args:
        force: If True, re-downloads even if files already exist.
        
    Returns:
        Dict[str, Path]: Map of dataset keys to local file paths.
    """
    config.ensure_directories()
    dest_path = config.raw_migration_dir / config.destination_filename
    bilateral_path = config.raw_migration_dir / config.bilateral_filename
    
    # Check/download destination file
    if force or not dest_path.exists():
        logger.info(f"UN DESA destination dataset not found at {dest_path}. Initiating download...")
        download_file(config.destination_url, dest_path)
    else:
        logger.info(f"Found existing UN DESA destination file: {dest_path}")
        
    # Check/download bilateral file
    if force or not bilateral_path.exists():
        logger.info(f"UN DESA bilateral dataset not found at {bilateral_path}. Initiating download...")
        download_file(config.bilateral_url, bilateral_path)
    else:
        logger.info(f"Found existing UN DESA bilateral file: {bilateral_path}")
        
    return {
        "destination": dest_path,
        "bilateral": bilateral_path,
    }


def load_raw_migration_destination(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load raw UN DESA International Migrant Stock by Destination (Table 1).
    
    Args:
        file_path: Optional path to Excel file. Defaults to configured path.
        
    Returns:
        pd.DataFrame: Raw destination migrant stock DataFrame.
    """
    path = file_path or (config.raw_migration_dir / config.destination_filename)
    if not path.exists():
        ensure_un_desa_data_downloaded()
        
    logger.info(f"Loading UN DESA destination migrant stock from {path} (Sheet: {config.destination_sheet})...")
    
    try:
        df = pd.read_excel(
            path,
            sheet_name=config.destination_sheet,
            header=config.destination_header_row,
            engine="openpyxl"
        )
    except Exception as e:
        logger.error(f"Error reading Excel sheet '{config.destination_sheet}' from {path}: {e}")
        raise
        
    logger.info(f"Raw destination dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df


def load_raw_migration_bilateral(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load raw UN DESA International Migrant Stock by Destination and Origin (Table 1).
    
    Args:
        file_path: Optional path to Excel file. Defaults to configured path.
        
    Returns:
        pd.DataFrame: Raw bilateral migrant stock DataFrame.
    """
    path = file_path or (config.raw_migration_dir / config.bilateral_filename)
    if not path.exists():
        ensure_un_desa_data_downloaded()
        
    logger.info(f"Loading UN DESA bilateral migrant stock from {path} (Sheet: {config.bilateral_sheet})...")
    
    try:
        df = pd.read_excel(
            path,
            sheet_name=config.bilateral_sheet,
            header=config.bilateral_header_row,
            engine="openpyxl"
        )
    except Exception as e:
        logger.error(f"Error reading Excel sheet '{config.bilateral_sheet}' from {path}: {e}")
        raise
        
    logger.info(f"Raw bilateral dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df


def _fetch_wb_with_retry(url: str, params: Dict[str, Any], max_retries: int = 3, backoff_factor: float = 1.5) -> Dict[str, Any]:
    """Execute a World Bank API request with exponential backoff retry."""
    headers = {"User-Agent": "Global-Migration-Observatory/1.0 (Research Pipeline)"}
    last_err: Optional[Exception] = None
    
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=config.wb_api_timeout)
            resp.raise_for_status()
            res_json = resp.json()
            return res_json
        except Exception as e:
            last_err = e
            wait_time = backoff_factor ** attempt
            logger.warning(f"WB API request failed (attempt {attempt}/{max_retries}): {e}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
            
    raise RuntimeError(f"Failed World Bank API request after {max_retries} retries: {last_err}") from last_err


def fetch_world_bank_indicator(
    indicator_code: str,
    date_range: Optional[str] = None,
    use_cache: bool = True
) -> pd.DataFrame:
    """
    Fetch a specific indicator from the World Bank API with local disk caching and retries.
    
    Args:
        indicator_code: World Bank series code (e.g. 'NY.GDP.MKTP.CD').
        date_range: Date range string (e.g. '1990:2020').
        use_cache: Whether to use cached JSON responses.
        
    Returns:
        pd.DataFrame: Raw indicator data points with metadata.
    """
    config.ensure_directories()
    date_range = date_range or config.wb_date_range
    cache_file = config.raw_world_bank_dir / f"{indicator_code}_{date_range.replace(':', '_')}.json"
    
    data_records: List[Dict[str, Any]] = []
    
    if use_cache and cache_file.exists():
        logger.info(f"Loading cached World Bank indicator '{indicator_code}' from {cache_file}...")
        with open(cache_file, "r", encoding="utf-8") as f:
            data_records = json.load(f)
    else:
        url = f"{config.wb_api_base_url}/country/all/indicator/{indicator_code}"
        params = {
            "format": "json",
            "date": date_range,
            "per_page": 4000,
            "page": 1,
        }
        
        logger.info(f"Querying World Bank API for {indicator_code} ({date_range})...")
        try:
            res_json = _fetch_wb_with_retry(url, params)
            
            if len(res_json) < 2 or not isinstance(res_json[1], list):
                raise ValueError(f"Unexpected response format from World Bank API: {res_json}")
                
            data_records = res_json[1]
            page_meta = res_json[0]
            total_pages = page_meta.get("pages", 1)
            
            # Fetch remaining pages if any
            for page in range(2, total_pages + 1):
                params["page"] = page
                logger.info(f"Fetching page {page}/{total_pages} for {indicator_code}...")
                res_page = _fetch_wb_with_retry(url, params)
                if len(res_page) >= 2 and isinstance(res_page[1], list):
                    data_records.extend(res_page[1])
                    
            # Save cache
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data_records, f, indent=2)
            logger.info(f"Cached {len(data_records)} records to {cache_file}")
            
        except Exception as e:
            logger.error(f"Failed to fetch World Bank indicator {indicator_code}: {e}")
            if cache_file.exists():
                logger.warning("Falling back to existing cache file despite use_cache=False.")
                with open(cache_file, "r", encoding="utf-8") as f:
                    data_records = json.load(f)
            else:
                raise RuntimeError(
                    f"Failed to retrieve World Bank data for '{indicator_code}' from API.\n"
                    f"Please check your internet connection or place raw JSON in:\n{cache_file.resolve()}"
                ) from e
                
    # Normalize records into tabular structure
    parsed_rows = []
    for item in data_records:
        parsed_rows.append({
            "indicator_id": item.get("indicator", {}).get("id", indicator_code),
            "indicator_name": item.get("indicator", {}).get("value", ""),
            "country_iso2": item.get("country", {}).get("id", ""),
            "country_name": item.get("country", {}).get("value", ""),
            "country_iso3": item.get("countryiso3code", ""),
            "year": item.get("date"),
            "value": item.get("value"),
            "unit": item.get("unit", ""),
        })
        
    df = pd.DataFrame(parsed_rows)
    logger.info(f"Parsed indicator '{indicator_code}': {len(df)} records.")
    return df


def load_world_bank_data(
    indicators: Optional[Dict[str, Dict[str, str]]] = None,
    date_range: Optional[str] = None,
    use_cache: bool = True
) -> pd.DataFrame:
    """
    Fetch and combine all configured World Bank indicators into a unified raw DataFrame.
    
    Args:
        indicators: Dictionary of indicator configurations. Defaults to config.wb_indicators.
        date_range: Date range string. Defaults to config.wb_date_range.
        use_cache: Whether to use disk cache.
        
    Returns:
        pd.DataFrame: Combined raw World Bank indicators DataFrame.
    """
    ind_dict = indicators or config.wb_indicators
    dfs: List[pd.DataFrame] = []
    
    for ind_code in ind_dict.keys():
        df_ind = fetch_world_bank_indicator(ind_code, date_range=date_range, use_cache=use_cache)
        dfs.append(df_ind)
        
    combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    logger.info(f"Loaded all World Bank indicators: total {len(combined)} raw records across {len(ind_dict)} indicators.")
    return combined


def load_processed_data(file_name: str) -> pd.DataFrame:
    """
    Load a processed dataset from data/processed/.
    Supports .csv and .parquet.
    
    Args:
        file_name: Base filename (e.g. 'migration_destination_cleaned.csv').
        
    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    file_path = config.processed_dir / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at: {file_path.resolve()}")
        
    if file_name.endswith(".parquet"):
        return pd.read_parquet(file_path)
    elif file_name.endswith(".csv"):
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format for {file_name}. Expected .csv or .parquet.")
