import { useQuery } from '@tanstack/react-query';
import type { GetStatisticParams } from '../statistic/types';
import { interestApi } from '../../interestApi';

export const useGetInterest = (params: GetStatisticParams) => {
  return useQuery({
    queryKey: ['deposits', JSON.stringify(params)],
    queryFn: () => interestApi.getInterest(params),
  });
};
