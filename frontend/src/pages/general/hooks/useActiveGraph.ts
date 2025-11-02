import { useRef, useState, useCallback } from 'react';
import { createRafSetter } from '../utils/rafUtils';

export const useActiveGraph = (initialId = '') => {
  const [activeId, setActiveId] = useState<string>(initialId);
  const activeRef = useRef(initialId);

  const setActiveGraphOptimized = useCallback(
    createRafSetter<string>((id: string) => {
      activeRef.current = id;
      setActiveId(id);
    }),
    []
  );

  return { activeId, setActiveGraphOptimized };
};
