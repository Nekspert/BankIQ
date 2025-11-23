export const monthToApiDate = (ym: string | null): string | null => {
  if (!ym) return null;
  const [yStr, mStr] = ym.split('-');
  const y = Number(yStr);
  const m = Number(mStr);
  if (!y || !m) return null;
  return new Date(Date.UTC(y, m - 1, 1, 0, 0, 0)).toISOString();
};
