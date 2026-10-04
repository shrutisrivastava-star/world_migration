import React from 'react';

export function Select({
  label,
  value,
  onChange,
  options = [],
  disabled = false,
  id,
  className = '',
  ...props
}) {
  const selectId = id || (label ? label.toLowerCase().replace(/[^a-z0-9]/g, '-') : 'select-control');

  return (
    <div className={`select-wrapper ${className}`}>
      {label && (
        <label htmlFor={selectId} className="select-label">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className="select-control"
        value={value}
        onChange={onChange}
        disabled={disabled}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
