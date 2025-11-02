import axios from 'axios';

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
};
