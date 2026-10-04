import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatNumber } from '../../utils/formatters';

export function CorrelationChart({
  points = [],
  stats = {},
  xLabel = 'X Indicator',
  yLabel = 'Y Indicator',
  height = 480,
  className = '',
}) {
  const { isDark } = useTheme();

  const plotlyData = useMemo(() => {
    if (!points || points.length === 0) return [];

    const nodeX = [];
    const nodeY = [];
    const hoverText = [];

    points.forEach((p) => {
      nodeX.push(p.plot_x);
      nodeY.push(p.plot_y);

      const hover =
        `<b>${p.display_name} (${p.country_code})</b><br><br>` +
        `${xLabel}: <b>${formatNumber(p.x_value)}</b><br>` +
        `${yLabel}: <b>${formatNumber(p.y_value)}</b><br>` +
        (p.migrant_stock ? `Migrant Stock: ${formatNumber(p.migrant_stock)}<br>` : '') +
        (p.gdp_per_capita ? `GDP per Capita: $${formatNumber(p.gdp_per_capita)}` : '') +
        `<extra></extra>`;

      hoverText.push(hover);
    });

    const scatterTrace = {
      type: 'scatter',
      mode: 'markers',
      name: 'Nations',
      x: nodeX,
      y: nodeY,
      text: hoverText,
      hoverinfo: 'text',
      marker: {
        size: 10,
        color: isDark ? '#38bdf8' : '#0284c7',
        opacity: 0.85,
        line: {
          width: 1.5,
          color: isDark ? '#0f172a' : '#ffffff',
        },
      },
    };

    const traces = [scatterTrace];

    // Compute linear regression fit line if slope & intercept exist
    if (
      stats.slope !== undefined &&
      stats.intercept !== undefined &&
      !isNaN(stats.slope) &&
      !isNaN(stats.intercept) &&
      nodeX.length > 1
    ) {
      const minX = Math.min(...nodeX);
      const maxX = Math.max(...nodeX);
      const lineX = [minX, maxX];
      const lineY = [stats.intercept + stats.slope * minX, stats.intercept + stats.slope * maxX];

      const lineTrace = {
        type: 'scatter',
        mode: 'lines',
        name: 'Linear Regression Fit',
        x: lineX,
        y: lineY,
        line: {
          color: '#f59e0b',
          width: 2.5,
          dash: 'dash',
        },
        hoverinfo: 'none',
      };
      traces.push(lineTrace);
    }

    return traces;
  }, [points, stats, xLabel, yLabel, isDark]);

  const layout = useMemo(() => {
    return getPlotlyLayout(isDark, {
      height,
      margin: { l: 85, r: 36, t: 40, b: 70, pad: 4 },
      xaxis: {
        automargin: true,
        title: { text: xLabel, standoff: 18 },
        showgrid: true,
        zeroline: false,
      },
      yaxis: {
        automargin: true,
        title: { text: yLabel, standoff: 20 },
        showgrid: true,
        zeroline: false,
      },
      hovermode: 'closest',
      showlegend: true,
      legend: {
        x: 0.02,
        y: 0.98,
        bgcolor: isDark ? 'rgba(30, 41, 59, 0.75)' : 'rgba(255, 255, 255, 0.85)',
        bordercolor: isDark ? '#334155' : '#cbd5e1',
        borderwidth: 1,
        font: { size: 11 },
      },
    });
  }, [isDark, height, xLabel, yLabel]);

  return (
    <div className={`correlation-chart-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
