import { type FC } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import styles from './styles.module.scss';
import { useAuth } from '@/shared/hooks/useAuth';
import Input from '@/shared/ui/input/Input';
import Button from '@/shared/ui/button/Button';
import { loginSchema } from './constants';
import type { Form } from './types';

export const LoginForm: FC<{ onClose: () => void }> = ({ onClose }) => {
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    setError,
    clearErrors,
    formState: { errors, isSubmitting },
  } = useForm<Form>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: Form) => {
    clearErrors();

    try {
      await login(data.username, data.password);
      onClose();
    } catch (err: any) {
      if (err.response?.status === 400) {
        const server = err.response.data;

        if (server?.detail) {
          setError('username', { message: server.detail });
        }

        return;
      }

      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
      <Input
        placeholder="Логин"
        {...register('username')}
        error={errors.username?.message}
      />

      <Input
        type="password"
        placeholder="Пароль"
        {...register('password')}
        error={errors.password?.message}
      />

      <Button type="submit" disabled={isSubmitting}>
        Войти
      </Button>
    </form>
  );
};
