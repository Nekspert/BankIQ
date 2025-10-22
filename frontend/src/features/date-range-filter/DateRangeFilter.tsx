import React, { useState, useEffect } from 'react';
import styles from './styles.module.scss';

interface Props {
  initialFromYear: number;
  initialToYear: number;
  minYear: number;
  maxYear?: number;
  onApply: (fromYear: number, toYear: number) => void;
}

export const DateRangeFilter: React.FC<Props> = ({
  initialFromYear,
  initialToYear,
  minYear,
  maxYear = new Date().getFullYear(),
  onApply,
}) => {
  const [fromYear, setFromYear] = useState<string>(String(initialFromYear));
  const [toYear, setToYear] = useState<string>(String(initialToYear));
  const [error, setError] = useState<string>('');

  useEffect(() => {
    setFromYear(String(initialFromYear));
    setToYear(String(initialToYear));
  }, [initialFromYear, initialToYear]);

  const validateAndApply = () => {
    const from = Number(fromYear);
    const to = Number(toYear);

    // Проверка на валидность
    if (!fromYear || !toYear) {
      setError('Заполните оба поля');
      return;
    }

    if (isNaN(from) || isNaN(to)) {
      setError('Введите корректные годы');
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

  return (
    <div className={styles['date-filter']}>
      <div className={styles['date-filter__inputs']}>
        <label className={styles['date-filter__field']}>
          <span className={styles['date-filter__label']}>
            От (мин. {minYear})
          </span>
          <input
            type="number"
            min={minYear}
            max={maxYear}
            value={fromYear}
            onChange={(e) => setFromYear(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={String(minYear)}
            className={styles['date-filter__input']}
          />
        </label>

        <label className={styles['date-filter__field']}>
          <span className={styles['date-filter__label']}>
            До (макс. {maxYear})
          </span>
          <input
            type="number"
            min={minYear}
            max={maxYear}
            value={toYear}
            onChange={(e) => setToYear(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={String(maxYear)}
            className={styles['date-filter__input']}
          />
        </label>

        <button
          type="button"
          onClick={validateAndApply}
          className={styles['date-filter__btn']}
        >
          Применить
        </button>
      </div>

      {error && <div className={styles['date-filter__error']}>{error}</div>}
    </div>
  );
};

export default DateRangeFilter;