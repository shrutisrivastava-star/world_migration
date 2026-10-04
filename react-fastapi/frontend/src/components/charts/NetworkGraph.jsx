import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatNumber } from '../../utils/formatters';

export function NetworkGraph({
  nodes = [],
  edges = [],
  layoutType = 'Spring',
  nodeSizeMetric = 'total_strength',
  nodeColorMetric = 'total_strength',
  height = 580,
  className = '',
}) {
  const { isDark } = useTheme();
  const isCircular = layoutType === 'Circular';

  const plotlyData = useMemo(() => {
    if (!nodes || nodes.length === 0) return [];

    // 1. Edge Line Traces
    const edgeX = [];
    const edgeY = [];
    const edgeHoverX = [];
    const edgeHoverY = [];
    const edgeHoverText = [];

    edges.forEach((e) => {
      const x0 = isCircular ? e.circ_x0 : e.x0;
      const y0 = isCircular ? e.circ_y0 : e.y0;
      const x1 = isCircular ? e.circ_x1 : e.x1;
      const y1 = isCircular ? e.circ_y1 : e.y1;

      edgeX.push(x0, x1, null);
      edgeY.push(y0, y1, null);

      edgeHoverX.push((x0 + x1) / 2.0);
      edgeHoverY.push((y0 + y1) / 2.0);
      edgeHoverText.push(
        `<b>${e.origin_name || e.origin_code} → ${e.destination_name || e.destination_code}</b><br>` +
        `Migrant Stock: <b>${formatNumber(e.migrant_stock)}</b>`
      );
    });

    const edgeLineTrace = {
      type: 'scatter',
      mode: 'lines',
      x: edgeX,
      y: edgeY,
      line: {
        width: 1.0,
        color: isDark ? 'rgba(56, 189, 248, 0.28)' : 'rgba(2, 132, 199, 0.24)',
      },
      hoverinfo: 'none',
      showlegend: false,
    };

    const edgeMidpointTrace = {
      type: 'scatter',
      mode: 'markers',
      x: edgeHoverX,
      y: edgeHoverY,
      text: edgeHoverText,
      hoverinfo: 'text',
      marker: {
        size: 4,
        color: 'rgba(0,0,0,0)',
      },
      showlegend: false,
    };

    // 2. Node Marker Traces
    const nodeX = [];
    const nodeY = [];
    const nodeText = [];
    const nodeLabels = [];
    const rawSizes = [];
    const nodeColors = [];

    nodes.forEach((n) => {
      const nx = isCircular ? n.circ_x : n.x;
      const ny = isCircular ? n.circ_y : n.y;

      nodeX.push(nx);
      nodeY.push(ny);
      nodeLabels.push(n.country_code);

      const valSize = n[nodeSizeMetric] !== undefined ? n[nodeSizeMetric] : n.total_strength;
      const valColor = n[nodeColorMetric] !== undefined ? n[nodeColorMetric] : n.total_strength;

      rawSizes.push(valSize);
      nodeColors.push(valColor);

      const hoverHtml =
        `<b>${n.country_name} (${n.country_code})</b><br><br>` +
        `Weighted Strength: <b>${formatNumber(n.total_strength)}</b><br>` +
        `Inbound Foreign-Born: ${formatNumber(n.in_strength)}<br>` +
        `Outbound Diaspora: ${formatNumber(n.out_strength)}<br>` +
        `Total Degree: ${n.total_degree} corridors<br>` +
        `Betweenness: ${n.betweenness_centrality.toFixed(4)}<br>` +
        `PageRank: ${n.pagerank.toFixed(4)}` +
        `<extra></extra>`;

      nodeText.push(hoverHtml);
    });

    const minS = rawSizes.length > 0 ? Math.min(...rawSizes) : 1;
    const maxS = rawSizes.length > 0 ? Math.max(...rawSizes) : 1;

    const scaledSizes = rawSizes.map((val) => {
      if (maxS > minS) {
        return 9 + 23 * ((val - minS) / (maxS - minS));
      }
      return 14;
    });

    const metricLabelMap = {
      total_strength: 'Weighted Strength',
      betweenness_centrality: 'Betweenness Centrality',
      total_degree: 'Total Degree',
      pagerank: 'PageRank',
    };

    const nodeTrace = {
      type: 'scatter',
      mode: 'markers+text',
      x: nodeX,
      y: nodeY,
      text: nodeLabels,
      textposition: 'top center',
      textfont: {
        size: 10,
        color: isDark ? '#cbd5e1' : '#334155',
        family: 'Inter, monospace',
      },
      hoverinfo: 'text',
      hovertext: nodeText,
      marker: {
        showscale: true,
        colorscale: isDark
          ? [
              [0, '#0f172a'],
              [0.2, '#0369a1'],
              [0.5, '#0ea5e9'],
              [0.8, '#14b8a6'],
              [1, '#34d399'],
            ]
          : [
              [0, '#bae6fd'],
              [0.3, '#38bdf8'],
              [0.6, '#0284c7'],
              [0.85, '#0f766e'],
              [1, '#064e3b'],
            ],
        color: nodeColors,
        size: scaledSizes,
        colorbar: {
          title: {
            text: metricLabelMap[nodeColorMetric] || 'Metric',
            font: { size: 10, color: isDark ? '#cbd5e1' : '#475569' },
          },
          thickness: 12,
          len: 0.65,
          x: 0.98,
          y: 0.5,
          tickfont: { size: 9, color: isDark ? '#94a3b8' : '#64748b' },
        },
        line: {
          width: 1.5,
          color: isDark ? '#1e293b' : '#ffffff',
        },
      },
      showlegend: false,
    };

    return [edgeLineTrace, edgeMidpointTrace, nodeTrace];
  }, [nodes, edges, isCircular, nodeSizeMetric, nodeColorMetric, isDark]);

  const layout = useMemo(() => {
    return getPlotlyLayout(isDark, {
      height: height,
      margin: { l: 24, r: 24, t: 24, b: 24 },
      xaxis: {
        showgrid: false,
        zeroline: false,
        showticklabels: false,
        autorange: true,
      },
      yaxis: {
        showgrid: false,
        zeroline: false,
        showticklabels: false,
        autorange: true,
      },
      hovermode: 'closest',
    });
  }, [isDark, height]);

  return (
    <div className={`network-graph-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
