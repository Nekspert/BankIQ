import type { User } from '@/shared/types';

export interface UserRegisterData {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  password: string;
}

export interface UserLoginData {
  username: string;
  password: string;
}

export interface UserLoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RefreshResponse {
  access: string;
  refresh: string;
}
