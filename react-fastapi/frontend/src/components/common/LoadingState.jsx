import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingState({ message = 'Loading empirical datasets from backend...', className = '' }) {
  return (
    <div className={`loading-container ${className}`} role="status">
      <Loader2 className="animate-spin" style={{ width: 28, height: 28, color: 'var(--primary)' }} />
      <div style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-medium)', color: 'var(--text-muted)' }}>
        {message}
      </div>
    </div>
  );
}

export function SkeletonLine({ width = '100%', height = 16, style = {} }) {
  return <div className="skeleton" style={{ width, height, ...style }} />;
}
