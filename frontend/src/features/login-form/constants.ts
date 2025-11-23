import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string(),
  password: z.string().min(4),
});
