import { type FC } from 'react';
import { useDateRangeFilter } from './hooks/useDateRangeFilter';
import styles from './styles.module.scss';
import CustomSelect from '@/shared/ui/custom-select/CustomSelect';
import { Section } from '@/shared/ui/section/Section';
import { Button } from '@/shared/ui/button/Button';
import { Title } from '@/shared/ui/title/Title';
import type { DateRangeFilterProps } from './types';

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
      padding="medium"
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
