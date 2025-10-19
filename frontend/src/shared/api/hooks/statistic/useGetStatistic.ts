import { useQuery } from '@tanstack/react-query';
import { statisticApi } from '../../statisticApi';
import type { GetStatisticParams } from './types';

export const useGetStatistic = (params: GetStatisticParams) => {
  return useQuery({
    queryKey: [JSON.stringify(params)],
    queryFn: () => statisticApi.getStatistic(params),
  });
};
