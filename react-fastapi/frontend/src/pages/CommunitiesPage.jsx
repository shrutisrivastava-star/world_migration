import React, { useState, useEffect, useContext } from 'react';
import { Users, Network, Layers, ShieldAlert, Globe, Compass, ArrowRight } from 'lucide-react';
import { AppContext, normalizeYear } from '../context/AppContext';
import { getCommunities, getCommunityDetail } from '../services/api';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/common/KPICard';
import { Select } from '../components/common/Select';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { SectionHeader } from '../components/common/SectionHeader';
import { CommunityGraph } from '../components/charts/CommunityGraph';
import { formatNumber, formatCompactNumber, formatPercent } from '../utils/formatters';

const EDGE_OPTIONS = [
  { value: '100', label: '100 Strongest Corridors' },
  { value: '150', label: '150 Strongest Corridors' },
  { value: '250', label: '250 Strongest Corridors' },
  { value: '400', label: '400 Strongest Corridors' },
];

export function CommunitiesPage() {
  const { selectedYear, setSelectedYear } = useContext(AppContext);
  const [topNEdges, setTopNEdges] = useState(150);
  const [selectedCommunityId, setSelectedCommunityId] = useState(null);
  const [communityData, setCommunityData] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState(null);

  const safeYear = normalizeYear(selectedYear);

  const fetchCommunities = async () => {
    try {
      setLoading(true);
      setError(null);
      const safeEdges = Number.isInteger(Number(topNEdges)) ? Number(topNEdges) : 150;
      const data = await getCommunities(safeYear, safeEdges);
      setCommunityData(data);
      if (data.communities && data.communities.length > 0) {
        setSelectedCommunityId(data.communities[0].community_id);
      }
    } catch (err) {
      console.error('Failed to load communities:', err);
      setError(err.message || 'Failed to detect migration communities');
    } finally {
      setLoading(false);
    }
  };

  const fetchCommunityDetail = async (cId) => {
    if (!cId) return;
    try {
      setDetailLoading(true);
      const safeEdges = Number.isInteger(Number(topNEdges)) ? Number(topNEdges) : 150;
      const data = await getCommunityDetail(cId, safeYear, safeEdges);
      setDetailData(data);
    } catch (err) {
      console.error('Failed to load community detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    fetchCommunities();
  }, [safeYear, topNEdges]);

  useEffect(() => {
    if (selectedCommunityId) {
      fetchCommunityDetail(selectedCommunityId);
    }
  }, [selectedCommunityId, safeYear, topNEdges]);

  const communityColumns = [
    { key: 'community_id', label: 'ID', width: '60px', isNumeric: true, render: (val) => <strong>#{val}</strong> },
    {
      key: 'community_name',
      label: 'Community Cluster',
      render: (val, row) => (
        <div>
          <button
            className="btn-link"
            onClick={() => setSelectedCommunityId(row.community_id)}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              color: selectedCommunityId === row.community_id ? 'var(--primary)' : 'inherit',
              fontWeight: 600,
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            {val}
          </button>
        </div>
      ),
    },
    {
      key: 'size',
      label: 'Members',
      isNumeric: true,
      render: (val) => `${val} nations`,
    },
    {
      key: 'total_migrant_stock',
      label: 'Migrant Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => formatCompactNumber(val),
    },
    {
      key: 'share_pct',
      label: 'Share of Global',
      isNumeric: true,
      isMono: true,
      render: (val) => formatPercent(val),
    },
    {
      key: 'top_anchor_countries',
      label: 'Anchor Nations',
      render: (val) => <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>{val}</span>,
    },
    {
      key: 'action',
      label: 'Action',
      width: '90px',
      render: (_, row) => (
        <button
          className={`btn ${selectedCommunityId === row.community_id ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          onClick={() => setSelectedCommunityId(row.community_id)}
          style={{ padding: '2px 10px', fontSize: 'var(--text-2xs)' }}
        >
          Inspect
        </button>
      ),
    },
  ];

  const hubColumns = [
    { key: 'rank', label: 'Rank', width: '60px', isNumeric: true, render: (_, __, idx) => <strong>#{idx + 1}</strong> },
    {
      key: 'country_name',
      label: 'Country / Sovereign State',
      render: (val, row) => (
        <span>
          <strong>{val}</strong> <span style={{ color: 'var(--text-subtle)', fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)' }}>({row.country_code})</span>
        </span>
      ),
    },
    {
      key: 'total_strength',
      label: 'Total Strength',
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
  ];

  const internalCorridorColumns = [
    { key: 'rank', label: 'Rank', width: '60px', isNumeric: true, render: (val) => <strong>#{val}</strong> },
    {
      key: 'corridor_label',
      label: 'Internal Bilateral Corridor',
      render: (val) => <strong>{val}</strong>,
    },
    {
      key: 'migrant_stock',
      label: 'Residing Migrant Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
  ];

  return (
    <PageContainer
      title="Network Modularity & Communities"
      subtitle="Modularity-based community detection identifying empirical demographic clusters in the global bilateral migrant-stock network."
      breadcrumb={['Observatory', 'Network Analysis', 'Communities']}
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
        </div>

        <div className="filter-group">
          <Select
            label="Network Backbone Cutoff:"
            value={String(topNEdges)}
            onChange={(e) => {
              const raw = e.target ? e.target.value : e;
              const parsed = parseInt(raw, 10);
              setTopNEdges(isNaN(parsed) ? 150 : parsed);
            }}
            options={EDGE_OPTIONS}
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Executing Louvain community detection algorithm on migration network..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchCommunities} />
      ) : communityData ? (
        <>
          {/* KPI Cards */}
          <div className="kpi-grid">
            <KPICard
              title="Detected Communities"
              value={communityData.num_communities}
              subtitle="Discrete structural clusters"
              icon={Users}
              accent="blue"
              isMono={true}
            />
            <KPICard
              title="Modularity Score (Q)"
              value={communityData.modularity.toFixed(3)}
              subtitle="Partition quality metric [0-1]"
              icon={Layers}
              accent="teal"
              isMono={true}
            />
            <KPICard
              title="Largest Community Size"
              value={`${communityData.largest_community_size} nations`}
              subtitle="Most expansive country cluster"
              icon={Globe}
              accent="amber"
              isMono={true}
            />
            <KPICard
              title="Largest Community Share"
              value={formatPercent(communityData.largest_community_share)}
              subtitle="Share of network migrant stock"
              icon={Network}
              accent="emerald"
              isMono={true}
            />
          </div>

          {/* Interactive Community Graph */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title={`Empirical Community Cluster Network (${safeYear})`}
              subtitle="Sovereign nations colored by detected modularity cluster ID. Click a community in the summary table to highlight members."
              badge={`${safeYear}`}
            />
            <CommunityGraph
              nodes={communityData.nodes}
              edges={communityData.edges}
              communities={communityData.communities}
              selectedCommunityId={selectedCommunityId}
              height={580}
            />
          </div>

          {/* Summary Table */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title="Detected Migration Communities Leaderboard"
              subtitle="All detected community partitions ranked by member size and cumulative migrant stock."
            />
            <DataTable columns={communityColumns} data={communityData.communities} />
          </div>

          {/* Selected Community Detail Panel */}
          {detailLoading ? (
            <LoadingState message="Loading community details..." />
          ) : detailData ? (
            <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
              <SectionHeader
                title={`Deep Dive: ${detailData.community_name}`}
                subtitle={`Analyzing ${detailData.size} member countries and top internal migration corridors.`}
                badge={`Cluster #${detailData.community_id}`}
              />

              {/* Member Pills */}
              <div style={{ marginBottom: 'var(--space-5)' }}>
                <h5 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-xs)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Member Countries ({detailData.size})
                </h5>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {detailData.member_countries.map((name, i) => (
                    <span key={i} className="badge badge-subtle" style={{ fontSize: 'var(--text-xs)', padding: '4px 10px' }}>
                      {name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Leading Hubs in Community */}
              <div style={{ marginBottom: 'var(--space-5)' }}>
                <SectionHeader
                  title="Leading Anchor Nations in this Community"
                  subtitle="Top nodes within this demographic cluster by bilateral strength and degree"
                />
                <DataTable columns={hubColumns} data={detailData.top_hubs} />
              </div>

              {/* Internal Corridors */}
              {detailData.internal_corridors && detailData.internal_corridors.length > 0 && (
                <div>
                  <SectionHeader
                    title="Top Internal Bilateral Corridors"
                    subtitle="Major intra-community migration linkages"
                  />
                  <DataTable columns={internalCorridorColumns} data={detailData.internal_corridors} />
                </div>
              )}
            </div>
          ) : null}

          {/* Methodological Callout */}
          <div className="methodology-callout">
            <ShieldAlert className="methodology-callout-icon" />
            <div>
              <div className="methodology-callout-title">Methodological & Scientific Definitions</div>
              <div className="methodology-callout-text">
                Community detection partitions are derived through modularity optimization (Louvain algorithm)
                on an undirected transformation of the UN DESA bilateral migrant-stock network where reciprocal weights
                are summed. Community membership reflects empirical demographic clustering and does NOT indicate
                political alliances, trade unions, or causal migration policy blocs.
              </div>
            </div>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
