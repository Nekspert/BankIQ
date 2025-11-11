/**
 * ¬озвращает ISO-строку, соответствующую первому дню предыдущего мес€ца
 * относительно переданной даты.
 * »спользуетс€ дл€ расчЄта начальной даты диапазона по умолчанию.
 *
 * @utility
 * @param {Date | null} date Ч »сходна€ дата, от которой нужно получить предыдущий мес€ц.
 * @returns {string | null} ISO-строка (`"YYYY-MM-01T00:00:00"`) или `null`, если дата не указана.
 *
 * @example
 * ```ts
 * getPrevMonth(new Date('2025-04-15'));
 * // => "2025-03-01T00:00:00"
 * ```
 *
 * @see {@link getMonthRange} Ч »спользуетс€ совместно дл€ формировани€ диапазона дат.
 * @see {@link useBanksComparison} Ч ѕримен€ет при инициализации диапазона дл€ выборки данных.
 */
export const getPrevMonth = (date: Date | null): string | null => {
    if (!date) return null;
    const year = date.getFullYear();
    const month = date.getMonth();
    const prevMonthDate = new Date(year, month - 1, 1, 0, 0, 0);
    return prevMonthDate.toISOString().split('Z')[0];
};
