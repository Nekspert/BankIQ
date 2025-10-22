import React from 'react';
import styles from './styles.module.scss';

export const Loader: React.FC<{ size?: number; label?: string }> = ({
  size = 40,
  label,
}) => {
  return (
    <div
      className={styles.loader}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <svg
        className={styles.spinner}
        width={size}
        height={size}
        viewBox="0 0 50 50"
        aria-hidden="true"
      >
        <circle
          className={styles.path}
          cx="25"
          cy="25"
          r="20"
          fill="none"
          strokeWidth="4"
        />
      </svg>
      {label && <span className={styles.label}>{label}</span>}
    </div>
  );
};

export default Loader;
