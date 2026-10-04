"""
Overview Service module.
Calculates executive KPI metrics by delegating to the scientific Python analytics layer.
"""

from fastapi import HTTPException, status
from app.config import OBSERVATION_YEARS
from app.services.data_service import data_service
from app.schemas.overview import OverviewKPIsResponse
from src.dashboard_data import get_overview_kpis


class OverviewService:
    """Service for computing executive migration overview indicators."""

    def get_overview_kpis_for_year(self, year: int) -> OverviewKPIsResponse:
        """
        Calculate overview KPIs for a specified census round year.
        
        Args:
            year: Census round year (e.g. 2020).
            
        Returns:
            OverviewKPIsResponse: Pydantic validated KPI summary.
            
        Raises:
            HTTPException: 400 Bad Request if year is invalid.
        """
        if year not in OBSERVATION_YEARS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid census observation year: {year}. Valid UN DESA years are: {OBSERVATION_YEARS}",
            )

        df_merged = data_service.get_country_socioeconomic_data()
        df_bilateral = data_service.get_bilateral_corridor_data()

        kpis_dict = get_overview_kpis(df_merged, df_bilateral, year=year)

        return OverviewKPIsResponse(**kpis_dict)


overview_service = OverviewService()
