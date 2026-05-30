'use client';

import { useState, useCallback } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T) => void, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const item = localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T) => {
      try {
        setStoredValue(value);
        localStorage.setItem(key, JSON.stringify(value));
      } catch (error) {
        console.error(`useLocalStorage: failed to set key "${key}"`, error);
      }
    },
    [key],
  );

  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`useLocalStorage: failed to remove key "${key}"`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}
