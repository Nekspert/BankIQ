import { type FC } from 'react';
import { useDateRangeFilter } from './hooks/useDateRangeFilter';
import styles from './styles.module.scss';
import CustomSelect from '@/shared/ui/custom-select/CustomSelect';
import { Section } from '@/shared/ui/section/Section';
import { Button } from '@/shared/ui/button/Button';
import { Title } from '@/shared/ui/title/Title';
import type { DateRangeFilterProps } from './types';
/**
 * Компонент фильтрации данных по диапазону лет.
 * 
 * Позволяет выбрать начальный и конечный год в заданных границах (min/max),
 * валидирует ввод и вызывает callback при применении фильтра.
 * Использует хук {@link useDateRangeFilter} для управления состоянием.
 *
 * @component
 * @param {DateRangeFilterProps} props - Свойства компонента.
 * @param {number} props.initialFromYear - Начальное значение "От" при инициализации.
 * @param {number} props.initialToYear - Начальное значение "До" при инициализации.
 * @param {number} props.minYear - Минимально допустимый год.
 * @param {number} props.maxYear - Максимально допустимый год.
 * @param {(fromYear: number, toYear: number) => void} props.onApply - Callback при успешном применении фильтра.
 *
 * @returns {JSX.Element} Компонент React, отображающий два выпадающих списка выбора годов и кнопку "Применить".
 *
 * @example
 * ```tsx
 * <DateRangeFilter
 *   initialFromYear={2015}
 *   initialToYear={2024}
 *   minYear={2010}
 *   maxYear={2025}
 *   onApply={(from, to) => console.log(`Выбран диапазон: ${from} - ${to}`)}
 * />
 * ```
 *
 * @see useDateRangeFilter
 */

export const DateRangeFilter: FC<DateRangeFilterProps> = ({
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
    <Section
      padding="none"
      background="secondary"
      className={styles['date-filter']}
    >
      <Title level={3} size="small" className={styles['date-filter__title']}>
        Фильтр по дате
      </Title>

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

        <Button
          variant="primary"
          size="small"
          onClick={validateAndApply}
          className={styles['date-filter__btn']}
        >
          Применить
        </Button>
      </div>

      {error && (
        <Section padding="small" background="transparent">
          <div className={styles['date-filter__error']}>{error}</div>
        </Section>
      )}
    </Section>
  );
};

export default DateRangeFilter;
