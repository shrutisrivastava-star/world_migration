import React from 'react';
import { PageContainer } from '../layout/PageContainer';
import { useAppContext } from '../../hooks/useAppContext';

export function PlaceholderPage({
  icon: Icon,
  title,
  description,
  breadcrumb = ['Observatory'],
  plannedPhase = 'Phase 3',
}) {
  const { selectedYear } = useAppContext();

  return (
    <PageContainer title={title} subtitle={description} breadcrumb={breadcrumb}>
      <div className="empty-container" style={{ margin: 'var(--space-4) 0' }}>
        <div className="empty-icon-wrap">
          {Icon && <Icon style={{ width: 28, height: 28 }} />}
        </div>
        <h3 className="empty-title">{title}</h3>
        <p className="empty-desc">{description}</p>
        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center', marginTop: 'var(--space-2)' }}>
          <span
            style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 'var(--weight-bold)',
              padding: '0.25rem 0.65rem',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-medium)',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            Round: {selectedYear}
          </span>
          <span
            style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 'var(--weight-bold)',
              padding: '0.25rem 0.65rem',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--primary-subtle)',
              border: '1px solid var(--primary)',
              color: 'var(--primary)',
            }}
          >
            Scheduled for {plannedPhase}
          </span>
        </div>
      </div>
    </PageContainer>
  );
}
