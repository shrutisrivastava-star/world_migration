import React from 'react';

export function KPICard({
  title,
  value,
  subtitle,
  trend,
  icon: Icon,
  accent = 'blue',
  variant,
  isLoading = false,
  isMono = false,
  className = '',
}) {
  const accentClass = variant || accent || 'blue';

  if (isLoading) {
    return (
      <div className={`kpi-card ${className}`}>
        <div className={`kpi-card-accent-strip ${accentClass}`} />
        <div className="kpi-card-header">
          <div className="skeleton" style={{ width: '45%', height: 14 }} />
          <div className="skeleton" style={{ width: 28, height: 28, borderRadius: 'var(--radius-sm)' }} />
        </div>
        <div className="skeleton" style={{ width: '70%', height: 36, margin: '8px 0' }} />
        <div className="skeleton" style={{ width: '90%', height: 14 }} />
      </div>
    );
  }

  return (
    <div className={`kpi-card ${className}`}>
      <div className={`kpi-card-accent-strip ${accentClass}`} />
      
      <div className="kpi-card-header">
        <span className="kpi-card-title">{title}</span>
        {Icon && (
          <div className="kpi-card-icon-wrap">
            <Icon className="kpi-card-icon" />
          </div>
        )}
      </div>

      <div className={`kpi-card-value ${isMono ? 'mono' : ''}`}>
        {value !== undefined && value !== null ? value : 'N/A'}
      </div>

      {trend && (
        <div style={{ marginBottom: 'var(--space-1-5)' }}>
          <span className={`kpi-card-trend ${trend.positive ? 'positive' : 'negative'}`}>
            {trend.value}
          </span>
          {trend.label && (
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginLeft: 6 }}>
              {trend.label}
            </span>
          )}
        </div>
      )}

      {subtitle && <div className="kpi-card-subtitle">{subtitle}</div>}
    </div>
  );
}
