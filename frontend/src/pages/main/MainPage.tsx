import { useState } from 'react';
import { StatisticTable } from '@/features/statistic-table/StatisticTable';
import styles from './styles.module.scss';

const summaryInfo = {
  publication_id: 14,
  dataset_id: 25,
  measure_id: 2,
  from_year: 2024,
  to_year: 2025,
};
const territorialInfo = {
  publication_id: 15,
  dataset_id: 30,
  measure_id: 23,
  from_year: 2024,
  to_year: 2025,
};

export const MainPage = () => {
  // sharedColumns holds the chosen column keys for both tables
  const [sharedColumns, setSharedColumns] = useState<string[] | null>(null);

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Статистика — общий фильтр</h1>
        <p className={styles.lead}>
          Выберите показатели, которые будут показаны в обеих таблицах
        </p>
      </header>

      <div className={styles.grid}>
        <article className={styles.card}>
          <StatisticTable
            requestData={summaryInfo}
            externalSelectedColumns={sharedColumns ?? undefined}
          />
        </article>

        <article className={styles.card}>
          <StatisticTable
            requestData={territorialInfo}
            externalSelectedColumns={sharedColumns ?? undefined}
          />
        </article>
      </div>
    </section>
  );
};
