import Loader from '@/shared/ui/loader/Loader';
import { SkeletonBlock } from '@/shared/ui/loader/SkeletonBlock';
import styles from './styles.module.scss';

export const TableLoader = () => {
  return (
    <div className={styles['statistic-block']}>
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

      <div style={{ marginTop: 12 }}>
        <Loader label="Загружаем данные" />
      </div>
    </div>
  );
};
