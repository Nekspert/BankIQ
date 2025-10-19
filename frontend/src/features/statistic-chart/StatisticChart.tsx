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

type Row = Record<string, number | null>;
type TableData = Record<string, Row>;

interface ChartProps {
  data: TableData;
  columns: string[];
}

const COLORS = [
  '#2563EB', // blue
  '#EF4444', // red
  '#10B981', // green
  '#F59E0B', // amber
  '#8B5CF6', // violet
  '#06B6D4', // cyan
  '#F97316', // orange
  '#3B82F6', // light blue
  '#0EA5A4',
  '#E11D48',
];

export const StatisticChart: React.FC<ChartProps> = ({ data, columns }) => {
  const chartData = useMemo(() => {
    return Object.entries(data).map(([dt, row]) => {
      const obj: Record<string, number | string | undefined> = { dt };
      columns.forEach((col) => {
        const v = row[col];
        obj[col] = typeof v === 'number' ? Number(v.toFixed(2)) : undefined;
      });
      return obj;
    });
  }, [data, columns]);

  return (
    <div className={styles['chart-wrapper']}>
      <h4 className={styles['chart-title']}>Динамика показателей</h4>
      <ResponsiveContainer width="100%" height={420}>
        <LineChart
          data={chartData}
          margin={{ top: 16, right: 24, left: 8, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e6eef6" />
          <XAxis
            dataKey="dt"
            tick={{ fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#e6e9ef' }}
            interval="preserveStartEnd"
          />
          <YAxis
            tickFormatter={(v) => (typeof v === 'number' ? `${v}` : String(v))}
            tick={{ fontSize: 12 }}
            axisLine={{ stroke: '#e6e9ef' }}
            tickLine={false}
          />
          <Tooltip
            formatter={(value: any) => (value == null ? '-' : String(value))}
            labelFormatter={(label) => `Дата: ${label}`}
          />
          <Legend
            verticalAlign="top"
            height={60}
            wrapperStyle={{ paddingBottom: 16 }}
          />
          {columns.map((col, idx) => (
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
  );
};
