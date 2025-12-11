import { useAuth } from '@/shared/hooks/useAuth';
import styles from './styles.module.scss';
import Section from '@/shared/ui/section/Section';
import { LkProfileCard } from '@/features/lk-profile-card/LkProfileCard';

export const LkPage = () => {
  const { user } = useAuth();

  return (
    <div className={styles.wrapper}>
      <LkProfileCard />
      <Section withBorder padding="medium">
        <h3 className={styles.blockTitle}>Контактная информация</h3>
        <div className={styles.row}>
          <span className={styles.label}>Email:</span>
          <span className={styles.value}>{user?.email}</span>
        </div>
      </Section>
    </div>
  );
};
