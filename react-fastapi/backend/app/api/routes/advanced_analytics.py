"""
Advanced Migration Analytics API Router.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.schemas.advanced_analytics import (
    AnalyticsOverviewResponse,
    ConcentrationResponse,
    CorrelationsResponse,
    ScatterPlotResponse,
    OutliersResponse,
    CountryComparisonResponse,
    InsightsResponse,
)
from app.services.advanced_analytics_service import advanced_analytics_service
from app.services.insight_service import insight_service

router = APIRouter()
VALID_YEARS = {1990, 1995, 2000, 2005, 2010, 2015, 2020}
VALID_METRICS = {
    "migrant_stock",
    "migrant_stock_pct_population",
    "stock_growth_pct_5yr",
    "gdp_per_capita",
    "population",
    "unemployment",
    "gdp",
}


@router.get(
    "/analytics/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get executive advanced analytics overview for a census year",
)
async def get_analytics_overview_endpoint(
    year: int = Query(2020, description="Census observation round year"),
):
    """
    Retrieve executive advanced analytics overview including HHI concentration, top correlation, outlier counts, and key insights.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return advanced_analytics_service.get_overview(year=year)


@router.get(
    "/analytics/concentration",
    response_model=ConcentrationResponse,
    summary="Get destination and origin Herfindahl-Hirschman Index concentration metrics",
)
async def get_concentration_endpoint(
    year: int = Query(2020, description="Census observation round year"),
):
    """
    Calculate destination and origin migrant stock concentration metrics (HHI and Top 5/10/25 shares).
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return advanced_analytics_service.get_concentration(year=year)


@router.get(
    "/analytics/correlations",
    response_model=CorrelationsResponse,
    summary="Get Pearson and Spearman socioeconomic correlation statistics",
)
async def get_correlations_endpoint(
    year: int = Query(2020, description="Census observation round year"),
):
    """
    Compute Pearson and Spearman statistical association metrics across standard socioeconomic indicators.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return advanced_analytics_service.get_correlations(year=year)


@router.get(
    "/analytics/scatter",
    response_model=ScatterPlotResponse,
    summary="Get bivariate scatter plot points with linear regression statistics",
)
async def get_scatter_endpoint(
    x_metric: str = Query("gdp_per_capita", description="Column for X axis"),
    y_metric: str = Query("migrant_stock_pct_population", description="Column for Y axis"),
    year: int = Query(2020, description="Census observation round year"),
    log_x: bool = Query(True, description="Whether to log10-transform X axis values"),
    log_y: bool = Query(False, description="Whether to log10-transform Y axis values"),
):
    """
    Extract clean country data points for interactive bivariate scatter charts with linear regression parameters.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    if x_metric not in VALID_METRICS or y_metric not in VALID_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid indicator columns. Valid options: {sorted(list(VALID_METRICS))}",
        )
    return advanced_analytics_service.get_scatter_data(
        x_metric=x_metric,
        y_metric=y_metric,
        year=year,
        log_x=log_x,
        log_y=log_y,
    )


@router.get(
    "/analytics/outliers",
    response_model=OutliersResponse,
    summary="Detect statistical outlier countries using IQR or Z-score method",
)
async def get_outliers_endpoint(
    year: int = Query(2020, description="Census observation round year"),
    metric: str = Query("migrant_stock", description="Target indicator column"),
    method: str = Query("IQR", description="Detection algorithm: 'IQR' or 'Z-Score'"),
    threshold: float = Query(1.5, ge=0.5, le=5.0, description="Outlier cutoff threshold multiplier"),
):
    """
    Identify statistical outliers in migrant stock or socioeconomic indicators using transparent IQR or Z-Score formulas.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    if metric not in VALID_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric '{metric}'. Valid options: {sorted(list(VALID_METRICS))}",
        )
    clean_method = "Z-Score" if method.lower() == "z-score" else "IQR"
    return advanced_analytics_service.get_outliers(
        year=year,
        metric=metric,
        method=clean_method,
        threshold=threshold,
    )


@router.get(
    "/analytics/compare",
    response_model=CountryComparisonResponse,
    summary="Compare 2 to 5 sovereign countries across demographics and historical trajectories",
)
async def get_country_comparison_endpoint(
    year: int = Query(2020, description="Census observation round year"),
    countries: str = Query("USA,IND,DEU", description="Comma-separated country ISO3 codes (2-5 countries)"),
):
    """
    Generate absolute and min-max normalized comparison matrices and longitudinal trajectories for 2–5 countries.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    code_list = [c.strip().upper() for c in countries.split(",") if c.strip()]
    if len(code_list) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 sovereign country ISO3 codes are required for comparative profiling.",
        )
    if len(code_list) > 5:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 5 countries can be compared simultaneously.",
        )
    return advanced_analytics_service.get_country_comparison(
        country_codes=code_list,
        year=year,
    )


@router.get(
    "/analytics/insights",
    response_model=InsightsResponse,
    summary="Get categorized deterministic migration storytelling insights",
)
async def get_insights_endpoint(
    year: int = Query(2020, description="Census observation round year"),
    category: Optional[str] = Query("All", description="Insight category filter"),
):
    """
    Generate deterministic, rule-based scientific migration insights derived directly from data.
    """
    if year not in VALID_YEARS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid census year {year}. Available quinquennial rounds: {sorted(list(VALID_YEARS))}",
        )
    return insight_service.get_insights(year=year, category=category)
