import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyGeoLayout } from '../../utils/chartTheme';
import { formatNumber, formatPercent, formatCurrency } from '../../utils/formatters';

export function ChoroplethMap({
  data = [],
  metricName = 'Migrant Stock',
  height = 560,
  className = '',
}) {
  const { isDark } = useTheme();

  const { locations, zValues, hoverTexts } = useMemo(() => {
    const locs = [];
    const zs = [];
    const texts = [];

    data.forEach((item) => {
      if (!item.country_code) return;
      locs.push(item.country_code);
      const val = item.metric_value !== null && item.metric_value !== undefined ? item.metric_value : null;
      zs.push(val);

      const popFormatted = item.population ? formatNumber(item.population) : 'N/A';
      const stockFormatted = item.migrant_stock ? formatNumber(item.migrant_stock) : 'N/A';
      const shareFormatted = item.migrant_stock_pct_population !== null ? formatPercent(item.migrant_stock_pct_population) : 'N/A';
      const gdpFormatted = item.gdp_per_capita !== null ? formatCurrency(item.gdp_per_capita) : 'N/A';

      const hoverHtml = `<b>${item.display_name}</b> (${item.country_code})<br><br>` +
        `<b>${metricName}:</b> ${val !== null ? (metricName.includes('%') ? formatPercent(val) : formatNumber(val)) : 'N/A'}<br>` +
        `<b>Migrant Stock:</b> ${stockFormatted}<br>` +
        `<b>Share of Pop:</b> ${shareFormatted}<br>` +
        `<b>Population:</b> ${popFormatted}<br>` +
        `<b>GDP per Capita:</b> ${gdpFormatted}` +
        `<extra></extra>`;

      texts.push(hoverHtml);
    });

    return { locations: locs, zValues: zs, hoverTexts: texts };
  }, [data, metricName]);

  const plotlyData = useMemo(() => {
    return [
      {
        type: 'choropleth',
        locations: locations,
        locationmode: 'ISO-3',
        z: zValues,
        text: hoverTexts,
        hoverinfo: 'text',
        colorscale: isDark
          ? [
              [0, '#0f172a'],
              [0.2, '#0369a1'],
              [0.5, '#0ea5e9'],
              [0.8, '#14b8a6'],
              [1, '#34d399'],
            ]
          : [
              [0, '#e0f2fe'],
              [0.2, '#38bdf8'],
              [0.5, '#0284c7'],
              [0.8, '#0f766e'],
              [1, '#064e3b'],
            ],
        colorbar: {
          title: {
            text: metricName,
            font: {
              size: 11,
              color: isDark ? '#cbd5e1' : '#475569',
            },
          },
          thickness: 14,
          len: 0.7,
          x: 0.98,
          y: 0.5,
          tickfont: {
            size: 10,
            color: isDark ? '#94a3b8' : '#64748b',
          },
        },
        marker: {
          line: {
            color: isDark ? '#1e293b' : '#ffffff',
            width: 0.6,
          },
        },
      },
    ];
  }, [locations, zValues, hoverTexts, isDark, metricName]);

  const layout = useMemo(() => {
    return getPlotlyGeoLayout(isDark, {
      height: height,
    });
  }, [isDark, height]);

  return (
    <div className={`choropleth-map-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
