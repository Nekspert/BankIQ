import styles from './styles.module.scss';
import classNames from 'classnames';
import type { SectionProps } from './types';
import type { FC } from 'react';

export const Section: FC<SectionProps> = ({
  children,
  className,
  padding = 'medium',
  background = 'secondary',
}) => {
  return (
    <section
      className={classNames(
        styles.section,
        styles[`section--padding-${padding}`],
        styles[`section--background-${background}`],
        className
      )}
    >
      {children}
    </section>
  );
};

export default Section;
