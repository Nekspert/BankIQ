import { useQuery } from '@tanstack/react-query';
import { authApi, type UserRegisterData } from '../../auth/authApi';

export const useRegister = ({ userData }: { userData: UserRegisterData }) => {
  return useQuery({
    queryKey: ['register'],
    queryFn: () => authApi.register(userData),
  });
};
