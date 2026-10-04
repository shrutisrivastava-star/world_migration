import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatNumber, formatPercent } from '../../utils/formatters';

const COMPARISON_COLORS = ['#0284c7', '#0d9488', '#f59e0b', '#f43f5e', '#8b5cf6'];

export function ComparisonChart({
  trajectories = [],
  metricMode = 'migrant_stock',
  height = 400,
  className = '',
}) {
  const { isDark } = useTheme();
  const isPct = metricMode === 'pct_population';

  const plotlyData = useMemo(() => {
    if (!trajectories || trajectories.length === 0) return [];

    return trajectories.map((traj, idx) => {
      const color = COMPARISON_COLORS[idx % COMPARISON_COLORS.length];
      const yVals = isPct ? traj.pct_population_history : traj.migrant_stock_history;

      return {
        type: 'scatter',
        mode: 'lines+markers',
        name: traj.country_name || traj.country_code,
        x: traj.years,
        y: yVals,
        line: {
          color,
          width: 2.5,
          shape: 'spline',
          smoothing: 0.8,
        },
        marker: {
          size: 7,
          color,
          symbol: 'circle',
          line: {
            color: isDark ? '#0f172a' : '#ffffff',
            width: 1.5,
          },
        },
        hovertemplate: `<b>${traj.country_name} (%{x})</b><br>${
          isPct ? 'Migrant % Population: %{y:.2f}%' : 'Migrant Stock: %{y:,.0f}'
        }<extra></extra>`,
      };
    });
  }, [trajectories, isPct, isDark]);

  const layout = useMemo(() => {
    return getPlotlyLayout(isDark, {
      height,
      margin: { l: 80, r: 32, t: 40, b: 65, pad: 4 },
      xaxis: {
        automargin: true,
        title: { text: 'UN DESA Census Round', standoff: 16 },
        tickmode: 'array',
        tickvals: [1990, 1995, 2000, 2005, 2010, 2015, 2020],
        showgrid: true,
      },
      yaxis: {
        automargin: true,
        title: {
          text: isPct ? 'Migrant Stock % of Population' : 'Residing Migrant Stock (People)',
          standoff: 18,
        },
        tickformat: isPct ? '.1f' : ',.0f',
        showgrid: true,
      },
      hovermode: 'x unified',
      showlegend: true,
      legend: {
        orientation: 'h',
        yanchor: 'bottom',
        y: 1.05,
        xanchor: 'center',
        x: 0.5,
        font: { size: 11, color: isDark ? '#cbd5e1' : '#475569' },
      },
    });
  }, [isDark, height, isPct]);

  return (
    <div className={`comparison-chart-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
