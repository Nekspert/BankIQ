import React from 'react';
import { useDateRangeFilter } from './hooks/useDateRangeFilter';
import styles from './styles.module.scss';
import CustomSelect from '@/shared/ui/custom-select/CustomSelect';

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
  maxYear,
  onApply,
}) => {
  const {
    fromYear,
    setFromYear,
    toYear,
    setToYear,
    error,
    availableFromYears,
    availableToYears,
    validateAndApply,
    handleKeyPress,
  } = useDateRangeFilter({
    initialFromYear,
    initialToYear,
    minYear,
    maxYear,
    onApply,
  });

  return (
    <div className={styles['date-filter']}>
      <div className={styles['date-filter__inputs']}>
        <div className={styles['date-filter__field']}>
          <span className={styles['date-filter__label']}>
            От (мин. {minYear})
          </span>
          <CustomSelect
            value={fromYear}
            onChange={setFromYear}
            options={availableFromYears}
            placeholder="Выберите год"
            className={styles['date-filter__select']}
            onKeyDown={handleKeyPress}
          />
        </div>

        <div className={styles['date-filter__field']}>
          <span className={styles['date-filter__label']}>
            До (макс. {maxYear})
          </span>
          <CustomSelect
            value={toYear}
            onChange={setToYear}
            options={availableToYears}
            placeholder="Выберите год"
            className={styles['date-filter__select']}
            onKeyDown={handleKeyPress}
          />
        </div>

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
