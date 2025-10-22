import axios from 'axios';
import type { GetStatisticParams } from './hooks/statistic/types';

export const interestApi = {
  getInterest: async (params: GetStatisticParams) => {
    const { data } = await axios.post(
      '/api/parse/interest_rates_deposit',
      params
    );
    return data;
  },
};
