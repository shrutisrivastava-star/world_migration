/**
 * Universal Plotly Theme & Layout Generator for Light and Dark Modes.
 * Formulated with generous margins, crisp axis label standoff, and automated collision prevention.
 */

export const CHART_PALETTE = [
  '#0284c7', // Sky blue
  '#0d9488', // Teal
  '#f59e0b', // Amber
  '#10b981', // Emerald
  '#f43f5e', // Rose
  '#8b5cf6', // Violet
  '#3b82f6', // Blue
  '#eab308', // Yellow
  '#ec4899', // Pink
  '#06b6d4', // Cyan
];

/**
 * Standard Cartesian Chart Layout
 */
export function getPlotlyLayout(isDark = false, customLayout = {}) {
  const textColor = isDark ? '#f8fafc' : '#0f172a';
  const textMuted = isDark ? '#94a3b8' : '#475569';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
  const zeroLineColor = isDark ? 'rgba(255, 255, 255, 0.16)' : 'rgba(0, 0, 0, 0.12)';
  const bgColor = 'rgba(0, 0, 0, 0)';

  return {
    autosize: true,
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: {
      family: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      size: 12,
      color: textColor,
    },
    // Standard generous margins to ensure zero label collision
    margin: {
      l: 80,
      r: 32,
      t: customLayout.title ? 50 : 28,
      b: 70,
      pad: 6,
      ...(customLayout.margin || {}),
    },
    xaxis: {
      automargin: true,
      gridcolor: gridColor,
      zerolinecolor: zeroLineColor,
      tickfont: { color: textMuted, size: 11, family: 'Inter, sans-serif' },
      title: {
        font: { color: textColor, size: 12, weight: 600 },
        standoff: 16,
      },
      ...(customLayout.xaxis || {}),
    },
    yaxis: {
      automargin: true,
      gridcolor: gridColor,
      zerolinecolor: zeroLineColor,
      tickfont: { color: textMuted, size: 11, family: 'Inter, sans-serif' },
      title: {
        font: { color: textColor, size: 12, weight: 600 },
        standoff: 18,
      },
      ...(customLayout.yaxis || {}),
    },
    hoverlabel: {
      bgcolor: isDark ? '#1e293b' : '#ffffff',
      bordercolor: isDark ? '#334155' : '#cbd5e1',
      font: {
        family: 'Inter, sans-serif',
        size: 12,
        color: isDark ? '#f8fafc' : '#0f172a',
      },
    },
    legend: {
      font: { color: textColor, size: 11 },
      orientation: 'h',
      yanchor: 'bottom',
      y: 1.04,
      xanchor: 'right',
      x: 1,
      bgcolor: 'rgba(0,0,0,0)',
      ...(customLayout.legend || {}),
    },
    ...customLayout,
  };
}

/**
 * Geographic Choropleth Layout
 */
export function getPlotlyGeoLayout(isDark = false, customLayout = {}) {
  const base = getPlotlyLayout(isDark, customLayout);
  const landColor = isDark ? '#1e293b' : '#f1f5f9';
  const oceanColor = isDark ? '#080c14' : '#e2e8f0';
  const coastColor = isDark ? '#334155' : '#cbd5e1';
  const countryColor = isDark ? '#475569' : '#94a3b8';

  return {
    ...base,
    margin: { l: 0, r: 0, t: 10, b: 0, ...(customLayout.margin || {}) },
    geo: {
      showframe: false,
      showcoastlines: true,
      coastlinecolor: coastColor,
      showcountries: true,
      countrycolor: countryColor,
      countrywidth: 0.7,
      showocean: true,
      oceancolor: oceanColor,
      showlakes: true,
      lakecolor: oceanColor,
      showland: true,
      landcolor: landColor,
      bgcolor: 'rgba(0,0,0,0)',
      projection: {
        type: 'natural earth',
      },
      ...(customLayout.geo || {}),
    },
  };
}

/**
 * Default Plotly Config
 */
export function getPlotlyConfig() {
  return {
    responsive: true,
    displayModeBar: false,
    scrollZoom: false,
  };
}
