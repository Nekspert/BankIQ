import axios from 'axios';

export const restrictionApi = {
  getRestriction: async () => {
    const { data } = await axios.post('/api/reports/check_params/');
    return data;
  },
};
