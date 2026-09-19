"""
Reusable UI Components for the Global Migration Observatory.
Provides consistent mastheads, section headers, metric/KPI cards, scientific callouts,
insight cards, correlation badges, multi-country comparison widgets, and advisory callouts
conforming to the centralized design system.
"""

from typing import Any, Dict, List, Optional
import streamlit as st

from src.ui_theme import get_theme_colors


def render_masthead(theme_mode: str = "Light"):
    """Render the application header with title, subtitle, and data source badge."""
    c = get_theme_colors(theme_mode)
    html = f"""
    <div class="app-header">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">
            <div>
                <h1 style="margin: 0; font-size: 1.85rem; font-weight: 700; letter-spacing: -0.025em; color: {c['text_primary']};">
                    GLOBAL MIGRATION OBSERVATORY
                </h1>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.95rem; color: {c['text_secondary']}; line-height: 1.4;">
                    Explore where people migrate, how migration patterns change, and how migration relates to socioeconomic factors.
                </p>
            </div>
            <div>
                <span style="background-color: {c['card_bg']}; border: 1px solid {c['card_border']}; color: {c['text_primary']}; font-size: 0.8rem; font-weight: 600; padding: 0.45rem 0.85rem; border-radius: 6px; box-shadow: {c['shadow_sm']};">
                    UN DESA 2020 Rev. & World Bank WDI
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_sidebar_header(theme_mode: str = "Light"):
    """Render the sidebar branding and subtitle."""
    c = get_theme_colors(theme_mode)
    html = f"""
    <div style="padding: 0.25rem 0 0.5rem 0;">
        <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: {c['text_primary']}; letter-spacing: -0.02em;">
            🌍 MIGRATION OBSERVATORY
        </h2>
        <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: {c['text_secondary']};">
            Empirical Migration Dynamics & Networks (1990–2020)
        </p>
    </div>
    """
    st.sidebar.markdown(html, unsafe_allow_html=True)


def render_section_title(title: str, subtitle: str = ""):
    """Render a consistent section title with optional subtitle."""
    if subtitle:
        html = f"""
        <div class="section-header">
            <span class="section-title">{title}</span>
            <span class="section-subtitle">{subtitle}</span>
        </div>
        """
    else:
        html = f"""
        <div class="section-header">
            <span class="section-title">{title}</span>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtitle: str = "", theme_mode: str = "Light") -> str:
    """Generate HTML for a standardized metric / KPI card."""
    c = get_theme_colors(theme_mode)
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-val">{value}</div>
        {f'<div class="metric-sub">{subtitle}</div>' if subtitle else ''}
    </div>
    """


def render_scientific_alert(text: str, theme_mode: str = "Light"):
    """Render a highlighted callout for scientific principles and definitions."""
    c = get_theme_colors(theme_mode)
    html = f"""
    <div class="stock-alert">
        {text}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_insight_card(
    category: str,
    title: str,
    message: str,
    badge_text: Optional[str] = None,
    theme_mode: str = "Light"
):
    """
    Render a stylized insight storytelling card.
    
    Args:
        category: Analytical category (e.g. 'Global Trend', 'Concentration').
        title: Headline of the insight.
        message: Human-readable analytical narrative.
        badge_text: Optional key statistical badge.
        theme_mode: 'Light' or 'Dark'.
    """
    c = get_theme_colors(theme_mode)
    badge_html = (
        f'<span style="background-color: {c["card_border"]}; color: {c["text_primary"]}; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 4px; font-family: \'JetBrains Mono\', monospace;">{badge_text}</span>'
        if badge_text else ""
    )
    
    html = f"""
    <div class="metric-card" style="margin-bottom: 1rem; border-left: 4px solid {c['accent_blue']};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: {c['accent_blue']};">
                {category}
            </span>
            {badge_html}
        </div>
        <h4 style="margin: 0 0 0.4rem 0; font-size: 1.05rem; font-weight: 700; color: {c['text_primary']};">
            {title}
        </h4>
        <p style="margin: 0; font-size: 0.9rem; color: {c['text_secondary']}; line-height: 1.5;">
            {message}
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_correlation_badge(
    pair_name: str,
    r_pearson: float,
    rho_spearman: float,
    sig_label: str,
    theme_mode: str = "Light"
) -> str:
    """Generate HTML snippet for a bivariate correlation statistical card."""
    c = get_theme_colors(theme_mode)
    return f"""
    <div class="metric-card" style="padding: 0.85rem 1rem;">
        <div class="metric-title">{pair_name}</div>
        <div style="display: flex; gap: 1rem; margin-top: 0.4rem; align-items: baseline;">
            <div>
                <span style="font-size: 0.75rem; color: {c['text_secondary']};">Spearman ρ:</span>
                <span style="font-size: 1.15rem; font-weight: 700; color: {c['accent_blue']}; font-family: 'JetBrains Mono', monospace;">{rho_spearman:+.2f}</span>
            </div>
            <div>
                <span style="font-size: 0.75rem; color: {c['text_secondary']};">Pearson r:</span>
                <span style="font-size: 1.15rem; font-weight: 700; color: {c['text_primary']}; font-family: 'JetBrains Mono', monospace;">{r_pearson:+.2f}</span>
            </div>
        </div>
        <div style="font-size: 0.75rem; color: {c['text_secondary']}; margin-top: 0.35rem;">
            {sig_label}
        </div>
    </div>
    """


def render_warning_callout(text: str, theme_mode: str = "Light"):
    """Render a subtle amber/yellow advisory callout."""
    c = get_theme_colors(theme_mode)
    html = f"""
    <div style="background-color: {c['card_bg']}; border-left: 4px solid {c['accent_amber']}; border-top: 1px solid {c['card_border']}; border-right: 1px solid {c['card_border']}; border-bottom: 1px solid {c['card_border']}; padding: 0.75rem 1rem; border-radius: 0 6px 6px 0; margin: 0.85rem 0; font-size: 0.85rem; color: {c['text_primary']}; line-height: 1.45;">
        {text}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_comparison_metric(
    label: str,
    values_dict: Dict[str, Any],
    theme_mode: str = "Light"
) -> str:
    """
    Generate an HTML snippet for a side-by-side comparison row across countries.
    
    Args:
        label: Metric title.
        values_dict: Dictionary mapping country name to formatted value string.
        theme_mode: 'Light' or 'Dark'.
        
    Returns:
        str: HTML markup.
    """
    c = get_theme_colors(theme_mode)
    cols_html = "".join([
        f'<div style="flex: 1; min-width: 120px; padding: 0.5rem; background-color: {c["card_bg"]}; border: 1px solid {c["card_border"]}; border-radius: 6px;">'
        f'<div style="font-size: 0.75rem; color: {c["text_secondary"]};">{c_name}</div>'
        f'<div style="font-size: 1.1rem; font-weight: 700; color: {c["text_primary"]}; font-family: \'JetBrains Mono\', monospace;">{val}</div>'
        f'</div>'
        for c_name, val in values_dict.items()
    ])
    
    return f"""
    <div style="margin-bottom: 0.85rem;">
        <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: {c['text_secondary']}; margin-bottom: 0.3rem;">{label}</div>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            {cols_html}
        </div>
    </div>
    """
