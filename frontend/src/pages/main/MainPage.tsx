import { type FC } from 'react';
import styles from './styles.module.scss';
import { BanksComparison } from '@/features/banks-comparison/BanksComparison';
import Title from '@/shared/ui/title/Title';
import Form123Table from '@/features/f-123/form123-table/Form123Table';
import { Form810Table } from '@/features/f-810/form810-table/Form810Table';

export const MainPage: FC = () => {
  return (
    <section className={styles.page}>
      <Title level={1} size="xlarge">
        Главная страница
      </Title>
      <BanksComparison />
      <Form123Table />
      <Form810Table />
    </section>
  );
};

export default MainPage;
