import React from 'react';
import { useAppContext } from '../../hooks/useAppContext';

export function StatusBadge({ className = '' }) {
  const { backendHealth } = useAppContext();

  let label = 'Connecting...';
  let badgeClass = 'connecting';

  if (backendHealth.status === 'connected') {
    label = 'FastAPI Connected';
    badgeClass = 'connected';
  } else if (backendHealth.status === 'error') {
    label = 'Backend Offline';
    badgeClass = 'error';
  }

  return (
    <div
      className={`status-badge ${badgeClass} ${className}`}
      title={backendHealth.error || 'FastAPI Service Operational on port 8000'}
      role="status"
      aria-live="polite"
    >
      <span className="status-dot" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
