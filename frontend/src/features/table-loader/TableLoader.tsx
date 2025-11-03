import { SkeletonBlock } from '@/shared/ui/loader/SkeletonBlock';
import styles from './styles.module.scss';
import Section from '@/shared/ui/section/Section';

export const TableLoader = () => {
  return (
    <Section withBorder>
      <div className={styles['statistic-header']}>
        <div>
          <h2 className={styles['title']}>Загрузка...</h2>
          <h3 className={styles['subtitle']}>Подготавливаем данные</h3>
        </div>
      </div>

      <div className={styles['table-container']} style={{ marginTop: 12 }}>
        <SkeletonBlock kind="table" />
      </div>

      <div style={{ marginTop: 12 }}>
        <SkeletonBlock kind="chart" />
      </div>
    </Section>
  );
};
