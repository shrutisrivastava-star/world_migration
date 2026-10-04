"""
Corridor Intelligence & Concentration API Router.
"""

from typing import List
from fastapi import APIRouter, Query, HTTPException
from app.schemas.corridor import (
    CorridorOverviewResponse,
    CorridorConcentrationPoint,
    CorridorDetailResponse,
)
from app.services.corridor_service import corridor_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get("/corridors/overview", response_model=CorridorOverviewResponse, summary="Get corridor intelligence overview and top rankings")
async def get_corridors_overview_endpoint(
    year: int = Query(2020, description="Census observation round year"),
    top_n: int = Query(10, ge=1, le=100, description="Number of top corridors to return"),
):
    """
    Retrieve corridor intelligence overview metrics, top ranked corridors, and longitudinal concentration trend.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return corridor_service.get_overview(year=year, top_n=top_n)


@router.get("/corridors/concentration", response_model=List[CorridorConcentrationPoint], summary="Get 1990–2020 corridor concentration trend")
async def get_corridor_concentration_endpoint():
    """
    Retrieve global bilateral corridor concentration shares (Top 10, Top 25, Top 50) across 1990–2020.
    """
    return corridor_service.get_concentration()


@router.get("/corridors/detail", response_model=CorridorDetailResponse, summary="Get deep-dive metrics and trajectory for a bilateral corridor")
async def get_corridor_detail_endpoint(
    origin: str = Query(..., description="Origin ISO3 code (e.g. 'MEX')"),
    destination: str = Query(..., description="Destination ISO3 code (e.g. 'USA')"),
    year: int = Query(2020, description="Census observation round year"),
):
    """
    Compute historical trajectory, 5-year growth rate, deterministic classification, and rank for a corridor pair.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return corridor_service.get_corridor_detail(
        origin_code=origin.upper(), destination_code=destination.upper(), year=year
    )
