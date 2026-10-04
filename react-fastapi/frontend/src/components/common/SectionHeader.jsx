import React from 'react';

export function SectionHeader({ title, subtitle, badge, action, className = '' }) {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-3)',
        marginBottom: 'var(--space-4)',
        marginTop: 'var(--space-2)',
      }}
    >
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <h3
            style={{
              fontSize: 'var(--text-lg)',
              fontWeight: 'var(--weight-bold)',
              color: 'var(--text-main)',
              margin: 0,
              letterSpacing: '-0.02em',
            }}
          >
            {title}
          </h3>
          {badge && (
            <span
              style={{
                fontSize: 'var(--text-2xs)',
                fontWeight: 'var(--weight-bold)',
                padding: '0.2rem 0.55rem',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'var(--primary-subtle)',
                color: 'var(--primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
              }}
            >
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p
            style={{
              fontSize: 'var(--text-xs)',
              color: 'var(--text-secondary)',
              marginTop: 'var(--space-1)',
              lineHeight: 'var(--leading-normal)',
            }}
          >
            {subtitle}
          </p>
        )}
      </div>

      {action && <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>{action}</div>}
    </div>
  );
}
