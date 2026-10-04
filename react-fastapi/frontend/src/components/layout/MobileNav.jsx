import React from 'react';
import { X, Sun, Moon } from 'lucide-react';
import { useAppContext } from '../../hooks/useAppContext';
import { useTheme } from '../../hooks/useTheme';
import { NAVIGATION_SECTIONS } from './Sidebar';

export function MobileNav() {
  const { mobileNavOpen, setMobileNavOpen, activeRoute, setActiveRoute } = useAppContext();
  const { theme, toggleTheme } = useTheme();

  if (!mobileNavOpen) return null;

  const handleNavClick = (path) => {
    setActiveRoute(path);
    window.location.hash = path;
    setMobileNavOpen(false);
  };

  return (
    <div
      className="mobile-nav-overlay"
      onClick={() => setMobileNavOpen(false)}
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation"
    >
      <div className="mobile-nav-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="mobile-nav-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <span style={{ fontSize: '1.25rem' }}>🌍</span>
            <span style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-bold)', color: '#ffffff' }}>
              Migration Observatory
            </span>
          </div>

          <button
            type="button"
            className="btn-icon"
            onClick={() => setMobileNavOpen(false)}
            aria-label="Close navigation"
          >
            <X style={{ width: 18, height: 18 }} />
          </button>
        </div>

        <nav style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-4) var(--space-3)' }}>
          {NAVIGATION_SECTIONS.map((group, groupIdx) => (
            <div key={groupIdx} style={{ marginBottom: 'var(--space-4)' }}>
              <div className="nav-group-title">{group.title}</div>
              <div className="nav-group-items">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeRoute === item.path || (item.path === '/overview' && activeRoute === '/');
                  return (
                    <a
                      key={item.path}
                      href={`#${item.path}`}
                      className={`nav-link ${isActive ? 'active' : ''}`}
                      onClick={(e) => {
                        e.preventDefault();
                        handleNavClick(item.path);
                      }}
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
          <span>Theme Mode</span>
          <button
            type="button"
            className="btn-icon"
            onClick={toggleTheme}
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun style={{ width: 16, height: 16, color: '#fbbf24' }} /> : <Moon style={{ width: 16, height: 16 }} />}
          </button>
        </div>
      </div>
    </div>
  );
}
