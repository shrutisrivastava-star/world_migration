import React, { useState, useEffect, useContext, useCallback } from 'react';
import {
  Sparkles,
  Filter,
  Globe,
  PieChart,
  TrendingUp,
  Activity,
  ArrowRightLeft,
  Link2,
  Share2,
  ShieldCheck,
} from 'lucide-react';
import { AppContext, normalizeYear } from '../context/AppContext';
import { getInsights } from '../services/api';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/common/KPICard';
import { Select } from '../components/common/Select';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { InsightCard } from '../components/common/InsightCard';

export function InsightsPage() {
  const { selectedYear, setSelectedYear } = useContext(AppContext);
  const safeYear = normalizeYear(selectedYear);

  const [selectedCategory, setSelectedCategory] = useState('All');
  const [insightsData, setInsightsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInsights = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getInsights(safeYear, selectedCategory);
      setInsightsData(data);
    } catch (err) {
      console.error('Failed to load insights:', err);
      setError(err.message || 'Failed to load migration storytelling insights');
    } finally {
      setLoading(false);
    }
  }, [safeYear, selectedCategory]);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const categories = [
    'All',
    'Global Trend',
    'Concentration',
    'Fastest Growth',
    'Largest Changes',
    'Major Corridors',
    'Socioeconomic Associations',
    'Network Structure',
  ];

  return (
    <PageContainer
      title="Deterministic Migration Insights & Storytelling"
      subtitle="Executive data-storytelling engine translating complex empirical calculations into rule-based, verified scientific narratives."
      breadcrumb={['Observatory', 'Advanced Analytics', 'Insights Engine']}
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
            label="Domain Category:"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target ? e.target.value : e)}
            options={categories.map((c) => ({ value: c, label: c === 'All' ? 'All Insight Categories' : c }))}
          />
        </div>
      </div>

      {/* Category Filter Pills */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '8px',
          marginBottom: 'var(--section-gap)',
        }}
      >
        {categories.map((cat) => {
          const isActive = selectedCategory.toLowerCase() === cat.toLowerCase();
          return (
            <button
              key={cat}
              className={`btn ${isActive ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {loading ? (
        <LoadingState message="Synthesizing rule-based migration insights across global matrices..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchInsights} />
      ) : insightsData ? (
        <>
          {/* Scientific Transparency Callout */}
          <div className="info-banner" style={{ marginBottom: 'var(--section-gap)' }}>
            <ShieldCheck className="info-banner-icon" />
            <div>
              <div className="info-banner-title">Algorithmic Integrity & Deterministic Logic</div>
              <div className="info-banner-text">
                All insights are generated deterministically from explicit data-driven rules over UN DESA and World Bank observations. No speculative or unverified claims are produced.
              </div>
            </div>
          </div>

          {/* KPI Summary Cards */}
          <div className="kpi-grid">
            <KPICard
              title="Verified Insights"
              value={insightsData.total_insights}
              subtitle={`For ${safeYear} census round`}
              icon={Sparkles}
              accent="blue"
              isMono={true}
            />
            <KPICard
              title="Active Domain"
              value={selectedCategory}
              subtitle="Analytical narrative scope"
              icon={Filter}
              accent="teal"
            />
            <KPICard
              title="Census Observation"
              value={`${safeYear}`}
              subtitle="Quinquennial observation round"
              icon={Globe}
              accent="amber"
              isMono={true}
            />
          </div>

          {/* Insights Grid */}
          {insightsData.insights && insightsData.insights.length > 0 ? (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                gap: 'var(--grid-gap)',
              }}
            >
              {insightsData.insights.map((insight, idx) => (
                <InsightCard key={idx} insight={insight} />
              ))}
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
              <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                No insights found for category "{selectedCategory}" in {safeYear}.
              </p>
            </div>
          )}
        </>
      ) : null}
    </PageContainer>
  );
}
