"""
FastAPI application entrypoint for the Global Migration Observatory.
Provides decoupled REST API endpoints for the React + Vite frontend.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import sys
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend root is in sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    ALLOWED_ORIGINS,
    API_PREFIX,
)
from app.api.routes import (
    health,
    years,
    countries,
    overview,
    map as map_route,
    trends,
    rankings,
    routes as routes_route,
    country,
    network,
    corridors,
    communities,
    advanced_analytics,
)
from app.services.data_service import data_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gmo.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for warming caches and cleanup."""
    logger.info(f"Starting {PROJECT_NAME} (version: {PROJECT_VERSION})...")
    try:
        data_service.preload_all()
        logger.info("Observatory datasets loaded into memory successfully.")
    except Exception as e:
        logger.warning(f"Could not preload datasets during startup (will lazy-load): {e}")
    yield
    logger.info("Shutting down Global Migration Observatory API service.")


app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION,
    description="Scientific analytics API for global migration stock and socioeconomic indicators (UN DESA & World Bank).",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local React / Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register API Routers under /api prefix
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(years.router, prefix=API_PREFIX)
app.include_router(countries.router, prefix=API_PREFIX)
app.include_router(overview.router, prefix=API_PREFIX)
app.include_router(map_route.router, prefix=API_PREFIX)
app.include_router(trends.router, prefix=API_PREFIX)
app.include_router(rankings.router, prefix=API_PREFIX)
app.include_router(routes_route.router, prefix=API_PREFIX)
app.include_router(country.router, prefix=API_PREFIX)
app.include_router(network.router, prefix=API_PREFIX)
app.include_router(corridors.router, prefix=API_PREFIX)
app.include_router(communities.router, prefix=API_PREFIX)
app.include_router(advanced_analytics.router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"])
def health_alias():
    """Root health alias."""
    return {"status": "ok", "project": PROJECT_NAME, "version": PROJECT_VERSION}


@app.get("/", tags=["Root"])
def root():
    """Root metadata endpoint."""
    return {
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
        "api_endpoints": [
            f"{API_PREFIX}/health",
            f"{API_PREFIX}/years",
            f"{API_PREFIX}/countries",
            f"{API_PREFIX}/overview",
            f"{API_PREFIX}/map",
            f"{API_PREFIX}/trends/global",
            f"{API_PREFIX}/trends/countries",
            f"{API_PREFIX}/rankings",
            f"{API_PREFIX}/routes",
            f"{API_PREFIX}/country/{{country_code}}",
            f"{API_PREFIX}/network",
            f"{API_PREFIX}/corridors/overview",
            f"{API_PREFIX}/corridors/concentration",
            f"{API_PREFIX}/corridors/detail",
            f"{API_PREFIX}/communities",
            f"{API_PREFIX}/communities/{{community_id}}",
            f"{API_PREFIX}/analytics/overview",
            f"{API_PREFIX}/analytics/concentration",
            f"{API_PREFIX}/analytics/correlations",
            f"{API_PREFIX}/analytics/scatter",
            f"{API_PREFIX}/analytics/outliers",
            f"{API_PREFIX}/analytics/compare",
            f"{API_PREFIX}/analytics/insights",
        ],
    }
