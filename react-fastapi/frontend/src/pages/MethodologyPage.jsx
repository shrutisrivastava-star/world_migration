import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import {
  BookOpen,
  Globe,
  Share2,
  PieChart,
  BarChart3,
  Layers,
  ShieldCheck,
  Info,
  Scale,
} from 'lucide-react';

export function MethodologyPage() {
  return (
    <PageContainer
      title="Observatory Scientific Methodology & Data Definitions"
      subtitle="Formal documentation of UN DESA 2020 Revision international migrant stock definitions, World Bank WDI indicators, NetworkX graph modeling, and econometric formulas."
      breadcrumb={['Observatory', 'Information', 'Methodology']}
    >
      {/* Principle Callout */}
      <div className="info-banner" style={{ marginBottom: 'var(--section-gap)' }}>
        <ShieldCheck className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Foundational Scientific Principle</div>
          <div className="info-banner-text">
            <strong>Migrant Stock is NOT annual migration flow.</strong> UN DESA data strictly represents the accumulated total number of foreign-born individuals residing in a destination nation at mid-year of each 5-year census round (1990, 1995, 2000, 2005, 2010, 2015, 2020).
          </div>
        </div>
      </div>

      {/* Grid of Methodology Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--section-gap)' }}>
        {/* Section 1: Core Datasets */}
        <div className="card" style={{ padding: 'var(--card-padding)' }}>
          <SectionHeader
            title="1. Core Empirical Datasets & Entity Inclusions"
            subtitle="Authoritative international sources underpinning all observatory calculations"
            badge="Primary Sources"
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--grid-gap)', marginTop: 'var(--space-4)' }}>
            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <Globe size={18} style={{ color: 'var(--primary)' }} />
                <h4 style={{ margin: 0, fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)' }}>UN DESA 2020 Revision</h4>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                United Nations Department of Economic and Social Affairs (UN DESA) Population Division. Bilateral foreign-born stock matrix covering 232 countries and territories across 7 quinquennial observation rounds (1990–2020).
              </p>
            </div>

            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <Scale size={18} style={{ color: 'var(--accent-teal)' }} />
                <h4 style={{ margin: 0, fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)' }}>World Bank WDI</h4>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                World Bank World Development Indicators providing macro demographic baseline indicators: Total National Population (SP.POP.TOTL), GDP per Capita in current USD (NY.GDP.PCAP.CD), and Unemployment Rate (SL.UEM.TOTL.ZS).
              </p>
            </div>

            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <ShieldCheck size={18} style={{ color: 'var(--accent-amber)' }} />
                <h4 style={{ margin: 0, fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)' }}>Sovereign State Filtering</h4>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                Geographic regional aggregates (such as "World", "Europe", "Asia", "Latin America") are strictly filtered out of country leaderboards and regression calculations to guarantee scientific validity.
              </p>
            </div>
          </div>
        </div>

        {/* Section 2: Network Analysis & Graph Theory */}
        <div className="card" style={{ padding: 'var(--card-padding)' }}>
          <SectionHeader
            title="2. Network Topology & Centrality Algorithms"
            subtitle="NetworkX directed graph modeling of global migration linkages"
            badge="Graph Theory"
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--grid-gap)', marginTop: 'var(--space-4)' }}>
            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: 'var(--text-main)' }}>
                Weighted Strength & Degree
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                <strong>In-Strength:</strong> Total foreign-born stock residing in a nation from all global origins.
                <br />
                <strong>Out-Strength:</strong> Total diaspora from an origin residing across all destination nations.
                <br />
                <strong>Total Degree:</strong> Total count of non-zero bilateral migration corridors linked to that nation.
              </p>
            </div>

            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: 'var(--text-main)' }}>
                Betweenness & PageRank
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                <strong>Betweenness Centrality:</strong> Quantifies how frequently a country acts as an intermediary bridge along shortest paths between other nation pairs.
                <br />
                <strong>PageRank:</strong> Measures eigenvector influence based on connections to other highly connected global hubs.
              </p>
            </div>

            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: 'var(--text-main)' }}>
                Louvain Modularity Communities
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                Partitions the network into discrete demographic clusters by maximizing modularity Q. Edge weights are transformed into an undirected sum of reciprocal bilateral stock (wij + wji) to identify organic regional demographic clusters.
              </p>
            </div>
          </div>
        </div>

        {/* Section 3: Econometrics & Concentration */}
        <div className="card" style={{ padding: 'var(--card-padding)' }}>
          <SectionHeader
            title="3. Concentration Indices & Econometric Formulations"
            subtitle="Mathematical models evaluating demographic distribution inequality and correlation"
            badge="Econometrics"
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--grid-gap)', marginTop: 'var(--space-4)' }}>
            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: 'var(--text-main)' }}>
                Herfindahl-Hirschman Index (HHI)
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                Measures demographic concentration across host destinations and origin diasporas:
                <br />
                <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--primary)' }}>HHI = Σ (Share_i %)^2</code>
                <br />
                Scores below 1,500 denote unconcentrated distributions; 1,500–2,500 moderate; &gt;2,500 highly concentrated.
              </p>
            </div>

            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: 'var(--text-main)' }}>
                Pearson & Spearman Correlations
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                <strong>Pearson r:</strong> Measures parametric linear relationship between bivariate pairs.
                <br />
                <strong>Spearman ρ:</strong> Non-parametric monotonic rank correlation resilient to extreme skewed distributions and power-law scaling.
              </p>
            </div>

            <div className="card card-subtle" style={{ padding: 'var(--space-4)' }}>
              <h4 style={{ margin: '0 0 var(--space-2) 0', fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: 'var(--text-main)' }}>
                Transparent Outlier Detection
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
                <strong>IQR Method:</strong> Identifies values exceeding Q3 + k × IQR.
                <br />
                <strong>Z-Score Method:</strong> Flags sovereign nations with |z| = |x - μ| / σ &gt; threshold.
                <br />
                <strong>Preservation:</strong> Outliers are genuine empirical signals (microstates, geopolitical shocks) and are never dropped.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
