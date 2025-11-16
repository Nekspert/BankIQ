import type { StatisticResponse } from '@/shared/api/hooks/statistic/types';
/**
 * Преобразует сырые данные статистики из API в структурированный формат таблицы.
 *
 * Создает объект, где ключ — дата, а значение — набор показателей с их значениями.
 * Заголовки колонок берутся из `headerData`, если отсутствуют — используется `id_element`.
 *
 * @param {StatisticResponse | undefined} rawStatisticData - Сырые данные статистики из API.
 *
 * @returns {Record<string, Record<string, number | null>> | undefined} Преобразованные данные таблицы или undefined, если исходных данных нет.
 *
 * @example
 * ```ts
 * const structuredData = getStructuredData(apiData);
 * console.log(structuredData['2023-01']['ROE']); // 12.3
 * ```
 *
 * @see StatisticResponse
 */

export const getStructuredData = (rawStatisticData?: StatisticResponse) => {
  if (!rawStatisticData) return;
  const tableMap: Record<string, Record<string, number | null>> = {};
  const headerMap: Record<number, string> = {};
  rawStatisticData.headerData.forEach((h) => {
    headerMap[h.id] = h.elname;
  });

  rawStatisticData.RawData.forEach((item) => {
    if (!tableMap[item.dt]) tableMap[item.dt] = {};

    const colName = headerMap[item.element_id] || `id_${item.element_id}`;
    tableMap[item.dt][colName] = item.obs_val;
  });
  return tableMap;
};
