import { useQuery } from '@tanstack/react-query';
import { indicatorsApi } from '../../indicatorsApi';

export interface GetBankIndicatorParams {
  reg_number: number;
  ind_code: string;
  date_from: string;
  date_to: string;
}

export const useGetIndicatorData = (params: GetBankIndicatorParams) => {
  return useQuery({
    queryKey: ['indicator-data', params],
    queryFn: () => indicatorsApi.getIndicatorData(params),
  });
};
