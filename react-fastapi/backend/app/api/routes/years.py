"""
Observation years route.
"""

from fastapi import APIRouter
from app.config import OBSERVATION_YEARS
from app.schemas.years import YearsResponse

router = APIRouter(prefix="/years", tags=["Years"])


@router.get("", response_model=YearsResponse, summary="Get list of available UN DESA census observation years")
def get_years() -> YearsResponse:
    """Returns the official UN DESA 1990-2020 census observation round years."""
    return YearsResponse(years=OBSERVATION_YEARS)
