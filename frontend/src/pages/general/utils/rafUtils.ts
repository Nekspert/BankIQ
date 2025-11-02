export const createRafSetter = <T extends string>(
  setter: (value: T) => void
) => {
  let rafId: number | null = null;
  let lastValue: T | null = null;

  return (value: T) => {
    if (value === lastValue) return;
    lastValue = value;

    if (rafId) cancelAnimationFrame(rafId);

    rafId = requestAnimationFrame(() => {
      setter(value);
    });
  };
};
