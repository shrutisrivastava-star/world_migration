"""
Service layer for deterministic, rule-based Migration Storytelling Insights.
"""

from typing import Optional, List
from app.schemas.advanced_analytics import MigrationInsight, InsightsResponse
from app.services.data_service import data_service
from src.insight_engine import generate_all_insights
from src.network_analysis import build_migration_network, calculate_network_metrics


class InsightService:
    """Service generating deterministic scientific migration insights."""

    def get_insights(self, year: int = 2020, category: Optional[str] = None) -> InsightsResponse:
        """
        Generate categorized deterministic insight cards for a given census round.
        
        Args:
            year: Census observation round year (1990–2020)
            category: Optional category filter ('All' or specific category name)
            
        Returns:
            InsightsResponse: Total count, list of available categories, and insight objects.
        """
        df_country = data_service.get_country_socioeconomic_data()
        df_bilateral = data_service.get_bilateral_corridor_data()

        # Build network metrics for network-level insights
        G = build_migration_network(
            df_bilateral,
            year=year,
            top_n_edges=100,
            sovereign_only=True,
            directed=True,
        )
        df_net_metrics = calculate_network_metrics(G) if len(G) > 0 else None

        raw_insights = generate_all_insights(
            df_country,
            df_bilateral,
            year=year,
            df_net_metrics=df_net_metrics,
        )

        all_categories = sorted(list(set(item["category"] for item in raw_insights)))

        insights: List[MigrationInsight] = []
        for item in raw_insights:
            if category and category != "All" and item["category"].lower() != category.lower():
                continue
            insights.append(
                MigrationInsight(
                    category=str(item["category"]),
                    title=str(item["title"]),
                    message=str(item["message"]),
                    year=int(item["year"]),
                    country_code=str(item["country_code"]) if item.get("country_code") else None,
                    metric=str(item["metric"]) if item.get("metric") else None,
                    value=float(item["value"]) if item.get("value") is not None else None,
                    badge=str(item["badge"]) if item.get("badge") else None,
                )
            )

        return InsightsResponse(
            year=year,
            total_insights=len(insights),
            categories=["All"] + all_categories,
            insights=insights,
        )


insight_service = InsightService()
