import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import { Select } from '../components/common/Select';
import { KPICard } from '../components/common/KPICard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { ChoroplethMap } from '../components/charts/ChoroplethMap';
import { useAppContext } from '../hooks/useAppContext';
import { getMapData } from '../services/api';
import { MAP_METRIC_OPTIONS, SCIENTIFIC_DEFINITIONS } from '../utils/scientificLabels';
import { formatNumber, formatPercent, formatCurrency } from '../utils/formatters';
import { Globe, Trophy, BarChart2, Info } from 'lucide-react';

export function GlobalMapPage() {
  const { selectedYear } = useAppContext();
  const [metric, setMetric] = useState('Migrant Stock');
  const [mapData, setMapData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMap = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getMapData(selectedYear, metric);
      if (res && res.data) {
        setMapData(res.data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [selectedYear, metric]);

  useEffect(() => {
    fetchMap();
  }, [fetchMap]);

  // Compute map summary statistics
  const validRecords = mapData.filter((d) => d.metric_value !== null && !isNaN(d.metric_value));
  const topRecord = validRecords.length > 0
    ? [...validRecords].sort((a, b) => b.metric_value - a.metric_value)[0]
    : null;

  const totalSum = validRecords.reduce((acc, r) => acc + (r.metric_value || 0), 0);

  return (
    <PageContainer
      title="Global Choropleth Map"
      subtitle={`Geospatial distribution of international migration stock and socioeconomic indicators for round ${selectedYear}`}
      breadcrumb={['Observatory', 'Core Explorer', 'Global Map']}
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <Select
            label="Metric:"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            options={MAP_METRIC_OPTIONS}
          />
        </div>
      }
    >
      <div className="info-banner" role="region" aria-label="UN DESA Definition">
        <Info className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Geospatial Choropleth Mapping</div>
          <div className="info-banner-text">
            Choropleth polygons display sovereign nations shaded according to <strong>{metric}</strong> at mid-year {selectedYear}. {SCIENTIFIC_DEFINITIONS.MIGRANT_STOCK}
          </div>
        </div>
      </div>

      {error && (
        <ErrorState
          title="Could not load map dataset"
          message={error}
          onRetry={fetchMap}
        />
      )}

      {/* Map Card */}
      <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)', minHeight: 560 }}>
        {isLoading ? (
          <LoadingState message={`Rendering global choropleth map for ${metric} (${selectedYear})...`} />
        ) : (
          <ChoroplethMap data={mapData} metricName={metric} height={540} />
        )}
      </div>

      {/* Summary Metrics */}
      <SectionHeader
        title="Global Distribution Summary"
        subtitle={`Summary distribution for ${metric} in census round ${selectedYear}`}
        badge={`${selectedYear}`}
      />

      <div className="kpi-grid">
        <KPICard
          title="Global Maximum"
          value={
            topRecord
              ? metric.includes('%')
                ? formatPercent(topRecord.metric_value)
                : metric.includes('GDP')
                ? formatCurrency(topRecord.metric_value)
                : formatNumber(topRecord.metric_value)
              : 'N/A'
          }
          subtitle={topRecord ? `${topRecord.display_name} (${topRecord.country_code})` : 'No data'}
          icon={Trophy}
          accent="amber"
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title={metric.includes('%') || metric.includes('GDP') ? 'Global Average' : 'Global Sovereign Total'}
          value={
            validRecords.length > 0
              ? metric.includes('%')
                ? formatPercent(totalSum / validRecords.length)
                : metric.includes('GDP')
                ? formatCurrency(totalSum / validRecords.length)
                : formatNumber(totalSum)
              : 'N/A'
          }
          subtitle={`Computed across ${validRecords.length} sovereign states`}
          icon={Globe}
          accent="blue"
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title="Participating Nations"
          value={validRecords.length}
          subtitle="Sovereign nations with verified empirical observations"
          icon={BarChart2}
          accent="teal"
          isMono={true}
          isLoading={isLoading}
        />
      </div>
    </PageContainer>
  );
}
