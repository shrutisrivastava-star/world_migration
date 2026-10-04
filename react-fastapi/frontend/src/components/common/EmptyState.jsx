import React from 'react';
import { Database } from 'lucide-react';

export function EmptyState({
  title = 'No Data Available',
  description = 'No empirical records match the current filter criteria or observation year.',
  icon: Icon = Database,
  action,
  className = '',
}) {
  return (
    <div className={`empty-container ${className}`}>
      <div className="empty-icon-wrap">
        <Icon style={{ width: 28, height: 28 }} />
      </div>
      <h4 className="empty-title">{title}</h4>
      <p className="empty-desc">{description}</p>
      {action && <div style={{ marginTop: 'var(--space-2)' }}>{action}</div>}
    </div>
  );
}
