"""
Backend application configuration module.
Loads settings and environment variables for the FastAPI service.
"""

from pathlib import Path
from typing import List
import os

# Project base paths
BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent if (BACKEND_ROOT.parent / "data").exists() else BACKEND_ROOT
DATA_DIR = PROJECT_ROOT / "data"

# Application Settings
PROJECT_NAME: str = "Global Migration Observatory"
PROJECT_VERSION: str = "react-vite"
API_PREFIX: str = "/api"

# CORS Configuration
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Supported Census Observation Years
OBSERVATION_YEARS: List[int] = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
