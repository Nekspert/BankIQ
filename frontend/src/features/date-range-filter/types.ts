/**
 * Свойства компонента {@link DateRangeFilter}.
 *
 * Определяет параметры и поведение фильтра по диапазону лет.
 * Используется для задания начальных значений, ограничений и обработчика применения фильтра.
 *
 * @interface DateRangeFilterProps
 *
 * @property {number} initialFromYear - Начальное значение года "От" при инициализации.
 * @property {number} initialToYear - Начальное значение года "До" при инициализации.
 * @property {number} minYear - Минимально допустимый год для выбора.
 * @property {number} [maxYear] - Максимально допустимый год (необязательно).
 * @property {(fromYear: number, toYear: number) => void} onApply - Функция, вызываемая при успешном применении фильтра.
 *
 * @example
 * ```ts
 * const props: DateRangeFilterProps = {
 *   initialFromYear: 2015,
 *   initialToYear: 2023,
 *   minYear: 2010,
 *   maxYear: 2025,
 *   onApply: (from, to) => console.log(`Выбран диапазон: ${from}-${to}`),
 * };
 * ```
 */
export interface DateRangeFilterProps {
  initialFromYear: number;
  initialToYear: number;
  minYear: number;
  maxYear?: number;
  onApply: (fromYear: number, toYear: number) => void;
}
