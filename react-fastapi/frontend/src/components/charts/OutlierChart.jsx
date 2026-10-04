import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatNumber } from '../../utils/formatters';

export function OutlierChart({
  outliers = [],
  summary = {},
  metricLabel = 'Indicator Value',
  height = 440,
  className = '',
}) {
  const { isDark } = useTheme();

  const chartHeight = Math.max(height, Math.min(650, (outliers.length || 10) * 32 + 100));

  const plotlyData = useMemo(() => {
    if (!outliers || outliers.length === 0) return [];

    // Sort ascending for bottom-to-top horizontal bar chart
    const sorted = [...outliers].reverse();

    const countryLabels = sorted.map((d) => `${d.display_name} (${d.country_code})`);
    const values = sorted.map((d) => d.metric_value);
    const colors = sorted.map((d) =>
      d.outlier_type.includes('High') ? (isDark ? '#f43f5e' : '#e11d48') : (isDark ? '#38bdf8' : '#0284c7')
    );

    const hoverText = sorted.map(
      (d) =>
        `<b>${d.display_name} (${d.country_code})</b><br><br>` +
        `Observed Value: <b>${formatNumber(d.metric_value)}</b><br>` +
        `Outlier Classification: <b>${d.outlier_type}</b><br>` +
        `Deviation Multiple: ${d.deviation.toFixed(2)}x<br>` +
        (d.migrant_stock ? `Migrant Stock: ${formatNumber(d.migrant_stock)}<br>` : '') +
        (d.population ? `Total Population: ${formatNumber(d.population)}` : '') +
        `<extra></extra>`
    );

    const barTrace = {
      type: 'bar',
      orientation: 'h',
      x: values,
      y: countryLabels,
      text: values.map((v) => formatNumber(v)),
      textposition: 'auto',
      hoverinfo: 'text',
      hovertext: hoverText,
      marker: {
        color: colors,
        line: {
          color: isDark ? '#1e293b' : '#ffffff',
          width: 1,
        },
      },
    };

    return [barTrace];
  }, [outliers, isDark]);

  const layout = useMemo(() => {
    const upperBound = summary.upper_bound;
    const shapes = [];

    if (upperBound !== undefined && upperBound !== null && !isNaN(upperBound)) {
      shapes.push({
        type: 'line',
        x0: upperBound,
        x1: upperBound,
        y0: -0.5,
        y1: (outliers.length || 1) - 0.5,
        line: {
          color: '#f59e0b',
          width: 2,
          dash: 'dash',
        },
      });
    }

    return getPlotlyLayout(isDark, {
      height: chartHeight,
      margin: { l: 180, r: 40, t: 30, b: 60, pad: 4 },
      xaxis: {
        automargin: true,
        title: { text: metricLabel, standoff: 16 },
        showgrid: true,
        zeroline: true,
      },
      yaxis: {
        automargin: true,
        showgrid: false,
        tickfont: { size: 11, family: 'Inter, sans-serif' },
      },
      shapes,
      showlegend: false,
    });
  }, [isDark, chartHeight, metricLabel, summary, outliers.length]);

  return (
    <div className={`outlier-chart-container ${className}`} style={{ width: '100%', minHeight: chartHeight }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height: chartHeight }} />
    </div>
  );
}
