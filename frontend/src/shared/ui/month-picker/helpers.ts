import { format } from 'date-fns';

export const toDate = (ym: string | null): Date | null => {
  if (!ym) return null;
  const [y, m] = ym.split('-').map(Number);
  return new Date(y, m - 1, 1);
};

export const toYYYYMM = (d: Date | null): string | null => {
  if (!d) return null;
  return format(d, 'yyyy-MM');
};
