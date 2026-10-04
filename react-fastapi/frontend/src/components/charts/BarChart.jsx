import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatNumber, formatPercent } from '../../utils/formatters';

export function BarChart({
  categories = [],
  values = [],
  title,
  xTitle,
  yTitle,
  orientation = 'h',
  color = '#0284c7',
  height = 440,
  isPercent = false,
  className = '',
}) {
  const { isDark } = useTheme();
  const isHorizontal = orientation === 'h';

  const plotlyData = useMemo(() => {
    // For horizontal bar chart, reverse so highest is on top
    const cats = isHorizontal ? [...categories].reverse() : categories;
    const vals = isHorizontal ? [...values].reverse() : values;

    return [
      {
        type: 'bar',
        orientation: orientation,
        x: isHorizontal ? vals : cats,
        y: isHorizontal ? cats : vals,
        marker: {
          color: color,
          opacity: 0.92,
          line: {
            color: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.08)',
            width: 0.5,
          },
        },
        hovertemplate: isHorizontal
          ? `<b>%{y}</b><br>${xTitle || 'Value'}: <b>%{x:,.2f}${isPercent ? '%' : ''}</b><extra></extra>`
          : `<b>%{x}</b><br>${yTitle || 'Value'}: <b>%{y:,.2f}${isPercent ? '%' : ''}</b><extra></extra>`,
      },
    ];
  }, [categories, values, orientation, isHorizontal, color, isDark, xTitle, yTitle, isPercent]);

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
      margin: isHorizontal
        ? { l: 170, r: 32, t: title ? 44 : 20, b: 50, pad: 4 }
        : { l: 75, r: 32, t: title ? 44 : 20, b: 80, pad: 4 },
      xaxis: {
        automargin: true,
        title: xTitle ? { text: xTitle, standoff: 14 } : undefined,
        tickformat: isHorizontal && isPercent ? '.1f' : ',.0f',
      },
      yaxis: {
        automargin: true,
        title: yTitle ? { text: yTitle, standoff: 16 } : undefined,
        tickfont: { size: 11, family: 'Inter, sans-serif' },
      },
      showlegend: false,
    });
  }, [isDark, title, height, isHorizontal, xTitle, yTitle, isPercent]);

  return (
    <div className={`bar-chart-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
