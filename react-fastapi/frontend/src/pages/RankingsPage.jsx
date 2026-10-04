import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import { Select } from '../components/common/Select';
import { Button } from '../components/common/Button';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { BarChart } from '../components/charts/BarChart';
import { useAppContext } from '../hooks/useAppContext';
import { getRankings } from '../services/api';
import { RANKINGS_METRIC_OPTIONS } from '../utils/scientificLabels';
import { formatNumber, formatPercent, formatCurrency } from '../utils/formatters';
import { ArrowUpDown, Info } from 'lucide-react';

const TOP_N_OPTIONS = [
  { value: 10, label: 'Top 10' },
  { value: 25, label: 'Top 25' },
  { value: 50, label: 'Top 50' },
  { value: 100, label: 'Top 100' },
];

export function RankingsPage() {
  const { selectedYear } = useAppContext();
  const [metric, setMetric] = useState('Migrant Stock');
  const [topN, setTopN] = useState(10);
  const [ascending, setAscending] = useState(false);

  const [rankingsData, setRankingsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRankings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getRankings(selectedYear, metric, topN, ascending);
      if (res && res.rankings) {
        setRankingsData(res.rankings);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [selectedYear, metric, topN, ascending]);

  useEffect(() => {
    fetchRankings();
  }, [fetchRankings]);

  const categories = rankingsData.map((r) => r.display_name);
  const values = rankingsData.map((r) => r.metric_value || 0);

  const tableColumns = [
    { key: 'rank', label: 'Rank', isNumeric: true, width: '60px' },
    {
      key: 'display_name',
      label: 'Country / Sovereign State',
      render: (val, row) => (
        <div>
          <span style={{ fontWeight: 'var(--weight-semibold)' }}>{val}</span>
          <span style={{ marginLeft: 6, fontSize: 'var(--text-xs)', color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>
            ({row.country_code})
          </span>
        </div>
      ),
    },
    {
      key: 'metric_value',
      label: metric,
      isNumeric: true,
      isMono: true,
      render: (val) =>
        val !== null
          ? metric.includes('%')
            ? formatPercent(val)
            : metric.includes('GDP')
            ? formatCurrency(val)
            : formatNumber(val)
          : '—',
    },
    {
      key: 'migrant_stock',
      label: 'Migrant Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? formatNumber(val) : '—'),
    },
    {
      key: 'migrant_stock_pct_population',
      label: '% of Population',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? formatPercent(val) : '—'),
    },
    {
      key: 'population',
      label: 'Total Population',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? formatNumber(val) : '—'),
    },
    {
      key: 'gdp_per_capita',
      label: 'GDP per Capita',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? formatCurrency(val) : '—'),
    },
  ];

  return (
    <PageContainer
      title="Global Country Rankings"
      subtitle={`Leaderboards and sovereign state rankings by demographic indicators for round ${selectedYear}`}
      breadcrumb={['Observatory', 'Core Explorer', 'Country Rankings']}
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
          <Select
            label="Metric:"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            options={RANKINGS_METRIC_OPTIONS}
          />
          <Select
            label="Show:"
            value={topN}
            onChange={(e) => setTopN(Number(e.target.value))}
            options={TOP_N_OPTIONS}
          />
          <Button
            variant="secondary"
            size="sm"
            icon={ArrowUpDown}
            onClick={() => setAscending(!ascending)}
            title="Toggle sort order"
          >
            {ascending ? 'Lowest First' : 'Highest First'}
          </Button>
        </div>
      }
    >
      <div className="info-banner" role="region" aria-label="Ranking Note">
        <Info className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Sovereign Country Rankings</div>
          <div className="info-banner-text">
            Rankings include recognized sovereign nations with UN DESA empirical observations. Regional geographic aggregates (e.g. "World", "Europe", "Latin America") are excluded from country leaderboards to ensure scientific consistency.
          </div>
        </div>
      </div>

      {error && <ErrorState title="Could not load rankings" message={error} onRetry={fetchRankings} />}

      {/* Bar Chart Visualization */}
      <SectionHeader
        title={`Top ${topN} Countries by ${metric}`}
        subtitle={`Visual ranking representation for census round ${selectedYear}`}
        badge={`${selectedYear}`}
      />

      <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
        {isLoading ? (
          <LoadingState message={`Computing top ${topN} rankings for ${metric}...`} />
        ) : (
          <BarChart
            categories={categories}
            values={values}
            xTitle={metric}
            orientation="h"
            isPercent={metric.includes('%')}
            height={Math.max(380, topN * 30)}
          />
        )}
      </div>

      {/* Ranked Data Table */}
      <SectionHeader
        title="Complete Ranking Table"
        subtitle={`Detailed tabular records with associated demographic and socioeconomic indicators`}
      />

      <DataTable
        columns={tableColumns}
        data={rankingsData}
        isLoading={isLoading}
        emptyMessage="No sovereign country records available for the selected criteria."
      />
    </PageContainer>
  );
}
