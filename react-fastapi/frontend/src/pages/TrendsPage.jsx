import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import { Select } from '../components/common/Select';
import { Button } from '../components/common/Button';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { LineChart } from '../components/charts/LineChart';
import { useAppContext } from '../hooks/useAppContext';
import { getGlobalTrend, getCountryTrends } from '../services/api';
import { TRENDS_METRIC_OPTIONS, SCIENTIFIC_DEFINITIONS } from '../utils/scientificLabels';
import { Info, Plus, X } from 'lucide-react';

const PRESET_COUNTRIES = [
  { code: 'USA', label: 'United States' },
  { code: 'IND', label: 'India' },
  { code: 'DEU', label: 'Germany' },
  { code: 'SAU', label: 'Saudi Arabia' },
  { code: 'RUS', label: 'Russian Federation' },
  { code: 'GBR', label: 'United Kingdom' },
  { code: 'CAN', label: 'Canada' },
  { code: 'AUS', label: 'Australia' },
];

export function TrendsPage() {
  const { countries: allCountries } = useAppContext();
  const [metric, setMetric] = useState('Migrant Stock');
  const [selectedCountryCodes, setSelectedCountryCodes] = useState(['USA', 'IND', 'DEU', 'SAU']);
  const [selectedToAdd, setSelectedToAdd] = useState('');

  const [globalData, setGlobalData] = useState([]);
  const [isLoadingGlobal, setIsLoadingGlobal] = useState(true);

  const [countryTrendsData, setCountryTrendsData] = useState([]);
  const [isLoadingCountry, setIsLoadingCountry] = useState(true);
  const [error, setError] = useState(null);

  // Load global trend
  useEffect(() => {
    let isMounted = true;
    async function loadGlobal() {
      setIsLoadingGlobal(true);
      try {
        const res = await getGlobalTrend();
        if (isMounted && res && res.points) {
          setGlobalData(res.points);
        }
      } catch (err) {
        console.error('Error fetching global trends:', err);
      } finally {
        if (isMounted) setIsLoadingGlobal(false);
      }
    }
    loadGlobal();
    return () => {
      isMounted = false;
    };
  }, []);

  // Load country comparison trends
  const fetchCountryTrends = useCallback(async () => {
    if (selectedCountryCodes.length === 0) {
      setCountryTrendsData([]);
      setIsLoadingCountry(false);
      return;
    }
    setIsLoadingCountry(true);
    setError(null);
    try {
      const res = await getCountryTrends(selectedCountryCodes, metric);
      if (res && res.points) {
        setCountryTrendsData(res.points);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoadingCountry(false);
    }
  }, [selectedCountryCodes, metric]);

  useEffect(() => {
    fetchCountryTrends();
  }, [fetchCountryTrends]);

  const handleAddCountry = () => {
    if (selectedToAdd && !selectedCountryCodes.includes(selectedToAdd)) {
      setSelectedCountryCodes([...selectedCountryCodes, selectedToAdd]);
      setSelectedToAdd('');
    }
  };

  const handleRemoveCountry = (code) => {
    setSelectedCountryCodes(selectedCountryCodes.filter((c) => c !== code));
  };

  // Group country trend points into series
  const countrySeriesMap = {};
  countryTrendsData.forEach((p) => {
    const key = p.display_name;
    if (!countrySeriesMap[key]) {
      countrySeriesMap[key] = {
        name: key,
        x: [],
        y: [],
      };
    }
    countrySeriesMap[key].x.push(p.year);
    countrySeriesMap[key].y.push(p.metric_value);
  });

  const countrySeries = Object.values(countrySeriesMap);

  const globalSeries = [
    {
      name: 'Global Migrant Stock',
      x: globalData.map((p) => p.year),
      y: globalData.map((p) => p.total_migrant_stock),
      color: '#0284c7',
    },
  ];

  const availableAddOptions = [
    { value: '', label: '+ Add country to comparison...' },
    ...allCountries
      .filter((c) => c.country_code && !selectedCountryCodes.includes(c.country_code))
      .map((c) => ({ value: c.country_code, label: c.display_name })),
  ];

  return (
    <PageContainer
      title="Longitudinal Trends (1990–2020)"
      subtitle="30-year historical trajectory analysis across quinquennial UN DESA census rounds"
      breadcrumb={['Observatory', 'Core Explorer', 'Historical Trends']}
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <Select
            label="Metric:"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            options={TRENDS_METRIC_OPTIONS}
          />
        </div>
      }
    >
      <div className="info-banner" role="region" aria-label="UN DESA Definition">
        <Info className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Longitudinal Trajectory Methodology</div>
          <div className="info-banner-text">
            {SCIENTIFIC_DEFINITIONS.QUINQUENNIAL_ROUNDS} {SCIENTIFIC_DEFINITIONS.MIGRANT_STOCK}
          </div>
        </div>
      </div>

      {error && <ErrorState title="Could not load trends" message={error} onRetry={fetchCountryTrends} />}

      {/* Global Aggregate Trend */}
      <SectionHeader
        title="Global Migrant Stock Trajectory"
        subtitle="Worldwide aggregated international migrant stock from 1990 to 2020"
        badge="Global Aggregate"
      />

      <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
        {isLoadingGlobal ? (
          <LoadingState message="Loading global trajectory..." />
        ) : (
          <LineChart
            series={globalSeries}
            xTitle="UN DESA Census Round"
            yTitle="Total Migrant Stock (People)"
            height={360}
          />
        )}
      </div>

      {/* Country Comparative Trends */}
      <SectionHeader
        title="Comparative Country Trajectories"
        subtitle={`Multi-country longitudinal comparison for ${metric}`}
        badge="Multi-Country"
      />

      {/* Country Selector Chips & Add Dropdown */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: 'var(--space-2)',
          marginBottom: 'var(--space-4)',
        }}
      >
        {selectedCountryCodes.map((code) => {
          const cObj = allCountries.find((c) => c.country_code === code) || PRESET_COUNTRIES.find((p) => p.code === code);
          const name = cObj ? cObj.display_name || cObj.label : code;
          return (
            <span
              key={code}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '0.35rem 0.75rem',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-full)',
                fontSize: 'var(--text-xs)',
                fontWeight: 'var(--weight-semibold)',
                color: 'var(--text-main)',
                boxShadow: 'var(--shadow-xs)',
              }}
            >
              <span>{name}</span>
              <button
                type="button"
                onClick={() => handleRemoveCountry(code)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  padding: 0,
                }}
                aria-label={`Remove ${name}`}
              >
                <X style={{ width: 14, height: 14 }} />
              </button>
            </span>
          );
        })}

        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
          <Select
            value={selectedToAdd}
            onChange={(e) => setSelectedToAdd(e.target.value)}
            options={availableAddOptions}
            aria-label="Add Country"
          />
          {selectedToAdd && (
            <Button size="sm" variant="primary" icon={Plus} onClick={handleAddCountry}>
              Add
            </Button>
          )}
        </div>
      </div>

      <div className="card" style={{ padding: 'var(--card-padding)' }}>
        {isLoadingCountry ? (
          <LoadingState message={`Loading multi-country trajectories for ${metric}...`} />
        ) : (
          <LineChart
            series={countrySeries}
            xTitle="UN DESA Census Round"
            yTitle={metric}
            isPercent={metric.includes('%')}
            isCurrency={metric.includes('GDP')}
            height={420}
          />
        )}
      </div>
    </PageContainer>
  );
}
