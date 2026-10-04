/**
 * Formatting utilities for demographic stock numbers, percentages, and financial indicators.
 */

export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  const val = Number(num);
  const abs = Math.abs(val);

  if (abs >= 1e9) {
    return (val / 1e9).toFixed(decimals) + ' B';
  }
  if (abs >= 1e6) {
    return (val / 1e6).toFixed(decimals) + ' M';
  }
  if (abs >= 1e3 && abs < 1e5) {
    return (val / 1e3).toFixed(1) + ' K';
  }
  return val.toLocaleString(undefined, { maximumFractionDigits: decimals });
}

export function formatCompactNumber(num, decimals = 2) {
  return formatNumber(num, decimals);
}

export function formatInteger(num) {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return Math.round(Number(num)).toLocaleString();
}

export function formatPercent(num, decimals = 2) {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return Number(num).toFixed(decimals) + '%';
}

export function formatCurrency(num, decimals = 0) {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return '$' + Number(num).toLocaleString(undefined, { maximumFractionDigits: decimals });
}
