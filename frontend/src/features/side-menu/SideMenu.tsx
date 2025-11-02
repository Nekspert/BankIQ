import { useEffect, useRef, type FC, type MouseEvent } from 'react';
import type { SideMenuProps } from './types';
import styles from './styles.module.scss';
import classNames from 'classnames';
import Button from '@/shared/ui/button/Button';

export const SideMenu: FC<SideMenuProps> = ({
  tableList,
  isOpen,
  activeId,
  onLinkClick,
  handleClose,
}) => {
  const menuRef = useRef<HTMLElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  const handleClick = (id: string, event: MouseEvent) => {
    event.preventDefault();
    onLinkClick?.(id);

    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;

      if (
        isOpen &&
        menuRef.current &&
        !menuRef.current.contains(target) &&
        overlayRef.current &&
        !overlayRef.current.contains(target)
      ) {
        handleClose?.();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        handleClose?.();
      }
    };

    document.addEventListener('mousedown', handleClickOutside as any);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside as any);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, handleClose]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <>
      {isOpen && <div ref={overlayRef} className={styles['menu__overlay']} />}
      <aside
        ref={menuRef}
        className={classNames(styles['menu'], {
          [styles['menu--closed']]: !isOpen,
        })}
      >
        <div className={styles['menu__header']}>
          <h2 className={styles['menu__title']}>Навигация по графикам</h2>
          <div className={styles['menu__divider']} />
        </div>
        <nav className={styles['menu__nav']}>
          <ul className={styles['menu__list']}>
            {tableList.map((link, index) => (
              <li key={link.id} className={styles['menu__item']}>
                <a
                  href={`#${link.id}`}
                  className={classNames(styles['menu__link'], {
                    [styles['menu__link--active']]: activeId === link.id,
                  })}
                  onClick={(e) => handleClick(link.id, e)}
                >
                  <span className={styles['menu__link-icon']}>{index + 1}</span>
                  <span className={styles['menu__link-text']}>
                    {link.title}
                  </span>
                  {activeId === link.id && (
                    <div className={styles['menu__link-indicator']} />
                  )}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className={styles['menu__footer']}>
          <div className={styles['menu__divider']} />
          <Button
            onClick={handleClose}
            size="small"
            variant="primary"
            className={styles['menu__hint']}
          >
            Закрыть
          </Button>
        </div>
      </aside>
    </>
  );
};
