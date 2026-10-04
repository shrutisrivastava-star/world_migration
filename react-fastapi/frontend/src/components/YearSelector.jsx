import React from 'react';
import { useAppContext } from '../hooks/useAppContext';

export function YearSelector() {
  const { selectedYear, setSelectedYear, availableYears } = useAppContext();

  return (
    <div className="year-selector-container">
      <span className="year-selector-label">Census Round:</span>
      <select
        id="year-select"
        className="year-select"
        value={selectedYear}
        onChange={(e) => setSelectedYear(Number(e.target.value))}
      >
        {availableYears.map((yr) => (
          <option key={yr} value={yr}>
            {yr}
          </option>
        ))}
      </select>
    </div>
  );
}
