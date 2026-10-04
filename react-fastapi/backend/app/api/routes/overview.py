"""
Overview KPIs route.
"""

from fastapi import APIRouter, Query
from app.schemas.overview import OverviewKPIsResponse
from app.services.overview_service import overview_service

router = APIRouter(prefix="/overview", tags=["Overview"])


@router.get("", response_model=OverviewKPIsResponse, summary="Get executive migration overview KPIs for a selected year")
def get_overview(
    year: int = Query(
        2020,
        description="Census observation round year (1990, 1995, 2000, 2005, 2010, 2015, 2020)",
        examples=[2020],
    )
) -> OverviewKPIsResponse:
    """Computes global migrant stock, share of world population, participating countries, and top destinations."""
    return overview_service.get_overview_kpis_for_year(year=year)
