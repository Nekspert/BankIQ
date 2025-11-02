import axios from 'axios';
import type {
  GetStatisticParams,
  StatisticResponse,
} from './hooks/statistic/types';

export const statisticApi = {
  getStatistic: async (
    params: GetStatisticParams,
    endpoint: string
  ): Promise<StatisticResponse> => {
    const { data } = await axios.post(`/api/reports/${endpoint}/`, params);
    return data;
  },
};
