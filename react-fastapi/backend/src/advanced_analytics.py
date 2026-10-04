"""
Advanced Migration Analytics Core for the Global Migration Observatory.
Provides concentration metrics (HHI, Top N shares), socioeconomic bivariate correlations (Pearson & Spearman),
transparent outlier & anomaly detection (IQR, Z-score), growth classifications, multi-country comparisons,
and corridor intelligence adhering strictly to the UN DESA migrant-stock definition.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config


# =============================================================================
# 1. CONCENTRATION ANALYTICS (HHI & TOP SHARES)
# =============================================================================

def compute_destination_concentration(
    df_country: pd.DataFrame,
    year: int,
    sovereign_only: bool = True
) -> Dict[str, Any]:
    """
    Calculate global migrant-stock destination concentration metrics for a given observation year.
    
    Metrics:
    - Top 5, 10, 25 destination shares (%)
    - Herfindahl-Hirschman Index (HHI): sum of squared market shares, range [0, 10000]
    
    Args:
        df_country: Cleaned country socioeconomic DataFrame.
        year: Target UN DESA observation census round year.
        sovereign_only: If True, exclude aggregate regional entities.
        
    Returns:
        Dict[str, Any]: Concentration metrics and top destination summary.
    """
    if df_country.empty or "year" not in df_country.columns or "migrant_stock" not in df_country.columns:
        return {
            "year": year,
            "total_migrant_stock": 0.0,
            "num_countries": 0,
            "top_5_share": 0.0,
            "top_10_share": 0.0,
            "top_25_share": 0.0,
            "hhi": 0.0,
            "hhi_category": "Unconcentrated (< 1,000)",
            "top_destinations": []
        }

    df_yr = df_country[df_country["year"] == year].copy()
    if sovereign_only and "is_aggregate" in df_yr.columns:
        df_yr = df_yr[~df_yr["is_aggregate"]]
        
    if df_yr.empty:
        return {
            "year": year,
            "total_migrant_stock": 0.0,
            "num_countries": 0,
            "top_5_share": 0.0,
            "top_10_share": 0.0,
            "top_25_share": 0.0,
            "hhi": 0.0,
            "hhi_category": "Unconcentrated (< 1,000)",
            "top_destinations": []
        }

    df_yr = df_yr[df_yr["migrant_stock"] > 0].sort_values("migrant_stock", ascending=False)
    
    if df_yr.empty:
        return {
            "year": year,
            "total_migrant_stock": 0.0,
            "num_countries": 0,
            "top_5_share": 0.0,
            "top_10_share": 0.0,
            "top_25_share": 0.0,
            "hhi": 0.0,
            "hhi_category": "Unconcentrated (< 1,000)",
            "top_destinations": []
        }
        
    total_stock = float(df_yr["migrant_stock"].sum())
    shares = (df_yr["migrant_stock"] / total_stock) * 100.0
    
    top_5_share = float(shares.iloc[:5].sum()) if len(shares) >= 5 else float(shares.sum())
    top_10_share = float(shares.iloc[:10].sum()) if len(shares) >= 10 else float(shares.sum())
    top_25_share = float(shares.iloc[:25].sum()) if len(shares) >= 25 else float(shares.sum())
    
    # HHI = sum(s_i^2)
    hhi = float((shares ** 2).sum())
    
    if hhi < 1000:
        hhi_cat = "Unconcentrated (< 1,000)"
    elif hhi < 1800:
        hhi_cat = "Moderately Concentrated (1,000–1,800)"
    else:
        hhi_cat = "Highly Concentrated (> 1,800)"
        
    cols_present = [c for c in ["display_name", "country_code", "migrant_stock"] if c in df_yr.columns]
    top_destinations = df_yr[cols_present].head(10).to_dict(orient="records")
    for d in top_destinations:
        d["share_pct"] = (d["migrant_stock"] / total_stock) * 100.0
        
    return {
        "year": year,
        "total_migrant_stock": total_stock,
        "num_countries": len(df_yr),
        "top_5_share": top_5_share,
        "top_10_share": top_10_share,
        "top_25_share": top_25_share,
        "hhi": hhi,
        "hhi_category": hhi_cat,
        "top_destinations": top_destinations
    }


def compute_origin_concentration(
    df_bilat: pd.DataFrame,
    year: int,
    sovereign_only: bool = True
) -> Dict[str, Any]:
    """
    Calculate global emigrant stock origin concentration metrics for a given observation year.
    
    Args:
        df_bilat: Cleaned bilateral migration DataFrame.
        year: Target observation census year.
        sovereign_only: If True, exclude aggregate routes.
        
    Returns:
        Dict[str, Any]: Origin concentration metrics.
    """
    if df_bilat.empty or "year" not in df_bilat.columns or "migrant_stock" not in df_bilat.columns:
        return {
            "year": year,
            "total_emigrant_stock": 0.0,
            "num_origins": 0,
            "top_5_origin_share": 0.0,
            "top_10_origin_share": 0.0,
            "top_25_origin_share": 0.0,
            "origin_hhi": 0.0,
            "top_origins": []
        }

    df_yr = df_bilat[df_bilat["year"] == year].copy()
    if sovereign_only and "is_aggregate_route" in df_yr.columns:
        df_yr = df_yr[~df_yr["is_aggregate_route"]]
        
    if "origin_code" not in df_yr.columns or "destination_code" not in df_yr.columns:
        return {
            "year": year,
            "total_emigrant_stock": 0.0,
            "num_origins": 0,
            "top_5_origin_share": 0.0,
            "top_10_origin_share": 0.0,
            "top_25_origin_share": 0.0,
            "origin_hhi": 0.0,
            "top_origins": []
        }

    df_yr = df_yr[
        df_yr["origin_code"].notna() &
        df_yr["destination_code"].notna() &
        (df_yr["origin_code"] != df_yr["destination_code"]) &
        (df_yr["migrant_stock"] > 0)
    ]
    
    if df_yr.empty:
        return {
            "year": year,
            "total_emigrant_stock": 0.0,
            "num_origins": 0,
            "top_5_origin_share": 0.0,
            "top_10_origin_share": 0.0,
            "top_25_origin_share": 0.0,
            "origin_hhi": 0.0,
            "top_origins": []
        }
        
    group_cols = ["origin_code"]
    if "origin_display_name" in df_yr.columns:
        group_cols.append("origin_display_name")
        
    orig_grouped = df_yr.groupby(group_cols)["migrant_stock"].sum().reset_index()
    orig_grouped = orig_grouped.sort_values("migrant_stock", ascending=False)
    
    total_stock = float(orig_grouped["migrant_stock"].sum())
    shares = (orig_grouped["migrant_stock"] / total_stock) * 100.0
    
    top_5_share = float(shares.iloc[:5].sum()) if len(shares) >= 5 else float(shares.sum())
    top_10_share = float(shares.iloc[:10].sum()) if len(shares) >= 10 else float(shares.sum())
    top_25_share = float(shares.iloc[:25].sum()) if len(shares) >= 25 else float(shares.sum())
    hhi = float((shares ** 2).sum())
    
    top_origins = orig_grouped.head(10).to_dict(orient="records")
    for d in top_origins:
        d["share_pct"] = (d["migrant_stock"] / total_stock) * 100.0
        
    return {
        "year": year,
        "total_emigrant_stock": total_stock,
        "num_origins": len(orig_grouped),
        "top_5_origin_share": top_5_share,
        "top_10_origin_share": top_10_share,
        "top_25_origin_share": top_25_share,
        "origin_hhi": hhi,
        "top_origins": top_origins
    }


def compute_longitudinal_concentration_trend(
    df_country: pd.DataFrame,
    df_bilat: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute destination and origin concentration metrics across all UN DESA census rounds (1990–2020).
    
    Args:
        df_country: Country socioeconomic DataFrame.
        df_bilat: Bilateral migration DataFrame.
        
    Returns:
        pd.DataFrame: Longitudinal concentration metrics table.
    """
    if df_country.empty:
        return pd.DataFrame()
        
    years = sorted(df_country["year"].unique())
    records = []
    
    for yr in years:
        dest_conc = compute_destination_concentration(df_country, year=yr)
        orig_conc = compute_origin_concentration(df_bilat, year=yr)
        
        records.append({
            "year": yr,
            "total_migrant_stock": dest_conc["total_migrant_stock"],
            "dest_top_5_share": dest_conc["top_5_share"],
            "dest_top_10_share": dest_conc["top_10_share"],
            "dest_top_25_share": dest_conc["top_25_share"],
            "dest_hhi": dest_conc["hhi"],
            "orig_top_5_share": orig_conc["top_5_origin_share"],
            "orig_top_10_share": orig_conc["top_10_origin_share"],
            "orig_top_25_share": orig_conc["top_25_origin_share"],
            "orig_hhi": orig_conc["origin_hhi"],
        })
        
    return pd.DataFrame(records)


def compute_migration_dependence(
    df_country: pd.DataFrame,
    df_bilat: pd.DataFrame,
    year: int
) -> pd.DataFrame:
    """
    Calculate country-level migrant-stock demographic intensity and inbound origin concentration metrics.
    
    Metrics:
    - country_code, country_name
    - migrant_stock: Total residing foreign-born population
    - population: Host nation total population
    - migrant_stock_pct_population: Share of destination population (%)
    - top_origin_code: Origin sending largest bilateral stock to this destination
    - top_origin_name: Display name of top origin
    - top_origin_stock: Stock from primary origin
    - top_origin_share_pct: Share of host country's residing immigrant stock from primary origin (%)
    - origin_concentration_hhi: HHI measuring concentration of inbound origins for this host country
    
    Terminology note: Descriptive measures of migrant-stock share and origin concentration,
    strictly avoiding causal 'dependency' claims.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        df_bilat: Bilateral migration DataFrame.
        year: Target census year.
        
    Returns:
        pd.DataFrame: Table of country-level migrant-stock share and origin concentration metrics.
    """
    if df_country.empty or df_bilat.empty:
        return pd.DataFrame()

    df_c_yr = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False))
    ].copy()
    
    df_b_yr = df_bilat[
        (df_bilat["year"] == year) &
        (~df_bilat.get("is_aggregate_route", False)) &
        (df_bilat["origin_code"].notna()) &
        (df_bilat["destination_code"].notna()) &
        (df_bilat["origin_code"] != df_bilat["destination_code"]) &
        (df_bilat["migrant_stock"] > 0)
    ].copy()
    
    records = []
    for row in df_c_yr.itertuples():
        c_code = row.country_code
        c_name = getattr(row, "display_name", getattr(row, "country", str(c_code)))
        stock = getattr(row, "migrant_stock", np.nan)
        pop = getattr(row, "population", np.nan)
        pct_pop = getattr(row, "migrant_stock_pct_population", np.nan)
        
        inbound = df_b_yr[df_b_yr["destination_code"] == c_code].sort_values("migrant_stock", ascending=False)
        if not inbound.empty and pd.notna(stock) and stock > 0:
            top_orig = inbound.iloc[0]
            top_orig_code = top_orig["origin_code"]
            top_orig_name = getattr(top_orig, "origin_display_name", getattr(top_orig, "origin_country", top_orig_code))
            top_orig_stock = float(top_orig["migrant_stock"])
            top_orig_share = (top_orig_stock / float(stock)) * 100.0
            
            inbound_shares = (inbound["migrant_stock"] / float(stock)) * 100.0
            origin_hhi = float((inbound_shares ** 2).sum())
        else:
            top_orig_code = "N/A"
            top_orig_name = "N/A"
            top_orig_stock = 0.0
            top_orig_share = 0.0
            origin_hhi = 0.0
            
        records.append({
            "country_code": c_code,
            "country_name": c_name,
            "year": year,
            "migrant_stock": stock,
            "population": pop,
            "migrant_stock_pct_population": pct_pop,
            "top_origin_code": top_orig_code,
            "top_origin_name": top_orig_name,
            "top_origin_stock": top_orig_stock,
            "top_origin_share_pct": top_orig_share,
            "origin_concentration_hhi": origin_hhi,
        })
        
    return pd.DataFrame(records).sort_values("migrant_stock", ascending=False).reset_index(drop=True)


# =============================================================================
# 2. CORRIDOR CONCENTRATION & EVOLUTION
# =============================================================================

def compute_corridor_concentration_trend(df_bilat: pd.DataFrame) -> pd.DataFrame:
    """
    Track global bilateral corridor concentration shares (Top 10, Top 25, Top 50 corridors) across years.
    
    Args:
        df_bilat: Bilateral DataFrame.
        
    Returns:
        pd.DataFrame: Yearly corridor concentration shares table.
    """
    if df_bilat.empty:
        return pd.DataFrame()
        
    years = sorted(df_bilat["year"].unique())
    records = []
    
    for yr in years:
        df_yr = df_bilat[
            (df_bilat["year"] == yr) &
            (~df_bilat["is_aggregate_route"]) &
            (df_bilat["origin_code"].notna()) &
            (df_bilat["destination_code"].notna()) &
            (df_bilat["origin_code"] != df_bilat["destination_code"]) &
            (df_bilat["migrant_stock"] > 0)
        ].sort_values("migrant_stock", ascending=False)
        
        tot_stock = float(df_yr["migrant_stock"].sum())
        if tot_stock > 0:
            top_10_share = (df_yr.iloc[:10]["migrant_stock"].sum() / tot_stock) * 100.0
            top_25_share = (df_yr.iloc[:25]["migrant_stock"].sum() / tot_stock) * 100.0
            top_50_share = (df_yr.iloc[:50]["migrant_stock"].sum() / tot_stock) * 100.0
            num_corr = len(df_yr)
            top_row = df_yr.iloc[0]
            o_name = top_row.get("origin_display_name", top_row.get("origin_country", top_row["origin_code"]))
            d_name = top_row.get("dest_display_name", top_row.get("destination_country", top_row["destination_code"]))
            top_1_corr = f"{o_name} → {d_name} ({top_row['migrant_stock']:,.0f})"
        else:
            top_10_share, top_25_share, top_50_share = 0.0, 0.0, 0.0
            num_corr = 0
            top_1_corr = "None"
            
        records.append({
            "year": yr,
            "total_corridor_stock": tot_stock,
            "active_corridor_count": num_corr,
            "top_10_corridor_share": top_10_share,
            "top_25_corridor_share": top_25_share,
            "top_50_corridor_share": top_50_share,
            "largest_corridor": top_1_corr
        })
        
    return pd.DataFrame(records)


def compute_corridor_trajectories(df_bilat: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Track longitudinal stock evolution and rankings of top global bilateral corridors across 1990–2020.
    
    Args:
        df_bilat: Bilateral DataFrame.
        top_n: Number of top corridors from the latest year to trace historically.
        
    Returns:
        pd.DataFrame: Longitudinal corridor trajectory DataFrame.
    """
    if df_bilat.empty:
        return pd.DataFrame()
        
    latest_yr = max(df_bilat["year"].unique())
    latest_top = df_bilat[
        (df_bilat["year"] == latest_yr) &
        (~df_bilat["is_aggregate_route"]) &
        (df_bilat["origin_code"].notna()) &
        (df_bilat["destination_code"].notna()) &
        (df_bilat["origin_code"] != df_bilat["destination_code"])
    ].sort_values("migrant_stock", ascending=False).head(top_n)
    
    target_pairs = set(zip(latest_top["origin_code"], latest_top["destination_code"]))
    
    records = []
    for row in df_bilat.itertuples():
        if (row.origin_code, row.destination_code) in target_pairs and not row.is_aggregate_route:
            records.append({
                "corridor_label": getattr(row, "corridor_label", f"{getattr(row, 'origin_country', row.origin_code)} → {getattr(row, 'destination_country', row.destination_code)}"),
                "origin_code": row.origin_code,
                "destination_code": row.destination_code,
                "origin_name": getattr(row, "origin_display_name", str(getattr(row, "origin_country", row.origin_code))),
                "dest_name": getattr(row, "dest_display_name", str(getattr(row, "destination_country", row.destination_code))),
                "year": row.year,
                "migrant_stock": float(row.migrant_stock),
            })
            
    df_traj = pd.DataFrame(records)
    return df_traj.sort_values(["corridor_label", "year"]).reset_index(drop=True)


# =============================================================================
# 3. SOCIOECONOMIC BIVARIATE CORRELATION ENGINE
# =============================================================================

def compute_socioeconomic_correlations(
    df_country: pd.DataFrame,
    year: int,
    df_net_metrics: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Compute Pearson and Spearman correlation coefficients with two-tailed p-values
    for standard socioeconomic and migrant-stock indicators.
    
    Pairs evaluated:
    1. Migrant Stock vs. GDP (Total scale)
    2. Migrant Stock % of Population vs. GDP per Capita (Income intensity)
    3. Migrant Stock vs. Population (Demographic scale)
    4. Migrant Stock % of Population vs. Unemployment Rate (Labor context)
    5. Weighted Network Strength vs. GDP per Capita (Connectivity vs Wealth)
    
    IMPORTANT: All outputs represent statistical associations and do not imply causal mechanisms.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        year: Census year.
        df_net_metrics: Optional network metrics DataFrame for the same year.
        
    Returns:
        pd.DataFrame: Table of correlation statistics.
    """
    if df_country.empty or "year" not in df_country.columns:
        return pd.DataFrame()

    df_yr = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False))
    ].copy()
    
    if df_net_metrics is not None and not df_net_metrics.empty:
        net_cols = [c for c in ["country_code", "total_strength", "betweenness_centrality", "pagerank"] if c in df_net_metrics.columns]
        df_yr = df_yr.merge(df_net_metrics[net_cols], on="country_code", how="left")
        
    pairs = [
        ("migrant_stock_pct_population", "gdp_per_capita", "Migrant Stock % Pop vs. GDP per Capita", "Income Intensity Association"),
        ("migrant_stock", "gdp", "Migrant Stock vs. Total GDP", "Economic Scale Association"),
        ("migrant_stock", "population", "Migrant Stock vs. Total Population", "Demographic Scale Association"),
        ("migrant_stock_pct_population", "unemployment", "Migrant Stock % Pop vs. Unemployment Rate", "Labor Context Association"),
    ]
    
    if "total_strength" in df_yr.columns:
        pairs.append(("total_strength", "gdp_per_capita", "Network Strength vs. GDP per Capita", "Network Connectivity vs Wealth"))

    results = []
    for col_x, col_y, pair_name, desc in pairs:
        if col_x not in df_yr.columns or col_y not in df_yr.columns:
            continue
            
        valid = df_yr[[col_x, col_y]].dropna()
        valid = valid[(valid[col_x] > 0) & (valid[col_y] > 0)]
        n = len(valid)
        
        if n >= 5:
            r_pearson, p_pearson = stats.pearsonr(valid[col_x], valid[col_y])
            r_spearman, p_spearman = stats.spearmanr(valid[col_x], valid[col_y])
            
            abs_r = abs(r_spearman)
            if abs_r >= 0.7:
                strength = "Strong " + ("Positive" if r_spearman > 0 else "Negative")
            elif abs_r >= 0.4:
                strength = "Moderate " + ("Positive" if r_spearman > 0 else "Negative")
            elif abs_r >= 0.2:
                strength = "Weak " + ("Positive" if r_spearman > 0 else "Negative")
            else:
                strength = "Negligible / Uncorrelated"
                
            sig_label = "p < 0.001 (Highly Sig.)" if p_spearman < 0.001 else ("p < 0.05 (Significant)" if p_spearman < 0.05 else "Not Significant (p ≥ 0.05)")
        else:
            r_pearson, p_pearson, r_spearman, p_spearman = np.nan, np.nan, np.nan, np.nan
            strength = "Insufficient Data"
            sig_label = "N/A"
            
        results.append({
            "pair_name": pair_name,
            "description": desc,
            "year": year,
            "sample_size": n,
            "pearson_r": r_pearson,
            "pearson_p_value": p_pearson,
            "spearman_rho": r_spearman,
            "spearman_p_value": p_spearman,
            "relationship_strength": strength,
            "statistical_significance": sig_label,
        })
        
    return pd.DataFrame(results)


def get_bivariate_scatter_data(
    df_country: pd.DataFrame,
    x_metric_col: str,
    y_metric_col: str,
    year: int,
    log_scale_x: bool = False,
    log_scale_y: bool = False
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Extract clean country-level dataframe for bivariate interactive scatter plots with linear regression stats.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        x_metric_col: Column name for X axis.
        y_metric_col: Column name for Y axis.
        year: Selected year.
        log_scale_x: If True, log-transform X.
        log_scale_y: If True, log-transform Y.
        
    Returns:
        Tuple:
            - pd.DataFrame: Clean scatter points DataFrame.
            - Dict[str, float]: Correlation & regression fit statistics.
    """
    if df_country.empty or x_metric_col not in df_country.columns or y_metric_col not in df_country.columns:
        return pd.DataFrame(), {}

    raw_needed = ["display_name", "country_code", x_metric_col, y_metric_col, "migrant_stock", "population", "gdp_per_capita"]
    present_cols = []
    for c in raw_needed:
        if c in df_country.columns and c not in present_cols:
            present_cols.append(c)
    
    df_yr = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False))
    ][present_cols].dropna()
    
    if df_yr.empty:
        return pd.DataFrame(), {}
        
    valid = df_yr[(df_yr[x_metric_col] > 0) & (df_yr[y_metric_col] > 0)].copy()
    if valid.empty:
        return pd.DataFrame(), {}
        
    x_vals = np.log10(valid[x_metric_col]) if log_scale_x else valid[x_metric_col]
    y_vals = np.log10(valid[y_metric_col]) if log_scale_y else valid[y_metric_col]
    
    valid["plot_x"] = x_vals
    valid["plot_y"] = y_vals
    
    r_p, p_p = stats.pearsonr(valid[x_metric_col], valid[y_metric_col])
    r_s, p_s = stats.spearmanr(valid[x_metric_col], valid[y_metric_col])
    slope, intercept, _, _, _ = stats.linregress(valid["plot_x"], valid["plot_y"])
    
    stats_dict = {
        "n": len(valid),
        "pearson_r": r_p,
        "pearson_p": p_p,
        "spearman_rho": r_s,
        "spearman_p": p_s,
        "slope": slope,
        "intercept": intercept
    }
    return valid, stats_dict


# =============================================================================
# 4. MIGRATION CHANGE CLASSIFICATION & RANKINGS
# =============================================================================

def classify_stock_changes(df_country: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Classify countries based on their 5-year intercensal migrant-stock percentage growth.
    
    Transparent Thresholds:
    - Strong Increase: growth >= +25.0%
    - Moderate Increase: +5.0% <= growth < +25.0%
    - Stable: -5.0% <= growth < +5.0%
    - Moderate Decrease: -20.0% <= growth < -5.0%
    - Strong Decrease: growth < -20.0%
    
    Args:
        df_country: Country socioeconomic DataFrame.
        year: Selected year (1995–2020; 1990 has no previous round).
        
    Returns:
        pd.DataFrame: Table with growth classification columns.
    """
    if df_country.empty or "year" not in df_country.columns:
        return df_country
        
    df_yr = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False))
    ].copy()
    
    if "stock_growth_pct_5yr" not in df_yr.columns:
        return df_yr
        
    def _classify(val):
        if pd.isna(val):
            return "No Baseline (1990 Round)"
        elif val >= 25.0:
            return "Strong Increase (≥ +25%)"
        elif val >= 5.0:
            return "Moderate Increase (+5% to +25%)"
        elif val >= -5.0:
            return "Stable (-5% to +5%)"
        elif val >= -20.0:
            return "Moderate Decrease (-5% to -20%)"
        else:
            return "Strong Decrease (< -20%)"
            
    df_yr["change_category"] = df_yr["stock_growth_pct_5yr"].apply(_classify)
    return df_yr


def get_top_growth_and_declining_countries(
    df_country: pd.DataFrame,
    year: int,
    top_n: int = 10
) -> Dict[str, pd.DataFrame]:
    """
    Extract leaderboards for fastest-growing, largest absolute increase, and largest decrease in migrant stock.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        year: Selected year.
        top_n: Number of countries per category.
        
    Returns:
        Dict[str, pd.DataFrame]: Tables for fastest growth, largest increase, and largest decrease.
    """
    if df_country.empty or "year" not in df_country.columns:
        return {
            "fastest_growth_pct": pd.DataFrame(),
            "largest_increase_abs": pd.DataFrame(),
            "largest_decrease_abs": pd.DataFrame(),
        }

    df_yr = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False)) &
        (df_country.get("stock_change_5yr", pd.Series(dtype=float)).notna())
    ].copy()
    
    if df_yr.empty:
        return {
            "fastest_growth_pct": pd.DataFrame(),
            "largest_increase_abs": pd.DataFrame(),
            "largest_decrease_abs": pd.DataFrame(),
        }
        
    fastest_pct = df_yr[df_yr["migrant_stock"] >= 10000].sort_values("stock_growth_pct_5yr", ascending=False).head(top_n)
    largest_inc = df_yr.sort_values("stock_change_5yr", ascending=False).head(top_n)
    largest_dec = df_yr.sort_values("stock_change_5yr", ascending=True).head(top_n)
    
    return {
        "fastest_growth_pct": fastest_pct.reset_index(drop=True),
        "largest_increase_abs": largest_inc.reset_index(drop=True),
        "largest_decrease_abs": largest_dec.reset_index(drop=True),
    }


# =============================================================================
# 5. OUTLIER & ANOMALY DETECTION
# =============================================================================

def detect_migration_anomalies(
    df_country: pd.DataFrame,
    metric_col: str,
    year: int,
    method: str = "IQR",
    threshold: float = 1.5
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Identify countries exhibiting unusual statistical distributions in migrant stock or demographic shares.
    
    Methods:
    - IQR (Interquartile Range): Outliers defined beyond Q1 - k*IQR or Q3 + k*IQR (default k=1.5).
    - Z-Score: Outliers defined where |z| > threshold (default |z| > 2.5).
    
    IMPORTANT: An anomaly represents a statistically unusual observation requiring analytical
    investigation (e.g. city-states, rapid humanitarian shocks), NOT a data entry error.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        metric_col: Target indicator column name.
        year: Selected year.
        method: 'IQR' or 'Z-Score'.
        threshold: Multiplier for IQR (1.5 or 3.0) or critical z-score threshold (e.g. 2.5).
        
    Returns:
        Tuple:
            - pd.DataFrame: Outlier observations with deviation metrics.
            - Dict[str, Any]: Distribution summary (Q1, Q3, Mean, Std, bounds).
    """
    if df_country.empty or metric_col not in df_country.columns or "year" not in df_country.columns:
        return pd.DataFrame(), {"method": method, "threshold": threshold, "outlier_count": 0}

    df_yr = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False)) &
        (df_country[metric_col].notna())
    ].copy()
    
    if df_yr.empty:
        return pd.DataFrame(), {"method": method, "threshold": threshold, "outlier_count": 0}
        
    vals = df_yr[metric_col].values
    
    if method == "Z-Score":
        mean_val = float(np.mean(vals))
        std_val = float(np.std(vals, ddof=1)) if len(vals) > 1 else 1.0
        
        if std_val > 0:
            df_yr["z_score"] = (df_yr[metric_col] - mean_val) / std_val
        else:
            df_yr["z_score"] = 0.0
            
        lower_bound = mean_val - threshold * std_val
        upper_bound = mean_val + threshold * std_val
        
        outliers = df_yr[df_yr["z_score"].abs() >= threshold].copy()
        outliers["outlier_type"] = np.where(outliers["z_score"] > 0, "High Outlier (Z > +threshold)", "Low Outlier (Z < -threshold)")
        
        summary = {
            "method": "Z-Score",
            "threshold": threshold,
            "mean": mean_val,
            "std": std_val,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": len(outliers)
        }
    else:  # Default IQR
        q1 = float(np.percentile(vals, 25))
        q3 = float(np.percentile(vals, 75))
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        df_yr["iqr_deviation"] = np.where(
            df_yr[metric_col] > upper_bound,
            (df_yr[metric_col] - q3) / (iqr if iqr > 0 else 1.0),
            np.where(
                df_yr[metric_col] < lower_bound,
                (q1 - df_yr[metric_col]) / (iqr if iqr > 0 else 1.0),
                0.0
            )
        )
        
        outliers = df_yr[(df_yr[metric_col] > upper_bound) | (df_yr[metric_col] < lower_bound)].copy()
        outliers["outlier_type"] = np.where(outliers[metric_col] > upper_bound, "High Outlier (> Q3 + k*IQR)", "Low Outlier (< Q1 - k*IQR)")
        
        summary = {
            "method": "IQR",
            "threshold": threshold,
            "q1": q1,
            "median": float(np.median(vals)),
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": len(outliers)
        }
        
    outliers = outliers.sort_values(metric_col, ascending=False).reset_index(drop=True)
    return outliers, summary


# =============================================================================
# 6. MULTI-COUNTRY COMPARATIVE ANALYTICS & NORMALIZATION
# =============================================================================

def compute_multicountry_comparison(
    df_country: pd.DataFrame,
    country_codes: List[str],
    year: int,
    df_net_metrics: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate absolute and min-max normalized comparison matrices across selected countries for a chosen census round.
    
    Normalized Score Formulation:
    Score_norm = ((x - x_min_global) / (x_max_global - x_min_global)) * 100 in range [0, 100]
    
    Disclaimer: Normalized scores are relative comparison measures scaled across global sovereign
    nations for that census round, NOT original physical measurements.
    
    Args:
        df_country: Country socioeconomic DataFrame.
        country_codes: List of country ISO3 codes (2–5 countries).
        year: Selected year.
        df_net_metrics: Optional network metrics DataFrame.
        
    Returns:
        Tuple:
            - pd.DataFrame: Absolute values table.
            - pd.DataFrame: Normalized [0, 100] comparison table.
    """
    if df_country.empty or "year" not in df_country.columns:
        return pd.DataFrame(), pd.DataFrame()

    df_global = df_country[
        (df_country["year"] == year) &
        (~df_country.get("is_aggregate", False))
    ].copy()
    
    if df_net_metrics is not None and not df_net_metrics.empty:
        net_cols = [c for c in ["country_code", "total_strength", "total_degree", "betweenness_centrality", "pagerank"] if c in df_net_metrics.columns]
        df_global = df_global.merge(df_net_metrics[net_cols], on="country_code", how="left")
        
    cols_to_compare = [
        ("migrant_stock", "Total Migrant Stock (People)"),
        ("migrant_stock_pct_population", "Migrant Stock % of Population"),
        ("stock_growth_pct_5yr", "5-Year Stock Growth (%)"),
        ("gdp_per_capita", "GDP per Capita (USD)"),
        ("population", "Total Population"),
        ("unemployment", "Unemployment Rate (%)"),
    ]
    
    if "total_strength" in df_global.columns:
        cols_to_compare.extend([
            ("total_strength", "Network Weighted Strength"),
            ("total_degree", "Network Degree Centrality"),
            ("pagerank", "PageRank Score"),
        ])
        
    df_selected = df_global[df_global["country_code"].isin(country_codes)].copy()
    if df_selected.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    abs_records = []
    norm_records = []
    
    for row in df_selected.itertuples():
        c_code = row.country_code
        c_name = getattr(row, "display_name", getattr(row, "country", str(c_code)))
        
        abs_dict = {"country_code": c_code, "country_name": c_name}
        norm_dict = {"country_code": c_code, "country_name": c_name}
        
        for col_name, display_label in cols_to_compare:
            val = getattr(row, col_name, np.nan)
            abs_dict[display_label] = val
            
            if col_name in df_global.columns:
                glob_series = df_global[col_name].dropna()
                g_min, g_max = (glob_series.min(), glob_series.max()) if not glob_series.empty else (0, 0)
                
                if pd.notna(val) and g_max > g_min:
                    norm_score = ((float(val) - float(g_min)) / (float(g_max) - float(g_min))) * 100.0
                else:
                    norm_score = np.nan
            else:
                norm_score = np.nan
            norm_dict[display_label] = norm_score
            
        abs_records.append(abs_dict)
        norm_records.append(norm_dict)
        
    return pd.DataFrame(abs_records), pd.DataFrame(norm_records)
