import { type FC } from 'react';
import styles from './styles.module.scss';
import classNames from 'classnames';
import type { TitleProps } from './types';

export const Title: FC<TitleProps> = ({
  children,
  level = 2,
  size = 'medium',
  align = 'left',
  className,
}) => {
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;

  return (
    <Tag
      className={classNames(
        styles.title,
        styles[`title--${size}`],
        styles[`title--align-${align}`],
        className
      )}
    >
      {children}
    </Tag>
  );
};

export default Title;
