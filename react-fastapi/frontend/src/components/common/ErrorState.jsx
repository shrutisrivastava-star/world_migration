import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export function ErrorState({
  title = 'Data Processing Error',
  message = 'An unexpected error occurred while communicating with the backend API.',
  technicalDetails,
  onRetry,
  className = '',
}) {
  return (
    <div className={`error-container ${className}`} role="alert">
      <AlertCircle className="error-icon" />
      <div style={{ flex: 1 }}>
        <div className="error-title">{title}</div>
        <div className="error-message">{message}</div>
        {technicalDetails && (
          <pre
            style={{
              marginTop: 'var(--space-2)',
              padding: 'var(--space-2)',
              backgroundColor: 'rgba(0,0,0,0.1)',
              borderRadius: 'var(--radius-xs)',
              fontSize: 'var(--text-2xs)',
              fontFamily: 'var(--font-mono)',
              overflowX: 'auto',
            }}
          >
            {technicalDetails}
          </pre>
        )}
        {onRetry && (
          <div style={{ marginTop: 'var(--space-3)' }}>
            <Button
              variant="danger"
              size="sm"
              icon={RefreshCw}
              onClick={onRetry}
            >
              Retry Request
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
