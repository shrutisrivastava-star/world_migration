import React from 'react';
import { useAppContext } from '../hooks/useAppContext';

export function StatusBadge() {
  const { backendHealth } = useAppContext();

  let label = 'Connecting...';
  let badgeClass = 'connecting';

  if (backendHealth.status === 'connected') {
    label = 'Backend Connected';
    badgeClass = 'connected';
  } else if (backendHealth.status === 'error') {
    label = 'Backend Offline';
    badgeClass = 'error';
  }

  return (
    <div className={`status-badge ${badgeClass}`} title={backendHealth.error || 'FastAPI Service Operational'}>
      <span className="status-dot"></span>
      <span>{label}</span>
    </div>
  );
}
