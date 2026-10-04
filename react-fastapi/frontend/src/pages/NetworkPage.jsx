import React, { useState, useEffect, useContext } from 'react';
import { Share2, Globe, GitBranch, ShieldAlert, Cpu } from 'lucide-react';
import { AppContext, normalizeYear } from '../context/AppContext';
import { getNetworkOverview } from '../services/api';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/common/KPICard';
import { Select } from '../components/common/Select';
import { Tabs } from '../components/common/Tabs';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { SectionHeader } from '../components/common/SectionHeader';
import { NetworkGraph } from '../components/charts/NetworkGraph';
import { formatNumber, formatCompactNumber } from '../utils/formatters';

const METRIC_OPTIONS = [
  { value: 'total_strength', label: 'Weighted Strength (Total Volume)' },
  { value: 'betweenness_centrality', label: 'Betweenness Centrality (Bridge Hubs)' },
  { value: 'total_degree', label: 'Total Degree (Total Corridors)' },
  { value: 'pagerank', label: 'PageRank Score (Influence)' },
];

const LAYOUT_OPTIONS = [
  { value: 'Spring', label: 'Force-Directed Layout (Spring)' },
  { value: 'Circular', label: 'Circular Concentric Layout' },
];

const EDGE_OPTIONS = [
  { value: '50', label: 'Top 50 Corridors' },
  { value: '100', label: 'Top 100 Corridors' },
  { value: '250', label: 'Top 250 Corridors' },
  { value: '500', label: 'Top 500 Corridors' },
];

export function NetworkPage() {
  const { selectedYear, setSelectedYear } = useContext(AppContext);
  const [topNEdges, setTopNEdges] = useState(100);
  const [layoutType, setLayoutType] = useState('Spring');
  const [nodeMetric, setNodeMetric] = useState('total_strength');
  const [rankingTab, setRankingTab] = useState('strength');
  const [networkData, setNetworkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const safeYear = normalizeYear(selectedYear);

  const fetchNetwork = async () => {
    try {
      setLoading(true);
      setError(null);
      const safeEdges = Number.isInteger(Number(topNEdges)) ? Number(topNEdges) : 100;
      const data = await getNetworkOverview(safeYear, safeEdges);
      setNetworkData(data);
    } catch (err) {
      console.error('Failed to load migration network:', err);
      setError(err.message || 'Failed to construct migration network graph');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNetwork();
  }, [safeYear, topNEdges]);

  // Rankings table data based on active tab
  const getRankedNodes = () => {
    if (!networkData || !networkData.nodes) return [];
    const copy = [...networkData.nodes];
    if (rankingTab === 'betweenness') {
      copy.sort((a, b) => b.betweenness_centrality - a.betweenness_centrality);
    } else if (rankingTab === 'pagerank') {
      copy.sort((a, b) => b.pagerank - a.pagerank);
    } else if (rankingTab === 'degree') {
      copy.sort((a, b) => b.total_degree - a.total_degree);
    } else {
      copy.sort((a, b) => b.total_strength - a.total_strength);
    }
    return copy.slice(0, 15).map((n, idx) => ({ ...n, rank: idx + 1 }));
  };

  const hubColumns = [
    { key: 'rank', label: 'Rank', width: '70px', render: (val) => <strong>#{val}</strong> },
    {
      key: 'country_name',
      label: 'Country / Sovereign State',
      render: (val, row) => (
        <div>
          <span style={{ fontWeight: 'var(--weight-semibold)' }}>{val}</span>
          <span style={{ color: 'var(--text-subtle)', fontSize: 'var(--text-xs)', marginLeft: '6px', fontFamily: 'var(--font-mono)' }}>
            ({row.country_code})
          </span>
        </div>
      ),
    },
    {
      key: 'total_strength',
      label: 'Weighted Strength',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
    {
      key: 'in_strength',
      label: 'Inbound Foreign-Born',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
    {
      key: 'out_strength',
      label: 'Outbound Diaspora',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
    {
      key: 'total_degree',
      label: 'Corridors',
      isNumeric: true,
      isMono: true,
      render: (val) => `${val} pairs`,
    },
    {
      key: 'betweenness_centrality',
      label: 'Betweenness',
      isNumeric: true,
      isMono: true,
      render: (val) => val.toFixed(4),
    },
    {
      key: 'pagerank',
      label: 'PageRank',
      isNumeric: true,
      isMono: true,
      render: (val) => val.toFixed(4),
    },
  ];

  return (
    <PageContainer
      title="Migration Network Topology"
      subtitle="NetworkX graph modeling analyzing country centralities, bilateral connectivity backbone, and hub formation across UN DESA census rounds."
      breadcrumb={['Observatory', 'Network Analysis', 'Migration Network']}
    >
      {/* Control Toolbar */}
      <div className="filter-toolbar">
        <div className="filter-group">
          <Select
            label="Census Round:"
            value={String(safeYear)}
            onChange={(e) => setSelectedYear(e.target ? e.target.value : e)}
            options={[1990, 1995, 2000, 2005, 2010, 2015, 2020].map((y) => ({
              value: String(y),
              label: `${y} Round`,
            }))}
          />

          <Select
            label="Layout:"
            value={layoutType}
            onChange={(e) => setLayoutType(e.target ? e.target.value : e)}
            options={LAYOUT_OPTIONS}
          />
        </div>

        <div className="filter-group">
          <Select
            label="Node Metric:"
            value={nodeMetric}
            onChange={(e) => setNodeMetric(e.target ? e.target.value : e)}
            options={METRIC_OPTIONS}
          />

          <Select
            label="Edges:"
            value={String(topNEdges)}
            onChange={(e) => {
              const raw = e.target ? e.target.value : e;
              const parsed = parseInt(raw, 10);
              setTopNEdges(isNaN(parsed) ? 100 : parsed);
            }}
            options={EDGE_OPTIONS}
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Constructing NetworkX graph and calculating centralities..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchNetwork} />
      ) : networkData ? (
        <>
          {/* KPI Cards */}
          <div className="kpi-grid">
            <KPICard
              title="Active Country Nodes"
              value={networkData.node_count}
              subtitle="Sovereign territories connected"
              icon={Globe}
              accent="blue"
              isMono={true}
            />
            <KPICard
              title="Migration Corridors"
              value={networkData.edge_count}
              subtitle={`Top ${topNEdges} strongest edges`}
              icon={GitBranch}
              accent="teal"
              isMono={true}
            />
            <KPICard
              title="Observed Migrant Stock"
              value={formatCompactNumber(networkData.total_observed_stock)}
              subtitle="Residing foreign-born population"
              icon={Share2}
              accent="amber"
              isMono={true}
            />
            <KPICard
              title="Directed Network Density"
              value={networkData.network_density.toFixed(4)}
              subtitle="Graph connectivity ratio [0-1]"
              icon={Cpu}
              accent="emerald"
              isMono={true}
            />
          </div>

          {/* Interactive Network Graph */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title={`Interactive 2D Migration Network (${safeYear})`}
              subtitle={`Visualizing ${networkData.node_count} countries and ${networkData.edge_count} major bilateral corridors with ${layoutType} layout.`}
              badge={`${safeYear}`}
            />
            <NetworkGraph
              nodes={networkData.nodes}
              edges={networkData.edges}
              layoutType={layoutType}
              nodeSizeMetric={nodeMetric}
              nodeColorMetric={nodeMetric}
              height={580}
            />
          </div>

          {/* Network Hub Rankings */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title="Global Network Hubs & Centrality Leaderboard"
              subtitle="Top 15 countries ranked by network position, bridge intermediary role, and eigenvector influence."
            />
            <Tabs
              tabs={[
                { id: 'strength', label: 'Weighted Strength' },
                { id: 'betweenness', label: 'Betweenness Centrality' },
                { id: 'pagerank', label: 'PageRank Score' },
                { id: 'degree', label: 'Total Degree' },
              ]}
              activeTab={rankingTab}
              onChange={setRankingTab}
            />
            <div style={{ marginTop: 'var(--space-4)' }}>
              <DataTable columns={hubColumns} data={getRankedNodes()} />
            </div>
          </div>

          {/* Methodological Callout */}
          <div className="methodology-callout">
            <ShieldAlert className="methodology-callout-icon" />
            <div>
              <div className="methodology-callout-title">Methodological & Scientific Definitions</div>
              <div className="methodology-callout-text">
                Bilateral network edge weights strictly represent accumulated mid-year foreign-born migrant stocks
                estimated by the UN DESA 2020 Revision. Network connections reflect demographic residency relationships
                and do NOT represent annual migration flows, gross border crossings, or unilateral visa issuances.
              </div>
            </div>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
