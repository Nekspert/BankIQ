import type { User } from '@/shared/types';
import { deepKeysToCamel, deepKeysToSnake } from '@/shared/utils/case';
import axios from 'axios';
import type {
  RefreshResponse,
  UserLoginData,
  UserLoginResponse,
  UserRegisterData,
} from './types';

export const authApi = {
  register: async (userData: UserRegisterData): Promise<User> => {
    const { data } = await axios.post(
      '/api/register/',
      deepKeysToSnake(userData)
    );
    return deepKeysToCamel(data);
  },

  login: async (userInfo: UserLoginData): Promise<UserLoginResponse> => {
    const { data } = await axios.post(
      '/api/login/',
      deepKeysToSnake(userInfo),
      { withCredentials: true }
    );

    const result = deepKeysToCamel(data);
    return result;
  },

  me: async (): Promise<User> => {
    const accessToken = localStorage.getItem('access');
    const { data } = await axios.get('/api/me/', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return deepKeysToCamel(data);
  },

  refresh: async (): Promise<RefreshResponse> => {
    const refreshToken = localStorage.getItem('refresh');
    if (!refreshToken) throw new Error('No refresh token');

    const { data } = await axios.post('/api/token/refresh/', {
      refresh: refreshToken,
    });

    return data;
  },
};
