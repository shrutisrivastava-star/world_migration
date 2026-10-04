"""
Pydantic schemas for Advanced Migration Analytics, Correlations, Outliers, Comparisons, and Insights.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConcentrationEntity(BaseModel):
    """Destination or Origin country with market share in migration stock."""
    country_code: str = Field(..., description="ISO3 country code")
    display_name: str = Field(..., description="Country display name")
    migrant_stock: float = Field(..., description="Estimated residing migrant stock count")
    share_pct: float = Field(..., description="Percentage share of global migrant stock (%)")


class ConcentrationMetrics(BaseModel):
    """Destination Herfindahl-Hirschman Index and Top N shares."""
    year: int = Field(..., description="Census observation round year")
    total_migrant_stock: float = Field(..., description="Global residing migrant stock sum")
    num_countries: int = Field(..., description="Number of active sovereign destinations")
    top_5_share: float = Field(..., description="Cumulative percentage share of Top 5 destinations (%)")
    top_10_share: float = Field(..., description="Cumulative percentage share of Top 10 destinations (%)")
    top_25_share: float = Field(..., description="Cumulative percentage share of Top 25 destinations (%)")
    hhi: float = Field(..., description="Herfindahl-Hirschman Index (0-10,000)")
    hhi_category: str = Field(..., description="HHI classification category")
    top_destinations: List[ConcentrationEntity] = Field(default_factory=list, description="Top 10 destinations")


class OriginConcentrationMetrics(BaseModel):
    """Origin Herfindahl-Hirschman Index and Top N shares."""
    year: int = Field(..., description="Census observation round year")
    total_emigrant_stock: float = Field(..., description="Global origin diaspora stock sum")
    num_origins: int = Field(..., description="Number of active origin nations")
    top_5_origin_share: float = Field(..., description="Cumulative percentage share of Top 5 origins (%)")
    top_10_origin_share: float = Field(..., description="Cumulative percentage share of Top 10 origins (%)")
    top_25_origin_share: float = Field(..., description="Cumulative percentage share of Top 25 origins (%)")
    origin_hhi: float = Field(..., description="Origin Herfindahl-Hirschman Index (0-10,000)")
    top_origins: List[Dict[str, Any]] = Field(default_factory=list, description="Top 10 origins")


class ConcentrationResponse(BaseModel):
    """Combined destination and origin concentration payload."""
    year: int = Field(..., description="Census round year")
    destination: ConcentrationMetrics = Field(..., description="Destination concentration metrics")
    origin: OriginConcentrationMetrics = Field(..., description="Origin concentration metrics")


class CorrelationPair(BaseModel):
    """Statistical association metrics between two indicators."""
    pair_name: str = Field(..., description="Indicator pair name")
    description: str = Field(..., description="Descriptive context of relationship")
    year: int = Field(..., description="Census round year")
    sample_size: int = Field(..., description="Number of valid country observations")
    pearson_r: Optional[float] = Field(None, description="Pearson correlation coefficient")
    pearson_p_value: Optional[float] = Field(None, description="Two-tailed Pearson p-value")
    spearman_rho: Optional[float] = Field(None, description="Spearman rank correlation coefficient")
    spearman_p_value: Optional[float] = Field(None, description="Two-tailed Spearman p-value")
    relationship_strength: str = Field(..., description="Categorical correlation strength")
    statistical_significance: str = Field(..., description="Significance threshold label")


class CorrelationsResponse(BaseModel):
    """List of all evaluated bivariate socioeconomic associations."""
    year: int = Field(..., description="Census round year")
    correlations: List[CorrelationPair] = Field(default_factory=list, description="Computed correlation pairs")


class ScatterPoint(BaseModel):
    """Single country data point for bivariate interactive scatter plots."""
    country_code: str = Field(..., description="ISO3 country code")
    display_name: str = Field(..., description="Country display name")
    x_value: float = Field(..., description="Raw X metric value")
    y_value: float = Field(..., description="Raw Y metric value")
    plot_x: float = Field(..., description="Plotly plotted X coordinate (optionally log10)")
    plot_y: float = Field(..., description="Plotly plotted Y coordinate (optionally log10)")
    migrant_stock: Optional[float] = Field(None, description="Residing migrant stock")
    population: Optional[float] = Field(None, description="Host total population")
    gdp_per_capita: Optional[float] = Field(None, description="GDP per capita")


class ScatterPlotResponse(BaseModel):
    """Bivariate scatter plot payload with regression statistics."""
    year: int = Field(..., description="Census round year")
    x_metric: str = Field(..., description="Column name for X axis")
    y_metric: str = Field(..., description="Column name for Y axis")
    points: List[ScatterPoint] = Field(default_factory=list, description="Plotted country data points")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Regression fit and correlation stats")


class OutlierPoint(BaseModel):
    """Country observation identified as a statistical outlier."""
    country_code: str = Field(..., description="ISO3 country code")
    display_name: str = Field(..., description="Country display name")
    metric_value: float = Field(..., description="Observed metric value")
    deviation: float = Field(..., description="IQR multiple deviation or absolute Z-score")
    outlier_type: str = Field(..., description="High Outlier or Low Outlier")
    migrant_stock: Optional[float] = Field(None, description="Residing migrant stock")
    population: Optional[float] = Field(None, description="Total population")
    gdp_per_capita: Optional[float] = Field(None, description="GDP per capita")


class OutliersResponse(BaseModel):
    """Outlier detection results under chosen method and threshold."""
    year: int = Field(..., description="Census round year")
    metric: str = Field(..., description="Target indicator evaluated")
    method: str = Field(..., description="Detection method ('IQR' or 'Z-Score')")
    threshold: float = Field(..., description="Configured outlier threshold multiplier")
    outlier_count: int = Field(..., description="Total number of detected outliers")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Distribution parameters (Q1, Q3, Mean, Std, bounds)")
    outliers: List[OutlierPoint] = Field(default_factory=list, description="Ranked list of outlier countries")


class CountryComparisonSeries(BaseModel):
    """Longitudinal trajectory of a single country for multi-country charts."""
    country_code: str = Field(..., description="ISO3 country code")
    country_name: str = Field(..., description="Country display name")
    years: List[int] = Field(default_factory=list, description="Census years")
    migrant_stock_history: List[float] = Field(default_factory=list, description="Residing migrant stock across years")
    pct_population_history: List[Optional[float]] = Field(default_factory=list, description="Migrant stock % of population across years")


class CountryComparisonResponse(BaseModel):
    """Comparative profiling matrix across 2 to 5 sovereign nations."""
    year: int = Field(..., description="Selected census round year")
    countries: List[str] = Field(default_factory=list, description="Selected country ISO3 codes")
    absolute_comparison: List[Dict[str, Any]] = Field(default_factory=list, description="Raw absolute metrics table")
    normalized_comparison: List[Dict[str, Any]] = Field(default_factory=list, description="Min-max [0, 100] normalized scores table")
    trajectories: List[CountryComparisonSeries] = Field(default_factory=list, description="Historical 1990–2020 trajectories")


class MigrationInsight(BaseModel):
    """Deterministic, rule-based scientific migration insight card."""
    category: str = Field(..., description="Insight category (Global Trend, Concentration, Fastest Growth, Largest Changes, Major Corridors, Socioeconomic Associations, Network Structure)")
    title: str = Field(..., description="Insight headline title")
    message: str = Field(..., description="Detailed explanatory paragraph adhering to scientific terminology")
    year: int = Field(..., description="Census observation round year")
    country_code: Optional[str] = Field(None, description="Associated country ISO3 code if applicable")
    metric: Optional[str] = Field(None, description="Primary supporting indicator column")
    value: Optional[float] = Field(None, description="Primary indicator value")
    badge: Optional[str] = Field(None, description="Display badge string")


class InsightsResponse(BaseModel):
    """Collection of categorized deterministic migration insights."""
    year: int = Field(..., description="Census round year")
    total_insights: int = Field(..., description="Total count of generated insights")
    categories: List[str] = Field(default_factory=list, description="Available insight categories")
    insights: List[MigrationInsight] = Field(default_factory=list, description="List of generated insight cards")


class AnalyticsOverviewResponse(BaseModel):
    """Executive summary of advanced analytics for the dashboard."""
    year: int = Field(..., description="Census round year")
    destination_hhi: float = Field(..., description="Destination HHI score")
    hhi_category: str = Field(..., description="Destination HHI classification")
    top_10_destination_share: float = Field(..., description="Percentage of global stock in top 10 destinations (%)")
    active_destinations: int = Field(..., description="Count of sovereign destination nations")
    strongest_correlation: Optional[CorrelationPair] = Field(None, description="Top statistical association pair")
    outlier_counts: Dict[str, int] = Field(default_factory=dict, description="Outlier counts across primary metrics")
    total_insights: int = Field(..., description="Total generated insights count")
    top_insights: List[MigrationInsight] = Field(default_factory=list, description="Top 4 highlight insight cards")
