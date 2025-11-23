import { LoginForm } from '@/features/login-form/LoginForm';
import styles from './styles.module.scss';
import type { FC } from 'react';

export const LoginPopup: FC<{ handleChangeForm: () => void }> = ({
  handleChangeForm,
}) => {
  return (
    <div className={styles.login}>
      <h2 className={styles.login__title}>Вход</h2>
      <LoginForm />
      <div className={styles.login__about}>
        Нет аккаунта?{' '}
        <button onClick={handleChangeForm}>Зарегистрироваться</button>
      </div>
    </div>
  );
};
