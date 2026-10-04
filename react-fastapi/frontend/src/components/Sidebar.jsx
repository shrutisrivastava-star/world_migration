import React from 'react';
import {
  LayoutDashboard,
  Globe,
  TrendingUp,
  BarChart3,
  GitFork,
  Flag,
  Share2,
  ArrowRightLeft,
  Users,
  LineChart,
  Scale,
  Sparkles,
  BookOpen,
} from 'lucide-react';
import { useAppContext } from '../hooks/useAppContext';

const NAV_ITEMS = [
  {
    section: 'Macro Observatory',
    items: [
      { path: '/overview', label: 'Overview & KPIs', icon: LayoutDashboard },
      { path: '/global-map', label: 'Global Choropleth Map', icon: Globe },
      { path: '/trends', label: 'Historical Trends', icon: TrendingUp },
      { path: '/rankings', label: 'Country Rankings', icon: BarChart3 },
    ],
  },
  {
    section: 'Corridor Dynamics',
    items: [
      { path: '/routes', label: 'Migration Routes', icon: GitFork },
      { path: '/country', label: 'Country Explorer', icon: Flag },
      { path: '/corridors', label: 'Bilateral Corridors', icon: ArrowRightLeft },
    ],
  },
  {
    section: 'Network & Modeling',
    items: [
      { path: '/network', label: 'Network Graph', icon: Share2 },
      { path: '/communities', label: 'Community Detection', icon: Users },
      { path: '/analytics', label: 'Advanced Analytics', icon: LineChart },
      { path: '/comparison', label: 'Country Comparison', icon: Scale },
      { path: '/insights', label: 'Automated Insights', icon: Sparkles },
    ],
  },
  {
    section: 'Information',
    items: [
      { path: '/methodology', label: 'Methodology & Terms', icon: BookOpen },
    ],
  },
];

export function Sidebar() {
  const { activeRoute, setActiveRoute } = useAppContext();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo-icon">🌍</span>
        <div className="sidebar-brand">
          <span className="sidebar-title">Global Migration</span>
          <span className="sidebar-subtitle">React / Vite Edition</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((section, idx) => (
          <div key={idx}>
            <div className="nav-section-label">{section.section}</div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = activeRoute === item.path || (item.path === '/overview' && activeRoute === '/');
              return (
                <a
                  key={item.path}
                  href={`#${item.path}`}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveRoute(item.path);
                    window.location.hash = item.path;
                  }}
                >
                  <Icon className="nav-icon" />
                  <span className="nav-label">{item.label}</span>
                </a>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div>Phase 1 &bull; v1.0.0</div>
        <div style={{ fontSize: '0.65rem', color: '#475569', marginTop: '0.2rem' }}>UN DESA Mid-Year Stock</div>
      </div>
    </aside>
  );
}
