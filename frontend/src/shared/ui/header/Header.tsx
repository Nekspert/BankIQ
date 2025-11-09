import { headerNavList } from '@/shared/config/constants';
import { Link } from 'react-router-dom';
import styles from './styles.module.scss';
import { AppRoutes } from '@/shared/config/routes';
import ThemeSwitcher from '@/features/theme-switcher/ThemeSwitcher';

export const Header = () => {
  return (
    <header className={styles['header']}>
      <Link to={AppRoutes.home} className={styles['header__logo']}>
        <img src="/logo.svg" alt="Logo" /> BankIQ
      </Link>
      <nav className={styles['header__nav']}>
        {headerNavList.map((item) => (
          <Link to={item.link}>{item.name}</Link>
        ))}
      </nav>
      <ThemeSwitcher />
    </header>
  );
};
