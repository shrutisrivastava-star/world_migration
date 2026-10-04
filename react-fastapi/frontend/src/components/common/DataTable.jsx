import React from 'react';

export function DataTable({
  columns = [],
  data = [],
  isLoading = false,
  emptyMessage = 'No records found',
  className = '',
}) {
  if (isLoading) {
    return (
      <div className={`table-container ${className}`}>
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={col.key || idx} style={{ width: col.width, textAlign: col.isNumeric ? 'right' : 'left' }}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3, 4, 5].map((rowIdx) => (
              <tr key={rowIdx}>
                {columns.map((col, colIdx) => (
                  <td key={col.key || colIdx} style={{ textAlign: col.isNumeric ? 'right' : 'left' }}>
                    <div className="skeleton" style={{ height: 16, width: col.isNumeric ? '50%' : '80%', marginLeft: col.isNumeric ? 'auto' : 0 }} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={`table-container ${className}`} style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={`table-container ${className}`}>
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th
                key={col.key || idx}
                style={{
                  width: col.width,
                  textAlign: col.isNumeric ? 'right' : 'left',
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {columns.map((col, colIdx) => {
                const rawVal = row[col.key];
                const content = col.render ? col.render(rawVal, row, rowIdx) : rawVal;
                return (
                  <td
                    key={col.key || colIdx}
                    className={`${col.isMono ? 'cell-mono' : ''} ${col.isNumeric ? 'cell-numeric' : ''}`}
                    style={{ textAlign: col.isNumeric ? 'right' : 'left' }}
                  >
                    {content !== undefined && content !== null ? content : '—'}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
