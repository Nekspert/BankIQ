import { type FC } from 'react';
import styles from './styles.module.scss';
import { BanksComparison } from '@/features/banks-comparison/BanksComparison';
import Title from '@/shared/ui/title/Title';

export const MainPage: FC = () => {
  return (
    <section className={styles.page}>
      <Title level={1} size="xlarge">
        Главная страница
      </Title>
      <BanksComparison />
    </section>
  );
};

export default MainPage;
