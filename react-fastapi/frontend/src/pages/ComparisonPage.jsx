import React, { useState, useEffect, useContext, useCallback } from 'react';
import {
  Scale,
  Plus,
  X,
  TrendingUp,
  Globe,
  DollarSign,
  Users,
  ShieldAlert,
  Sliders,
} from 'lucide-react';
import { AppContext, normalizeYear } from '../context/AppContext';
import { getCountryComparison } from '../services/api';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/common/KPICard';
import { Select } from '../components/common/Select';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { SectionHeader } from '../components/common/SectionHeader';
import { ComparisonChart } from '../components/charts/ComparisonChart';
import { formatNumber, formatPercent, formatCurrency } from '../utils/formatters';

const PRESET_COMPARISONS = [
  { label: 'Global Migration Giants', countries: ['USA', 'DEU', 'SAU', 'RUS', 'GBR'] },
  { label: 'Major Emigrant Origins', countries: ['IND', 'MEX', 'CHN', 'RUS', 'SYR'] },
  { label: 'High Demographic Intensity', countries: ['ARE', 'QAT', 'KWT', 'SGP', 'CHE'] },
  { label: 'North America & Europe', countries: ['USA', 'CAN', 'DEU', 'GBR', 'FRA'] },
];

export function ComparisonPage() {
  const { selectedYear, setSelectedYear, countries: allCountries } = useContext(AppContext);
  const safeYear = normalizeYear(selectedYear);

  const [selectedCountryCodes, setSelectedCountryCodes] = useState(['USA', 'IND', 'DEU']);
  const [selectedToAdd, setSelectedToAdd] = useState('');
  const [metricMode, setMetricMode] = useState('migrant_stock');

  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchComparison = useCallback(async () => {
    if (selectedCountryCodes.length < 2) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getCountryComparison(selectedCountryCodes, safeYear);
      setComparisonData(data);
    } catch (err) {
      console.error('Failed to load country comparison:', err);
      setError(err.message || 'Failed to load country comparison');
    } finally {
      setLoading(false);
    }
  }, [selectedCountryCodes, safeYear]);

  useEffect(() => {
    fetchComparison();
  }, [fetchComparison]);

  const handleAddCountry = (code) => {
    if (!code) return;
    if (selectedCountryCodes.includes(code)) return;
    if (selectedCountryCodes.length >= 5) return;
    setSelectedCountryCodes([...selectedCountryCodes, code]);
    setSelectedToAdd('');
  };

  const handleRemoveCountry = (code) => {
    if (selectedCountryCodes.length <= 2) return;
    setSelectedCountryCodes(selectedCountryCodes.filter((c) => c !== code));
  };

  const handleApplyPreset = (presetCodes) => {
    setSelectedCountryCodes(presetCodes);
  };

  const availableOptions = (allCountries || [])
    .filter((c) => c.country_code && !selectedCountryCodes.includes(c.country_code))
    .map((c) => ({
      value: c.country_code,
      label: `${c.display_name} (${c.country_code})`,
    }));

  const tableColumns = [
    {
      key: 'country_name',
      label: 'Country / Sovereign Nation',
      render: (val, row) => (
        <span>
          <strong>{val}</strong> <span style={{ color: 'var(--text-subtle)', fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)' }}>({row.country_code})</span>
        </span>
      ),
    },
    {
      key: 'Total Migrant Stock (People)',
      label: 'Migrant Stock',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null && val !== undefined ? formatNumber(val) : 'N/A'),
    },
    {
      key: 'Migrant Stock % of Population',
      label: 'Migrant % Pop',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null && val !== undefined ? formatPercent(val) : 'N/A'),
    },
    {
      key: '5-Year Stock Growth (%)',
      label: '5-Yr Growth',
      isNumeric: true,
      isMono: true,
      render: (val) =>
        val !== null && val !== undefined ? `${val >= 0 ? '+' : ''}${val.toFixed(1)}%` : 'N/A',
    },
    {
      key: 'GDP per Capita (USD)',
      label: 'GDP per Capita',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null && val !== undefined ? formatCurrency(val) : 'N/A'),
    },
    {
      key: 'Total Population',
      label: 'Total Population',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null && val !== undefined ? formatNumber(val) : 'N/A'),
    },
    {
      key: 'Unemployment Rate (%)',
      label: 'Unemployment',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null && val !== undefined ? formatPercent(val) : 'N/A'),
    },
  ];

  return (
    <PageContainer
      title="Multi-Country Comparative Profiling"
      subtitle="Side-by-side comparative analysis evaluating demographic intensity, historical trajectories, and socioeconomic context across 2 to 5 selected sovereign nations."
      breadcrumb={['Observatory', 'Advanced Analytics', 'Country Comparison']}
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
            label="Add Nation (2–5):"
            value={selectedToAdd}
            onChange={(e) => handleAddCountry(e.target ? e.target.value : e)}
            options={[{ value: '', label: '-- Select a Country to Add --' }, ...availableOptions]}
            disabled={selectedCountryCodes.length >= 5}
          />
        </div>
      </div>

      {/* Selected Country Chips & Presets Toolbar */}
      <div className="card" style={{ padding: 'var(--space-4)', marginBottom: 'var(--section-gap)' }}>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: 'var(--space-3)' }}>
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--text-muted)', marginRight: '4px', textTransform: 'uppercase' }}>
            Comparing ({selectedCountryCodes.length}/5):
          </span>
          {selectedCountryCodes.map((code) => {
            const countryObj = (allCountries || []).find((c) => c.country_code === code);
            const name = countryObj ? countryObj.display_name : code;
            return (
              <span
                key={code}
                className="badge badge-primary"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', fontSize: 'var(--text-xs)' }}
              >
                <span>{name} ({code})</span>
                {selectedCountryCodes.length > 2 && (
                  <button
                    onClick={() => handleRemoveCountry(code)}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      color: 'inherit',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                    }}
                    title="Remove country"
                  >
                    <X size={14} />
                  </button>
                )}
              </span>
            );
          })}
        </div>

        {/* Quick Presets */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px', paddingTop: 'var(--space-2)', borderTop: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', fontWeight: 500 }}>Quick Presets:</span>
          {PRESET_COMPARISONS.map((p, idx) => (
            <button
              key={idx}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: 'var(--text-xs)', padding: '3px 10px' }}
              onClick={() => handleApplyPreset(p.countries)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingState message="Extracting multi-country trajectories and comparative indicators..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchComparison} />
      ) : comparisonData ? (
        <>
          {/* Historical Trajectory Comparison Chart */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 'var(--space-3)',
                marginBottom: 'var(--space-4)',
              }}
            >
              <div>
                <SectionHeader
                  title="Longitudinal Trajectory Comparison (1990–2020)"
                  subtitle="Tracking migrant stock across 7 UN DESA quinquennial census rounds."
                  badge="1990–2020"
                />
              </div>

              {/* Chart Metric Toggle */}
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  className={`btn ${metricMode === 'migrant_stock' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                  onClick={() => setMetricMode('migrant_stock')}
                >
                  Total Migrant Stock
                </button>
                <button
                  className={`btn ${metricMode === 'pct_population' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                  onClick={() => setMetricMode('pct_population')}
                >
                  Migrant Stock % of Population
                </button>
              </div>
            </div>

            <ComparisonChart
              trajectories={comparisonData.trajectories}
              metricMode={metricMode}
              height={400}
            />
          </div>

          {/* Absolute Metrics Comparison Table */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title={`Side-by-Side Socioeconomic Matrix (${safeYear})`}
              subtitle="Comparing absolute demographic, economic, and migration indicators for the selected census round."
            />
            <DataTable columns={tableColumns} data={comparisonData.absolute_comparison} />
          </div>

          {/* Scientific Callout */}
          <div className="methodology-callout">
            <ShieldAlert className="methodology-callout-icon" />
            <div>
              <div className="methodology-callout-title">Scientific Methodology Note</div>
              <div className="methodology-callout-text">
                Migrant stock figures reflect accumulated mid-year foreign-born population residing in destination
                countries as documented in UN DESA census rounds. Differences in migration intensity across countries
                are shaped by historical ties, geographical scale, labor market structures, and demographic baseline sizes.
              </div>
            </div>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
