import React from 'react';
import {
  TrendingUp,
  PieChart,
  Activity,
  ArrowRightLeft,
  Link2,
  Share2,
  Globe,
  Sparkles,
} from 'lucide-react';

const CATEGORY_ICONS = {
  'Global Trend': Globe,
  'Concentration': PieChart,
  'Fastest Growth': TrendingUp,
  'Largest Changes': Activity,
  'Major Corridors': ArrowRightLeft,
  'Socioeconomic Associations': Link2,
  'Network Structure': Share2,
};

const CATEGORY_ACCENTS = {
  'Global Trend': 'var(--primary)',
  'Concentration': 'var(--accent-violet)',
  'Fastest Growth': 'var(--accent-teal)',
  'Largest Changes': 'var(--accent-amber)',
  'Major Corridors': 'var(--primary)',
  'Socioeconomic Associations': 'var(--accent-violet)',
  'Network Structure': 'var(--accent-teal)',
};

export function InsightCard({ insight, className = '' }) {
  if (!insight) return null;

  const Icon = CATEGORY_ICONS[insight.category] || Sparkles;
  const accentColor = CATEGORY_ACCENTS[insight.category] || 'var(--primary)';

  return (
    <div
      className={`card insight-card ${className}`}
      style={{
        borderLeft: `4px solid ${accentColor}`,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
        padding: 'var(--card-padding)',
        minHeight: '200px',
      }}
    >
      <div>
        {/* Header with Category & Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 'var(--space-2)',
            gap: 'var(--space-2)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Icon size={16} style={{ color: accentColor }} />
            <span
              style={{
                fontSize: 'var(--text-xs)',
                fontWeight: 'var(--weight-bold)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: accentColor,
              }}
            >
              {insight.category}
            </span>
          </div>

          <span
            className="badge badge-subtle"
            style={{ fontSize: 'var(--text-2xs)', padding: '2px 8px' }}
          >
            {insight.year} Round
          </span>
        </div>

        {/* Title */}
        <h4
          style={{
            margin: '0 0 var(--space-2) 0',
            fontSize: 'var(--text-base)',
            fontWeight: 'var(--weight-bold)',
            color: 'var(--text-main)',
            lineHeight: 'var(--leading-snug)',
          }}
        >
          {insight.title}
        </h4>

        {/* Narrative */}
        <p
          style={{
            margin: 0,
            fontSize: 'var(--text-sm)',
            color: 'var(--text-secondary)',
            lineHeight: 'var(--leading-relaxed)',
          }}
        >
          {insight.message}
        </p>
      </div>

      {/* Supporting Metric Badge Footer */}
      {insight.badge && (
        <div
          style={{
            marginTop: 'var(--space-4)',
            paddingTop: 'var(--space-2)',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-2)',
          }}
        >
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
            Observed Signal:
          </span>
          <span
            className="badge badge-primary"
            style={{ fontSize: 'var(--text-xs)', fontWeight: 'var(--weight-semibold)' }}
          >
            {insight.badge}
          </span>
        </div>
      )}
    </div>
  );
}
