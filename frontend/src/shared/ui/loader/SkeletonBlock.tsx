import React from 'react';
import styles from './styles.module.scss';

export const SkeletonBlock: React.FC<{
  kind?: 'table' | 'chart';
  className?: string;
}> = ({ kind = 'table', className }) => {
  return (
    <div
      className={`${kind === 'chart' ? styles['skeleton-chart'] : styles['skeleton-table']} ${styles.skeleton} ${className ?? ''}`}
    />
  );
};
