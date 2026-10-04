import React from 'react';
import { useAppContext } from '../hooks/useAppContext';

export function PlaceholderPage({ icon: Icon, title, description, plannedPhase = 'Phase 2' }) {
  const { selectedYear } = useAppContext();

  return (
    <div className="placeholder-card">
      <div className="placeholder-icon-wrap">
        {Icon && <Icon style={{ width: 32, height: 32 }} />}
      </div>
      <h3 className="placeholder-title">{title}</h3>
      <p className="placeholder-desc">{description}</p>
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 8 }}>
        <span className="phase-pill">Selected Year: {selectedYear}</span>
        <span className="phase-pill" style={{ backgroundColor: 'var(--primary-light)', borderColor: 'var(--primary)', color: 'var(--primary)' }}>
          Scheduled: {plannedPhase}
        </span>
      </div>
    </div>
  );
}
