import React, { createContext, useState, useEffect, useCallback } from 'react';
import { getHealth, getYears, getCountries, getOverview } from '../services/api';

export const AppContext = createContext(null);

const THEME_STORAGE_KEY = 'gmo_theme';
export const VALID_CENSUS_YEARS = [1990, 1995, 2000, 2005, 2010, 2015, 2020];
export const DEFAULT_CENSUS_YEAR = 2020;

/**
 * Defensive normalizer ensuring census year is always a valid integer.
 */
export function normalizeYear(val, fallback = DEFAULT_CENSUS_YEAR) {
  if (val === null || val === undefined || val === '') return fallback;
  // If val is an event object (e.g. from an unextracted onChange handler)
  const raw = typeof val === 'object' && val !== null && 'target' in val ? val.target.value : val;
  const parsed = Number(raw);
  if (isNaN(parsed) || !isFinite(parsed)) return fallback;
  if (VALID_CENSUS_YEARS.includes(parsed)) return parsed;
  if (parsed >= 1990 && parsed <= 2020) {
    return VALID_CENSUS_YEARS.reduce((prev, curr) =>
      Math.abs(curr - parsed) < Math.abs(prev - parsed) ? curr : prev
    );
  }
  return fallback;
}

export function AppProvider({ children }) {
  // Navigation & Shell State
  const [activeRoute, setActiveRoute] = useState('/overview');
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  // Theme Management (Light / Dark)
  const [theme, setThemeState] = useState(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    // Fallback to system preference
    if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  // Apply theme to DOM and persist
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const setTheme = useCallback((newTheme) => {
    if (newTheme === 'light' || newTheme === 'dark') {
      setThemeState(newTheme);
    }
  }, []);

  // Scientific Observation Data State
  const [selectedYear, setSelectedYearState] = useState(DEFAULT_CENSUS_YEAR);
  const [availableYears, setAvailableYears] = useState(VALID_CENSUS_YEARS);
  const [backendHealth, setBackendHealth] = useState({
    status: 'connecting', // 'connecting' | 'connected' | 'error'
    data: null,
    error: null,
  });

  const setSelectedYear = useCallback((newYear) => {
    const safeYear = normalizeYear(newYear, DEFAULT_CENSUS_YEAR);
    setSelectedYearState(safeYear);
  }, []);

  const [overviewData, setOverviewData] = useState(null);
  const [isLoadingOverview, setIsLoadingOverview] = useState(true);
  const [overviewError, setOverviewError] = useState(null);

  const [countries, setCountries] = useState([]);
  const [isLoadingCountries, setIsLoadingCountries] = useState(false);

  // Check health and load available observation years on mount
  useEffect(() => {
    let isMounted = true;

    async function initSystem() {
      try {
        const [healthRes, yearsRes] = await Promise.all([getHealth(), getYears()]);
        if (isMounted) {
          setBackendHealth({ status: 'connected', data: healthRes, error: null });
          if (yearsRes && Array.isArray(yearsRes.years)) {
            const validFetched = yearsRes.years.filter((y) => VALID_CENSUS_YEARS.includes(Number(y)));
            if (validFetched.length > 0) {
              setAvailableYears(validFetched);
            }
          }
        }
      } catch (err) {
        if (isMounted) {
          setBackendHealth({ status: 'error', data: null, error: err.message });
        }
      }
    }

    initSystem();
    const interval = setInterval(initSystem, 30000); // Polling health every 30s
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Fetch overview whenever selectedYear changes
  const fetchOverview = useCallback(async (year) => {
    const validYear = normalizeYear(year, DEFAULT_CENSUS_YEAR);
    setIsLoadingOverview(true);
    setOverviewError(null);
    try {
      const data = await getOverview(validYear);
      setOverviewData(data);
    } catch (err) {
      setOverviewError(err.message);
    } finally {
      setIsLoadingOverview(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview(selectedYear);
  }, [selectedYear, fetchOverview]);

  // Fetch countries list on mount
  useEffect(() => {
    let isMounted = true;
    async function loadCountries() {
      setIsLoadingCountries(true);
      try {
        const res = await getCountries(false);
        if (isMounted && res && res.countries) {
          setCountries(res.countries);
        }
      } catch (err) {
        console.error('Failed to load countries:', err);
      } finally {
        if (isMounted) setIsLoadingCountries(false);
      }
    }
    loadCountries();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <AppContext.Provider
      value={{
        activeRoute,
        setActiveRoute,
        mobileNavOpen,
        setMobileNavOpen,
        theme,
        setTheme,
        toggleTheme,
        selectedYear,
        setSelectedYear,
        availableYears,
        backendHealth,
        overviewData,
        isLoadingOverview,
        overviewError,
        countries,
        isLoadingCountries,
        refreshOverview: () => fetchOverview(selectedYear),
      }}
    >
      {children}
    </AppContext.Provider>
  );
}
