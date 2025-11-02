import { useEffect, useRef } from 'react';
import scrollama, { type ScrollamaInstance, type DecimalType } from 'scrollama';

interface UseScrollamaObserverProps {
  stepSelector: string;
  offset?: DecimalType;
  onStepEnter?: (id: string) => void;
  containerId?: string;
}

export const useScrollamaObserver = ({
  stepSelector,
  offset = 0.48 as DecimalType,
  onStepEnter,
  containerId,
}: UseScrollamaObserverProps) => {
  const scrollerRef = useRef<ScrollamaInstance | null>(null);

  useEffect(() => {
    const sc = scrollama();
    scrollerRef.current = sc;

    sc.setup({
      step: stepSelector,
      offset,
      progress: false,
      // container: containerId ? `#${containerId}` : undefined,
    }).onStepEnter((response) => {
      if (!response?.element?.id) return;
      onStepEnter?.(response.element.id);
    });

    const handleResize = () => sc.resize();
    window.addEventListener('resize', handleResize, { passive: true });
    sc.resize();

    return () => {
      try {
        sc.destroy();
      } catch {}
      window.removeEventListener('resize', handleResize);
    };
  }, [stepSelector, offset, onStepEnter, containerId]);

  return scrollerRef;
};
