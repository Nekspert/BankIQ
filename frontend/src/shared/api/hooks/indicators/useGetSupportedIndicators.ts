import { useQuery } from '@tanstack/react-query';
import { indicatorsApi } from '../../indicatorsApi';

export interface GetSupportedIndicatorsParams {
  reg_number: number;
  dt: string;
}
export const useGetSupportedIndicators = (
  params: GetSupportedIndicatorsParams
) => {
  return useQuery({
    queryKey: ['supportedIndicators', params],
    queryFn: () => indicatorsApi.getSupportedIndicators(params)
  });
};
