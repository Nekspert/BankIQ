import { useQuery } from '@tanstack/react-query';
import { indicatorsApi } from '../../indicatorsApi';

export const useGetAllBanks = () => {
  return useQuery({
    queryKey: ['all-banks'],
    queryFn: () => indicatorsApi.getAllBanks(),
  });
};
