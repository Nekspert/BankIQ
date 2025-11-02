import type { TableItem } from '@/features/table-filter-panel/types';
import type { GetStatisticParams } from '@/shared/api/hooks/statistic/types';
import type { TableConfig } from './types';

export const tableArray: TableItem[] = [
  {
    id: 'summary',
    title: 'Ставки по кредитам нефинансовым организациям. В целом по РФ',
  },
  {
    id: 'territorial',
    title:
      'Ставки по кредитам нефинансовым организациям в рублях. В территориальном разрезе',
  },
  {
    id: 'depositsSummary',
    title: 'Ставки по вкладам физических лиц. В целом по РФ',
  },
  {
    id: 'depositsRegional',
    title:
      'Ставки по кредитам нефинансовым организациям. По видам экономической деятельности',
  },
  {
    id: 'depositsTerritorial',
    title: 'Ставки по вкладам физических лиц в рублях. В территориальном разрезе',
  },
];

export const summaryInfo: GetStatisticParams = {
  publication_id: 14,
  dataset_id: 25,
  measure_id: 2,
  from_year: 2024,
  to_year: 2025,
};

export const territorialInfo: GetStatisticParams = {
  publication_id: 15,
  dataset_id: 30,
  measure_id: 23,
  from_year: 2024,
  to_year: 2025,
};

export const someInfo: GetStatisticParams = {
  publication_id: 16,
  dataset_id: 35,
  measure_id: 21,
  from_year: 2024,
  to_year: 2025,
};

export const depositInfo: GetStatisticParams = {
  publication_id: 18,
  dataset_id: 37,
  measure_id: 2,
  from_year: 2024,
  to_year: 2025,
};

export const depositInfo2: GetStatisticParams = {
  publication_id: 19,
  dataset_id: 39,
  measure_id: 23,
  from_year: 2024,
  to_year: 2025,
};

export const tableConfigs: Record<string, TableConfig> = {
  summary: {
    requestData: summaryInfo,
    endpoint: 'interest-rates/credit',
    minYear: 2014,
  },
  territorial: {
    requestData: territorialInfo,
    endpoint: 'interest-rates/credit',
    minYear: 2019,
  },
  depositsRegional: {
    requestData: someInfo,
    endpoint: 'interest-rates/credit',
    minYear: 2019,
  },
  depositsSummary: {
    requestData: depositInfo,
    endpoint: 'interest-rates/deposit',
    minYear: 2014,
  },
  depositsTerritorial: {
    requestData: depositInfo2,
    endpoint: 'interest-rates/deposit',
    minYear: 2019,
  },
};
