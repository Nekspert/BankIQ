'use client';

import { useState, useEffect, useCallback } from 'react';

export const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [state, setState] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setLocalStorageState = useCallback(
    (value: T | ((prev: T) => T)) => {
      setState((prev) => {
        const newValue =
          typeof value === 'function' ? (value as Function)(prev) : value;
        try {
          localStorage.setItem(key, JSON.stringify(newValue));
        } catch {}
        return newValue;
      });
    },
    [key]
  );

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch {}
  }, [key, state]);

  return [state, setLocalStorageState] as const;
};
