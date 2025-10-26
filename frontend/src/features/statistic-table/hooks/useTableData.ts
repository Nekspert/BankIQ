import { useEffect, useState } from 'react';
import type { TableData } from '../types';
import { getStructuredData } from '../utils/getStructuredData';
import type { StatisticResponse } from '@/shared/api/hooks/statistic/types';

export const useTableData = (rawStatisticData?: StatisticResponse) => {
  const [data, setData] = useState<TableData | null>(null);

  useEffect(() => {
    if (!rawStatisticData) return;
    setData(getStructuredData(rawStatisticData));
  }, [rawStatisticData]);

  return data;
};
