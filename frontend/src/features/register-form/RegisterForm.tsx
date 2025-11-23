import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { useEffect, type FC } from 'react';
import styles from './styles.module.scss';
import Button from '@/shared/ui/button/Button';
import { AppRoutes } from '@/shared/config/routes';
import Input from '@/shared/ui/input/Input';
import { useAuth } from '@/shared/hooks/useAuth';
import { registerSchema } from './constants';
import type { Form } from './types';

export const RegisterForm: FC = () => {
  const navigate = useNavigate();
  const { register: regFn, user } = useAuth();
  const { register, handleSubmit, formState, getValues } = useForm<Form>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: Form) => {
    await regFn(data.email, data.password);
  };

  useEffect(() => {
    if (user) {
      navigate(AppRoutes.home);
    }
  }, [user, navigate]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
      <Input
        value={getValues().email}
        placeholder="E-mail"
        {...register('email')}
      />
      <Input
        value={getValues().password}
        placeholder="Пароль"
        type="password"
        {...register('password')}
      />
      <Button type="submit" disabled={formState.isSubmitting}>
        Зарегистрироваться
      </Button>
    </form>
  );
};
