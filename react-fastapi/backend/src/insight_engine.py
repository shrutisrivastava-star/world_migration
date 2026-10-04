"""
Deterministic Rule-Based Migration Insight Engine for the Global Migration Observatory.
Transforms verified dataframe calculations into structured, human-readable analytical summaries
while adhering strictly to scientific terminology (Migrant Stock != Migration Flow) and avoiding
unsupported causal claims.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.advanced_analytics import (
    compute_destination_concentration,
    compute_origin_concentration,
    compute_socioeconomic_correlations,
    get_top_growth_and_declining_countries,
)


def generate_global_insights(
    df_country: pd.DataFrame,
    df_bilat: pd.DataFrame,
    year: int
) -> List[Dict[str, Any]]:
    """
    Generate deterministic global-level insights for a given UN DESA observation year.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        df_bilat: Bilateral migration DataFrame.
        year: Observation year.
        
    Returns:
        List[Dict[str, Any]]: Structured global insight objects.
    """
    insights = []
    
    # 1. Total Global Stock & Scale
    df_yr = df_country[(df_country["year"] == year) & (~df_country["is_aggregate"])]
    if not df_yr.empty:
        tot_stock = float(df_yr["migrant_stock"].sum())
        top_dest = df_yr.sort_values("migrant_stock", ascending=False).iloc[0]
        top_dest_name = top_dest["display_name"]
        top_dest_stock = float(top_dest["migrant_stock"])
        top_dest_share = (top_dest_stock / tot_stock) * 100.0
        
        insights.append({
            "category": "Global Trend",
            "title": f"Global Residing Migrant Stock in {year}",
            "message": (
                f"In the {year} UN DESA census round, approximately {tot_stock:,.0f} international migrants "
                f"were estimated to reside outside their country of birth across {len(df_yr)} sovereign nations and territories. "
                f"{top_dest_name} hosted the largest residing migrant population ({top_dest_stock:,.0f} individuals), "
                f"accounting for {top_dest_share:.1f}% of the global total."
            ),
            "year": year,
            "country_code": str(top_dest["country_code"]),
            "metric": "total_migrant_stock",
            "value": tot_stock,
            "badge": f"{tot_stock / 1e6:.1f}M Global Stock"
        })
        
    # 2. 5-Year Intercensal Growth (if year > 1990)
    if year > 1990:
        prev_yr = year - 5
        df_prev = df_country[(df_country["year"] == prev_yr) & (~df_country["is_aggregate"])]
        if not df_prev.empty and not df_yr.empty:
            prev_tot = float(df_prev["migrant_stock"].sum())
            abs_diff = tot_stock - prev_tot
            pct_diff = (abs_diff / prev_tot) * 100.0 if prev_tot > 0 else 0.0
            
            trend_word = "increased" if abs_diff >= 0 else "decreased"
            insights.append({
                "category": "Global Trend",
                "title": f"5-Year Net Global Stock Evolution ({prev_yr} → {year})",
                "message": (
                    f"Between {prev_yr} and {year}, global residing migrant stock {trend_word} by {abs(abs_diff):,.0f} "
                    f"({pct_diff:+.1f}% net 5-year change). This reflects the cumulative balance of international movements, "
                    f"vital statistics among residing migrants, naturalizations, and census methodology updates."
                ),
                "year": year,
                "country_code": None,
                "metric": "5yr_stock_change",
                "value": abs_diff,
                "badge": f"{pct_diff:+.1f}% (5-Yr Change)"
            })
            
    return insights


def generate_concentration_insights(
    df_country: pd.DataFrame,
    df_bilat: pd.DataFrame,
    year: int
) -> List[Dict[str, Any]]:
    """
    Generate deterministic insights regarding geographic destination and origin concentration.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        df_bilat: Bilateral migration DataFrame.
        year: Observation year.
        
    Returns:
        List[Dict[str, Any]]: Structured concentration insight objects.
    """
    insights = []
    
    dest_conc = compute_destination_concentration(df_country, year=year)
    orig_conc = compute_origin_concentration(df_bilat, year=year)
    
    if dest_conc["total_migrant_stock"] > 0:
        top_5 = dest_conc["top_5_share"]
        top_10 = dest_conc["top_10_share"]
        hhi = dest_conc["hhi"]
        
        insights.append({
            "category": "Concentration",
            "title": f"Destination Geographic Concentration ({year})",
            "message": (
                f"In {year}, global migrant stock exhibited a destination Herfindahl-Hirschman Index (HHI) of {hhi:,.0f}. "
                f"The top 5 destinations accounted for {top_5:.1f}% of all international migrants globally, while the top 10 "
                f"destinations hosted {top_10:.1f}%. The destination distribution is categorized as {dest_conc['hhi_category']}."
            ),
            "year": year,
            "country_code": None,
            "metric": "destination_hhi",
            "value": hhi,
            "badge": f"HHI: {hhi:,.0f} ({top_10:.0f}% Top 10)"
        })
        
    if orig_conc["total_emigrant_stock"] > 0:
        top_5_orig = orig_conc["top_5_origin_share"]
        top_10_orig = orig_conc["top_10_origin_share"]
        top_orig_name = orig_conc["top_origins"][0]["origin_display_name"] if orig_conc["top_origins"] else "N/A"
        top_orig_share = orig_conc["top_origins"][0]["share_pct"] if orig_conc["top_origins"] else 0.0
        
        insights.append({
            "category": "Concentration",
            "title": f"Origin Diaspora Dispersion ({year})",
            "message": (
                f"On the origin side, {top_orig_name} represented the largest origin diaspora in {year} ({top_orig_share:.1f}% "
                f"of global emigrant stock). The top 10 origin nations combined accounted for {top_10_orig:.1f}% of total "
                f"international migrant origins globally."
            ),
            "year": year,
            "country_code": orig_conc["top_origins"][0]["origin_code"] if orig_conc["top_origins"] else None,
            "metric": "origin_top_10_share",
            "value": top_10_orig,
            "badge": f"{top_10_orig:.1f}% Top 10 Origin Share"
        })
        
    return insights


def generate_change_insights(
    df_country: pd.DataFrame,
    year: int
) -> List[Dict[str, Any]]:
    """
    Generate deterministic insights for fastest growing destinations and largest absolute stock adjustments.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        year: Observation year (1995–2020).
        
    Returns:
        List[Dict[str, Any]]: Structured change insight objects.
    """
    if year <= 1990:
        return []
        
    insights = []
    top_changes = get_top_growth_and_declining_countries(df_country, year=year, top_n=5)
    
    # 1. Largest absolute stock increase
    if not top_changes["largest_increase_abs"].empty:
        top_inc = top_changes["largest_increase_abs"].iloc[0]
        c_name = top_inc["display_name"]
        inc_val = float(top_inc["stock_change_5yr"])
        growth_pct = float(top_inc["stock_growth_pct_5yr"]) if pd.notna(top_inc["stock_growth_pct_5yr"]) else 0.0
        
        insights.append({
            "category": "Largest Changes",
            "title": f"Leading Absolute Stock Expansion ({year - 5} → {year})",
            "message": (
                f"{c_name} recorded the largest absolute increase in residing foreign-born population between {year - 5} and {year}, "
                f"expanding by {inc_val:,.0f} individuals ({growth_pct:+.1f}% 5-year growth). "
                f"Total residing migrant stock reached {top_inc['migrant_stock']:,.0f} in {year}."
            ),
            "year": year,
            "country_code": str(top_inc["country_code"]),
            "metric": "stock_change_5yr",
            "value": inc_val,
            "badge": f"+{inc_val / 1e3:,.0f}k Net Change"
        })
        
    # 2. Fastest percentage growth
    if not top_changes["fastest_growth_pct"].empty:
        top_pct = top_changes["fastest_growth_pct"].iloc[0]
        p_name = top_pct["display_name"]
        p_pct = float(top_pct["stock_growth_pct_5yr"])
        p_stock = float(top_pct["migrant_stock"])
        
        insights.append({
            "category": "Fastest Growth",
            "title": f"Fastest-Growing Residing Stock Rate ({year - 5} → {year})",
            "message": (
                f"Among destinations hosting at least 10,000 migrants, {p_name} exhibited the fastest 5-year percentage "
                f"growth at {p_pct:+.1f}% between {year - 5} and {year}, bringing its residing stock to {p_stock:,.0f}."
            ),
            "year": year,
            "country_code": str(top_pct["country_code"]),
            "metric": "stock_growth_pct_5yr",
            "value": p_pct,
            "badge": f"{p_pct:+.1f}% 5-Yr Growth"
        })
        
    return insights


def generate_corridor_insights(
    df_bilat: pd.DataFrame,
    year: int
) -> List[Dict[str, Any]]:
    """
    Generate deterministic insights for major bilateral migrant-stock corridors.
    
    Args:
        df_bilat: Bilateral migration DataFrame.
        year: Observation year.
        
    Returns:
        List[Dict[str, Any]]: Structured corridor insight objects.
    """
    insights = []
    
    df_yr = df_bilat[
        (df_bilat["year"] == year) &
        (~df_bilat["is_aggregate_route"]) &
        (df_bilat["origin_code"].notna()) &
        (df_bilat["destination_code"].notna()) &
        (df_bilat["origin_code"] != df_bilat["destination_code"]) &
        (df_bilat["migrant_stock"] > 0)
    ].sort_values("migrant_stock", ascending=False)
    
    if not df_yr.empty:
        top_c = df_yr.iloc[0]
        tot_stock = float(df_yr["migrant_stock"].sum())
        top_stock = float(top_c["migrant_stock"])
        c_share = (top_stock / tot_stock) * 100.0 if tot_stock > 0 else 0.0
        
        orig_name = top_c["origin_display_name"]
        dest_name = top_c["dest_display_name"]
        
        insights.append({
            "category": "Major Corridors",
            "title": f"Primary Global Bilateral Corridor ({year})",
            "message": (
                f"The {orig_name} → {dest_name} corridor remained the single largest bilateral migrant-stock pathway in {year}, "
                f"with an estimated {top_stock:,.0f} residing individuals. This corridor represents {c_share:.2f}% of all "
                f"bilateral migrant-stock pairings globally."
            ),
            "year": year,
            "country_code": str(top_c["destination_code"]),
            "metric": "top_corridor_stock",
            "value": top_stock,
            "badge": f"{top_stock / 1e6:.2f}M ({orig_name} → {dest_name})"
        })
        
    return insights


def generate_socioeconomic_insights(
    df_country: pd.DataFrame,
    year: int
) -> List[Dict[str, Any]]:
    """
    Generate deterministic statistical insights regarding socioeconomic associations.
    
    Strict Rule: Clarifies that associations do NOT establish causal mechanisms.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        year: Observation year.
        
    Returns:
        List[Dict[str, Any]]: Structured socioeconomic insight objects.
    """
    insights = []
    
    corr_df = compute_socioeconomic_correlations(df_country, year=year)
    if not corr_df.empty:
        # Find strongest statistical association
        valid_corr = corr_df.dropna(subset=["spearman_rho", "spearman_p_value"])
        if not valid_corr.empty:
            top_assoc = valid_corr.sort_values(by="spearman_rho", key=abs, ascending=False).iloc[0]
            
            p_name = top_assoc["pair_name"]
            r_val = top_assoc["spearman_rho"]
            p_val = top_assoc["spearman_p_value"]
            strength = top_assoc["relationship_strength"]
            n_sample = top_assoc["sample_size"]
            
            direction = "positive" if r_val > 0 else "negative"
            insights.append({
                "category": "Socioeconomic Associations",
                "title": f"Empirical Association: {p_name} ({year})",
                "message": (
                    f"Cross-sectional correlation analysis across {n_sample} sovereign nations in {year} revealed a "
                    f"{strength.lower()} rank correlation (Spearman ρ = {r_val:+.3f}, p = {p_val:.4g}). "
                    f"Higher values of the economic/demographic metric were observed alongside {direction} ranks in migrant stock. "
                    f"Note: This empirical association describes macroeconomic context and does not constitute a causal mechanism."
                ),
                "year": year,
                "country_code": None,
                "metric": "spearman_rho",
                "value": r_val,
                "badge": f"Spearman ρ: {r_val:+.2f} ({top_assoc['statistical_significance']})"
            })
            
    return insights


def generate_network_insights(
    df_net_metrics: pd.DataFrame,
    year: int
) -> List[Dict[str, Any]]:
    """
    Generate deterministic insights regarding migration network topology and node centrality.
    
    Args:
        df_net_metrics: Network centrality metrics DataFrame for the selected year.
        year: Observation year.
        
    Returns:
        List[Dict[str, Any]]: Structured network insight objects.
    """
    insights = []
    
    if df_net_metrics is None or df_net_metrics.empty:
        return insights
        
    # Top PageRank hub
    if "pagerank" in df_net_metrics.columns:
        top_pr = df_net_metrics.sort_values("pagerank", ascending=False).iloc[0]
        pr_name = getattr(top_pr, "country_name", str(top_pr["country_code"]))
        pr_val = float(top_pr["pagerank"])
        
        insights.append({
            "category": "Network Structure",
            "title": f"Central Network Inflow Hub ({year})",
            "message": (
                f"In the {year} directed bilateral migrant-stock network, {pr_name} ranked #1 in PageRank centrality ({pr_val:.4f}), "
                f"indicating prominent global prestige as a destination receiving stock from internationally well-connected origin nodes."
            ),
            "year": year,
            "country_code": str(top_pr["country_code"]),
            "metric": "pagerank",
            "value": pr_val,
            "badge": f"Top PageRank ({pr_name})"
        })
        
    # Top Betweenness Bridge
    if "betweenness_centrality" in df_net_metrics.columns:
        top_bet = df_net_metrics.sort_values("betweenness_centrality", ascending=False).iloc[0]
        bet_name = getattr(top_bet, "country_name", str(top_bet["country_code"]))
        bet_val = float(top_bet["betweenness_centrality"])
        
        insights.append({
            "category": "Network Structure",
            "title": f"Network Brokerage & Bridging Node ({year})",
            "message": (
                f"{bet_name} recorded the highest betweenness centrality ({bet_val:.4f}) in {year}, "
                f"indicating an essential structural bridging position on the shortest bilateral paths connecting diverse world regions."
            ),
            "year": year,
            "country_code": str(top_bet["country_code"]),
            "metric": "betweenness_centrality",
            "value": bet_val,
            "badge": f"Top Betweenness ({bet_name})"
        })
        
    return insights


def generate_all_insights(
    df_country: pd.DataFrame,
    df_bilat: pd.DataFrame,
    year: int,
    df_net_metrics: Optional[pd.DataFrame] = None
) -> List[Dict[str, Any]]:
    """
    Generate master list of categorized, deterministic insight objects for the selected census year.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        df_bilat: Bilateral migration DataFrame.
        year: Observation year.
        df_net_metrics: Optional network centrality DataFrame.
        
    Returns:
        List[Dict[str, Any]]: Consolidated insights across all analytical categories.
    """
    all_insights = []
    
    all_insights.extend(generate_global_insights(df_country, df_bilat, year))
    all_insights.extend(generate_concentration_insights(df_country, df_bilat, year))
    all_insights.extend(generate_change_insights(df_country, year))
    all_insights.extend(generate_corridor_insights(df_bilat, year))
    all_insights.extend(generate_socioeconomic_insights(df_country, year))
    if df_net_metrics is not None and not df_net_metrics.empty:
        all_insights.extend(generate_network_insights(df_net_metrics, year))
        
    return all_insights
