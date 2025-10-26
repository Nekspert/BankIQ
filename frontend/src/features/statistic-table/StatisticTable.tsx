import { useMemo, type FC } from 'react';
import { useGetStatistic } from '@/shared/api/hooks/statistic/useGetStatistic';
import styles from './styles.module.scss';
import { StatisticChart } from '@/features/statistic-chart/StatisticChart';
import { DateRangeFilter } from '@/features/date-range-filter/DateRangeFilter';
import { TableLoader } from '../table-loader/TableLoader';
import type { StatisticTableProps } from './types';

import { useTableData } from './hooks/useTableData';
import { useTableColumns } from './hooks/useTableColumns';
import { useExpandableTable } from './hooks/useExpandableTable';
import { useRef } from 'react';
import { useDateRange } from './hooks/useDateRange';

export const StatisticTable: FC<StatisticTableProps> = ({
  requestData,
  externalSelectedColumns,
  onColumnsReady,
  endpoint,
  minYear,
}) => {
  const tableRef = useRef<HTMLTableElement>(null);

  const { dateRange, handleDateChange } = useDateRange(
    requestData.from_year,
    requestData.to_year
  );

  const currentRequestData = useMemo(
    () => ({
      ...requestData,
      from_year: dateRange.from_year,
      to_year: dateRange.to_year,
    }),
    [requestData, dateRange]
  );

  const { data: rawStatisticData } = useGetStatistic(
    currentRequestData,
    endpoint
  );
  const data = useTableData(rawStatisticData);

  const { columns, activeColumns } = useTableColumns(
    data,
    externalSelectedColumns,
    onColumnsReady
  );

  const {
    isExpanded,
    setIsExpanded,
    containerStyle,
    displayedRows,
    showToggle,
  } = useExpandableTable(data, tableRef);

  if (!data) return <TableLoader />;

  return (
    <div>
      <div>
        <h2 className={styles.title}>
          {rawStatisticData?.SType?.[0]?.dsName ?? ''}
          {rawStatisticData?.SType?.[0]?.PublName
            ? `. ${rawStatisticData.SType[0].PublName}`
            : ''}
        </h2>
        <h3 className={styles.subtitle}>
          За период: {dateRange.from_year} - {dateRange.to_year}
        </h3>
      </div>

      <DateRangeFilter
        initialFromYear={dateRange.from_year}
        initialToYear={dateRange.to_year}
        minYear={minYear}
        onApply={handleDateChange}
      />

      <div className={styles['table-container']} style={containerStyle}>
        {!activeColumns || activeColumns.length === 0 ? (
          <div className={styles['no-selection']}>
            Нет выбранных показателей для отображения.
          </div>
        ) : (
          <table ref={tableRef} className={styles['statistic-table']}>
            <thead>
              <tr>
                <th className={styles['sticky-col']}>Дата</th>
                {activeColumns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {displayedRows.map(([dt, row]) => (
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
        {!isExpanded && showToggle && (
          <div className={styles['gradient-overlay']} />
        )}
      </div>

      {showToggle && (
        <button
          className={styles['toggle-button']}
          onClick={() => setIsExpanded((prev) => !prev)}
        >
          {isExpanded ? 'Свернуть' : 'Развернуть'}
        </button>
      )}

      <StatisticChart
        data={data}
        columns={columns}
        selectedColumns={activeColumns}
      />
    </div>
  );
};

export default StatisticTable;
