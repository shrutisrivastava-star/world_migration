import React, { useMemo } from 'react';
import { PlotlyChart } from './PlotlyChart';
import { useTheme } from '../../hooks/useTheme';
import { getPlotlyLayout } from '../../utils/chartTheme';
import { formatNumber } from '../../utils/formatters';

const COMMUNITY_PALETTE = [
  '#0284c7', // Sky
  '#0d9488', // Teal
  '#f59e0b', // Amber
  '#10b981', // Emerald
  '#f43f5e', // Rose
  '#8b5cf6', // Violet
  '#3b82f6', // Blue
  '#eab308', // Yellow
  '#ec4899', // Pink
  '#6366f1', // Indigo
  '#14b8a6', // Cyan
  '#f97316', // Orange
];

export function CommunityGraph({
  nodes = [],
  edges = [],
  communities = [],
  selectedCommunityId = null,
  height = 580,
  className = '',
}) {
  const { isDark } = useTheme();

  const commNameMap = useMemo(() => {
    const map = {};
    communities.forEach((c) => {
      map[c.community_id] = c.community_name || `Community ${c.community_id}`;
    });
    return map;
  }, [communities]);

  const plotlyData = useMemo(() => {
    if (!nodes || nodes.length === 0) return [];

    // 1. Edge Line Traces
    const edgeX = [];
    const edgeY = [];

    edges.forEach((e) => {
      edgeX.push(e.x0, e.x1, null);
      edgeY.push(e.y0, e.y1, null);
    });

    const edgeLineTrace = {
      type: 'scatter',
      mode: 'lines',
      x: edgeX,
      y: edgeY,
      line: {
        width: 0.8,
        color: isDark ? 'rgba(255, 255, 255, 0.14)' : 'rgba(0, 0, 0, 0.10)',
      },
      hoverinfo: 'none',
      showlegend: false,
    };

    // 2. Group nodes by Community ID
    const commGroups = {};
    nodes.forEach((n) => {
      const cId = n.community_id || 1;
      if (!commGroups[cId]) {
        commGroups[cId] = [];
      }
      commGroups[cId].push(n);
    });

    const nodeTraces = Object.keys(commGroups).map((cIdStr) => {
      const cId = Number(cIdStr);
      const groupNodes = commGroups[cId];
      const color = COMMUNITY_PALETTE[(cId - 1) % COMMUNITY_PALETTE.length];
      const isSelected = selectedCommunityId === null || selectedCommunityId === cId;

      const nodeX = [];
      const nodeY = [];
      const nodeLabels = [];
      const nodeText = [];
      const nodeSizes = [];

      groupNodes.forEach((n) => {
        nodeX.push(n.x);
        nodeY.push(n.y);
        nodeLabels.push(n.country_code);

        const scaledSize = Math.max(10, Math.min(28, 10 + Math.sqrt(n.total_strength || 1000) / 350));
        nodeSizes.push(scaledSize);

        const hoverHtml =
          `<b>${n.country_name} (${n.country_code})</b><br>` +
          `Cluster: <b>${commNameMap[cId] || `Community ${cId}`}</b><br><br>` +
          `Weighted Strength: <b>${formatNumber(n.total_strength)}</b><br>` +
          `Inbound Foreign-Born: ${formatNumber(n.in_strength)}<br>` +
          `Outbound Diaspora: ${formatNumber(n.out_strength)}<br>` +
          `Corridor Degree: ${n.total_degree}` +
          `<extra></extra>`;

        nodeText.push(hoverHtml);
      });

      return {
        type: 'scatter',
        mode: 'markers+text',
        name: commNameMap[cId] || `Community ${cId}`,
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
          color: color,
          size: nodeSizes,
          opacity: isSelected ? 1.0 : 0.22,
          line: {
            width: 1.5,
            color: isDark ? '#1e293b' : '#ffffff',
          },
        },
        showlegend: true,
      };
    });

    return [edgeLineTrace, ...nodeTraces];
  }, [nodes, edges, communities, selectedCommunityId, isDark, commNameMap]);

  const layout = useMemo(() => {
    return getPlotlyLayout(isDark, {
      height: height,
      margin: { l: 24, r: 24, t: 24, b: 60 },
      xaxis: {
        showgrid: false,
        zeroline: false,
        showticklabels: false,
      },
      yaxis: {
        showgrid: false,
        zeroline: false,
        showticklabels: false,
      },
      hovermode: 'closest',
      legend: {
        font: { size: 10, color: isDark ? '#cbd5e1' : '#475569' },
        orientation: 'h',
        yanchor: 'bottom',
        y: -0.12,
        xanchor: 'center',
        x: 0.5,
      },
    });
  }, [isDark, height]);

  return (
    <div className={`community-graph-container ${className}`} style={{ width: '100%', minHeight: height }}>
      <PlotlyChart data={plotlyData} layout={layout} style={{ height }} />
    </div>
  );
}
