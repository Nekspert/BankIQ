export type MonthPickerProps = {
  value: string | null;
  onChange: (val: string | null) => void;
  maxDate?: Date;
  minDate?: Date;
  placeholder?: string;
  className?: string;
  ariaLabel?: string;
};
