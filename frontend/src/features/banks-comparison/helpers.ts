/**
 * ƒополн€ет число ведущим нулЄм до двух символов.
 * »спользуетс€ при форматировании мес€цев и дней в строковом представлении даты.
 *
 * @utility
 * @param {number} n Ч „исло, которое нужно привести к строке длиной 2 символа.
 * @returns {string} —трока, содержаща€ число с ведущим нулЄм при необходимости.
 *
 * @example
 * ```ts
 * pad2(3); // "03"
 * pad2(12); // "12"
 * ```
 *
 * @see {@link dateToYYYYMM} Ч использует pad2 при форматировании даты в строку.
 */
const pad2 = (n: number) => String(n).padStart(2, '0');

/**
 * ѕреобразует строку в формате `"YYYY-MM"` в объект `Date`,
 * соответствующий первому дню указанного мес€ца.
 *
 * @utility
 * @param {string | null} ym Ч —трока с годом и мес€цем, например `"2025-04"`.
 * @returns {Date | null} ќбъект `Date` или `null`, если вход некорректен.
 *
 * @example
 * ```ts
 * monthToDate("2025-04"); // new Date(2025, 3, 1)
 * monthToDate(null); // null
 * ```
 *
 * @see {@link dateToYYYYMM} Ч обратна€ функци€ дл€ преобразовани€ даты в строку.
 * @see {@link useBanksComparison} Ч используетс€ дл€ корректировки выбранных периодов.
 */
export const monthToDate = (ym: string | null): Date | null => {
    if (!ym) return null;
    const [yStr, mStr] = ym.split('-');
    const y = Number(yStr);
    const m = Number(mStr);
    if (Number.isNaN(y) || Number.isNaN(m)) return null;
    return new Date(y, m - 1, 1);
};

/**
 * ѕреобразует объект `Date` в строку формата `"YYYY-MM"`.
 * »спользуетс€ дл€ хранени€ и отображени€ выбранных мес€цев в локальном состо€нии.
 *
 * @utility
 * @param {Date} d Ч ќбъект даты дл€ преобразовани€.
 * @returns {string} —трока в формате `"YYYY-MM"`.
 *
 * @example
 * ```ts
 * dateToYYYYMM(new Date(2025, 3, 1)); // "2025-04"
 * ```
 *
 * @see {@link monthToDate} Ч выполн€ет обратное преобразование строки в дату.
 * @see {@link useBanksComparison} Ч примен€ет дл€ вычислени€ диапазонов дат.
 */
export const dateToYYYYMM = (d: Date) =>
    `${d.getFullYear()}-${pad2(d.getMonth() + 1)}`;
