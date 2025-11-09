import { type FC } from 'react';
import ReactDatePicker, { registerLocale } from 'react-datepicker';
import classNames from 'classnames';
import styles from './styles.module.scss';
import type { MonthPickerProps } from './types';
import { toDate, toYYYYMM } from './helpers';
import { ru } from 'date-fns/locale';

registerLocale('ru', ru);

export const MonthPicker: FC<MonthPickerProps> = ({
  value,
  onChange,
  maxDate,
  minDate,
  placeholder = 'Выбрать месяц',
  className,
  ariaLabel,
}) => {
  const selected = toDate(value);

  return (
    <div className={classNames(styles['month-picker-wrapper'], className)}>
      <ReactDatePicker
        selected={selected ?? undefined}
        onChange={(date) => {
          onChange(date ? toYYYYMM(date as Date) : null);
        }}
        dateFormat="LLLL yyyy"
        showMonthYearPicker
        showFullMonthYearPicker
        maxDate={maxDate}
        minDate={minDate}
        placeholderText={placeholder}
        className={styles['month-input']}
        aria-label={ariaLabel}
        locale="ru"
      />
    </div>
  );
};

export default MonthPicker;
