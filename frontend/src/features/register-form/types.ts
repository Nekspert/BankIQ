import type { registerSchema } from './constants';
import { z } from 'zod';

export type Form = z.infer<typeof registerSchema>;
