import { z } from 'zod';

export const loginSchema = z.object({
  username: z.string().min(1, 'Введите логин'),
  password: z.string().min(8, 'Минимум 8 символов'),
});