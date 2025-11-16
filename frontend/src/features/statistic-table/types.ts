import type { GetStatisticParams } from "@/shared/api/hooks/statistic/types";
/**
 * Тип данных таблицы статистики.
 *
 * Представляет объект, где ключ — дата (строка), а значение — набор показателей с числовыми значениями или null.
 *
 * @typedef {Record<string, Record<string, number | null>>} TableData
 *
 * @example
 * ```ts
 * const tableData: TableData = {
 *   "2023-01": { ROE: 12.3, ROA: 4.5 },
 *   "2023-02": { ROE: 13.1, ROA: 4.8 },
 * };
 * ```
 */
type Row = Record<string, number | null>;
export type TableData = Record<string, Row>;
/**
 * Свойства компонента {@link StatisticTable}.
 *
 * Определяет параметры запроса статистики, выбранные колонки и настройки фильтра по дате.
 *
 * @interface StatisticTableProps
 * @property {GetStatisticParams} requestData - Начальные параметры запроса статистики.
 * @property {string[] | null} [externalSelectedColumns] - Внешне выбранные колонки для отображения таблицы.
 * @property {(cols: string[]) => void} [onColumnsReady] - Callback, вызываемый после определения всех колонок.
 * @property {string} endpoint - API-эндпоинт для получения статистики.
 * @property {number} minYear - Минимальный год для фильтра по дате.
 *
 * @example
 * ```ts
 * const props: StatisticTableProps = {
 *   requestData: { from_year: 2015, to_year: 2024 },
 *   externalSelectedColumns: ["ROE", "ROA"],
 *   onColumnsReady: (cols) => console.log("Колонки:", cols),
 *   endpoint: "/api/statistics",
 *   minYear: 2010,
 * };
 * ```
 */
export interface StatisticTableProps {
  requestData: GetStatisticParams;
  externalSelectedColumns?: string[] | null;
  onColumnsReady?: (cols: string[]) => void;
  endpoint: string;
  minYear: number;
}
