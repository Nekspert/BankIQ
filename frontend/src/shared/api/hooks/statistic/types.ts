export interface GetStatisticParams {
  publication_id: number;
  dataset_id: number;
  measure_id: number;
  from_year: number;
  to_year: number;
}

export interface StatisticDataRange {
  FromY: number;
  ToY: number;
}

export interface StatisticMainData {
  colId: number;
  date: string;
  digits: number;
  dt: string;
  element_id: number;
  measure_id: number;
  obs_val: number;
  periodicity: string; // 'month'
  rowId: number;
  unit_id: number;
}

export interface StatisticInfo {
  PublName: string;
  dsName: string;
  sType: number;
}

export interface StatisticHeader {
  elname: string;
  id: number;
}

export interface StatisticUnit {
  id: number;
  val: string;
}

export interface StatisticResponse {
  DTRange: StatisticDataRange[];
  RawData: StatisticMainData[];
  SType: StatisticInfo[];
  headerData: StatisticHeader[];
  units: StatisticUnit[];
}
