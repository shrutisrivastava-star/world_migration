"""
Health check route.
"""

from fastapi import APIRouter
from app.config import PROJECT_NAME, PROJECT_VERSION
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="Get backend service health status")
def get_health() -> HealthResponse:
    """Returns the operational status, project name, and version of the API."""
    return HealthResponse(
        status="ok",
        project=PROJECT_NAME,
        version=PROJECT_VERSION,
    )
