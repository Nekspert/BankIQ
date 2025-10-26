import { useState } from 'react';

export const useDateRange = (initialFrom: number, initialTo: number) => {
  const [dateRange, setDateRange] = useState({
    from_year: initialFrom,
    to_year: initialTo,
  });

  const handleDateChange = (from: number, to: number) => {
    setDateRange({ from_year: from, to_year: to });
  };

  return { dateRange, handleDateChange };
};
