import { useEffect, useState } from 'react';
import type { TableData } from '../types';
import { getStructuredData } from '../utils/getStructuredData';
import type { StatisticResponse } from '@/shared/api/hooks/statistic/types';
/**
 * Хук для преобразования сырых данных статистики в структуру таблицы {@link TableData}.
 *
 * Использует утилиту {@link getStructuredData} для конвертации данных из API
 * в формат, удобный для отображения в таблицах и графиках.
 *
 * @hook
 * @param {StatisticResponse | undefined} rawStatisticData - Сырые данные статистики из API.
 *
 * @returns {TableData | null} Преобразованные данные таблицы или null, если данных нет.
 *
 * @example
 * ```ts
 * const tableData = useTableData(rawData);
 *
 * if (tableData) {
 *   console.log(Object.keys(tableData)); // ['2023-01', '2023-02', ...]
 * }
 * ```
 *
 * @see getStructuredData
 * @see TableData
 */

export const useTableData = (rawStatisticData?: StatisticResponse) => {
  const [data, setData] = useState<TableData | null>(null);

  useEffect(() => {
    if (!rawStatisticData) return;
    setData(getStructuredData(rawStatisticData));
  }, [rawStatisticData]);

  return data;
};
