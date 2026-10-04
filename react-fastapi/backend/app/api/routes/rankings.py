"""
Country Rankings API Router.
"""

from fastapi import APIRouter, Query, HTTPException
from app.schemas.rankings import RankingsResponse
from app.services.rankings_service import rankings_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get("/rankings", response_model=RankingsResponse, summary="Get country rankings for a census round")
async def get_rankings_endpoint(
    year: int = Query(2020, description="Census round year"),
    metric: str = Query("Migrant Stock", description="Metric to rank countries by"),
    top_n: int = Query(10, ge=1, le=250, description="Number of top countries to return"),
    ascending: bool = Query(False, description="Sort ascending (lowest first) if true"),
):
    """
    Compute and return sovereign country rankings for a specific census round.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return rankings_service.get_rankings(
        year=year, metric_name=metric, top_n=top_n, ascending=ascending
    )
