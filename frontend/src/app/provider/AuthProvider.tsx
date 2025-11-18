import {
  useCallback,
  useEffect,
  useState,
  type FC,
  type ReactNode,
} from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AppRoutes } from '@/shared/config/routes';
import { AuthContext, type AuthContextValue } from '@/shared/hooks/useAuth';

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const navigate = useNavigate();

  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const [loading, setLoading] = useState<boolean>(true)

  const getUserData = async () => {
    const { data } = await axios.get('/12312321/');
    setLoading(false)
    console.log(data)
    return data;
  };

  const user = getUserData();

  useEffect(() => {
    const isFirstLoad = user === undefined && isAuthorized === null;
    setIsAuthorized(isFirstLoad ? null : Boolean(user));
  }, [user, isAuthorized]);

  useEffect(() => {
    console.log('Состояние авторизованности: ', isAuthorized);
  }, [isAuthorized]);

  const login = async (email: string, password: string) => {
    try {
      await axios.post(
        '/api/auth/login',
        { email, password },
        { withCredentials: true }
      );
      // refetch();
      navigate(AppRoutes.home);
    } catch (err) {
      // notify('Ошибка при входе. Проверьте данные и попробуйте снова.', 'error');
      throw err;
    }
  };

  const register = useCallback(
    async (email: string, password: string) => {
      try {
        await axios.post('/api/auth/register', { email, password });
      } catch (err) {
        // notify('Ошибка при регистрации. Попробуйте еще раз.', 'error');
        throw err;
      }
    },
    [login]
  );

  const logout = useCallback(async () => {
    await axios.post('/api/auth/logout', {}, { withCredentials: true });
    // queryClient.clear();
    setIsAuthorized(false);
  }, []);

  const refresh = useCallback(async () => {
    await axios.post('/api/auth/refresh', {}, { withCredentials: true });
  }, []);

  useEffect(() => {
    console.log('Данные пользователя: ', user);
  }, [user]);

  const ctx: AuthContextValue = {
    user,
    loading,
    login,
    register,
    logout,
    refresh,
    isAuthorized,
  };

  return <AuthContext.Provider value={ctx}>{children}</AuthContext.Provider>;
};
