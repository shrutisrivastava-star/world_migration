/**
 * Scientific terminology definitions and metric metadata (UN DESA 2020 Revision & World Bank WDI).
 */

export const MAP_METRIC_OPTIONS = [
  { value: 'Migrant Stock', label: 'Migrant Stock (Total Count)' },
  { value: 'Migrant Stock % of Population', label: 'Migrant Stock (% of Population)' },
  { value: 'GDP per Capita', label: 'GDP per Capita (Current USD)' },
  { value: 'Population', label: 'Total Population' },
];

export const RANKINGS_METRIC_OPTIONS = [
  { value: 'Migrant Stock', label: 'Migrant Stock' },
  { value: 'Migrant Stock % of Population', label: 'Migrant Stock (% of Pop)' },
  { value: 'Population', label: 'Population' },
  { value: 'GDP per Capita', label: 'GDP per Capita' },
];

export const TRENDS_METRIC_OPTIONS = [
  { value: 'Migrant Stock', label: 'Total Migrant Stock' },
  { value: 'Migrant Stock % of Population', label: 'Migrant Stock (% of Pop)' },
  { value: 'GDP per Capita', label: 'GDP per Capita (USD)' },
];

export const SCIENTIFIC_DEFINITIONS = {
  MIGRANT_STOCK:
    'International migrant stock is strictly defined as the estimated count of foreign-born individuals (or foreign citizens where place of birth is unavailable) residing in a country or area at mid-year. It represents accumulated demographic presence, NOT annual migration flows, yearly visa grants, or border crossings.',
  QUINQUENNIAL_ROUNDS:
    'Observations are conducted at standardized 5-year census intervals (1990, 1995, 2000, 2005, 2010, 2015, 2020) by the United Nations Population Division.',
  BILATERAL_CORRIDORS:
    'Bilateral corridors capture the estimated matrix of foreign-born individuals from a specific sovereign origin residing within a specific destination state.',
};
