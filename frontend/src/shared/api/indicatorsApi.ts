import axios from 'axios';
import type { GetBankIndicatorParams } from './hooks/indicators/useGetIndicatorData';
import type { GetSupportedIndicatorsParams } from './hooks/indicators/useGetSupportedIndicators';

export interface BankIndicator {
  bic: string;
  name: string;
  reg_number: string;
  internal_code: string;
  registration_date: string;
  region_code: string;
  tax_id: string;
}

export interface IndicatorsResponse {
  banks: BankIndicator[];
}

export const indicatorsApi = {
  getAllBanks: async (): Promise<IndicatorsResponse> => {
    const { data } = await axios.get('/api/indicators/all-banks/');
    return data;
  },
  getSupportedDates: async (reg_number: number) => {
    const { data } = await axios.post('/api/indicators/bank-datetimes/', {
      reg_number,
    });
    return data;
  },
  getIndicatorData: async (params: GetBankIndicatorParams) => {
    const { data } = await axios.post(
      '/api/indicators/bank-indicator-data/',
      params
    );
    return data;
  },
  getSupportedIndicators: async (params: GetSupportedIndicatorsParams) => {
    const { data } = await axios.post(
      '/api/indicators/form-indicators/',
      params
    );
    return data;
  },
};
