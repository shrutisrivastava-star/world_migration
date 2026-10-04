import React, { useEffect } from 'react';
import { MainLayout } from './layouts/MainLayout';
import { useAppContext } from './hooks/useAppContext';

import { OverviewPage } from './pages/OverviewPage';
import { GlobalMapPage } from './pages/GlobalMapPage';
import { TrendsPage } from './pages/TrendsPage';
import { RankingsPage } from './pages/RankingsPage';
import { RoutesPage } from './pages/RoutesPage';
import { CountryPage } from './pages/CountryPage';
import { CorridorsPage } from './pages/CorridorsPage';
import { NetworkPage } from './pages/NetworkPage';
import { CommunitiesPage } from './pages/CommunitiesPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { InsightsPage } from './pages/InsightsPage';
import { MethodologyPage } from './pages/MethodologyPage';

export function App() {
  const { activeRoute, setActiveRoute } = useAppContext();

  // Listen to browser hash change events
  useEffect(() => {
    function handleHashChange() {
      const hash = window.location.hash.replace('#', '') || '/overview';
      setActiveRoute(hash);
    }

    if (window.location.hash) {
      handleHashChange();
    }

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [setActiveRoute]);

  // Route selector
  const renderCurrentPage = () => {
    switch (activeRoute) {
      case '/':
      case '/overview':
        return <OverviewPage />;
      case '/global-map':
        return <GlobalMapPage />;
      case '/trends':
        return <TrendsPage />;
      case '/rankings':
        return <RankingsPage />;
      case '/routes':
        return <RoutesPage />;
      case '/country':
        return <CountryPage />;
      case '/corridors':
        return <CorridorsPage />;
      case '/network':
        return <NetworkPage />;
      case '/communities':
        return <CommunitiesPage />;
      case '/analytics':
        return <AnalyticsPage />;
      case '/comparison':
        return <ComparisonPage />;
      case '/insights':
        return <InsightsPage />;
      case '/methodology':
        return <MethodologyPage />;
      default:
        return <OverviewPage />;
    }
  };

  return <MainLayout>{renderCurrentPage()}</MainLayout>;
}

export default App;
