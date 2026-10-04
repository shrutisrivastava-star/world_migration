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
  Sun,
  Moon,
} from 'lucide-react';
import { useAppContext } from '../../hooks/useAppContext';
import { useTheme } from '../../hooks/useTheme';

export const NAVIGATION_SECTIONS = [
  {
    title: 'CORE EXPLORER',
    items: [
      { path: '/overview', label: 'Overview', icon: LayoutDashboard },
      { path: '/global-map', label: 'Global Map', icon: Globe },
      { path: '/trends', label: 'Trends', icon: TrendingUp },
      { path: '/rankings', label: 'Rankings', icon: BarChart3 },
      { path: '/routes', label: 'Route Explorer', icon: GitFork },
      { path: '/country', label: 'Country Explorer', icon: Flag },
    ],
  },
  {
    title: 'NETWORK ANALYSIS',
    items: [
      { path: '/network', label: 'Migration Network', icon: Share2 },
      { path: '/corridors', label: 'Corridor Analysis', icon: ArrowRightLeft },
      { path: '/communities', label: 'Communities', icon: Users },
    ],
  },
  {
    title: 'ADVANCED ANALYTICS',
    items: [
      { path: '/analytics', label: 'Advanced Analytics', icon: LineChart },
      { path: '/comparison', label: 'Country Comparison', icon: Scale },
      { path: '/insights', label: 'Migration Insights', icon: Sparkles },
    ],
  },
  {
    title: 'INFORMATION',
    items: [
      { path: '/methodology', label: 'Methodology', icon: BookOpen },
    ],
  },
];

export function Sidebar({ className = '' }) {
  const { activeRoute, setActiveRoute } = useAppContext();
  const { theme, toggleTheme } = useTheme();

  const handleNavClick = (e, path) => {
    e.preventDefault();
    setActiveRoute(path);
    window.location.hash = path;
  };

  return (
    <aside className={`sidebar ${className}`} aria-label="Main Navigation">
      <div className="sidebar-header">
        <span className="sidebar-logo">🌍</span>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span className="sidebar-brand-title">Migration Observatory</span>
          <span className="sidebar-brand-subtitle">React / Vite Edition</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAVIGATION_SECTIONS.map((group, groupIdx) => (
          <div key={groupIdx} className="nav-group">
            <div className="nav-group-title">{group.title}</div>
            <div className="nav-group-items">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeRoute === item.path || (item.path === '/overview' && (activeRoute === '/' || activeRoute === ''));
                return (
                  <a
                    key={item.path}
                    href={`#${item.path}`}
                    className={`nav-link ${isActive ? 'active' : ''}`}
                    onClick={(e) => handleNavClick(e, item.path)}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <Icon className="nav-icon" />
                    <span>{item.label}</span>
                  </a>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span>UN DESA &bull; World Bank</span>
          <span style={{ fontSize: '0.625rem', color: '#64748b' }}>1990–2020 Mid-Year Stock</span>
        </div>
        <button
          type="button"
          className="btn-icon"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          aria-label={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          style={{ width: 32, height: 32, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          {theme === 'dark' ? <Sun style={{ width: 16, height: 16, color: '#fbbf24' }} /> : <Moon style={{ width: 16, height: 16, color: '#64748b' }} />}
        </button>
      </div>
    </aside>
  );
}
