import { useQuery } from '@tanstack/react-query';
import { indicatorsApi } from '../../indicatorsApi';

export const useGetUniqueIndicators = () => {
  return useQuery({
    queryKey: ['f-101-uniqueIndicators'],
    queryFn: () => indicatorsApi.getUniqueIndicators(),
  });
};
