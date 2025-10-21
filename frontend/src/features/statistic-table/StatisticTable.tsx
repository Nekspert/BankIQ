import { useEffect, useMemo, useState, type FC } from 'react';
import { useGetStatistic } from '@/shared/api/hooks/statistic/useGetStatistic';
import { getStructuredData } from './utils/getStructuredData';
import styles from './styles.module.scss';
import { StatisticChart } from '@/features/statistic-chart/StatisticChart';
import type { GetStatisticParams } from '@/shared/api/hooks/statistic/types';
import FilterPanel from '../filter-panel/FilterPanel';

type Row = Record<string, number | null>;
type TableData = Record<string, Row>;

interface Props {
  requestData: GetStatisticParams;
  externalSelectedColumns?: string[] | null;
  onColumnsReady?: (cols: string[]) => void;
}

export const StatisticTable: FC<Props> = ({
  requestData,
  externalSelectedColumns,
  onColumnsReady,
}) => {
  const { data: rawStatisticData } = useGetStatistic(requestData);
  const [data, setData] = useState<TableData | null>(null);
  const [internalSelected, setInternalSelected] = useState<string[]>([]);

  useEffect(() => {
    if (!rawStatisticData) return;
    setData(getStructuredData(rawStatisticData));
  }, [rawStatisticData]);

  const columns = useMemo(() => {
    if (!data) return [] as string[];
    const rows = Object.values(data);
    const colsSet = new Set<string>();
    if (rows.length > 0) Object.keys(rows[0]).forEach((k) => colsSet.add(k));
    rows.slice(1).forEach((r) => Object.keys(r).forEach((k) => colsSet.add(k)));
    return Array.from(colsSet);
  }, [data]);

  useEffect(() => {
    if (columns.length === 0) return;
    onColumnsReady?.(columns);
    setInternalSelected((prev) => {
      if (prev.length === 0) return columns;
      return prev.filter((c) => columns.includes(c));
    });
  }, [columns.join('|')]);

  useEffect(() => {
    if (externalSelectedColumns && externalSelectedColumns.length > 0) return;
    if (columns.length > 0 && internalSelected.length === 0)
      setInternalSelected(columns);
  }, [externalSelectedColumns, columns, internalSelected.length]);

  const activeColumns =
    externalSelectedColumns && externalSelectedColumns.length >= 0
      ? externalSelectedColumns
      : internalSelected;

  if (!data) return null;

  return (
    <div className={styles['statistic-block']}>
      <div className={styles['statistic-header']}>
        <div>
          <h2 className={styles['title']}>
            {rawStatisticData?.SType?.[0]?.dsName ?? ''}
            {rawStatisticData?.SType?.[0]?.PublName
              ? `. ${rawStatisticData.SType[0].PublName}`
              : ''}
          </h2>
          <h3 className={styles['subtitle']}>
            За период: {requestData.from_year} - {requestData.to_year}
          </h3>
        </div>
      </div>

      <div className={styles['table-container']}>
        {!activeColumns || activeColumns.length === 0 ? (
          <div className={styles['no-selection']}>
            Нет выбранных показателей для отображения.
          </div>
        ) : (
          <table className={styles['statistic-table']}>
            <thead>
              <tr>
                <th className={styles['sticky-col']}>Дата</th>
                {activeColumns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(data).map(([dt, row]) => (
                <tr key={dt}>
                  <td className={styles['sticky-col']}>{dt}</td>
                  {activeColumns.map((col) => {
                    const val = row[col];
                    const cell =
                      typeof val === 'number' ? val.toFixed(2) : (val ?? '-');
                    return <td key={col}>{cell}</td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <StatisticChart
        data={data}
        columns={columns}
        selectedColumns={activeColumns ?? []}
      />
    </div>
  );
};

export default StatisticTable;
