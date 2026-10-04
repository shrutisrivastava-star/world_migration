import React from 'react';
import { YearSelector } from './YearSelector';
import { StatusBadge } from './StatusBadge';

export function Header({ title = 'Overview & Executive KPIs' }) {
  return (
    <header className="header">
      <div className="header-left">
        <div className="header-title-container">
          <h2 className="header-page-title">{title}</h2>
          <span className="header-dataset-badge">UN DESA 2020 Revision &bull; World Bank WDI (1990–2020)</span>
        </div>
      </div>
      <div className="header-right">
        <YearSelector />
        <StatusBadge />
      </div>
    </header>
  );
}
