import Input from '@/shared/ui/input/Input';
import type { Form } from './types';
import { useForm } from 'react-hook-form';
import type { FC } from 'react';
import { useAuth } from '@/shared/hooks/useAuth';
import { zodResolver } from '@hookform/resolvers/zod';
import { defaultValues, registerSchema } from './constants';
import styles from './styles.module.scss';
import Button from '@/shared/ui/button/Button';

export const RegisterForm: FC<{ onClose: () => void }> = ({ onClose }) => {
  const { register: regFn } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    clearErrors,
  } = useForm<Form>({
    resolver: zodResolver(registerSchema),
    defaultValues,
  });

  const onSubmit = async (data: Form) => {
    clearErrors();

    try {
      await regFn(data);
      onClose();
    } catch (err: any) {
      if (
        err.response?.status === 400 &&
        typeof err.response.data === 'object'
      ) {
        const errorsObj = err.response.data;

        Object.entries(errorsObj).forEach(([field, messages]) => {
          setError(field as keyof Form, {
            type: 'server',
            message: (messages as string[])[0],
          });
        });
      } else {
        console.error(err);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
      <Input
        placeholder="E-mail"
        {...register('email')}
        error={errors.email?.message}
      />

      <Input
        placeholder="Имя"
        {...register('firstName')}
        error={errors.firstName?.message}
      />

      <Input
        placeholder="Фамилия"
        {...register('lastName')}
        error={errors.lastName?.message}
      />

      <Input
        placeholder="Пароль (мин. 8 символов)"
        type="password"
        {...register('password')}
        error={errors.password?.message}
      />

      <Input
        placeholder="Никнейм (необязательно)"
        {...register('username')}
        error={errors.username?.message}
      />

      <Button type="submit" disabled={isSubmitting}>
        Зарегистрироваться
      </Button>
    </form>
  );
};
