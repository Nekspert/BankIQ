import axios from 'axios';

export const restrictionApi = {
  getRestriction: async () => {
    const { data } = await axios.post('/api/parse/check_params');
    return data;
  },
};
