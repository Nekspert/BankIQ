import { useEffect, useState } from 'react';

export const useDebounce = <T>(value: T, delay = 300) => {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);

  return debounced;
};
