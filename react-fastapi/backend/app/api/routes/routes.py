"""
Bilateral Routes & Corridors API Router.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.routes import RouteResponse
from app.services.routes_service import routes_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get("/routes", response_model=RouteResponse, summary="Query bilateral migration routes and top corridors")
async def get_routes_endpoint(
    year: int = Query(2020, description="Census round year"),
    origin: Optional[str] = Query(None, description="Optional origin country ISO3 code (e.g. 'MEX')"),
    destination: Optional[str] = Query(None, description="Optional destination country ISO3 code (e.g. 'USA')"),
    top_n: int = Query(20, ge=1, le=100, description="Number of top corridors to return"),
):
    """
    Query bilateral route data, historical 1990–2020 trajectory for pair, and top corridors.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return routes_service.get_routes(
        year=year,
        origin_code=origin,
        destination_code=destination,
        top_n=top_n,
    )
