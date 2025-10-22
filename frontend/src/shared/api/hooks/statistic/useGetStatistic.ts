import { useQuery } from '@tanstack/react-query';
import { statisticApi } from '../../statisticApi';
import type { GetStatisticParams } from './types';

export const useGetStatistic = (
  params: GetStatisticParams,
  endpoint: string
) => {
  return useQuery({
    queryKey: ['statistic', JSON.stringify(params), endpoint],
    queryFn: () => statisticApi.getStatistic(params, endpoint),
    staleTime: Infinity,
  });
};
