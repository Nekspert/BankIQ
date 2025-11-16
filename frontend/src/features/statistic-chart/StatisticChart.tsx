import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import styles from './styles.module.scss';
import type { TableData } from '../statistic-table/types';
/**
 * Свойства компонента {@link StatisticChart}, отображающего график динамики показателей.
 *
 * Определяет структуру входных данных и список выбранных колонок для отображения.
 *
 * @interface ChartProps
 * @property {TableData} data - Объект с данными, где ключ — дата, а значение — набор показателей.
 * @property {string[]} columns - Все доступные колонки (показатели), доступные для отображения на графике.
 * @property {string[]} [selectedColumns] - Необязательный список выбранных показателей для отрисовки (если не указано, берутся все).
 *
 * @example
 * ```ts
 * const props: ChartProps = {
 *   data: {
 *     "2023-01": { ROE: 10.5, ROA: 4.2 },
 *     "2024-01": { ROE: 12.1, ROA: 4.8 },
 *   },
 *   columns: ["ROE", "ROA"],
 *   selectedColumns: ["ROE"],
 * };
 * ```
 */

interface ChartProps {
  data: TableData;
  columns: string[];
  selectedColumns?: string[];
}

const COLORS = [
  '#2563EB',
  '#EF4444',
  '#10B981',
  '#F59E0B',
  '#8B5CF6',
  '#06B6D4',
  '#F97316',
  '#3B82F6',
  '#0EA5A4',
  '#E11D48',
];
/**
 * Компонент визуализации динамики показателей банков.
 *
 * Отображает интерактивный линейный график на основе данных таблицы {@link TableData}.
 * Поддерживает множественный выбор показателей, адаптивную ширину и горизонтальную прокрутку.
 * Использует библиотеку **Recharts**.
 *
 * @component
 * @param {ChartProps} props - Свойства компонента.
 * @param {TableData} props.data - Объект с данными, где ключ — дата, а значение — значения показателей.
 * @param {string[]} props.columns - Все доступные колонки (показатели), которые могут быть отображены.
 * @param {string[]} [props.selectedColumns] - Необязательный список выбранных для отображения колонок.
 *
 * @returns {JSX.Element | null} JSX-компонент с графиком показателей или сообщение, если данных нет.
 *
 * @example
 * ```tsx
 * <StatisticChart
 *   data={{
 *     "2020-01": { ROE: 12.3, ROA: 4.5 },
 *     "2021-01": { ROE: 14.1, ROA: 5.2 },
 *   }}
 *   columns={["ROE", "ROA"]}
 *   selectedColumns={["ROE"]}
 * />
 * ```
 *
 * @see TableData
 * @see https://recharts.org/en-US/api/LineChart
 */

export const StatisticChart: React.FC<ChartProps> = ({
  data,
  columns,
  selectedColumns,
}) => {
  const active =
    selectedColumns && selectedColumns.length > 0 ? selectedColumns : columns;

  const chartData = useMemo(() => {
    return Object.entries(data).map(([dt, row]) => {
      const obj: Record<string, number | string | undefined> = { dt };
      active.forEach((col) => {
        const v = row[col];
        obj[col] = typeof v === 'number' ? Number(v.toFixed(2)) : undefined;
      });
      return obj;
    });
  }, [data, active]);

  if (!data) return null;

  if (active.length === 0) {
    return (
      <div className={styles['chart-wrapper']}>
        <h4 className={styles['chart-title']}>Динамика показателей</h4>
        <div style={{ padding: 16, color: '#666' }}>
          Нет выбранных показателей для отображения.
        </div>
      </div>
    );
  }

  const renderRotatedTick = (props: any) => {
    const { x, y, payload } = props;
    const offset = 5;
    return (
      <text
        x={x}
        y={y + offset}
        transform={`rotate(-60 ${x} ${y + offset})`}
        textAnchor="end"
        fontSize={10}
        style={{ fill: 'var(--text-primary)' }}
      >
        {payload.value}
      </text>
    );
  };

  const pointsCount = chartData.length;
  const minPointWidth = 50;
  const minChartWidth = 700;
  const chartWidth = Math.max(pointsCount * minPointWidth, minChartWidth);

  return (
    <div className={styles['chart-wrapper']}>
      <h4 className={styles['chart-title']}>Динамика показателей</h4>
      <div className={styles['chart-scroll']} style={{ overflowX: 'auto' }}>
        <div style={{ width: `${chartWidth}px`, minWidth: `${minChartWidth}px` }}>
          <ResponsiveContainer width="100%" height={420}>
            <LineChart
              data={chartData}
              margin={{ top: 16, right: 24, left: 8, bottom: 90 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--text-primary)" />
              <XAxis
                dataKey="dt"
                tick={renderRotatedTick}
                tickLine={false}
                axisLine={{ stroke: 'var(--text-primary)' }}
                interval={0}
                height={1}
              />
              <YAxis
                tickFormatter={(v) => (typeof v === 'number' ? `${v}` : String(v))}
                tick={{ fontSize: 12 }}
                axisLine={{ stroke: 'var(--text-primary)' }}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--background-secondary)',
                  border: '1px solid var(--text-muted)',
                  borderRadius: 8,
                  color: 'var(--text-primary)',
                  fontSize: 12,
                }}
                labelStyle={{
                  fontWeight: 600,
                  marginBottom: 4,
                  color: 'var(--text-primary)',
                }}
                itemStyle={{
                  color: 'var(--text-primary)',
                }}
                formatter={(value: any) => (value == null ? '-' : String(value))}
                labelFormatter={(label) => `Дата: ${label}`}
              />
              <Legend
                verticalAlign="top"
                height={60}
                content={({ payload }) => (
                  <ul className={styles['legend']}>
                    {payload?.map((entry, index) => (
                      <li key={`item-${index}`} className={styles['legend__item']}>
                        <span
                          className={styles['legend__item-text']}
                          style={{
                            backgroundColor: entry.color,
                          }}
                        />
                        {entry.value}
                      </li>
                    ))}
                  </ul>
                )}
              />
              {active.map((col, idx) => (
                <Line
                  key={col}
                  type="monotone"
                  dataKey={col}
                  name={col}
                  stroke={COLORS[idx % COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                  connectNulls={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
