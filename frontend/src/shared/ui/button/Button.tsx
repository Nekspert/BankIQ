import { type FC } from 'react';
import styles from './styles.module.scss';
import classNames from 'classnames';
import type { ButtonProps } from './types';

export const Button: FC<ButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'medium',
  disabled = false,
  className,
  icon,
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={classNames(
        styles.button,
        styles[`button--${variant}`],
        styles[`button--${size}`],
        className
      )}
    >
      {icon && <span className={styles.button__icon}>{icon}</span>}
      {children}
    </button>
  );
};

export default Button;
