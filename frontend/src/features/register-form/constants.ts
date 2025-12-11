import { z } from 'zod';
import type { Form } from './types';

export const registerSchema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(8),
  username: z.string(),
  firstName: z.string(),
  lastName: z.string(),
});

export const defaultValues: Form = {
  email: '',
  password: '',
  username: '',
  firstName: '',
  lastName: '',
};
