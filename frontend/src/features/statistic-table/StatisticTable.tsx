import { memo, useMemo, type FC } from 'react';
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
import { Section } from '@/shared/ui/section/Section';
import { Title } from '@/shared/ui/title/Title';
import { Button } from '@/shared/ui/button/Button';
/**
 * Компонент отображения статистической таблицы с возможностью фильтра по дате и графиком.
 *
 * Использует хуки {@link useTableData}, {@link useTableColumns}, {@link useExpandableTable} и {@link useDateRange}
 * для управления состоянием таблицы, колонок и диапазона дат. Поддерживает разворачивание таблицы,
 * отображение выбранных показателей и визуализацию динамики через {@link StatisticChart}.
 *
 * @component
 * @param {StatisticTableProps} props - Свойства компонента.
 * @param {object} props.requestData - Начальные параметры запроса статистики.
 * @param {string[]} [props.externalSelectedColumns] - Внешне выбранные колонки для отображения.
 * @param {(columns: string[]) => void} [props.onColumnsReady] - Callback при готовности колонок.
 * @param {string} props.endpoint - API-эндпоинт для запроса статистики.
 * @param {number} props.minYear - Минимальный год для фильтра по дате.
 *
 * @returns {JSX.Element} Компонент с таблицей статистики, фильтром по дате и графиком динамики показателей.
 *
 * @example
 * ```tsx
 * <StatisticTable
 *   requestData={{ from_year: 2015, to_year: 2024 }}
 *   externalSelectedColumns={["ROE", "ROA"]}
 *   onColumnsReady={(cols) => console.log("Все колонки:", cols)}
 *   endpoint="/api/statistics"
 *   minYear={2010}
 * />
 * ```
 *
 * @see useTableData
 * @see useTableColumns
 * @see useExpandableTable
 * @see useDateRange
 * @see StatisticChart
 * @see DateRangeFilter
 */

export const StatisticTable: FC<StatisticTableProps> = memo(
  ({
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

    const tableTitle = rawStatisticData?.SType?.[0]?.dsName ?? '';
    const tableSubtitle = rawStatisticData?.SType?.[0]?.PublName
      ? `${tableTitle}. ${rawStatisticData.SType[0].PublName}`
      : tableTitle;

    return (
      <Section
        padding="medium"
        background="secondary"
        className={styles.container}
        withBorder
      >
        <Title level={2} size="large" className={styles.title}>
          {tableSubtitle}
        </Title>
        <Title level={3} size="small" className={styles.subtitle}>
          За период: {dateRange.from_year} - {dateRange.to_year}
        </Title>

          <DateRangeFilter
            initialFromYear={dateRange.from_year}
            initialToYear={dateRange.to_year}
            minYear={minYear}
            onApply={handleDateChange}
          />

        <Section padding="none" background="transparent">
          <div className={styles['table-container']} style={containerStyle}>
            {!activeColumns || activeColumns.length === 0 ? (
              <Section padding="large" background="primary">
                <div className={styles['no-selection']}>
                  Нет выбранных показателей для отображения
                </div>
              </Section>
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
                          typeof val === 'number'
                            ? val.toFixed(2)
                            : (val ?? '-');
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
            <Section
              padding="none"
              background="transparent"
              className={styles['toggle-section']}
            >
              <Button
                variant="secondary"
                size="small"
                onClick={() => setIsExpanded((prev) => !prev)}
                className={styles['toggle-button']}
              >
                {isExpanded ? 'Свернуть' : 'Развернуть'}
              </Button>
            </Section>
          )}
        </Section>

        <Section padding="none" background="transparent">
          <StatisticChart
            data={data}
            columns={columns}
            selectedColumns={activeColumns}
          />
        </Section>
      </Section>
    );
  }
);

export default StatisticTable;
