import { type FC } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import styles from './styles.module.scss';
import { useAuth } from '@/shared/hooks/useAuth';
import Input from '@/shared/ui/input/Input';
import Button from '@/shared/ui/button/Button';
import { loginSchema } from './constants';
import type { Form } from './types';

export const LoginForm: FC = () => {
  const navigate = useNavigate();
  const { login, user } = useAuth();
  const { register, handleSubmit, formState, getValues } = useForm<Form>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: Form) => {
    await login(data.email, data.password);
  };

  // if (user) {
  //   navigate(AppRoutes.home);
  // }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
      <Input
        placeholder="E-mail"
        value={getValues('email')}
        {...register('email')}
      />
      <Input
        value={getValues('password')}
        {...register('password')}
        type="password"
        placeholder="Пароль"
      />
      <Button type="submit" disabled={formState.isSubmitting}>
        Войти
      </Button>
    </form>
  );
};
