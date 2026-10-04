"""
Community Detection API Router.
"""

from fastapi import APIRouter, Path, Query, HTTPException
from app.schemas.community import CommunitiesResponse, CommunityDetailResponse
from app.services.community_service import community_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}


@router.get("/communities", response_model=CommunitiesResponse, summary="Get migration network community partition")
async def get_communities_endpoint(
    year: int = Query(2020, description="Census observation round year"),
    top_n_edges: int = Query(150, ge=20, le=500, description="Number of edges in network graph for partitioning"),
):
    """
    Execute modularity community detection on the bilateral migration stock graph.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return community_service.get_communities(year=year, top_n_edges=top_n_edges)


@router.get(
    "/communities/{community_id}",
    response_model=CommunityDetailResponse,
    summary="Get member details and internal corridors for a community",
)
async def get_community_detail_endpoint(
    community_id: int = Path(..., description="Community ID (1-indexed)"),
    year: int = Query(2020, description="Census observation round year"),
    top_n_edges: int = Query(150, ge=20, le=500, description="Edge threshold"),
):
    """
    Retrieve member countries, top anchor hubs, and internal bilateral corridors for a specific community cluster.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return community_service.get_community_detail(
        community_id=community_id, year=year, top_n_edges=top_n_edges
    )
