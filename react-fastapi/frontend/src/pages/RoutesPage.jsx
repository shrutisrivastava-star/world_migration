import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import { Select } from '../components/common/Select';
import { KPICard } from '../components/common/KPICard';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { LineChart } from '../components/charts/LineChart';
import { useAppContext } from '../hooks/useAppContext';
import { getRoutes } from '../services/api';
import { formatNumber, formatPercent } from '../utils/formatters';
import { SCIENTIFIC_DEFINITIONS } from '../utils/scientificLabels';
import { GitFork, ArrowRightLeft, Users, Info } from 'lucide-react';

export function RoutesPage() {
  const { selectedYear, countries } = useAppContext();
  const [origin, setOrigin] = useState('MEX');
  const [destination, setDestination] = useState('USA');

  const [routeData, setRouteData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRoute = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getRoutes(selectedYear, origin, destination, 15);
      setRouteData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [selectedYear, origin, destination]);

  useEffect(() => {
    fetchRoute();
  }, [fetchRoute]);

  const originOptions = [
    { value: 'All', label: 'All Origins' },
    ...countries
      .filter((c) => c.country_code)
      .map((c) => ({ value: c.country_code, label: `${c.display_name} (${c.country_code})` })),
  ];

  const destOptions = [
    { value: 'All', label: 'All Destinations' },
    ...countries
      .filter((c) => c.country_code)
      .map((c) => ({ value: c.country_code, label: `${c.display_name} (${c.country_code})` })),
  ];

  // Route history trajectory series
  const historySeries = routeData && routeData.history && routeData.history.length > 0
    ? [
        {
          name: `${routeData.origin_name || origin} → ${routeData.destination_name || destination}`,
          x: routeData.history.map((h) => h.year),
          y: routeData.history.map((h) => h.migrant_stock),
          color: '#0284c7',
        },
      ]
    : [];

  const topCorridorsColumns = [
    { key: 'rank', label: 'Rank', isNumeric: true, width: '60px' },
    { key: 'corridor_label', label: 'Bilateral Corridor' },
    {
      key: 'migrant_stock',
      label: 'Migrant Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
    {
      key: 'origin_corridor_share_pct',
      label: "% of Origin's Diaspora",
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? formatPercent(val) : '—'),
    },
    {
      key: 'dest_corridor_share_pct',
      label: "% of Destination's Foreign-born",
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? formatPercent(val) : '—'),
    },
  ];

  const isSpecificRoute = origin !== 'All' && destination !== 'All';

  return (
    <PageContainer
      title="Bilateral Route Explorer"
      subtitle={`Origin-to-destination bilateral migration stock exploration for census round ${selectedYear}`}
      breadcrumb={['Observatory', 'Core Explorer', 'Route Explorer']}
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
          <Select
            label="Origin:"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            options={originOptions}
          />
          <Select
            label="Destination:"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            options={destOptions}
          />
        </div>
      }
    >
      <div className="info-banner" role="region" aria-label="Bilateral Definition">
        <Info className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Bilateral Route Definition</div>
          <div className="info-banner-text">
            {SCIENTIFIC_DEFINITIONS.BILATERAL_CORRIDORS} {SCIENTIFIC_DEFINITIONS.MIGRANT_STOCK}
          </div>
        </div>
      </div>

      {error && <ErrorState title="Could not load route data" message={error} onRetry={fetchRoute} />}

      {/* Selected Route Hero KPI */}
      {isSpecificRoute && (
        <div style={{ marginBottom: 'var(--section-gap)' }}>
          <SectionHeader
            title="Selected Route Profile"
            subtitle={`${routeData?.origin_name || origin} to ${routeData?.destination_name || destination}`}
            badge="Bilateral Pair"
          />

          <div className="kpi-grid">
            <KPICard
              title={`Migrant Stock (${selectedYear})`}
              value={routeData?.current_stock !== null && routeData?.current_stock !== undefined ? formatNumber(routeData.current_stock) : '0'}
              subtitle={`Estimated migrants from ${routeData?.origin_name || origin} residing in ${routeData?.destination_name || destination}`}
              icon={GitFork}
              accent="blue"
              isMono={true}
              isLoading={isLoading}
            />

            <KPICard
              title="Origin Diaspora Share"
              value={
                routeData?.history?.find((h) => h.year === selectedYear)?.origin_corridor_share_pct !== null &&
                routeData?.history?.find((h) => h.year === selectedYear)?.origin_corridor_share_pct !== undefined
                  ? formatPercent(routeData.history.find((h) => h.year === selectedYear).origin_corridor_share_pct)
                  : 'N/A'
              }
              subtitle={`Share of ${routeData?.origin_name || origin}'s total global emigrant diaspora`}
              icon={Users}
              accent="teal"
              isMono={true}
              isLoading={isLoading}
            />

            <KPICard
              title="Destination Foreign-Born Share"
              value={
                routeData?.history?.find((h) => h.year === selectedYear)?.dest_corridor_share_pct !== null &&
                routeData?.history?.find((h) => h.year === selectedYear)?.dest_corridor_share_pct !== undefined
                  ? formatPercent(routeData.history.find((h) => h.year === selectedYear).dest_corridor_share_pct)
                  : 'N/A'
              }
              subtitle={`Share of ${routeData?.destination_name || destination}'s total immigrant population`}
              icon={ArrowRightLeft}
              accent="amber"
              isMono={true}
              isLoading={isLoading}
            />
          </div>

          {/* Historical Trajectory of the Route */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginTop: 'var(--space-4)' }}>
            <h4 style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--weight-bold)', marginBottom: 'var(--space-1)' }}>
              Bilateral Migrant Stock Trajectory (1990–2020)
            </h4>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
              UN DESA mid-year migrant stock estimates for this bilateral corridor across quinquennial census rounds.
            </p>
            {isLoading ? (
              <LoadingState message="Loading route historical trajectory..." />
            ) : historySeries.length > 0 ? (
              <LineChart
                series={historySeries}
                xTitle="UN DESA Census Round"
                yTitle="Migrant Stock (People)"
                height={360}
              />
            ) : (
              <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
                No empirical corridor records found between these two nations across 1990–2020.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Top Corridors Section */}
      <div style={{ marginTop: 'var(--section-gap)' }}>
        <SectionHeader
          title={isSpecificRoute ? 'Global Comparative Corridors' : 'Top Migration Corridors'}
          subtitle={`Major bilateral migration corridors for round ${selectedYear}`}
          badge={`${selectedYear} Corridors`}
        />

        <DataTable
          columns={topCorridorsColumns}
          data={routeData?.top_corridors || []}
          isLoading={isLoading}
          emptyMessage="No bilateral corridors match the selected filter."
        />
      </div>
    </PageContainer>
  );
}
