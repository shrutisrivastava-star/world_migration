"""
Data Service layer.
Provides in-memory caching and thread-safe access to processed UN DESA and World Bank datasets,
ensuring high performance by avoiding repeated disk and parquet I/O on every API request.
"""

from pathlib import Path
import sys
from typing import Dict, Optional
import pandas as pd
import logging

# Ensure backend root is in sys.path so src.* modules can be imported
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.dashboard_data import (
    prepare_country_socioeconomic_data,
    prepare_bilateral_corridor_data,
    load_canonical_country_map,
)

logger = logging.getLogger("gmo.data_service")


class DataService:
    """Singleton in-memory data store for the Global Migration Observatory."""

    _instance: Optional["DataService"] = None

    def __new__(cls) -> "DataService":
        if cls._instance is None:
            cls._instance = super(DataService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._country_socioeconomic_df: Optional[pd.DataFrame] = None
        self._bilateral_corridor_df: Optional[pd.DataFrame] = None
        self._canonical_country_map: Optional[Dict[str, str]] = None
        self._initialized = True

    def get_country_socioeconomic_data(self) -> pd.DataFrame:
        """
        Get or lazily load the merged country socioeconomic dataset.
        
        Returns:
            pd.DataFrame: Cleaned country socioeconomic dataset.
        """
        if self._country_socioeconomic_df is None:
            logger.info("Loading country socioeconomic dataset into memory cache...")
            self._country_socioeconomic_df = prepare_country_socioeconomic_data()
            logger.info(f"Loaded country socioeconomic dataset: {len(self._country_socioeconomic_df)} rows.")
        return self._country_socioeconomic_df

    def get_bilateral_corridor_data(self) -> pd.DataFrame:
        """
        Get or lazily load the bilateral corridor dataset.
        
        Returns:
            pd.DataFrame: Cleaned bilateral migration corridor dataset.
        """
        if self._bilateral_corridor_df is None:
            logger.info("Loading bilateral corridor dataset into memory cache...")
            self._bilateral_corridor_df = prepare_bilateral_corridor_data()
            logger.info(f"Loaded bilateral corridor dataset: {len(self._bilateral_corridor_df)} rows.")
        return self._bilateral_corridor_df

    def get_canonical_country_map(self) -> Dict[str, str]:
        """
        Get or lazily load canonical ISO3-to-Display-Name mapping dictionary.
        
        Returns:
            Dict[str, str]: Mapping of ISO3 codes to clean country display names.
        """
        if self._canonical_country_map is None:
            self._canonical_country_map = load_canonical_country_map()
        return self._canonical_country_map

    def preload_all(self) -> None:
        """Preload all datasets into cache during application startup."""
        self.get_country_socioeconomic_data()
        self.get_bilateral_corridor_data()
        self.get_canonical_country_map()


# Global service instance
data_service = DataService()
