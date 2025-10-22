import { useMemo, useState } from 'react';
import { StatisticTable } from '@/features/statistic-table/StatisticTable';
import styles from './styles.module.scss';
import type { GetStatisticParams } from '@/shared/api/hooks/statistic/types';
import TableFilterPanel, {
  type TableItem,
} from '@/features/table-filter-panel/TableFilterPanel';

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
  from_year: 2015,
  to_year: 2025,
};

export const MainPage: React.FC = () => {
  const items: TableItem[] = useMemo(
    () => [
      {
        id: 'summary',
        title: 'Сводная статистика',
        requestData: summaryInfo,
        endpoint: 'interest_rates_credit',
      },
      {
        id: 'territorial',
        title: 'Территориальная статистика',
        requestData: territorialInfo,
        endpoint: 'interest_rates_credit',
      },
      {
        id: 'deposits',
        title: 'Депозиты',
        requestData: depositInfo,
        endpoint: 'interest_rates_deposit',
      },
    ],
    []
  );

  const [selectedIds, setSelectedIds] = useState<string[]>(
    items.map((it) => it.id)
  );
  const [globalFromYear, setGlobalFromYear] = useState<number | null>(null);
  const [globalToYear, setGlobalToYear] = useState<number | null>(null);

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
          initialFromYear={items[0].requestData.from_year}
          initialToYear={items[0].requestData.to_year}
          onApply={({ selectedIds: ids, from_year, to_year }) => {
            setSelectedIds(ids);
            setGlobalFromYear(from_year);
            setGlobalToYear(to_year);
          }}
        />
      </div>

      <div className={styles.grid}>
        {items.map((it) =>
          selectedIds.includes(it.id) ? (
            <article key={it.id} className={styles.card}>
              <StatisticTable
                requestData={it.requestData}
                endpoint={it.endpoint}
              />
            </article>
          ) : null
        )}
      </div>
    </section>
  );
};

export default MainPage;
