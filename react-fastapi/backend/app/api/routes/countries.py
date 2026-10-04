"""
Country entities route.
"""

from fastapi import APIRouter, Query
from app.schemas.countries import CountriesResponse
from app.services.countries_service import countries_service

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("", response_model=CountriesResponse, summary="Get list of available countries and regions")
def get_countries(
    sovereign_only: bool = Query(
        False,
        description="Filter to only recognized sovereign nations, excluding regional/income aggregates",
    )
) -> CountriesResponse:
    """Returns available countries and geographic entities from the observatory."""
    return countries_service.get_all_countries(sovereign_only=sovereign_only)
