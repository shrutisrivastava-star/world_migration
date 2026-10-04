import React from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { MobileNav } from '../components/layout/MobileNav';
import { useAppContext } from '../hooks/useAppContext';

const ROUTE_TITLES = {
  '/': 'Executive Overview',
  '/overview': 'Executive Overview',
  '/global-map': 'Global Choropleth Map',
  '/trends': 'Longitudinal Trends (1990–2020)',
  '/rankings': 'Global Country Rankings',
  '/routes': 'Bilateral Route Explorer',
  '/country': 'Country Demographics Profile',
  '/network': 'Migration Network Topology',
  '/corridors': 'Bilateral Corridor Analysis',
  '/communities': 'Community Detection',
  '/analytics': 'Advanced Analytics',
  '/comparison': 'Country Comparison',
  '/insights': 'Migration Insights',
  '/methodology': 'Scientific Methodology',
};

export function MainLayout({ children }) {
  const { activeRoute } = useAppContext();
  const pageTitle = ROUTE_TITLES[activeRoute] || 'Global Migration Observatory';

  return (
    <div className="app-container">
      <Sidebar />
      <MobileNav />
      <div className="main-wrapper">
        <Header title={pageTitle} />
        <main id="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
