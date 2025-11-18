import type { loginSchema } from "./constants";
import { z } from 'zod';

export type Form = z.infer<typeof loginSchema>;
