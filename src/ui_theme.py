"""
Universal Design System and Theme Engine for the Global Migration Observatory.
Centralizes design tokens, typography hierarchy, button states, input controls,
subtle micro-animations, prefers-reduced-motion support, and Plotly templates
for ☀️ Light Mode and 🌙 Dark Mode.
"""

from typing import Any, Dict
import streamlit as st


def get_theme_colors(theme_mode: str = "Light") -> Dict[str, str]:
    """
    Get dictionary of design tokens for the active theme mode.
    
    Args:
        theme_mode: 'Light' or 'Dark'
        
    Returns:
        Dict[str, str]: Color and styling tokens.
    """
    if theme_mode == "Dark":
        return {
            "mode": "Dark",
            "bg_color": "#0f172a",
            "sidebar_bg": "#1e293b",
            "card_bg": "#1e293b",
            "card_border": "#334155",
            "card_border_hover": "#475569",
            "text_primary": "#f8fafc",
            "text_secondary": "#94a3b8",
            "text_muted": "#64748b",
            "accent_blue": "#38bdf8",
            "accent_blue_hover": "#0ea5e9",
            "accent_teal": "#2dd4bf",
            "accent_amber": "#fbbf24",
            "alert_bg": "#1e293b",
            "alert_border": "#38bdf8",
            "plotly_template": "plotly_dark",
            "table_header_bg": "#334155",
            "table_row_even": "#1e293b",
            "table_row_odd": "#182234",
            "button_bg": "#334155",
            "button_text": "#f8fafc",
            "button_border": "#475569",
            "button_hover_bg": "#475569",
            "button_hover_border": "#64748b",
            "node_edge_color": "#475569",
            "node_default": "#38bdf8",
            "map_ocean": "#0f172a",
            "map_land": "#1e293b",
            "map_coastline": "#475569",
            "shadow_sm": "0 1px 3px rgba(0,0,0,0.3)",
            "shadow_md": "0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -2px rgba(0,0,0,0.3)",
        }
    else:
        return {
            "mode": "Light",
            "bg_color": "#f8fafc",
            "sidebar_bg": "#ffffff",
            "card_bg": "#ffffff",
            "card_border": "#e2e8f0",
            "card_border_hover": "#cbd5e1",
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
            "text_muted": "#94a3b8",
            "accent_blue": "#0284c7",
            "accent_blue_hover": "#0369a1",
            "accent_teal": "#0d9488",
            "accent_amber": "#d97706",
            "alert_bg": "#f8fafc",
            "alert_border": "#0284c7",
            "plotly_template": "plotly_white",
            "table_header_bg": "#f1f5f9",
            "table_row_even": "#ffffff",
            "table_row_odd": "#f8fafc",
            "button_bg": "#ffffff",
            "button_text": "#0f172a",
            "button_border": "#cbd5e1",
            "button_hover_bg": "#f1f5f9",
            "button_hover_border": "#94a3b8",
            "node_edge_color": "#cbd5e1",
            "node_default": "#0284c7",
            "map_ocean": "#f1f5f9",
            "map_land": "#ffffff",
            "map_coastline": "#cbd5e1",
            "shadow_sm": "0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03)",
            "shadow_md": "0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.04)",
        }


def get_plotly_layout(theme_mode: str = "Light", title: str = "", height: int = 400) -> Dict[str, Any]:
    """
    Generate unified Plotly layout parameters conforming to the design system.
    
    Args:
        theme_mode: 'Light' or 'Dark'
        title: Chart title
        height: Height in pixels
        
    Returns:
        Dict[str, Any]: Layout dictionary for fig.update_layout(**layout)
    """
    c = get_theme_colors(theme_mode)
    is_dark = (theme_mode == "Dark")

    axis_title_color = c["text_primary"]
    axis_tick_color = "#e2e8f0" if is_dark else c["text_primary"]
    legend_text_color = c["text_primary"]
    grid_color = "#334155" if is_dark else "#e2e8f0"
    zeroline_color = "#475569" if is_dark else "#cbd5e1"

    return {
        "template": c["plotly_template"],
        "title": {
            "text": title,
            "font": {
                "size": 15,
                "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                "color": c["text_primary"]
            },
            "x": 0.0,
            "xanchor": "left"
        },
        "font": {
            "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "size": 12,
            "color": c["text_primary"]
        },
        "xaxis": {
            "title": {
                "font": {
                    "size": 12,
                    "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    "color": axis_title_color
                }
            },
            "tickfont": {
                "size": 11,
                "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                "color": axis_tick_color
            },
            "gridcolor": grid_color,
            "zerolinecolor": zeroline_color,
            "linecolor": grid_color,
        },
        "yaxis": {
            "title": {
                "font": {
                    "size": 12,
                    "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    "color": axis_title_color
                }
            },
            "tickfont": {
                "size": 11,
                "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                "color": axis_tick_color
            },
            "gridcolor": grid_color,
            "zerolinecolor": zeroline_color,
            "linecolor": grid_color,
        },
        "legend": {
            "font": {
                "size": 11,
                "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                "color": legend_text_color
            },
            "title": {
                "font": {
                    "size": 12,
                    "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    "color": c["text_primary"]
                }
            },
            "bgcolor": "rgba(0,0,0,0)"
        },
        "margin": {"l": 24, "r": 24, "t": 48, "b": 24},
        "height": height,
        "hoverlabel": {
            "bgcolor": c["card_bg"],
            "font_size": 12,
            "font_family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "font_color": c["text_primary"],
            "bordercolor": c["card_border"]
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
    }


def apply_ui_theme(theme_mode: str = "Light"):
    """
    Inject cohesive CSS styles for typography, cards, buttons, inputs, tables, micro-animations,
    and accessibility prefers-reduced-motion media rules.
    
    Args:
        theme_mode: 'Light' or 'Dark'
    """
    c = get_theme_colors(theme_mode)
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* 1. Global Reset & Typography System */
        /* Inter -> titles, headings, body text, KPI values */
        html, body, [data-testid="stAppViewContainer"], h1, h2, h3, h4, h5, h6, p, span, label, div {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {c['bg_color']};
            color: {c['text_primary']};
        }}

        /* JetBrains Mono -> ISO codes, technical identifiers, numerical code/table values */
        code, kbd, pre, .font-mono, .iso-code, .tech-identifier, [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {{
            font-family: 'JetBrains Mono', 'Fira Code', 'Roboto Mono', Menlo, Monaco, Consolas, monospace !important;
        }}

        /* 2. Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {c['sidebar_bg']};
            border-right: 1px solid {c['card_border']};
        }}
        [data-testid="stSidebar"] hr {{
            border-color: {c['card_border']};
            margin: 1rem 0;
        }}
        [data-testid="stSidebar"] .stRadio label {{
            font-size: 0.875rem;
            color: {c['text_primary']} !important;
            font-weight: 500;
        }}

        /* 3. Header Masthead */
        .app-header {{
            padding: 1.25rem 0 1rem 0;
            border-bottom: 1px solid {c['card_border']};
            margin-bottom: 1.5rem;
            animation: fadeIn 0.25s ease-out;
        }}

        /* 4. Section Divider & Header */
        .section-header {{
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            border-bottom: 1px solid {c['card_border']};
            padding-bottom: 0.4rem;
        }}
        .section-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: {c['text_primary']};
            letter-spacing: -0.015em;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .section-subtitle {{
            font-size: 0.85rem;
            color: {c['text_secondary']};
            font-weight: 400;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* 5. Refined Metric / KPI Card */
        .metric-card {{
            background-color: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: 8px;
            padding: 1.1rem 1.25rem;
            box-shadow: {c['shadow_sm']};
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
            animation: fadeSlideUp 0.3s ease-out forwards;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: {c['shadow_md']};
            border-color: {c['card_border_hover']};
        }}
        .metric-title {{
            font-size: 0.75rem;
            font-weight: 600;
            color: {c['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .metric-val {{
            font-size: 1.7rem;
            font-weight: 700;
            color: {c['text_primary']};
            line-height: 1.15;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.02em;
        }}
        .metric-sub {{
            font-size: 0.775rem;
            color: {c['text_secondary']};
            margin-top: 0.35rem;
            line-height: 1.3;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* 6. Scientific Alert / Callout Box */
        .stock-alert {{
            background-color: {c['alert_bg']};
            border-left: 4px solid {c['alert_border']};
            border-top: 1px solid {c['card_border']};
            border-right: 1px solid {c['card_border']};
            border-bottom: 1px solid {c['card_border']};
            padding: 0.85rem 1.15rem;
            border-radius: 0 6px 6px 0;
            margin: 1.1rem 0;
            font-size: 0.875rem;
            color: {c['text_primary']};
            line-height: 1.55;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            animation: fadeIn 0.25s ease-out;
        }}

        /* 7. Button & Download Button Design System */
        .stButton > button, .stDownloadButton > button {{
            background-color: {c['button_bg']};
            border: 1px solid {c['button_border']};
            color: {c['button_text']};
            font-size: 0.85rem;
            font-weight: 600;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            padding: 0.45rem 0.95rem;
            border-radius: 6px;
            box-shadow: {c['shadow_sm']};
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: {c['button_hover_bg']};
            border-color: {c['button_hover_border']};
            transform: translateY(-1px);
            box-shadow: {c['shadow_md']};
            color: {c['text_primary']};
        }}
        .stButton > button:active, .stDownloadButton > button:active {{
            transform: translateY(0);
            box-shadow: {c['shadow_sm']};
        }}
        .stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{
            outline: 2px solid {c['accent_blue']};
            outline-offset: 2px;
        }}

        /* 8. Input Controls, Selectboxes & BaseWeb Dropdown Menus */
        .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label {{
            color: {c['text_primary']} !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
            margin-bottom: 0.25rem;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Closed selectbox & multiselect control styling */
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div,
        div[data-baseweb="select"] > div {{
            background-color: {c['card_bg']} !important;
            border: 1px solid {c['card_border']} !important;
            color: {c['text_primary']} !important;
            border-radius: 6px !important;
            font-size: 0.875rem !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        [data-testid="stSelectbox"] > div > div:focus-within,
        [data-testid="stMultiSelect"] > div > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {{
            border-color: {c['accent_blue']} !important;
            box-shadow: 0 0 0 1px {c['accent_blue']} !important;
        }}

        /* Closed select value text and placeholder */
        [data-baseweb="select"] div,
        [data-baseweb="select"] span,
        [data-testid="stSelectbox"] div[data-testid="stMarkdownContainer"] p {{
            color: {c['text_primary']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Dropdown arrow and clear icons */
        [data-baseweb="select"] svg,
        [data-testid="stSelectbox"] svg,
        [data-testid="stMultiSelect"] svg {{
            fill: {c['text_secondary']} !important;
            color: {c['text_secondary']} !important;
        }}

        /* BaseWeb Popover / Dropdown Menu Container (covers portal-rendered menus outside container) */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"],
        ul[data-baseweb="menu"],
        [role="listbox"],
        ul[role="listbox"],
        div[role="listbox"] {{
            background-color: {c['card_bg']} !important;
            border: 1px solid {c['card_border']} !important;
            color: {c['text_primary']} !important;
            border-radius: 6px !important;
            box-shadow: {c['shadow_md']} !important;
            overflow: hidden;
        }}

        /* Popover list options (individual dropdown entries) */
        [role="option"],
        li[role="option"],
        div[role="option"],
        ul[data-baseweb="menu"] li,
        div[data-baseweb="menu"] li,
        [data-baseweb="menu"] [role="option"] {{
            background-color: {c['card_bg']} !important;
            color: {c['text_primary']} !important;
            font-size: 0.875rem !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            padding: 0.5rem 0.85rem !important;
            cursor: pointer !important;
            transition: background-color 0.15s ease, color 0.15s ease !important;
        }}

        /* Text inside options */
        [role="option"] *,
        li[role="option"] *,
        div[role="option"] * {{
            color: {c['text_primary']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        /* Hovered / Focused option state */
        [role="option"]:hover,
        li[role="option"]:hover,
        div[role="option"]:hover,
        [role="option"]:focus,
        li[role="option"]:focus,
        [role="option"][aria-selected="false"]:hover,
        [data-baseweb="menu"] li:hover,
        [data-baseweb="menu"] [aria-highlighted="true"],
        li[data-highlighted="true"] {{
            background-color: {c['button_hover_bg']} !important;
            color: {c['text_primary']} !important;
        }}
        [role="option"]:hover *,
        li[role="option"]:hover *,
        [data-baseweb="menu"] [aria-highlighted="true"] * {{
            color: {c['text_primary']} !important;
        }}

        /* Selected option state */
        [role="option"][aria-selected="true"],
        li[role="option"][aria-selected="true"],
        div[role="option"][aria-selected="true"],
        [data-baseweb="menu"] [aria-selected="true"] {{
            background-color: {c['button_bg']} !important;
            color: {c['accent_blue']} !important;
            font-weight: 600 !important;
        }}
        [role="option"][aria-selected="true"] *,
        li[role="option"][aria-selected="true"] * {{
            color: {c['accent_blue']} !important;
            font-weight: 600 !important;
        }}

        /* Search / Input text inside select controls */
        [data-baseweb="select"] input,
        [data-baseweb="popover"] input,
        [data-testid="stSelectbox"] input,
        [data-testid="stMultiSelect"] input {{
            color: {c['text_primary']} !important;
            background-color: transparent !important;
            caret-color: {c['accent_blue']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        /* MultiSelect tags / pills */
        [data-baseweb="tag"] {{
            background-color: {c['button_bg']} !important;
            border: 1px solid {c['card_border']} !important;
            color: {c['text_primary']} !important;
            border-radius: 4px !important;
        }}
        [data-baseweb="tag"] span {{
            color: {c['text_primary']} !important;
        }}
        [data-baseweb="tag"] svg {{
            fill: {c['text_secondary']} !important;
        }}

        /* 9. Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 1px solid {c['card_border']};
            padding-bottom: 2px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 38px;
            padding: 0 14px;
            font-size: 0.85rem;
            font-weight: 500;
            color: {c['text_secondary']};
            background-color: transparent;
            border-radius: 6px 6px 0 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            transition: color 0.15s ease, background-color 0.15s ease;
        }}
        .stTabs [aria-selected="true"] {{
            color: {c['accent_blue']} !important;
            font-weight: 600;
            border-bottom: 2px solid {c['accent_blue']} !important;
            background-color: transparent !important;
        }}

        /* 10. DataFrames & Tables */
        [data-testid="stDataFrame"] {{
            border: 1px solid {c['card_border']};
            border-radius: 8px;
            overflow: hidden;
        }}

        /* 11. Keyframe Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes fadeSlideUp {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-fade {{
            animation: fadeIn 0.25s ease-out;
        }}
        .animate-slide-up {{
            animation: fadeSlideUp 0.3s ease-out forwards;
        }}

        /* 12. Accessibility: Prefers-Reduced-Motion Support */
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }}
            .animate-fade, .animate-slide-up, .metric-card, .app-header, .stock-alert {{
                animation: none !important;
                transition: none !important;
                transform: none !important;
            }}
            .stButton > button:hover, .stDownloadButton > button:hover, .metric-card:hover {{
                transform: none !important;
            }}
        }}

        /* 13. Headings and Base Elements */
        h1, h2, h3, h4, h5, h6 {{
            color: {c['text_primary']};
            letter-spacing: -0.02em;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        p, span, label {{
            color: {c['text_primary']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
