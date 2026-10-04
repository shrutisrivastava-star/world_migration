"""
Global Choropleth Map API Router.
"""

from fastapi import APIRouter, Query, HTTPException
from app.schemas.map import MapDataResponse
from app.services.map_service import map_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get("/map", response_model=MapDataResponse, summary="Get choropleth map country data")
async def get_map_data_endpoint(
    year: int = Query(2020, description="Census observation round year (1990, 1995, ..., 2020)"),
    metric: str = Query("Migrant Stock", description="Metric to visualize on world map"),
):
    """
    Retrieve country records for choropleth mapping.
    
    Validates observation round and returns resolved country metrics with ISO3 codes.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return map_service.get_map(year=year, metric_name=metric)
