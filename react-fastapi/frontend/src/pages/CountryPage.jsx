import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { SectionHeader } from '../components/common/SectionHeader';
import { Select } from '../components/common/Select';
import { KPICard } from '../components/common/KPICard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { LineChart } from '../components/charts/LineChart';
import { BarChart } from '../components/charts/BarChart';
import { useAppContext } from '../hooks/useAppContext';
import { getCountryProfile } from '../services/api';
import { formatNumber, formatPercent, formatCurrency } from '../utils/formatters';
import { SCIENTIFIC_DEFINITIONS } from '../utils/scientificLabels';
import {
  Globe,
  Users,
  Flag,
  ArrowRightLeft,
  Scale,
  DollarSign,
  Info,
} from 'lucide-react';

export function CountryPage() {
  const { selectedYear, countries } = useAppContext();
  const [selectedCountry, setSelectedCountry] = useState('USA');

  const [profileData, setProfileData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getCountryProfile(selectedCountry, selectedYear);
      setProfileData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCountry, selectedYear]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const countryOptions = countries
    .filter((c) => c.country_code)
    .map((c) => ({ value: c.country_code, label: `${c.display_name} (${c.country_code})` }));

  // Historical trajectory series
  const historySeries = profileData && profileData.history
    ? [
        {
          name: 'Immigrant Stock Residing in Country',
          x: profileData.history.map((h) => h.year),
          y: profileData.history.map((h) => h.migrant_stock),
          color: '#0284c7',
        },
      ]
    : [];

  // Top Inbound Origins (bar chart)
  const inboundCategories = profileData?.top_inbound_origins?.map((i) => i.country_name) || [];
  const inboundValues = profileData?.top_inbound_origins?.map((i) => i.migrant_stock) || [];

  // Top Outbound Destinations (bar chart)
  const outboundCategories = profileData?.top_outbound_destinations?.map((i) => i.country_name) || [];
  const outboundValues = profileData?.top_outbound_destinations?.map((i) => i.migrant_stock) || [];

  return (
    <PageContainer
      title={profileData ? `${profileData.country_name} (${profileData.country_code})` : 'Country Demographics Profile'}
      subtitle={`Detailed demographic profile, diaspora presence, and bilateral migration network for round ${selectedYear}`}
      breadcrumb={['Observatory', 'Core Explorer', 'Country Explorer']}
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Select
            label="Select Nation:"
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            options={countryOptions}
          />
        </div>
      }
    >
      <div className="info-banner" role="region" aria-label="Country Profile Definition">
        <Info className="info-banner-icon" />
        <div>
          <div className="info-banner-title">Country Profile Methodology</div>
          <div className="info-banner-text">
            <strong>Immigrant Stock</strong> represents foreign-born residents living in {profileData?.country_name || selectedCountry}. <strong>Emigrant Diaspora</strong> represents citizens / native-born individuals of {profileData?.country_name || selectedCountry} residing abroad in other nations. {SCIENTIFIC_DEFINITIONS.MIGRANT_STOCK}
          </div>
        </div>
      </div>

      {error && <ErrorState title="Could not load country dossier" message={error} onRetry={fetchProfile} />}

      {/* Country KPI Summary Grid */}
      <SectionHeader
        title="Demographic & Socioeconomic Indicators"
        subtitle={`Summary metrics for ${profileData?.country_name || selectedCountry} in census round ${selectedYear}`}
        badge={`${selectedYear}`}
      />

      <div className="kpi-grid">
        <KPICard
          title="Residing Migrant Stock"
          value={profileData ? formatNumber(profileData.immigrant_stock) : undefined}
          subtitle="Foreign-born residents living in this country (Inbound)"
          icon={Globe}
          accent="blue"
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title="Migrant Share of Population"
          value={profileData ? formatPercent(profileData.migrant_pct_population) : undefined}
          subtitle="Proportion of total national population"
          icon={Users}
          accent="teal"
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title="Emigrant Diaspora Abroad"
          value={profileData ? formatNumber(profileData.emigrant_stock) : undefined}
          subtitle="Native diaspora residing in other countries (Outbound)"
          icon={ArrowRightLeft}
          accent="amber"
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title="Net Migrant Stock Balance"
          value={profileData ? formatNumber(profileData.net_migrant_stock) : undefined}
          subtitle={
            profileData
              ? profileData.net_migrant_stock >= 0
                ? 'Net destination / host nation (+)'
                : 'Net origin / diaspora nation (-)'
              : 'Net balance'
          }
          icon={Scale}
          accent={profileData && profileData.net_migrant_stock >= 0 ? 'emerald' : 'rose'}
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title="Total Population"
          value={profileData ? formatNumber(profileData.total_population) : undefined}
          subtitle="National population count (World Bank)"
          icon={Flag}
          accent="blue"
          isMono={true}
          isLoading={isLoading}
        />

        <KPICard
          title="GDP per Capita"
          value={profileData ? formatCurrency(profileData.gdp_per_capita) : undefined}
          subtitle="Current USD per capita (World Bank WDI)"
          icon={DollarSign}
          accent="teal"
          isMono={true}
          isLoading={isLoading}
        />
      </div>

      {/* Historical Trajectory Line Chart */}
      <div style={{ marginTop: 'var(--section-gap)' }}>
        <SectionHeader
          title="Historical Migrant Stock Trajectory (1990–2020)"
          subtitle={`30-year evolution of foreign-born population residing in ${profileData?.country_name || selectedCountry}`}
          badge="1990–2020"
        />

        <div className="card" style={{ padding: 'var(--card-padding)', marginBottom: 'var(--section-gap)' }}>
          {isLoading ? (
            <LoadingState message="Loading historical time series..." />
          ) : (
            <LineChart
              series={historySeries}
              xTitle="UN DESA Census Round"
              yTitle="Immigrant Stock (People)"
              height={360}
            />
          )}
        </div>
      </div>

      {/* Inbound & Outbound Corridors Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 'var(--grid-gap)' }}>
        {/* Top 10 Inbound Origins */}
        <div>
          <SectionHeader
            title="Top 10 Inbound Origins"
            subtitle={`Leading source nations of foreign-born residing in ${profileData?.country_name || selectedCountry}`}
            badge="Inbound"
          />
          <div className="card" style={{ padding: 'var(--card-padding)' }}>
            {isLoading ? (
              <LoadingState message="Loading inbound origins..." />
            ) : inboundCategories.length > 0 ? (
              <BarChart
                categories={inboundCategories}
                values={inboundValues}
                xTitle="Migrant Stock (People)"
                orientation="h"
                color="#0284c7"
                height={380}
              />
            ) : (
              <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
                No inbound corridor records available.
              </div>
            )}
          </div>
        </div>

        {/* Top 10 Outbound Diaspora Destinations */}
        <div>
          <SectionHeader
            title="Top 10 Outbound Destinations"
            subtitle={`Leading host destinations for diaspora from ${profileData?.country_name || selectedCountry}`}
            badge="Outbound"
          />
          <div className="card" style={{ padding: 'var(--card-padding)' }}>
            {isLoading ? (
              <LoadingState message="Loading outbound destinations..." />
            ) : outboundCategories.length > 0 ? (
              <BarChart
                categories={outboundCategories}
                values={outboundValues}
                xTitle="Diaspora Stock (People)"
                orientation="h"
                color="#0d9488"
                height={380}
              />
            ) : (
              <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
                No outbound diaspora records available.
              </div>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
