import { useQuery } from '@tanstack/react-query';
import { restrictionApi } from '../../restrictionApi';

export const useGetRestrictions = () => {
  return useQuery({
    queryKey: ['restrictions'],
    queryFn: () => restrictionApi.getRestriction(),
  });
};
