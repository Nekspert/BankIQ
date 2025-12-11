import {
  useCallback,
  useEffect,
  useState,
  type FC,
  type ReactNode,
} from 'react';
import axios from 'axios';
import { AuthContext, type AuthContextValue } from '@/shared/hooks/useAuth';
import type { Form } from '@/features/register-form/types';
import { authApi } from '@/shared/api/auth/authApi';
import type { User } from '@/shared/types';

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthorized, setIsAuthorized] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

  const accessToken = localStorage.getItem('access');

  const refresh = async () => {
    const { refresh, access } = await authApi.refresh();
    localStorage.setItem('access', access);
    localStorage.setItem('refresh', refresh);
  };

  const getUserData = async () => {
    if (!accessToken) {
      await refresh();
      setLoading(false);
      return;
    }

    try {
      const user = await authApi.me();
      setUser(user);
      setIsAuthorized(true);
    } catch (e) {
      console.warn('Token invalid, clearing...');
      localStorage.removeItem('access');
      setIsAuthorized(false);
    } finally {
      setLoading(false);
    }
  };

  const login = useCallback(async (username: string, password: string) => {
    try {
      const res = await authApi.login({ username, password });

      localStorage.setItem('access', res.access);
      localStorage.setItem('refresh', res.refresh);

      setUser(res.user);
      setIsAuthorized(true);

      return res.user;
    } catch (err) {
      throw err;
    }
  }, []);

  const register = useCallback(async (data: Form) => {
    try {
      const user = await authApi.register(data);
      setIsAuthorized(true);
      return user;
    } catch (err) {
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    await axios.post('/api/logout/', {}, { withCredentials: true });
    setUser(null);
    setIsAuthorized(false);
  }, []);

  const ctx: AuthContextValue = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthorized,
    setUser
  };

  useEffect(() => {
    getUserData();
  }, [accessToken]);

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshed = await authApi.refresh();
            localStorage.setItem('access', refreshed.access);

            axios.defaults.headers.Authorization = `Bearer ${refreshed.access}`;
            originalRequest.headers.Authorization = `Bearer ${refreshed.access}`;

            return axios(originalRequest);
          } catch (refreshError) {
            console.warn('Refresh failed, logging out');
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            setUser(null);
            setIsAuthorized(false);
          }
        }

        throw error;
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  useEffect(() => {
    const interceptor = axios.interceptors.request.use((config) => {
      const token = localStorage.getItem('access');
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    return () => axios.interceptors.request.eject(interceptor);
  }, []);

  useEffect(() => {
    console.log('User info:', user);
  }, [user]);

  return <AuthContext.Provider value={ctx}>{children}</AuthContext.Provider>;
};
