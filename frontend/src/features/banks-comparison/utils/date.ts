/**
 * ¬озвращает диапазон дат (от и до) дл€ указанного мес€ца в формате ISO-строк.
 * »спользуетс€ дл€ формировани€ временных промежутков при запросах данных по мес€цам.
 *
 * @utility
 * @param {string | null} monthValue Ч «начение мес€ца в формате `"YYYY-MM"`.
 * @returns {{
 *   from: string | null;
 *   to: string | null;
 * }} ќбъект с начальной и конечной датой мес€ца:
 * - `from` Ч перва€ дата мес€ца в формате `"YYYY-MM-01T00:00:00"`;
 * - `to` Ч последн€€ дата мес€ца в формате `"YYYY-MM-DDT23:59:59"`.
 *
 * @example
 * ```ts
 * getMonthRange('2025-03');
 * // => { from: "2025-03-01T00:00:00", to: "2025-03-31T23:59:59" }
 * ```
 *
 * @see {@link useBanksComparison} Ч »спользует диапазон дат дл€ загрузки показателей.
 */
export const getMonthRange = (monthValue: string | null) => {
    if (!monthValue) return { from: null, to: null };
    const [yStr, mStr] = monthValue.split('-');
    const year = Number(yStr);
    const month = Number(mStr);

    const from = `${String(year).padStart(4,'0')}-${String(month).padStart(2,'0')}-01T00:00:00`;

    const lastDay = new Date(year, month, 0).getDate();
    const to = `${String(year).padStart(4,'0')}-${String(month).padStart(2,'0')}-${String(lastDay).padStart(2,'0')}T23:59:59`;

    return { from, to };
};
