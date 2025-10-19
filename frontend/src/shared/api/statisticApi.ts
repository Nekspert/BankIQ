import axios from 'axios';
import type {
  GetStatisticParams,
  StatisticResponse,
} from './hooks/statistic/types';

export const statisticApi = {
  getStatistic: async (
    params: GetStatisticParams
  ): Promise<StatisticResponse> => {
    const { data } = await axios.post(
      '/api/parse/interest_rates_credit',
      params
    );
    return data;
  },
};
