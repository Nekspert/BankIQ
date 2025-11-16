import { F123_ROWS } from '../constants';
import type { F123Response } from '../types';

export const parseF123Response = (
  data?: F123Response | null
): Record<string, number | null> => {
  const out: Record<string, number | null> = {};
  for (const row of F123_ROWS) out[row] = null;

  if (!Array.isArray(data)) return out;

  const rowIndex = new Map(F123_ROWS.map((r) => [r, r]));

  for (const item of data) {
    if (!item || typeof item.name !== 'string') continue;
    const name = item.name.trim();

    if (rowIndex.has(name)) {
      out[rowIndex.get(name)!] = item.value ?? null;
      continue;
    }

    for (const row of F123_ROWS) {
      if (row.includes(name) || name.includes(row)) {
        out[row] = item.value ?? null;
        break;
      }
    }
  }

  return out;
};
