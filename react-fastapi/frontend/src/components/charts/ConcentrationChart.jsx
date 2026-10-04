import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatPercent } from '../../utils/formatters';

export function ConcentrationChart({
  destination = {},
  origin = {},
  height = 360,
  className = '',
}) {
  const { isDark } = useTheme();

  const plotlyData = useMemo(() => {
    const categories = ['Top 5 Nations', 'Top 10 Nations', 'Top 25 Nations'];

    const destShares = [
      destination.top_5_share || 0,
      destination.top_10_share || 0,
      destination.top_25_share || 0,
    ];

    const origShares = [
      origin.top_5_origin_share || 0,
      origin.top_10_origin_share || 0,
      origin.top_25_origin_share || 0,
    ];

    const destTrace = {
      type: 'bar',
      name: 'Destination Host Concentration (%)',
      x: categories,
      y: destShares,
      text: destShares.map((v) => formatPercent(v)),
      textposition: 'auto',
      marker: {
        color: isDark ? '#38bdf8' : '#0284c7',
        line: {
          color: isDark ? '#1e293b' : '#ffffff',
          width: 1,
        },
      },
    };

    const origTrace = {
      type: 'bar',
      name: 'Origin Diaspora Concentration (%)',
      x: categories,
      y: origShares,
      text: origShares.map((v) => formatPercent(v)),
      textposition: 'auto',
      marker: {
        color: isDark ? '#2dd4bf' : '#0d9488',
        line: {
          color: isDark ? '#1e293b' : '#ffffff',
          width: 1,
        },
      },
    };

    return [destTrace, origTrace];
  }, [destination, origin, isDark]);

  const layout = useMemo(() => {
    return getPlotlyLayout(isDark, {
      height,
      barmode: 'group',
      margin: { l: 75, r: 24, t: 40, b: 60, pad: 4 },
      xaxis: {
        automargin: true,
        title: { text: 'Cumulative Demographic Segment', standoff: 14 },
        showgrid: false,
      },
      yaxis: {
        automargin: true,
        title: { text: 'Share of Total Global Stock (%)', standoff: 16 },
        range: [0, Math.max(100, Math.max(...(destination.top_25_share ? [destination.top_25_share] : [60])) + 10)],
        showgrid: true,
        tickformat: '.0f',
      },
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
  }, [isDark, height, destination.top_25_share]);

  return (
    <div className={`concentration-chart-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
