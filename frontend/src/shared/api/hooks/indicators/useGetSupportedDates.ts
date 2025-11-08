import { useQuery } from '@tanstack/react-query';
import { indicatorsApi } from '../../indicatorsApi';

export const useGetSupportedRoles = (regNumber: number) => {
  return useQuery({
    queryKey: ['bankSupportedDates', regNumber],
    queryFn: () => indicatorsApi.getSupportedDates(regNumber),
  });
};
