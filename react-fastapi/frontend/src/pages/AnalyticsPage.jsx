import React, { useState, useEffect, useContext, useCallback } from 'react';
import {
  LineChart as ChartIcon,
  PieChart,
  Link2,
  AlertTriangle,
  Sparkles,
  ShieldAlert,
  Sliders,
  TrendingUp,
  Activity,
  Globe,
} from 'lucide-react';
import { AppContext, normalizeYear } from '../context/AppContext';
import {
  getAnalyticsOverview,
  getConcentration,
  getCorrelations,
  getScatterData,
  getOutliers,
} from '../services/api';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/common/KPICard';
import { Select } from '../components/common/Select';
import { DataTable } from '../components/common/DataTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { SectionHeader } from '../components/common/SectionHeader';
import { CorrelationChart } from '../components/charts/CorrelationChart';
import { OutlierChart } from '../components/charts/OutlierChart';
import { ConcentrationChart } from '../components/charts/ConcentrationChart';
import { InsightCard } from '../components/common/InsightCard';
import { formatNumber, formatPercent } from '../utils/formatters';

const SCATTER_PAIRS = [
  {
    id: 'gdp_pc_vs_pct_pop',
    x: 'gdp_per_capita',
    y: 'migrant_stock_pct_population',
    label: 'Migrant Stock % Pop vs. GDP per Capita (Income Intensity)',
    xLabel: 'GDP per Capita (USD, Log Scale)',
    yLabel: 'Migrant Stock % of Population',
    logX: true,
    logY: false,
  },
  {
    id: 'gdp_vs_stock',
    x: 'gdp',
    y: 'migrant_stock',
    label: 'Migrant Stock vs. Total GDP (Economic Scale)',
    xLabel: 'Total GDP (USD, Log Scale)',
    yLabel: 'Migrant Stock (Log Scale)',
    logX: true,
    logY: true,
  },
  {
    id: 'pop_vs_stock',
    x: 'population',
    y: 'migrant_stock',
    label: 'Migrant Stock vs. Total Population (Demographic Scale)',
    xLabel: 'Total Population (Log Scale)',
    yLabel: 'Migrant Stock (Log Scale)',
    logX: true,
    logY: true,
  },
  {
    id: 'unemp_vs_pct_pop',
    x: 'unemployment',
    y: 'migrant_stock_pct_population',
    label: 'Migrant Stock % Pop vs. Unemployment Rate',
    xLabel: 'Unemployment Rate (%)',
    yLabel: 'Migrant Stock % of Population',
    logX: false,
    logY: false,
  },
];

const OUTLIER_METRICS = [
  { value: 'migrant_stock', label: 'Total Migrant Stock (Volume)' },
  { value: 'migrant_stock_pct_population', label: 'Migrant Stock % of Population (Intensity)' },
  { value: 'gdp_per_capita', label: 'GDP per Capita (Wealth)' },
  { value: 'population', label: 'Total Host Population' },
];

const OUTLIER_METHODS = [
  { value: 'IQR', label: 'Interquartile Range (IQR Method)' },
  { value: 'Z-Score', label: 'Standard Deviation (Z-Score Method)' },
];

export function AnalyticsPage() {
  const { selectedYear, setSelectedYear } = useContext(AppContext);
  const safeYear = normalizeYear(selectedYear);

  // States
  const [overview, setOverview] = useState(null);
  const [concentration, setConcentration] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [selectedPairId, setSelectedPairId] = useState('gdp_pc_vs_pct_pop');
  const [scatterData, setScatterData] = useState(null);

  // Outlier controls
  const [outlierMetric, setOutlierMetric] = useState('migrant_stock');
  const [outlierMethod, setOutlierMethod] = useState('IQR');
  const [outlierThreshold, setOutlierThreshold] = useState(1.5);
  const [outlierData, setOutlierData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const currentPair = SCATTER_PAIRS.find((p) => p.id === selectedPairId) || SCATTER_PAIRS[0];

  const fetchAllAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [overviewRes, concRes, corrRes, scatterRes, outlierRes] = await Promise.all([
        getAnalyticsOverview(safeYear),
        getConcentration(safeYear),
        getCorrelations(safeYear),
        getScatterData(currentPair.x, currentPair.y, safeYear, currentPair.logX, currentPair.logY),
        getOutliers(safeYear, outlierMetric, outlierMethod, outlierThreshold),
      ]);

      setOverview(overviewRes);
      setConcentration(concRes);
      setCorrelations(corrRes);
      setScatterData(scatterRes);
      setOutlierData(outlierRes);
    } catch (err) {
      console.error('Failed to load advanced analytics:', err);
      setError(err.message || 'Failed to load advanced analytics');
    } finally {
      setLoading(false);
    }
  }, [safeYear, currentPair, outlierMetric, outlierMethod, outlierThreshold]);

  useEffect(() => {
    fetchAllAnalytics();
  }, [fetchAllAnalytics]);

  // Table columns for correlations
  const correlationColumns = [
    { key: 'pair_name', label: 'Indicator Pair', render: (val) => <strong>{val}</strong> },
    { key: 'sample_size', label: 'Sample Size (N)', isNumeric: true, render: (val) => `${val} nations` },
    {
      key: 'spearman_rho',
      label: 'Spearman ρ (Rank)',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? val.toFixed(3) : 'N/A'),
    },
    {
      key: 'pearson_r',
      label: 'Pearson r (Linear)',
      isNumeric: true,
      isMono: true,
      render: (val) => (val !== null ? val.toFixed(3) : 'N/A'),
    },
    { key: 'relationship_strength', label: 'Strength' },
    {
      key: 'statistical_significance',
      label: 'Significance',
      render: (val) => <span className="badge badge-subtle">{val}</span>,
    },
  ];

  // Table columns for outliers
  const outlierColumns = [
    { key: 'rank', label: 'Rank', width: '60px', isNumeric: true, render: (_, __, idx) => <strong>#{idx + 1}</strong> },
    {
      key: 'display_name',
      label: 'Outlier Country',
      render: (val, row) => (
        <span>
          <strong>{val}</strong> <span style={{ color: 'var(--text-subtle)', fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)' }}>({row.country_code})</span>
        </span>
      ),
    },
    {
      key: 'metric_value',
      label: 'Observed Value',
      isNumeric: true,
      isMono: true,
      render: (val) => formatNumber(val),
    },
    {
      key: 'deviation',
      label: outlierMethod === 'Z-Score' ? 'Z-Score Deviation' : 'IQR Multiplier',
      isNumeric: true,
      isMono: true,
      render: (val) => `${val.toFixed(2)}x`,
    },
    {
      key: 'outlier_type',
      label: 'Type',
      render: (val) => (
        <span className={`badge ${val.includes('High') ? 'status-badge danger' : 'status-badge primary'}`}>
          {val}
        </span>
      ),
    },
  ];

  return (
    <PageContainer
      title="Advanced Migration Analytics & Econometrics"
      subtitle="Herfindahl-Hirschman concentration indexes, bivariate socioeconomic correlation engine, transparent IQR/Z-score anomaly detection, and deterministic insights."
      breadcrumb={['Observatory', 'Advanced Analytics', 'Analytics Overview']}
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
      </div>

      {loading ? (
        <LoadingState message="Executing econometric algorithms and statistical outlier models..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchAllAnalytics} />
      ) : overview ? (
        <>
          {/* Executive KPI Cards */}
          <div className="kpi-grid">
            <KPICard
              title="Destination HHI Score"
              value={overview.destination_hhi.toFixed(0)}
              subtitle={overview.hhi_category}
              icon={PieChart}
              accent="blue"
              isMono={true}
            />
            <KPICard
              title="Active Host Nations"
              value={overview.active_destinations}
              subtitle={`Top 10 hold ${formatPercent(overview.top_10_destination_share)}`}
              icon={Globe}
              accent="teal"
              isMono={true}
            />
            <KPICard
              title="Detected Volume Outliers"
              value={overview.outlier_counts.migrant_stock || 0}
              subtitle="IQR k=1.5 statistical anomalies"
              icon={AlertTriangle}
              accent="amber"
              isMono={true}
            />
            <KPICard
              title="Strongest Correlation"
              value={
                overview.strongest_correlation
                  ? `ρ = ${overview.strongest_correlation.spearman_rho.toFixed(2)}`
                  : 'N/A'
              }
              subtitle={
                overview.strongest_correlation
                  ? overview.strongest_correlation.pair_name.split('(')[0].trim()
                  : 'Socioeconomic association'
              }
              icon={Link2}
              accent="accent"
              isMono={true}
            />
          </div>

          {/* Section 1: Migration Concentration Analytics */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title={`Global Migration Stock Concentration (${safeYear})`}
              subtitle="Herfindahl-Hirschman Index (HHI) and cumulative percentage shares comparing destination hosts vs. origin diasporas."
              badge="HHI Market Model"
            />
            {concentration && (
              <ConcentrationChart
                destination={concentration.destination}
                origin={concentration.origin}
                height={360}
              />
            )}
          </div>

          {/* Section 2: Socioeconomic Correlation Engine */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title="Bivariate Socioeconomic Correlation Explorer"
              subtitle="Pearson linear correlation (r) and Spearman rank correlation (ρ) assessing cross-sectional macroeconomic associations."
              badge="Cross-Sectional Regression"
            />

            {/* Association Disclaimer */}
            <div className="info-banner" style={{ marginBottom: 'var(--space-4)' }}>
              <ShieldAlert className="info-banner-icon" />
              <div>
                <div className="info-banner-title">Scientific Principle — Statistical Association vs. Causality</div>
                <div className="info-banner-text">
                  Statistical correlation indicates empirical association across sovereign nations, NOT a causal mechanism. Observed relationships reflect macroeconomic and demographic conditions at mid-year {safeYear}.
                </div>
              </div>
            </div>

            {/* Pair Selector */}
            <div style={{ marginBottom: 'var(--space-5)' }}>
              <Select
                label="Indicator Pair:"
                value={selectedPairId}
                onChange={(e) => setSelectedPairId(e.target ? e.target.value : e)}
                options={SCATTER_PAIRS.map((p) => ({ value: p.id, label: p.label }))}
              />
            </div>

            {/* Scatter Plot */}
            {scatterData && (
              <CorrelationChart
                points={scatterData.points}
                stats={scatterData.stats}
                xLabel={currentPair.xLabel}
                yLabel={currentPair.yLabel}
                height={480}
              />
            )}

            {/* Correlation Matrix Table */}
            {correlations && correlations.correlations && (
              <div style={{ marginTop: 'var(--space-6)' }}>
                <SectionHeader
                  title={`Complete Socioeconomic Association Matrix (${safeYear})`}
                  subtitle="Correlation metrics across all standard development indicators"
                />
                <DataTable columns={correlationColumns} data={correlations.correlations} />
              </div>
            )}
          </div>

          {/* Section 3: Outlier & Anomaly Detection */}
          <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
              title="Transparent Outlier & Anomaly Detection"
              subtitle="Statistical anomaly detection identifying countries exhibiting unusual demographic scale, intensity, or growth distributions."
              badge="Distribution Models"
            />

            {/* Outlier Controls */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: 'var(--space-4)',
                marginBottom: 'var(--space-5)',
              }}
            >
              <Select
                label="Target Indicator:"
                value={outlierMetric}
                onChange={(e) => setOutlierMetric(e.target ? e.target.value : e)}
                options={OUTLIER_METRICS}
              />

              <Select
                label="Algorithm:"
                value={outlierMethod}
                onChange={(e) => setOutlierMethod(e.target ? e.target.value : e)}
                options={OUTLIER_METHODS}
              />

              <Select
                label="Threshold:"
                value={String(outlierThreshold)}
                onChange={(e) => {
                  const raw = e.target ? e.target.value : e;
                  setOutlierThreshold(parseFloat(raw) || 1.5);
                }}
                options={
                  outlierMethod === 'IQR'
                    ? [
                        { value: '1.5', label: '1.5x IQR (Standard Outliers)' },
                        { value: '3.0', label: '3.0x IQR (Extreme Outliers)' },
                      ]
                    : [
                        { value: '2.0', label: '2.0σ (|z| > 2.0)' },
                        { value: '2.5', label: '2.5σ (|z| > 2.5 — Standard)' },
                        { value: '3.0', label: '3.0σ (|z| > 3.0 — Extreme)' },
                      ]
                }
              />
            </div>

            {/* Outlier Summary Stats */}
            {outlierData && outlierData.summary && (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                  gap: 'var(--space-3)',
                  marginBottom: 'var(--space-5)',
                }}
              >
                <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                  <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Detected Outliers</span>
                  <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-base)', color: 'var(--accent-amber)', fontFamily: 'var(--font-mono)' }}>
                    {outlierData.outlier_count} nations
                  </h4>
                </div>
                {outlierMethod === 'IQR' ? (
                  <>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Q1 (25th %)</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.q1)}
                      </h4>
                    </div>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Median (50th %)</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.median)}
                      </h4>
                    </div>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Q3 (75th %)</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.q3)}
                      </h4>
                    </div>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Upper Cutoff Bound</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', color: 'var(--primary)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.upper_bound)}
                      </h4>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Global Mean (μ)</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.mean)}
                      </h4>
                    </div>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Standard Dev (σ)</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.std)}
                      </h4>
                    </div>
                    <div className="card card-subtle" style={{ padding: 'var(--space-3)' }}>
                      <span style={{ fontSize: 'var(--text-2xs)', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Upper Bound (+kσ)</span>
                      <h4 style={{ margin: '2px 0 0 0', fontSize: 'var(--text-sm)', color: 'var(--primary)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(outlierData.summary.upper_bound)}
                      </h4>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Outlier Chart & Table */}
            {outlierData && outlierData.outliers && outlierData.outliers.length > 0 ? (
              <>
                <OutlierChart
                  outliers={outlierData.outliers}
                  summary={outlierData.summary}
                  metricLabel={OUTLIER_METRICS.find((m) => m.value === outlierMetric)?.label || 'Value'}
                  height={Math.max(320, Math.min(600, outlierData.outliers.length * 30 + 90))}
                />
                <div style={{ marginTop: 'var(--space-5)' }}>
                  <DataTable columns={outlierColumns} data={outlierData.outliers} />
                </div>
              </>
            ) : (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', margin: 'var(--space-6) 0' }}>
                No statistical outliers detected under the selected {outlierMethod} threshold ({outlierThreshold}).
              </p>
            )}
          </div>

          {/* Section 4: Key Storytelling Highlights */}
          {overview.top_insights && overview.top_insights.length > 0 && (
            <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
              <SectionHeader
                title="Automated Data Storytelling Highlights"
                subtitle="Deterministic rule-based insights generated directly from verified observatory calculations."
                badge="Deterministic Insights"
              />
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 'var(--grid-gap)',
                }}
              >
                {overview.top_insights.map((insight, idx) => (
                  <InsightCard key={idx} insight={insight} />
                ))}
              </div>
            </div>
          )}
        </>
      ) : null}
    </PageContainer>
  );
}
