import { useAppContext } from './useAppContext';

export function useTheme() {
  const { theme, setTheme, toggleTheme } = useAppContext();
  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
  };
}
