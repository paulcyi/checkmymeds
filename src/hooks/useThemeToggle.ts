'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export function useThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const toggleTheme = () => {
    if (!resolvedTheme) return;
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return {
    isDark: resolvedTheme === 'dark',
    toggleTheme,
    mounted,
    resolvedTheme,
  };
}
