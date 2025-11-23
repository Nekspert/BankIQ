import axios from 'axios';

export const indicatorsF810Api = {
  getIndicator: async ({ regNum, date }: { regNum: number; date: string }) => {
    const { data } = await axios.post(
      '/api/indicators/f810/bank-indicator-data/',
      {
        reg_number: regNum,
        dt: date,
      }
    );
    return data;
  },
};
