import { motion, AnimatePresence } from 'framer-motion';
import classNames from 'classnames';
import { useTableFilterPanel } from './hooks/useTableFilterPanel';
import styles from './styles.module.scss';
import type { TableFilterPanelProps } from './types';
import type { FC } from 'react';

export const TableFilterPanel: FC<TableFilterPanelProps> = ({
  items,
  initialSelectedIds = [],
  onApply,
}) => {
  const {
    selectedItems,
    availableItems,
    addItem,
    removeItem,
    handleReset,
    handleApply,
  } = useTableFilterPanel({ items, initialSelectedIds, onApply });

  return (
    <div className={styles['filter-panel']}>
      <h2 className={styles['filter-panel__title--main']}>Настройте таблицы, которые хотите видеть</h2>
      <div className={styles['filter-panel__section']}>
        <h3 className={styles['filter-panel__title']}>Выбранное</h3>
        <ul className={styles['filter-panel__list']}>
          <AnimatePresence>
            {selectedItems.length === 0 ? (
              <motion.li
                className={styles['filter-panel__empty']}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                Ничего не выбрано
              </motion.li>
            ) : (
              selectedItems.map((item) => (
                <motion.li
                  key={item.id}
                  className={styles['filter-panel__item']}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <span>{item.title}</span>
                  <button
                    className={styles['filter-panel__remove']}
                    onClick={() => removeItem(item.id)}
                    aria-label={`Удалить ${item.title}`}
                  >
                    ✕
                  </button>
                </motion.li>
              ))
            )}
          </AnimatePresence>
        </ul>
      </div>

      <div className={styles['filter-panel__section']}>
        <h3 className={styles['filter-panel__title']}>Доступное</h3>
        <ul className={styles['filter-panel__list']}>
          <AnimatePresence>
            {availableItems.map((item) => (
              <motion.li
                key={item.id}
                className={classNames(styles['filter-panel__item'], {
                  [styles['filter-panel__item--available']]: true,
                })}
                onClick={() => addItem(item.id)}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -40 }}
                transition={{ duration: 0.2 }}
              >
                <span>{item.title}</span>
              </motion.li>
            ))}
            {!availableItems.length && (
              <motion.li
                className={styles['filter-panel__empty']}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                Всё выбрано
              </motion.li>
            )}
          </AnimatePresence>
        </ul>
      </div>

      <div className={styles['filter-panel__actions']}>
        <button
          className={styles['filter-panel__reset-btn']}
          onClick={handleReset}
        >
          Сбросить
        </button>
        <button
          className={styles['filter-panel__apply-btn']}
          onClick={handleApply}
        >
          Применить
        </button>
      </div>
    </div>
  );
};

export default TableFilterPanel;
