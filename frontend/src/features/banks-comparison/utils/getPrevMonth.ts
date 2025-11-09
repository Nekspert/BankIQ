export const getPrevMonth = (date: Date | null): string | null => {
  if (!date) return null;
  const year = date.getFullYear();
  const month = date.getMonth();
  const prevMonthDate = new Date(year, month - 1, 1, 0, 0, 0);
  return prevMonthDate.toISOString().split('Z')[0];
};
