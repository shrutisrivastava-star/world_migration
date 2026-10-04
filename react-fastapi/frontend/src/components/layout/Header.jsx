import React from 'react';
import { Menu, Sun, Moon } from 'lucide-react';
import { useAppContext } from '../../hooks/useAppContext';
import { useTheme } from '../../hooks/useTheme';
import { StatusBadge } from '../common/StatusBadge';
import { Select } from '../common/Select';

export function Header({ title = 'Global Migration Observatory' }) {
  const { selectedYear, setSelectedYear, availableYears, setMobileNavOpen } = useAppContext();
  const { theme, toggleTheme } = useTheme();

  const yearOptions = availableYears.map((yr) => ({
    value: yr,
    label: String(yr),
  }));

  return (
    <header className="header">
      <div className="header-left">
        <button
          type="button"
          className="btn-icon mobile-menu-btn"
          onClick={() => setMobileNavOpen(true)}
          aria-label="Open Navigation Menu"
        >
          <Menu style={{ width: 20, height: 20 }} />
        </button>

        <div>
          <h1 className="header-heading-title" style={{ margin: 0, fontSize: 'var(--text-base)' }}>
            {title}
          </h1>
          <span className="header-heading-dataset">
            UN DESA 2020 Rev. &bull; World Bank WDI (1990–2020)
          </span>
        </div>
      </div>

      <div className="header-right">
        <Select
          label="Round:"
          value={selectedYear}
          onChange={(e) => setSelectedYear(e.target ? e.target.value : e)}
          options={yearOptions}
          aria-label="Select Census Observation Round"
        />

        <StatusBadge />

        <button
          type="button"
          className="btn-icon"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          aria-label={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? (
            <Sun style={{ width: 18, height: 18, color: 'var(--accent-amber)' }} />
          ) : (
            <Moon style={{ width: 18, height: 18, color: 'var(--text-muted)' }} />
          )}
        </button>
      </div>
    </header>
  );
}
