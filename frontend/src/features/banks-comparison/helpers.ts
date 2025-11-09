const pad2 = (n: number) => String(n).padStart(2, '0');

export const monthToDate = (ym: string | null): Date | null => {
  if (!ym) return null;
  const [yStr, mStr] = ym.split('-');
  const y = Number(yStr);
  const m = Number(mStr);
  if (Number.isNaN(y) || Number.isNaN(m)) return null;
  return new Date(y, m - 1, 1);
};

export const dateToYYYYMM = (d: Date) =>
  `${d.getFullYear()}-${pad2(d.getMonth() + 1)}`;
