import { type FC } from 'react';
import classNames from 'classnames';
import styles from './styles.module.scss';
import type { ToggleSwitchProps } from './types';

export const ToggleSwitch: FC<ToggleSwitchProps> = ({
  checked,
  onChange,
  label,
  className,
  disabled,
}) => {
  return (
    <label className={classNames(styles.wrapper, className)}>
      <div
        className={classNames(styles.switch, {
          [styles.switchChecked]: checked,
          [styles.switchDisabled]: disabled,
        })}
        onClick={() => !disabled && onChange(!checked)}
        role="switch"
        aria-checked={checked}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            !disabled && onChange(!checked);
          }
        }}
      >
        <div
          className={classNames(styles.knob, { [styles.knobChecked]: checked })}
        />
      </div>
      {label && <span className={styles.label}>{label}</span>}
    </label>
  );
};

export default ToggleSwitch;
