import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout, CHART_PALETTE } from '../../utils/chartTheme';
import { formatNumber, formatPercent, formatCurrency } from '../../utils/formatters';

export function LineChart({
  series = [],
  title,
  xTitle = 'Census Round',
  yTitle,
  xAxisTitle,
  yAxisTitle,
  height = 380,
  isPercent = false,
  isCurrency = false,
  showMarkers = true,
  className = '',
}) {
  const { isDark } = useTheme();

  const finalXTitle = xAxisTitle || xTitle;
  const finalYTitle = yAxisTitle || yTitle;

  const plotlyData = useMemo(() => {
    return series.map((s, idx) => {
      const color = s.color || CHART_PALETTE[idx % CHART_PALETTE.length];
      return {
        type: 'scatter',
        mode: showMarkers ? 'lines+markers' : 'lines',
        name: s.name,
        x: s.x,
        y: s.y,
        line: {
          color: color,
          width: 2.5,
          dash: s.lineDash || 'solid',
          shape: 'spline',
          smoothing: 0.8,
        },
        marker: {
          size: 7,
          color: color,
          symbol: 'circle',
          line: {
            color: isDark ? '#0f172a' : '#ffffff',
            width: 1.5,
          },
        },
        hovertemplate:
          `<b>${s.name}</b><br>` +
          `${finalXTitle}: %{x}<br>` +
          `${finalYTitle || 'Value'}: <b>%{y:,.2f}${isPercent ? '%' : ''}</b><extra></extra>`,
      };
    });
  }, [series, showMarkers, finalXTitle, finalYTitle, isPercent, isDark]);

  const layout = useMemo(() => {
    return getPlotlyLayout(isDark, {
      title: title
        ? {
            text: title,
            font: { size: 14, color: isDark ? '#f8fafc' : '#0f172a', weight: 600 },
            x: 0.02,
            xanchor: 'left',
          }
        : undefined,
      height: height,
      margin: {
        l: 80,
        r: 32,
        t: title ? 48 : series.length > 1 ? 40 : 24,
        b: 65,
        pad: 4,
      },
      xaxis: {
        automargin: true,
        title: finalXTitle ? { text: finalXTitle, standoff: 16 } : undefined,
        tickmode: 'array',
        tickvals: [1990, 1995, 2000, 2005, 2010, 2015, 2020],
      },
      yaxis: {
        automargin: true,
        title: finalYTitle ? { text: finalYTitle, standoff: 18 } : undefined,
        tickformat: isPercent ? '.1f' : isCurrency ? '$,.0f' : ',.0f',
      },
      legend: {
        orientation: 'h',
        yanchor: 'bottom',
        y: 1.02,
        xanchor: 'right',
        x: 1,
        font: { size: 11, color: isDark ? '#cbd5e1' : '#475569' },
      },
      showlegend: series.length > 1,
    });
  }, [isDark, title, height, finalXTitle, finalYTitle, isPercent, isCurrency, series.length]);

  return (
    <div className={`line-chart-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
