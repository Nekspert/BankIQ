import { type FC } from 'react';
import styles from './styles.module.scss';
import { BanksComparison } from '@/features/banks-comparison/BanksComparison';
import Title from '@/shared/ui/title/Title';
import { indicatorsF123Api } from '@/shared/api/form-123/indicatorsApi';
import Form123Table from '@/features/f-123/form123-table/Form123Table';

export const MainPage: FC = () => {
  // const data = indicatorsF123Api.getBankDatetimes()
  const data = indicatorsF123Api.getIndicator({
    regNum: 1481,
    date: '2024-06-01T00:00:00Z',
  });
  console.log(data);
  return (
    <section className={styles.page}>
      <Title level={1} size="xlarge">
        Главная страница
      </Title>
      <BanksComparison />
      <Form123Table />
    </section>
  );
};

export default MainPage;
