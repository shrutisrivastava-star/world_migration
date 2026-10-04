import React from 'react';

export function Card({ title, value, subtitle, accent = 'blue', children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {accent && <div className={`card-accent-strip ${accent}`} />}
      {title && <div className="card-title">{title}</div>}
      {value !== undefined && <div className="card-value">{value}</div>}
      {subtitle && <div className="card-subtitle">{subtitle}</div>}
      {children}
    </div>
  );
}
