import axios from 'axios';

export const indicatorsF123Api = {
  getBankDatetimes: async () => {
    const { data } = await axios.post('/api/indicators/f123/bank-datetimes/', {
      reg_number: 1000,
    });
    return data;
  },
  getFormIndicators: async () => {
    const { data } = await axios.post('/api/indicators/f123/form-indicators/', {
      reg_number: 1481,
      dt: '2024-06-01T00:00:00Z',
    });
    return data;
  },
  getIndicator: async ({ regNum, date }: { regNum: number; date: string }) => {
    const { data } = await axios.post(
      '/api/indicators/f123/bank-indicator-data/',
      {
        reg_number: regNum,
        dt: date,
      }
    );
    return data;
  },
};
