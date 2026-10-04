"""
Longitudinal Trends API Router.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.trends import GlobalTrendResponse, CountryTrendResponse
from app.services.trends_service import trends_service

router = APIRouter()


@router.get("/trends/global", response_model=GlobalTrendResponse, summary="Get global 1990–2020 longitudinal trend")
async def get_global_trend_endpoint():
    """
    Retrieve global aggregated migrant stock trajectory across all 7 quinquennial rounds.
    """
    return trends_service.get_global_trend()


@router.get("/trends/countries", response_model=CountryTrendResponse, summary="Get multi-country comparative trends")
async def get_country_trends_endpoint(
    countries: str = Query("USA,IND,DEU", description="Comma-separated ISO3 country codes (e.g. 'USA,IND,DEU')"),
    metric: str = Query("Migrant Stock", description="Metric to compare over time"),
):
    """
    Retrieve multi-country longitudinal time series for comparison.
    """
    country_list = [c.strip().upper() for c in countries.split(",") if c.strip()]
    if not country_list:
        raise HTTPException(status_code=400, detail="At least one country ISO3 code must be provided.")
    return trends_service.get_country_trends(country_codes=country_list, metric_name=metric)
