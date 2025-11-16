import { useState } from 'react';
/**
 * Хук для управления диапазоном лет (от / до).
 *
 * Предоставляет состояние с выбранными годами и функцию для их обновления.
 * Удобен для фильтров и компонентов выбора диапазона дат.
 *
 * @hook
 * @param {number} initialFrom - Начальный год диапазона.
 * @param {number} initialTo - Конечный год диапазона.
 *
 * @returns {{
 *   dateRange: { from_year: number; to_year: number };
 *   handleDateChange: (from: number, to: number) => void;
 * }} Объект с текущим диапазоном лет и функцией обновления.
 *
 * @example
 * ```ts
 * const { dateRange, handleDateChange } = useDateRange(2015, 2024);
 *
 * console.log(dateRange); // { from_year: 2015, to_year: 2024 }
 *
 * handleDateChange(2018, 2023);
 * // dateRange теперь { from_year: 2018, to_year: 2023 }
 * ```
 */

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
