"""
Service layer for Advanced Migration Analytics (HHI Concentration, Correlations, Outliers, and Comparisons).
"""

import math
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd

from app.schemas.advanced_analytics import (
    ConcentrationMetrics,
    OriginConcentrationMetrics,
    ConcentrationResponse,
    ConcentrationEntity,
    CorrelationPair,
    CorrelationsResponse,
    ScatterPoint,
    ScatterPlotResponse,
    OutlierPoint,
    OutliersResponse,
    CountryComparisonSeries,
    CountryComparisonResponse,
    AnalyticsOverviewResponse,
)
from app.services.data_service import data_service
from src.advanced_analytics import (
    compute_destination_concentration,
    compute_origin_concentration,
    compute_socioeconomic_correlations,
    get_bivariate_scatter_data,
    detect_migration_anomalies,
    compute_multicountry_comparison,
)
from src.dashboard_data import load_canonical_country_map


def _safe_float(val: Optional[float], default: Optional[float] = None) -> Optional[float]:
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return default
    try:
        f = float(val)
        return default if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return default


class AdvancedAnalyticsService:
    """Service handling concentration, correlations, outliers, and multi-country comparisons."""

    def get_concentration(self, year: int = 2020) -> ConcentrationResponse:
        """
        Compute destination and origin migration stock concentration metrics (HHI).
        """
        df_country = data_service.get_country_socioeconomic_data()
        df_bilateral = data_service.get_bilateral_corridor_data()

        dest_raw = compute_destination_concentration(df_country, year=year, sovereign_only=True)
        orig_raw = compute_origin_concentration(df_bilateral, year=year, sovereign_only=True)

        top_dest_entities = [
            ConcentrationEntity(
                country_code=str(d.get("country_code", "")),
                display_name=str(d.get("display_name", d.get("country", ""))),
                migrant_stock=float(d.get("migrant_stock", 0.0)),
                share_pct=float(d.get("share_pct", 0.0)),
            )
            for d in dest_raw.get("top_destinations", [])
        ]

        dest_metrics = ConcentrationMetrics(
            year=year,
            total_migrant_stock=_safe_float(dest_raw.get("total_migrant_stock"), 0.0),
            num_countries=int(dest_raw.get("num_countries", 0)),
            top_5_share=_safe_float(dest_raw.get("top_5_share"), 0.0),
            top_10_share=_safe_float(dest_raw.get("top_10_share"), 0.0),
            top_25_share=_safe_float(dest_raw.get("top_25_share"), 0.0),
            hhi=_safe_float(dest_raw.get("hhi"), 0.0),
            hhi_category=str(dest_raw.get("hhi_category", "Unconcentrated (< 1,000)")),
            top_destinations=top_dest_entities,
        )

        orig_metrics = OriginConcentrationMetrics(
            year=year,
            total_emigrant_stock=_safe_float(orig_raw.get("total_emigrant_stock"), 0.0),
            num_origins=int(orig_raw.get("num_origins", 0)),
            top_5_origin_share=_safe_float(orig_raw.get("top_5_origin_share"), 0.0),
            top_10_origin_share=_safe_float(orig_raw.get("top_10_origin_share"), 0.0),
            top_25_origin_share=_safe_float(orig_raw.get("top_25_origin_share"), 0.0),
            origin_hhi=_safe_float(orig_raw.get("origin_hhi"), 0.0),
            top_origins=orig_raw.get("top_origins", []),
        )

        return ConcentrationResponse(
            year=year,
            destination=dest_metrics,
            origin=orig_metrics,
        )

    def get_correlations(self, year: int = 2020) -> CorrelationsResponse:
        """
        Compute Pearson and Spearman correlation statistics across socioeconomic indicators.
        """
        df_country = data_service.get_country_socioeconomic_data()
        df_corr = compute_socioeconomic_correlations(df_country, year=year)

        pairs: List[CorrelationPair] = []
        if not df_corr.empty:
            for _, row in df_corr.iterrows():
                pairs.append(
                    CorrelationPair(
                        pair_name=str(row["pair_name"]),
                        description=str(row["description"]),
                        year=int(row["year"]),
                        sample_size=int(row["sample_size"]),
                        pearson_r=_safe_float(row["pearson_r"]),
                        pearson_p_value=_safe_float(row["pearson_p_value"]),
                        spearman_rho=_safe_float(row["spearman_rho"]),
                        spearman_p_value=_safe_float(row["spearman_p_value"]),
                        relationship_strength=str(row["relationship_strength"]),
                        statistical_significance=str(row["statistical_significance"]),
                    )
                )

        return CorrelationsResponse(year=year, correlations=pairs)

    def get_scatter_data(
        self,
        x_metric: str = "gdp_per_capita",
        y_metric: str = "migrant_stock_pct_population",
        year: int = 2020,
        log_x: bool = False,
        log_y: bool = False,
    ) -> ScatterPlotResponse:
        """
        Extract clean country observations and linear regression statistics for bivariate scatter plots.
        """
        df_country = data_service.get_country_socioeconomic_data()
        df_valid, stats_dict = get_bivariate_scatter_data(
            df_country,
            x_metric_col=x_metric,
            y_metric_col=y_metric,
            year=year,
            log_scale_x=log_x,
            log_scale_y=log_y,
        )

        points: List[ScatterPoint] = []
        if not df_valid.empty:
            for _, row in df_valid.iterrows():
                points.append(
                    ScatterPoint(
                        country_code=str(row["country_code"]),
                        display_name=str(row["display_name"]),
                        x_value=float(row[x_metric]),
                        y_value=float(row[y_metric]),
                        plot_x=float(row["plot_x"]),
                        plot_y=float(row["plot_y"]),
                        migrant_stock=_safe_float(row.get("migrant_stock")),
                        population=_safe_float(row.get("population")),
                        gdp_per_capita=_safe_float(row.get("gdp_per_capita")),
                    )
                )

        clean_stats = {
            k: _safe_float(v) if isinstance(v, (float, np.floating)) else v
            for k, v in stats_dict.items()
        }

        return ScatterPlotResponse(
            year=year,
            x_metric=x_metric,
            y_metric=y_metric,
            points=points,
            stats=clean_stats,
        )

    def get_outliers(
        self,
        year: int = 2020,
        metric: str = "migrant_stock",
        method: str = "IQR",
        threshold: float = 1.5,
    ) -> OutliersResponse:
        """
        Identify statistical outliers using IQR or Z-score method.
        """
        df_country = data_service.get_country_socioeconomic_data()
        df_outliers, summary = detect_migration_anomalies(
            df_country,
            metric_col=metric,
            year=year,
            method=method,
            threshold=threshold,
        )

        points: List[OutlierPoint] = []
        dev_col = "z_score" if method == "Z-Score" else "iqr_deviation"

        if not df_outliers.empty:
            for _, row in df_outliers.iterrows():
                points.append(
                    OutlierPoint(
                        country_code=str(row["country_code"]),
                        display_name=str(row["display_name"]),
                        metric_value=float(row[metric]),
                        deviation=_safe_float(abs(row.get(dev_col, 0.0)), 0.0),
                        outlier_type=str(row.get("outlier_type", "Outlier")),
                        migrant_stock=_safe_float(row.get("migrant_stock")),
                        population=_safe_float(row.get("population")),
                        gdp_per_capita=_safe_float(row.get("gdp_per_capita")),
                    )
                )

        clean_summary = {
            k: _safe_float(v) if isinstance(v, (float, np.floating)) else v
            for k, v in summary.items()
        }

        return OutliersResponse(
            year=year,
            metric=metric,
            method=method,
            threshold=threshold,
            outlier_count=len(points),
            summary=clean_summary,
            outliers=points,
        )

    def get_country_comparison(
        self,
        country_codes: List[str],
        year: int = 2020,
    ) -> CountryComparisonResponse:
        """
        Compare 2 to 5 selected sovereign nations across demographic/economic metrics and historical trajectories.
        """
        if len(country_codes) < 2:
            country_codes = ["USA", "IND"]
        elif len(country_codes) > 5:
            country_codes = country_codes[:5]

        country_codes = [c.upper().strip() for c in country_codes]
        df_country = data_service.get_country_socioeconomic_data()
        name_map = load_canonical_country_map()

        df_abs, df_norm = compute_multicountry_comparison(df_country, country_codes=country_codes, year=year)

        # Replace NaN with None in dictionaries
        abs_list = df_abs.replace({np.nan: None}).to_dict(orient="records") if not df_abs.empty else []
        norm_list = df_norm.replace({np.nan: None}).to_dict(orient="records") if not df_norm.empty else []

        # 1990–2020 Historical trajectories for selected countries
        trajectories: List[CountryComparisonSeries] = []
        for code in country_codes:
            c_name = name_map.get(code, code)
            df_c_hist = df_country[
                (df_country["country_code"] == code) & (~df_country["is_aggregate"])
            ].sort_values("year")

            years_list = [int(y) for y in df_c_hist["year"]]
            stock_list = [_safe_float(s, 0.0) for s in df_c_hist["migrant_stock"]]
            pct_list = [_safe_float(p) for p in df_c_hist.get("migrant_stock_pct_population", pd.Series(dtype=float))]

            trajectories.append(
                CountryComparisonSeries(
                    country_code=code,
                    country_name=c_name,
                    years=years_list,
                    migrant_stock_history=stock_list,
                    pct_population_history=pct_list,
                )
            )

        return CountryComparisonResponse(
            year=year,
            countries=country_codes,
            absolute_comparison=abs_list,
            normalized_comparison=norm_list,
            trajectories=trajectories,
        )

    def get_overview(self, year: int = 2020) -> AnalyticsOverviewResponse:
        """
        Produce executive summary of advanced analytics for the selected census round.
        """
        conc = self.get_concentration(year)
        corr = self.get_correlations(year)

        # Find strongest correlation
        strongest = None
        if corr.correlations:
            valid_corrs = [c for c in corr.correlations if c.spearman_rho is not None]
            if valid_corrs:
                strongest = max(valid_corrs, key=lambda c: abs(c.spearman_rho))

        # Outlier counts across primary metrics
        stock_outliers = self.get_outliers(year=year, metric="migrant_stock", method="IQR", threshold=1.5)
        pct_outliers = self.get_outliers(year=year, metric="migrant_stock_pct_population", method="IQR", threshold=1.5)

        outlier_counts = {
            "migrant_stock": stock_outliers.outlier_count,
            "migrant_stock_pct_population": pct_outliers.outlier_count,
        }

        from app.services.insight_service import insight_service
        insights_res = insight_service.get_insights(year=year)

        return AnalyticsOverviewResponse(
            year=year,
            destination_hhi=conc.destination.hhi,
            hhi_category=conc.destination.hhi_category,
            top_10_destination_share=conc.destination.top_10_share,
            active_destinations=conc.destination.num_countries,
            strongest_correlation=strongest,
            outlier_counts=outlier_counts,
            total_insights=insights_res.total_insights,
            top_insights=insights_res.insights[:4],
        )


advanced_analytics_service = AdvancedAnalyticsService()
