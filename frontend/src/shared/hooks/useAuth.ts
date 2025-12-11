import type { Form as RegisterForm } from '@/features/register-form/types';
import {
  createContext,
  useContext,
  type Dispatch,
  type SetStateAction,
} from 'react';
import type { User } from '../types';

export type AuthContextValue = {
  user: User | null;
  isAuthorized: boolean | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<User>;
  register: (userData: RegisterForm) => Promise<User>;
  logout: () => Promise<void>;
  setUser: Dispatch<SetStateAction<User | null>>;
};

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
