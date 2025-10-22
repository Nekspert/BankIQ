import { useMemo, useState } from 'react';
import { StatisticTable } from '@/features/statistic-table/StatisticTable';
import styles from './styles.module.scss';
import type { GetStatisticParams } from '@/shared/api/hooks/statistic/types';
import TableFilterPanel from '@/features/table-filter-panel/TableFilterPanel';

interface TableItem {
  id: string;
  title: string;
}

interface TableConfig {
  requestData: GetStatisticParams;
  endpoint: string;
  minYear: number;
}

const summaryInfo: GetStatisticParams = {
  publication_id: 14,
  dataset_id: 25,
  measure_id: 2,
  from_year: 2024,
  to_year: 2025,
};

const territorialInfo: GetStatisticParams = {
  publication_id: 15,
  dataset_id: 30,
  measure_id: 23,
  from_year: 2024,
  to_year: 2025,
};

const depositInfo: GetStatisticParams = {
  publication_id: 18,
  dataset_id: 37,
  measure_id: 2,
  from_year: 2023,
  to_year: 2025,
};

export const MainPage: React.FC = () => {
  const items: TableItem[] = useMemo(
    () => [
      {
        id: 'summary',
        title: 'Сводная статистика',
      },
      {
        id: 'territorial',
        title: 'Территориальная статистика',
      },
      {
        id: 'deposits',
        title: 'Депозиты',
      },
    ],
    []
  );

  const tableConfigs: Record<string, TableConfig> = useMemo(
    () => ({
      summary: {
        requestData: summaryInfo,
        endpoint: 'interest_rates_credit',
        minYear: 2014,
      },
      territorial: {
        requestData: territorialInfo,
        endpoint: 'interest_rates_credit',
        minYear: 2019,
      },
      deposits: {
        requestData: depositInfo,
        endpoint: 'interest_rates_deposit',
        minYear: 2014,
      },
    }),
    []
  );

  const [selectedIds, setSelectedIds] = useState<string[]>(
    items.map((it) => it.id)
  );

  const handleApply = (ids: string[]) => {
    setSelectedIds(ids);
  };

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Статистика</h1>
        <p className={styles.lead}>
          Управляйте видимыми таблицами и диапазоном данных
        </p>
      </header>

      <div style={{ marginBottom: 20 }}>
        <TableFilterPanel
          items={items}
          initialSelectedIds={selectedIds}
          onApply={handleApply}
        />
      </div>

      <div className={styles.grid}>
        {items.map((it) => {
          const isSelected = selectedIds.includes(it.id);
          if (!isSelected) return null;

          const config = tableConfigs[it.id];
          if (!config) return null;

          return (
            <article key={it.id} className={styles.card}>
              <StatisticTable
                requestData={config.requestData}
                endpoint={config.endpoint}
                minYear={config.minYear}
              />
            </article>
          );
        })}
      </div>
    </section>
  );
};

export default MainPage;
