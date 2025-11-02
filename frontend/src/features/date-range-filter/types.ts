export interface DateRangeFilterProps {
  initialFromYear: number;
  initialToYear: number;
  minYear: number;
  maxYear?: number;
  onApply: (fromYear: number, toYear: number) => void;
}
