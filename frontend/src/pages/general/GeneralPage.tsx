import { useState, type FC } from 'react';
import { StatisticTable } from '@/features/statistic-table/StatisticTable';
import styles from './styles.module.scss';
import TableFilterPanel from '@/features/table-filter-panel/TableFilterPanel';
import { tableArray, tableConfigs } from './constants';

export const GeneralPage: FC = () => {
  const [selectedIds, setSelectedIds] = useState<string[]>(
    tableArray.map((it) => it.id)
  );

  const handleApply = (ids: string[]) => {
    setSelectedIds(ids);
  };

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Общая статистика, предоставляемая ЦБ РФ</h1>
      </header>

      <div style={{ marginBottom: 20 }}>
        <TableFilterPanel
          items={tableArray}
          initialSelectedIds={selectedIds}
          onApply={handleApply}
        />
      </div>

      <div className={styles.grid}>
        {tableArray.map((it) => {
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

export default GeneralPage;
