import React, { useState, useEffect, useContext } from 'react';
import { ArrowRightLeft, TrendingUp, BarChart3, Search, Activity, ShieldAlert, Award } from 'lucide-react';
import { AppContext, normalizeYear } from '../context/AppContext';
import { getCorridorOverview, getCorridorDetail } from '../services/api';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/common/KPICard';
import { Select } from '../components/common/Select';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { SectionHeader } from '../components/common/SectionHeader';
import { StatusBadge } from '../components/common/StatusBadge';
import { LineChart } from '../components/charts/LineChart';
import { formatNumber, formatCompactNumber, formatPercent } from '../utils/formatters';

const TOP_N_OPTIONS = [
  { value: '10', label: 'Top 10 Corridors' },
  { value: '25', label: 'Top 25 Corridors' },
  { value: '50', label: 'Top 50 Corridors' },
  { value: '100', label: 'Top 100 Corridors' },
];

export function CorridorsPage() {
  const { selectedYear, setSelectedYear, countries } = useContext(AppContext);
  const [topN, setTopN] = useState(10);
  const [overviewData, setOverviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Corridor Deep-Dive state
  const [origin, setOrigin] = useState('MEX');
  const [destination, setDestination] = useState('USA');
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const safeYear = normalizeYear(selectedYear);

  const countryOptions = React.useMemo(() => {
    if (!countries || countries.length === 0) return [];
    return countries.map((c) => ({
      value: c.country_code,
      label: `${c.display_name} (${c.country_code})`,
    }));
  }, [countries]);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const safeN = Number.isInteger(Number(topN)) ? Number(topN) : 10;
      const data = await getCorridorOverview(safeYear, safeN);
      setOverviewData(data);
    } catch (err) {
      console.error('Failed to load corridor overview:', err);
      setError(err.message || 'Failed to load corridor overview');
    } finally {
      setLoading(false);
    }
  };

  const fetchDetail = async () => {
    if (!origin || !destination) return;
    try {
      setDetailLoading(true);
      const data = await getCorridorDetail(origin, destination, safeYear);
      setDetailData(data);
    } catch (err) {
      console.error('Failed to load corridor detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, [safeYear, topN]);

  useEffect(() => {
    fetchDetail();
  }, [origin, destination, safeYear]);

  // Handle selecting a row from the top table
  const handleSelectCorridorRow = (row) => {
    if (row && row.origin_code && row.destination_code) {
      setOrigin(row.origin_code);
      setDestination(row.destination_code);
    }
  };

  // Concentration chart series
  const concentrationSeries = React.useMemo(() => {
    if (!overviewData || !overviewData.concentration_trend) return [];
    const trend = overviewData.concentration_trend;
    return [
      {
        name: 'Top 10 Corridors Share (%)',
        x: trend.map((t) => t.year),
        y: trend.map((t) => t.top_10_corridor_share),
        color: '#0284c7',
      },
      {
        name: 'Top 25 Corridors Share (%)',
        x: trend.map((t) => t.year),
        y: trend.map((t) => t.top_25_corridor_share),
        color: '#0d9488',
      },
      {
        name: 'Top 50 Corridors Share (%)',
        x: trend.map((t) => t.year),
        y: trend.map((t) => t.top_50_corridor_share),
        color: '#f59e0b',
      },
    ];
  }, [overviewData]);

  // Corridor Trajectory Series
  const trajectorySeries = React.useMemo(() => {
    if (!detailData || !detailData.history) return [];
    return [
      {
        name: `${detailData.corridor_label} (Stock)`,
        x: detailData.history.map((h) => h.year),
        y: detailData.history.map((h) => h.migrant_stock),
        color: '#0284c7',
      },
    ];
  }, [detailData]);

  const corridorColumns = [
    { key: 'rank', label: 'Rank', width: '70px', isNumeric: true, render: (val) => <strong>#{val}</strong> },
    {
      key: 'corridor_label',
      label: 'Bilateral Corridor',
      render: (val, row) => (
        <button
          className="btn-link"
          onClick={() => handleSelectCorridorRow(row)}
          style={{
            background: 'none',
            border: 'none',
            padding: 0,
            color: 'var(--primary)',
            fontWeight: 600,
            cursor: 'pointer',
            textAlign: 'left',
          }}
        >
          {row.origin_display_name} → {row.dest_display_name}
        </button>
      ),
    },
    {
      key: 'migrant_stock',
      label: 'Residing Migrant Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
    {
      key: 'share_of_total',
      label: 'Share of Global Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => formatPercent(val),
    },
    {
      key: 'origin_code',
      label: 'Origin ISO3',
      render: (val) => <span className="badge badge-subtle">{val}</span>,
    },
    {
      key: 'destination_code',
      label: 'Destination ISO3',
      render: (val) => <span className="badge badge-subtle">{val}</span>,
    },
  ];

  const getStatusVariant = (classification = '') => {
    if (classification.includes('Emerging')) return 'success';
    if (classification.includes('Persistent')) return 'primary';
    if (classification.includes('Declining')) return 'danger';
    return 'neutral';
  };

  return (
    <PageContainer
      title="Bilateral Corridor Intelligence & Concentration"
      subtitle="Longitudinal analysis of global migration corridors, cumulative stock concentration trends, and bilateral growth trajectories across UN DESA census rounds."
      breadcrumb={['Observatory', 'Network Analysis', 'Corridor Analysis']}
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
            label="Leaderboard Depth:"
            value={String(topN)}
            onChange={(e) => {
              const raw = e.target ? e.target.value : e;
              const parsed = parseInt(raw, 10);
              setTopN(isNaN(parsed) ? 10 : parsed);
            }}
            options={TOP_N_OPTIONS}
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Calculating bilateral corridor metrics and concentration indices..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchOverview} />
      ) : overviewData ? (
        <>
          {/* KPI Cards */}
          <div className="kpi-grid">
            <KPICard
              title="Active Bilateral Corridors"
              value={overviewData.total_corridors}
              subtitle="Distinct origin-destination pairs (> 0)"
              icon={ArrowRightLeft}
              accent="blue"
              isMono={true}
            />
            <KPICard
              title="Largest Global Corridor"
              value={overviewData.top_corridor.split('(')[0].trim()}
              subtitle={overviewData.top_corridor.includes('(') ? overviewData.top_corridor.split('(')[1].replace(')', '') : 'Top single bilateral pair'}
              icon={Award}
              accent="amber"
            />
            <KPICard
              title="Top Corridor Stock"
              value={formatCompactNumber(overviewData.top_corridor_stock)}
              subtitle="Residing foreign-born population"
              icon={Activity}
              accent="teal"
              isMono={true}
            />
            <KPICard
              title="Top 10 Corridors Share"
              value={formatPercent(overviewData.top_10_share)}
              subtitle="Share of total global bilateral stock"
              icon={TrendingUp}
              accent="emerald"
              isMono={true}
            />
          </div>

          {/* Top Corridors Leaderboard */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title={`Top ${topN} Global Bilateral Corridors (${safeYear})`}
              subtitle="Ranked by mid-year foreign-born migrant stock residing in destination from specified origin."
              badge={`${safeYear}`}
            />
            <DataTable columns={corridorColumns} data={overviewData.top_corridors} />
          </div>

          {/* Longitudinal Concentration Trend Line Chart */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title="Global Corridor Concentration Evolution (1990–2020)"
              subtitle="Cumulative percentage share of global migrant stock held by the Top 10, Top 25, and Top 50 corridors across 7 UN DESA census rounds."
              badge="1990–2020 Concentration"
            />
            <LineChart
              series={concentrationSeries}
              height={380}
              yAxisTitle="Share of Global Migrant Stock (%)"
              xAxisTitle="UN DESA Census Round"
              isPercent={true}
            />
          </div>

          {/* Corridor Deep-Dive & Trajectory Inspector */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title="Bilateral Corridor Deep-Dive & Trajectory Inspector"
              subtitle="Select origin and destination countries to analyze 30-year longitudinal stock evolution and growth classification."
              badge="Trajectory Dossier"
            />

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: 'var(--space-4)',
                marginBottom: 'var(--space-5)',
              }}
            >
              <Select
                label="Origin Country:"
                value={origin}
                onChange={(e) => setOrigin(e.target ? e.target.value : e)}
                options={countryOptions}
              />
              <Select
                label="Destination Country:"
                value={destination}
                onChange={(e) => setDestination(e.target ? e.target.value : e)}
                options={countryOptions}
              />
            </div>

            {detailLoading ? (
              <LoadingState message="Loading corridor trajectory..." />
            ) : detailData ? (
              <div>
                {/* Detail Summary Cards */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                    gap: 'var(--space-3)',
                    marginBottom: 'var(--space-5)',
                  }}
                >
                  <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                    <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Corridor</span>
                    <h4 style={{ margin: '4px 0 0 0', fontSize: 'var(--text-sm)' }}>{detailData.corridor_label}</h4>
                  </div>

                  <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                    <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>{safeYear} Stock</span>
                    <h4 style={{ margin: '4px 0 0 0', fontSize: 'var(--text-base)', color: 'var(--primary)', fontFamily: 'var(--font-mono)' }}>
                      {detailData.current_stock ? formatNumber(detailData.current_stock) : 'No Data'}
                    </h4>
                  </div>

                  <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                    <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Global Rank</span>
                    <h4 style={{ margin: '4px 0 0 0', fontSize: 'var(--text-base)', fontFamily: 'var(--font-mono)' }}>
                      {detailData.global_rank ? `#${detailData.global_rank}` : 'N/A'}
                    </h4>
                  </div>

                  <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                    <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>5-Year Growth</span>
                    <h4 style={{ margin: '4px 0 0 0', fontSize: 'var(--text-base)', fontFamily: 'var(--font-mono)' }}>
                      {detailData.pct_change_5yr !== null && detailData.pct_change_5yr !== undefined
                        ? `${detailData.pct_change_5yr >= 0 ? '+' : ''}${detailData.pct_change_5yr.toFixed(1)}%`
                        : 'N/A'}
                    </h4>
                  </div>

                  <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                    <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Classification</span>
                    <div style={{ marginTop: '4px' }}>
                      <StatusBadge
                        status={getStatusVariant(detailData.classification)}
                        label={detailData.classification}
                      />
                    </div>
                  </div>
                </div>

                {/* Corridor Trajectory Line Chart */}
                {detailData.history && detailData.history.length > 0 && (
                  <LineChart
                    series={trajectorySeries}
                    height={340}
                    yAxisTitle="Residing Migrant Stock (People)"
                    xAxisTitle="UN DESA Census Round"
                  />
                )}
              </div>
            ) : null}
          </div>

          {/* Methodological Callout */}
          <div className="methodology-callout">
            <ShieldAlert className="methodology-callout-icon" />
            <div>
              <div className="methodology-callout-title">Methodological & Scientific Definitions</div>
              <div className="methodology-callout-text">
                Bilateral migration corridors reflect accumulated mid-year foreign-born migrant stocks residing in
                the destination nation as documented in UN DESA census rounds. Corridor trajectory classifications
                are deterministic mathematical thresholds based on 5-year intercensal stock growth and volume scale.
              </div>
            </div>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
