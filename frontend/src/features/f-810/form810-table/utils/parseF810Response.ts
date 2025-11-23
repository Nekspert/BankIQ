import { F810_COLUMNS } from '../constants';

interface F810Item {
  NUM_STR: number;
  LABEL: string;
  NUM_P: string;
  USTKAP: number | null;
  SOB_AK: number | null;
  EMIS_DOH: number | null;
  PER_CB: number | null;
  PER_OS: number | null;
  DELTADVR: number | null;
  PER_IH: number | null;
  REZERVF: number | null;
  VKL_V_IM: number | null;
  NERASP_PU: number | null;
  ITOGO_IK: number | null;
}

export type F810Response = F810Item[];

export const parseF810Response = (
  data?: F810Response | null
): Record<string, number | null> => {
  const out: Record<string, number | null> = {};
  
  for (const col of F810_COLUMNS) {
    out[col.key] = null;
  }

  if (!Array.isArray(data) || data.length === 0) return out;

  const firstRow = data[0];
  
  if (!firstRow) return out;

  for (const col of F810_COLUMNS) {
    const value = firstRow[col.key as keyof F810Item];
    out[col.key] = typeof value === 'number' ? value : null;
  }

  return out;
};