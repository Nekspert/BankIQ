import { type FC } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCustomSelect } from './hooks/useCustomSelect';
import styles from './styles.module.scss';
import type { CustomSelectProps } from './types';
import classNames from 'classnames';

export const CustomSelect: FC<CustomSelectProps> = ({
  value,
  onChange,
  options,
  placeholder,
  className,
}) => {
  const {
    isOpen,
    setIsOpen,
    selectRef,
    handleSelect,
    handleKeyPress,
    selectedLabel,
  } = useCustomSelect({ value, onChange, options, placeholder });

  return (
    <div
      className={classNames(styles['custom-select'], className)}
      ref={selectRef}
      tabIndex={0}
      onKeyDown={handleKeyPress}
    >
      <div
        className={styles['custom-select__trigger']}
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <span
          className={classNames(styles['custom-select__label'], {
            [styles['custom-select__label--placeholder']]: !value,
          })}
        >
          {selectedLabel}
        </span>
        <span
          className={classNames(styles['custom-select__arrow'], {
            [styles['custom-select__arrow--open']]: isOpen,
          })}
        />
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.ul
            className={styles['custom-select__options']}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {options.map((option) => (
              <li
                key={option.value}
                className={classNames(styles['custom-select__option'], {
                  [styles['custom-select__option--selected']]:
                    option.value === value,
                })}
                onClick={() => handleSelect(option.value)}
                onKeyDown={(e) => handleKeyPress(e, option.value)}
                tabIndex={0}
              >
                {option.label}
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CustomSelect;
