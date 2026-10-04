"""
Country Explorer Profile API Router.
"""

from fastapi import APIRouter, Path, Query, HTTPException
from app.schemas.country import CountryProfileResponse
from app.services.country_service import country_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get(
    "/country/{country_code}",
    response_model=CountryProfileResponse,
    summary="Get complete country demographic dossier",
)
async def get_country_profile_endpoint(
    country_code: str = Path(..., description="ISO3 alpha-3 country code (e.g. 'USA')"),
    year: int = Query(2020, description="Census observation round year"),
):
    """
    Retrieve comprehensive country profile including inbound immigrant stock, outbound diaspora,
    net balance, 1990–2020 trajectory, top 10 inbound origins, and top 10 outbound destinations.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return country_service.get_profile(country_code=country_code.upper(), year=year)
