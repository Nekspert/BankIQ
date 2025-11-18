import { RegisterForm } from '@/features/register-form/RegisterForm';
import styles from './styles.module.scss';
import type { FC } from 'react';

export const RegisterPopup: FC<{ handleChangeForm: () => void }> = ({
  handleChangeForm,
}) => {
  return (
    <div className={styles.register}>
      <h2 className={styles.register__title}>Регистрация</h2>
      <RegisterForm />
      <div className={styles.register__about}>
        Уже есть аккаунт? <button onClick={handleChangeForm}>Войти</button>
      </div>
    </div>
  );
};
