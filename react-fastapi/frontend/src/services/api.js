/**
 * Centralized API client for Global Migration Observatory backend.
 * Provides typed promise-based query functions for all observatory endpoints
 * with defensive normalization for census years and query parameters.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const VALID_CENSUS_YEARS = [1990, 1995, 2000, 2005, 2010, 2015, 2020];
const DEFAULT_CENSUS_YEAR = 2020;

/**
 * Defensive normalizer ensuring year parameters are always valid integer census rounds.
 */
function sanitizeYear(year) {
  if (year === null || year === undefined || year === '') {
    return DEFAULT_CENSUS_YEAR;
  }
  const raw = typeof year === 'object' && year !== null && 'target' in year ? year.target.value : year;
  const num = Number(raw);
  if (isNaN(num) || !isFinite(num)) {
    return DEFAULT_CENSUS_YEAR;
  }
  if (VALID_CENSUS_YEARS.includes(num)) {
    return num;
  }
  if (num >= 1990 && num <= 2020) {
    return VALID_CENSUS_YEARS.reduce((prev, curr) =>
      Math.abs(curr - num) < Math.abs(prev - num) ? curr : prev
    );
  }
  return DEFAULT_CENSUS_YEAR;
}

/**
 * Generic fetch wrapper handling HTTP status and JSON parsing.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson && errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Fallback to generic status text
      }
      throw new Error(errorDetail);
    }

    return await response.json();
  } catch (error) {
    console.error(`[API Error] ${endpoint}:`, error.message);
    throw error;
  }
}

/**
 * Health check endpoint.
 */
export async function getHealth() {
  return request('/health');
}

/**
 * Retrieve list of UN DESA census observation round years (1990-2020).
 */
export async function getYears() {
  return request('/years');
}

/**
 * Retrieve country and regional entities.
 * @param {boolean} sovereignOnly - If true, filter to only recognized sovereign nations
 */
export async function getCountries(sovereignOnly = false) {
  const query = sovereignOnly ? '?sovereign_only=true' : '';
  return request(`/countries${query}`);
}

/**
 * Retrieve executive migration overview KPIs for a selected census round year.
 * @param {number} year - Census observation year (1990, 1995, 2000, 2005, 2010, 2015, 2020)
 */
export async function getOverview(year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  return request(`/overview?year=${safeYr}`);
}

/**
 * Retrieve global choropleth map country data.
 * @param {number} year - Census round year
 * @param {string} metric - Metric name (e.g. 'Migrant Stock', 'Migrant Stock % of Population')
 */
export async function getMapData(year = DEFAULT_CENSUS_YEAR, metric = 'Migrant Stock') {
  const safeYr = sanitizeYear(year);
  const encodedMetric = encodeURIComponent(metric);
  return request(`/map?year=${safeYr}&metric=${encodedMetric}`);
}

/**
 * Retrieve 1990–2020 global aggregated migrant stock trajectory.
 */
export async function getGlobalTrend() {
  return request('/trends/global');
}

/**
 * Retrieve multi-country comparative longitudinal time series.
 * @param {string[]|string} countries - Array or comma-separated string of ISO3 codes
 * @param {string} metric - Metric name
 */
export async function getCountryTrends(countries = ['USA', 'IND', 'DEU'], metric = 'Migrant Stock') {
  const countryList = Array.isArray(countries) ? countries.join(',') : countries;
  const encodedMetric = encodeURIComponent(metric);
  return request(`/trends/countries?countries=${countryList}&metric=${encodedMetric}`);
}

/**
 * Retrieve ranked sovereign country leaderboards for a census round.
 * @param {number} year - Census round year
 * @param {string} metric - Metric to rank by
 * @param {number} topN - Number of top ranked countries
 * @param {boolean} ascending - Sort ascending if true
 */
export async function getRankings(year = DEFAULT_CENSUS_YEAR, metric = 'Migrant Stock', topN = 10, ascending = false) {
  const safeYr = sanitizeYear(year);
  const encodedMetric = encodeURIComponent(metric);
  const safeTopN = Number.isInteger(Number(topN)) ? Number(topN) : 10;
  return request(`/rankings?year=${safeYr}&metric=${encodedMetric}&top_n=${safeTopN}&ascending=${ascending}`);
}

/**
 * Query bilateral route metrics and top corridors.
 * @param {number} year - Census round year
 * @param {string|null} origin - Origin ISO3 code
 * @param {string|null} destination - Destination ISO3 code
 * @param {number} topN - Max top corridors to return
 */
export async function getRoutes(year = DEFAULT_CENSUS_YEAR, origin = null, destination = null, topN = 20) {
  const safeYr = sanitizeYear(year);
  const params = new URLSearchParams();
  params.append('year', safeYr);
  if (origin && origin !== 'All') params.append('origin', origin);
  if (destination && destination !== 'All') params.append('destination', destination);
  params.append('top_n', topN);
  return request(`/routes?${params.toString()}`);
}

/**
 * Retrieve complete country demographic dossier.
 * @param {string} countryCode - ISO3 country code (e.g. 'USA')
 * @param {number} year - Census round year
 */
export async function getCountryProfile(countryCode = 'USA', year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  return request(`/country/${countryCode}?year=${safeYr}`);
}

/**
 * Retrieve migration network graph, node centralities, and 2D layout coordinates.
 * @param {number} year - Census round year
 * @param {number} topNEdges - Edge threshold
 * @param {number|null} minStock - Minimum stock cutoff
 */
export async function getNetworkOverview(year = DEFAULT_CENSUS_YEAR, topNEdges = 100, minStock = null) {
  const safeYr = sanitizeYear(year);
  const safeTopN = Number.isInteger(Number(topNEdges)) ? Number(topNEdges) : 100;
  const params = new URLSearchParams();
  params.append('year', safeYr);
  params.append('top_n_edges', safeTopN);
  if (minStock !== null && minStock !== undefined && Number(minStock) > 0) {
    params.append('min_stock', Number(minStock));
  }
  return request(`/network?${params.toString()}`);
}

/**
 * Retrieve corridor intelligence overview and top rankings.
 * @param {number} year - Census round year
 * @param {number} topN - Number of top corridors
 */
export async function getCorridorOverview(year = DEFAULT_CENSUS_YEAR, topN = 10) {
  const safeYr = sanitizeYear(year);
  const safeTopN = Number.isInteger(Number(topN)) ? Number(topN) : 10;
  return request(`/corridors/overview?year=${safeYr}&top_n=${safeTopN}`);
}

/**
 * Retrieve 1990–2020 corridor concentration trend points.
 */
export async function getCorridorConcentration() {
  return request('/corridors/concentration');
}

/**
 * Retrieve deep-dive metrics, trajectory, and classification for a bilateral corridor.
 * @param {string} origin - Origin ISO3 code
 * @param {string} destination - Destination ISO3 code
 * @param {number} year - Census round year
 */
export async function getCorridorDetail(origin, destination, year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  return request(`/corridors/detail?origin=${origin}&destination=${destination}&year=${safeYr}`);
}

/**
 * Retrieve modularity-based community detection partition for the migration network.
 * @param {number} year - Census round year
 * @param {number} topNEdges - Edge threshold
 */
export async function getCommunities(year = DEFAULT_CENSUS_YEAR, topNEdges = 150) {
  const safeYr = sanitizeYear(year);
  const safeTopN = Number.isInteger(Number(topNEdges)) ? Number(topNEdges) : 150;
  return request(`/communities?year=${safeYr}&top_n_edges=${safeTopN}`);
}

/**
 * Retrieve detailed breakdown for a specific community cluster.
 * @param {number} communityId - Community ID
 * @param {number} year - Census round year
 * @param {number} topNEdges - Edge threshold
 */
export async function getCommunityDetail(communityId, year = DEFAULT_CENSUS_YEAR, topNEdges = 150) {
  const safeYr = sanitizeYear(year);
  const safeTopN = Number.isInteger(Number(topNEdges)) ? Number(topNEdges) : 150;
  const safeCommId = Number.isInteger(Number(communityId)) ? Number(communityId) : 1;
  return request(`/communities/${safeCommId}?year=${safeYr}&top_n_edges=${safeTopN}`);
}

// =============================================================================
// PHASE 5: ADVANCED ANALYTICS & STORYTELLING
// =============================================================================

/**
 * Retrieve executive summary of advanced analytics for the dashboard.
 * @param {number} year - Census round year
 */
export async function getAnalyticsOverview(year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  return request(`/analytics/overview?year=${safeYr}`);
}

/**
 * Retrieve destination and origin HHI concentration metrics.
 * @param {number} year - Census round year
 */
export async function getConcentration(year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  return request(`/analytics/concentration?year=${safeYr}`);
}

/**
 * Retrieve Pearson and Spearman bivariate correlation statistics.
 * @param {number} year - Census round year
 */
export async function getCorrelations(year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  return request(`/analytics/correlations?year=${safeYr}`);
}

/**
 * Retrieve scatter plot points and regression parameters for two indicators.
 * @param {string} xMetric - X axis column name
 * @param {string} yMetric - Y axis column name
 * @param {number} year - Census round year
 * @param {boolean} logX - Whether to log10 X
 * @param {boolean} logY - Whether to log10 Y
 */
export async function getScatterData(
  xMetric = 'gdp_per_capita',
  yMetric = 'migrant_stock_pct_population',
  year = DEFAULT_CENSUS_YEAR,
  logX = true,
  logY = false
) {
  const safeYr = sanitizeYear(year);
  return request(
    `/analytics/scatter?x_metric=${xMetric}&y_metric=${yMetric}&year=${safeYr}&log_x=${logX}&log_y=${logY}`
  );
}

/**
 * Identify statistical outlier countries using IQR or Z-Score method.
 * @param {number} year - Census round year
 * @param {string} metric - Target metric column name
 * @param {string} method - 'IQR' or 'Z-Score'
 * @param {number} threshold - Outlier threshold multiplier
 */
export async function getOutliers(
  year = DEFAULT_CENSUS_YEAR,
  metric = 'migrant_stock',
  method = 'IQR',
  threshold = 1.5
) {
  const safeYr = sanitizeYear(year);
  return request(
    `/analytics/outliers?year=${safeYr}&metric=${metric}&method=${method}&threshold=${threshold}`
  );
}

/**
 * Retrieve comparative profiling matrix and trajectories for 2–5 countries.
 * @param {string[]|string} countries - Array or comma-separated string of country ISO3 codes
 * @param {number} year - Census round year
 */
export async function getCountryComparison(countries = ['USA', 'IND', 'DEU'], year = DEFAULT_CENSUS_YEAR) {
  const safeYr = sanitizeYear(year);
  const countryList = Array.isArray(countries) ? countries.join(',') : countries;
  return request(`/analytics/compare?year=${safeYr}&countries=${countryList}`);
}

/**
 * Retrieve categorized deterministic rule-based migration insights.
 * @param {number} year - Census round year
 * @param {string} category - Category filter (e.g. 'All', 'Global Trend', 'Concentration', etc.)
 */
export async function getInsights(year = DEFAULT_CENSUS_YEAR, category = 'All') {
  const safeYr = sanitizeYear(year);
  const encodedCat = encodeURIComponent(category);
  return request(`/analytics/insights?year=${safeYr}&category=${encodedCat}`);
}
