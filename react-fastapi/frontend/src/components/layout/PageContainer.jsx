import React from 'react';

export function PageContainer({
  title,
  subtitle,
  breadcrumb = ['Observatory'],
  action,
  children,
  className = '',
}) {
  return (
    <div className={`page-container ${className}`}>
      {(title || breadcrumb.length > 0) && (
        <div className="page-header">
          {breadcrumb.length > 0 && (
            <nav aria-label="Breadcrumb" className="page-breadcrumb">
              {breadcrumb.map((crumb, idx) => (
                <React.Fragment key={idx}>
                  {idx > 0 && <span className="page-breadcrumb-separator">/</span>}
                  <span className={idx === breadcrumb.length - 1 ? 'page-breadcrumb-current' : ''}>
                    {crumb}
                  </span>
                </React.Fragment>
              ))}
            </nav>
          )}

          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
            <div>
              {title && <h2 className="page-title">{title}</h2>}
              {subtitle && <p className="page-subtitle">{subtitle}</p>}
            </div>
            {action && <div>{action}</div>}
          </div>
        </div>
      )}

      <div className="page-content">{children}</div>
    </div>
  );
}
