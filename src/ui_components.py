"""
Reusable UI Components for the Global Migration Observatory.
Provides consistent mastheads, section headers, metric/KPI cards, scientific callouts,
and sidebar navigation elements conforming to the centralized design system.
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
