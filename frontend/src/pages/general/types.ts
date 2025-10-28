import type { GetStatisticParams } from "@/shared/api/hooks/statistic/types";

export interface TableItem {
  id: string;
  title: string;
}

export interface TableConfig {
  requestData: GetStatisticParams;
  endpoint: string;
  minYear: number;
}
