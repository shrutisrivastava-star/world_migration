import React, { useEffect, useState } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import { KPICard } from '../components/common/KPICard';
import { ErrorState } from '../components/common/ErrorState';
import { Button } from '../components/common/Button';
import { LineChart } from '../components/charts/LineChart';
import { useAppContext } from '../hooks/useAppContext';
import { getGlobalTrend } from '../services/api';
import { formatNumber, formatPercent } from '../utils/formatters';
import { SCIENTIFIC_DEFINITIONS } from '../utils/scientificLabels';
import {
  Globe,
  Users,
  Flag,
  Sparkles,
  GitFork,
  ArrowRightLeft,
  Info,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';

export function OverviewPage() {
  const {
    selectedYear,
    overviewData,
    isLoadingOverview,
    overviewError,
    refreshOverview,
  } = useAppContext();

  const [globalTrendData, setGlobalTrendData] = useState([]);
  const [isLoadingTrend, setIsLoadingTrend] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadTrend() {
      setIsLoadingTrend(true);
      try {
        const res = await getGlobalTrend();
        if (isMounted && res && res.points) {
          setGlobalTrendData(res.points);
        }
      } catch (err) {
        console.error('Failed to load global trends:', err);
      } finally {
        if (isMounted) setIsLoadingTrend(false);
      }
    }
    loadTrend();
    return () => {
      isMounted = false;
    };
  }, []);

  const trendSeries = [
    {
      name: 'Global Migrant Stock',
      x: globalTrendData.map((p) => p.year),
      y: globalTrendData.map((p) => p.total_migrant_stock),
      color: '#0284c7',
    },
  ];

  return (
    <PageContainer
      title="Global Migration Overview"
      subtitle={`Executive demographic indicators & global migrant stock summary for census round ${selectedYear}`}
      breadcrumb={['Observatory', 'Executive Overview']}
      action={
        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          isLoading={isLoadingOverview || isLoadingTrend}
          onClick={refreshOverview}
          aria-label="Refresh overview metrics"
        >
          Refresh Data
        </Button>
      }
    >
      {/* Scientific Principle Callout */}
      <div className="info-banner" role="region" aria-label="UN DESA Definition">
        <Info className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Scientific Definition — UN DESA 2020 Revision</div>
          <div className="info-banner-text">
            {SCIENTIFIC_DEFINITIONS.MIGRANT_STOCK}
          </div>
        </div>
      </div>

      {/* Error State */}
      {overviewError && (
        <ErrorState
          title="Could not load overview metrics"
          message={overviewError}
          onRetry={refreshOverview}
        />
      )}

      {/* Section 1: Executive KPI Cards */}
      <SectionHeader
        title="Executive Migration Indicators"
        subtitle={`Empirical metrics computed dynamically by FastAPI backend for round ${selectedYear}`}
        badge={`${selectedYear} Census`}
      />

      <div className="kpi-grid">
        <KPICard
          title={`Global Migrant Stock (${selectedYear})`}
          value={overviewData ? formatNumber(overviewData.total_migrant_stock) : undefined}
          subtitle="Total foreign-born population residing across sovereign states"
          icon={Globe}
          accent="blue"
          isMono={true}
          isLoading={isLoadingOverview}
        />

        <KPICard
          title="Global Migrant Share"
          value={overviewData ? formatPercent(overviewData.global_migrant_pct) : undefined}
          subtitle={
            overviewData
              ? `Share of sovereign world population (${formatNumber(overviewData.total_population)})`
              : 'Share of world population'
          }
          icon={Users}
          accent="teal"
          isMono={true}
          isLoading={isLoadingOverview}
        />

        <KPICard
          title="Participating Nations"
          value={overviewData ? overviewData.num_countries : undefined}
          subtitle="Recognized sovereign states with bilateral empirical records"
          icon={Flag}
          accent="amber"
          isMono={true}
          isLoading={isLoadingOverview}
        />

        <KPICard
          title="Top Destination Country"
          value={overviewData ? overviewData.top_destination_name : undefined}
          subtitle={
            overviewData
              ? `Host to ${formatNumber(overviewData.top_destination_stock)} foreign-born residents`
              : 'Host to highest migrant stock'
          }
          icon={ArrowRightLeft}
          accent="blue"
          isLoading={isLoadingOverview}
        />

        <KPICard
          title="Highest Migrant Share (% Pop)"
          value={overviewData ? overviewData.top_share_name : undefined}
          subtitle={
            overviewData
              ? `Migrants represent ${formatPercent(overviewData.top_share_pct)} of total population`
              : 'Highest concentration'
          }
          icon={Sparkles}
          accent="emerald"
          isLoading={isLoadingOverview}
        />

        <KPICard
          title="Active Bilateral Corridors"
          value={overviewData ? overviewData.num_corridors.toLocaleString() : undefined}
          subtitle="Unique origin-to-destination corridors with > 0 migrants"
          icon={GitFork}
          accent="teal"
          isMono={true}
          isLoading={isLoadingOverview}
        />
      </div>

      {/* Section 2: Historical Longitudinal Trend Chart */}
      <div style={{ marginTop: 'var(--section-gap)' }}>
        <SectionHeader
          title="Global Migrant Stock Over Time"
          subtitle="UN DESA accumulated migrant stock across quinquennial census rounds (1990–2020)"
          badge="1990–2020 Trajectory"
        />

        <div className="card" style={{ padding: 'var(--card-padding)' }}>
          <LineChart
            series={trendSeries}
            xTitle="UN DESA Census Round"
            yTitle="Global Migrant Stock (People)"
            height={380}
          />
        </div>
      </div>
    </PageContainer>
  );
}
