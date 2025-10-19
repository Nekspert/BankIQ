import type { StatisticResponse } from '@/shared/api/hooks/statistic/types';

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
