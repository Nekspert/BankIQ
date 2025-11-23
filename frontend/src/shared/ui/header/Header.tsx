import { headerNavList } from '@/shared/config/constants';
import { Link } from 'react-router-dom';
import styles from './styles.module.scss';
import { AppRoutes } from '@/shared/config/routes';
import ThemeSwitcher from '@/features/theme-switcher/ThemeSwitcher';
import UserSvg from '@/shared/icons/AddParticipant.svg?react';
import Button from '../button/Button';
import PopUp from '../pop-up/PopUp';
import { LoginPopup } from '@/widgets/login/LoginPopup';
import { useState } from 'react';
import { useAuth } from '@/shared/hooks/useAuth';
import { RegisterPopup } from '@/widgets/register/RegisterPopup';

export const Header = () => {
  const { user } = useAuth();
  const [formIsOpen, setFormIsOpen] = useState<boolean>(false);
  const [isAuthForm, setIsAuthForm] = useState<boolean>(true);

  const hangleChangeFormStatus = () => setFormIsOpen((prev) => !prev);

  const handleProfileClick = () => {
    // if (!user) {
    setFormIsOpen(true);
    // }
  };

  const handleChangeFormType = () => setIsAuthForm((prev) => !prev);

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
      <div className={styles['header__right']}>
        <Button
          onClick={handleProfileClick}
          className={styles['header__right-button']}
          variant="ghost"
        >
          <UserSvg />
        </Button>
        <ThemeSwitcher />
      </div>
      <PopUp isOpen={formIsOpen} onClose={hangleChangeFormStatus}>
        {isAuthForm ? (
          <LoginPopup handleChangeForm={handleChangeFormType} />
        ) : (
          <RegisterPopup handleChangeForm={handleChangeFormType} />
        )}
      </PopUp>
    </header>
  );
};
