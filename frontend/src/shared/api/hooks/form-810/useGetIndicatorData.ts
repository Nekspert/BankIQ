import { useQuery } from '@tanstack/react-query';
import { indicatorsF810Api } from '../../form-810/indicatorsApi';

export const useGetIndicatorData = (params: {
  regNum: number;
  date: string;
}) => {
  return useQuery({
    queryKey: ['f810-indicator', params.regNum, params.date],
    queryFn: () => indicatorsF810Api.getIndicator(params),
  });
};
