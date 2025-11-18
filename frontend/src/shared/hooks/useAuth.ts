import { createContext, useContext } from 'react';
export type User = {
  id: number;
  email: string;
  name: string | null;
  surname: string | null;
} | null;

export type AuthContextValue = {
  user?: User;
  isAuthorized: boolean | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
