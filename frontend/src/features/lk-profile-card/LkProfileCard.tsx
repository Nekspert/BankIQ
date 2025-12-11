import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/shared/hooks/useAuth';
import styles from './styles.module.scss';
import axios from 'axios';
import Section from '@/shared/ui/section/Section';

type FormValues = {
  firstName: string;
  lastName: string;
  avatar: FileList | null;
};

export const LkProfileCard = () => {
  const { user, setUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);

  const { register, handleSubmit, reset, watch } = useForm<FormValues>({
    defaultValues: {
      firstName: user?.firstName || '',
      lastName: user?.lastName || '',
      avatar: null,
    },
  });

  const avatarFile = watch('avatar');

  const onSubmit = async (data: FormValues) => {
    const formData = new FormData();

    formData.append('first_name', data.firstName);
    formData.append('last_name', data.lastName);

    if (data.avatar && data.avatar.length > 0) {
      formData.append('photo', data.avatar[0]);
    }

    try {
      const res = await axios.patch('/api/me/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUser(prev => ({...prev, ...res.data}));
      setIsEditing(false);
    } catch (err) {
      console.error(err);
    }
  };

  const cancelEdit = () => {
    reset();
    setIsEditing(false);
  };

  return (
    <Section withBorder padding="large">
      {!isEditing && (
        <div className={styles.header}>
          <img
            src={user?.profile?.imageUrl}
            alt="avatar"
            className={styles.avatar}
          />
          <div className={styles.info}>
            <h2 className={styles.name}>
              {user?.firstName} {user?.lastName}
            </h2>
            <p className={styles.username}>@{user?.username}</p>
            <p className={styles.username}>ID: {user?.id}</p>
          </div>

          <button className={styles.editBtn} onClick={() => setIsEditing(true)}>
            Редактировать
          </button>
        </div>
      )}

      {isEditing && (
        <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.formRow}>
            <label>Имя</label>
            <input {...register('firstName')} type="text" />
          </div>

          <div className={styles.formRow}>
            <label>Фамилия</label>
            <input {...register('lastName')} type="text" />
          </div>

          <div className={styles.formRow}>
            <label>Аватар</label>
            <input {...register('avatar')} type="file" accept="image/*" />
          </div>

          {avatarFile && avatarFile.length > 0 && (
            <img
              className={styles.preview}
              src={URL.createObjectURL(avatarFile[0])}
            />
          )}

          <div className={styles.buttons}>
            <button type="submit" className={styles.saveBtn}>
              Сохранить
            </button>
            <button
              type="button"
              className={styles.cancelBtn}
              onClick={cancelEdit}
            >
              Отмена
            </button>
          </div>
        </form>
      )}
    </Section>
  );
};
