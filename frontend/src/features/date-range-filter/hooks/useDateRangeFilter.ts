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
