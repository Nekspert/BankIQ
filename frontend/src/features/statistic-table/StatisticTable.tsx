import { useGetStatistic } from '@/shared/api/hooks/statistic/useGetStatistic';
import { useEffect, useMemo, useState } from 'react';
import { getStructuredData } from './utils/getStructuredData';
import styles from './styles.module.scss';
import { StatisticChart } from '../statistic-chart/StatisticChart';

export const StatisticTable = () => {
  const { data: rawStatisticData } = useGetStatistic({
    publication_id: 14,
    dataset_id: 25,
    measure_id: 2,
    from_year: 2024,
    to_year: 2025,
  });

  const [data, setData] = useState<Record<
    string,
    Record<string, number | null>
  > | null>(null);

  useEffect(() => {
    if (rawStatisticData) {
      setData(getStructuredData(rawStatisticData));
    }
  }, [rawStatisticData]);

  const columns = useMemo(() => {
    if (!data) return [] as string[];

    const rows = Object.values(data);
    const colsSet = new Set<string>();

    if (rows.length > 0) {
      Object.keys(rows[0]).forEach((k) => colsSet.add(k));
    }

    rows.slice(1).forEach((r) =>
      Object.keys(r).forEach((k) => {
        if (!colsSet.has(k)) colsSet.add(k);
      })
    );

    return Array.from(colsSet);
  }, [data]);

  if (!data) return null;

  return (
    <>
      <h2 className={styles['title']}>
        {rawStatisticData?.SType[0].dsName}.{' '}
        {rawStatisticData?.SType[0].PublName}
      </h2>
      <h3 className={styles['subtitle']}>
        За период: {2024} - {2025}
      </h3>
      <div className={styles['table-container']}>
        <table className={styles['statistic-table']}>
          <thead>
            <tr>
              <th className={styles['sticky-col']}>Дата</th>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(data).map(([dt, row]) => (
              <tr key={dt}>
                <td className={styles['sticky-col']}>{dt}</td>
                {columns.map((col) => {
                  const val = row[col];
                  const cell =
                    typeof val === 'number' ? val.toFixed(2) : (val ?? '-');
                  return <td key={col}>{cell}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <StatisticChart data={data} columns={columns} />
    </>
  );
};
