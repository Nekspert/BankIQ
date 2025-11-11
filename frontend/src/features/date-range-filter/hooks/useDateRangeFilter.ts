import { useState, useMemo, useEffect } from 'react';

interface UseDateRangeFilterProps {
  initialFromYear: number;
  initialToYear: number;
  minYear: number;
  maxYear?: number;
  onApply: (fromYear: number, toYear: number) => void;
}

interface Option {
  value: string;
  label: string;
}

/**
 * Хук для управления фильтром диапазона годов (например, "от" и "до").
 * Обеспечивает выбор, валидацию и применение диапазона годов с контролем ошибок.
 *
 * @param initialFromYear - Начальный год диапазона (по умолчанию выбран при инициализации)
 * @param initialToYear - Конечный год диапазона (по умолчанию выбран при инициализации)
 * @param minYear - Минимально допустимый год
 * @param maxYear - Максимально допустимый год (по умолчанию — текущий)
 * @param onApply - Колбэк, вызываемый при успешном применении диапазона годов
 *
 * @returns Объект со всеми состояниями и методами управления:
 * - `fromYear`, `toYear` — выбранные значения годов
 * - `setFromYear`, `setToYear` — функции изменения годов
 * - `error` — текст ошибки валидации (если есть)
 * - `years` — все доступные года для выбора
 * - `availableFromYears`, `availableToYears` — отфильтрованные значения годов с учётом диапазона
 * - `validateAndApply` — проверяет введённые значения и вызывает `onApply`, если данные корректны
 * - `handleKeyPress` — обработчик клавиши Enter для подтверждения выбора
 *
 * @example
 * const {
 *   fromYear, toYear, setFromYear, setToYear, validateAndApply, error
 * } = useDateRangeFilter({
 *   initialFromYear: 2015,
 *   initialToYear: 2024,
 *   minYear: 2000,
 *   onApply: (from, to) => console.log(from, to),
 * });
 *
 * @see React.useState - хранение состояний годов и ошибок
 * @see React.useMemo - вычисление списков годов и фильтров
 * @see React.useEffect - синхронизация значений при изменении входных параметров
 */
export const useDateRangeFilter = ({
  initialFromYear,
  initialToYear,
  minYear,
  maxYear = new Date().getFullYear(),
  onApply,
}: UseDateRangeFilterProps) => {
  const [fromYear, setFromYear] = useState<string>(String(initialFromYear));
  const [toYear, setToYear] = useState<string>(String(initialToYear));
  const [error, setError] = useState<string>('');

  const years: Option[] = useMemo(() => {
    const yearsArray: Option[] = [];
    for (let year = minYear; year <= maxYear; year++) {
      yearsArray.push({ value: String(year), label: String(year) });
    }
    return yearsArray;
  }, [minYear, maxYear]);

  const availableToYears = useMemo(() => {
    const from = Number(fromYear);
    return years.filter(
      (year) => !fromYear || isNaN(from) || Number(year.value) >= from
    );
  }, [years, fromYear]);

  const availableFromYears = useMemo(() => {
    const to = Number(toYear);
    return years.filter(
      (year) => !toYear || isNaN(to) || Number(year.value) <= to
    );
  }, [years, toYear]);

  useEffect(() => {
    setFromYear(String(initialFromYear));
    setToYear(String(initialToYear));
  }, [initialFromYear, initialToYear]);

  const validateAndApply = () => {
    const from = Number(fromYear);
    const to = Number(toYear);

    if (!fromYear || !toYear) {
      setError('Выберите оба года');
      return;
    }

    if (isNaN(from) || isNaN(to)) {
      setError('Выберите корректные годы');
      return;
    }

    if (from < minYear) {
      setError(`Минимальный год: ${minYear}`);
      return;
    }

    if (to > maxYear) {
      setError(`Максимальный год: ${maxYear}`);
      return;
    }

    if (from > to) {
      setError('Начальный год не может быть больше конечного');
      return;
    }

    setError('');
    onApply(from, to);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      validateAndApply();
    }
  };

  return {
    fromYear,
    setFromYear,
    toYear,
    setToYear,
    error,
    years,
    availableFromYears,
    availableToYears,
    validateAndApply,
    handleKeyPress,
  };
};
