import React from 'react';

export function Tabs({ tabs = [], activeTab, onChange, className = '' }) {
  return (
    <div className={`tabs-container ${className}`} role="tablist">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            className={`tab-item ${isActive ? 'active' : ''}`}
            onClick={() => onChange(tab.id)}
            type="button"
          >
            {Icon && <Icon style={{ width: 15, height: 15, marginRight: 6, display: 'inline' }} />}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
