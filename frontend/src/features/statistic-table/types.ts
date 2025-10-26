import type { GetStatisticParams } from "@/shared/api/hooks/statistic/types";

type Row = Record<string, number | null>;
export type TableData = Record<string, Row>;

export interface StatisticTableProps {
  requestData: GetStatisticParams;
  externalSelectedColumns?: string[] | null;
  onColumnsReady?: (cols: string[]) => void;
  endpoint: string;
  minYear: number;
}
