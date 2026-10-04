"""
Migration Network Analysis API Router.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.network import NetworkOverviewResponse
from app.services.network_service import network_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get("/network", response_model=NetworkOverviewResponse, summary="Get migration network graph and centrality metrics")
async def get_network_endpoint(
    year: int = Query(2020, description="Census observation round year"),
    top_n_edges: int = Query(100, ge=10, le=1000, description="Top N bilateral corridors filter threshold"),
    min_stock: Optional[float] = Query(None, description="Optional minimum migrant stock filter"),
):
    """
    Construct NetworkX migration stock graph, compute node centralities, and generate 2D layout coordinates.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return network_service.get_network(year=year, top_n_edges=top_n_edges, min_stock=min_stock)
