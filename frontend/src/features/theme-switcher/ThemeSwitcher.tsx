import { type FC } from 'react';
import { useTheme } from '@/shared/hooks/useTheme';
import styles from './styles.module.scss';

export const ThemeSwitcher: FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={styles.switcher}
      aria-label={`Переключить на ${theme === 'light' ? 'тёмную' : 'светлую'} тему`}
      title={`Переключить на ${theme === 'light' ? 'тёмную' : 'светлую'} тему`}
    >
      {theme === 'light' ? (
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
            fill="currentColor"
          />
        </svg>
      ) : (
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="12" cy="12" r="5" fill="currentColor" />
          <path
            d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      )}
    </button>
  );
};

export default ThemeSwitcher;
