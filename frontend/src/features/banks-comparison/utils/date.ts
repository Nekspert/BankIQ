export const getMonthRange = (monthValue: string | null) => {
  if (!monthValue) return { from: null, to: null };
  const [yStr, mStr] = monthValue.split('-');
  const year = Number(yStr);
  const month = Number(mStr);

  const from = `${String(year).padStart(4,'0')}-${String(month).padStart(2,'0')}-01T00:00:00`;

  const lastDay = new Date(year, month, 0).getDate();
  const to = `${String(year).padStart(4,'0')}-${String(month).padStart(2,'0')}-${String(lastDay).padStart(2,'0')}T23:59:59`;

  return { from, to };
};
