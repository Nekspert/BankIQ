import React, { useState } from 'react';
import styles from './styles.module.scss';

export interface TableItem {
  id: string;
  title: string;
}

interface Props {
  items: TableItem[];
  initialSelectedIds?: string[];
  onApply: (selectedIds: string[]) => void;
}

const TableFilterPanel: React.FC<Props> = ({
  items,
  initialSelectedIds = [],
  onApply,
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelectedIds);

  const toggleItem = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleReset = () => {
    setSelectedIds([]);
  };

  const handleApply = () => {
    onApply(selectedIds);
  };

  return (
    <div className={styles['filter-panel']}>
      {items.map((item) => {
        const isActive = selectedIds.includes(item.id);
        return (
          <label
            key={item.id}
            className={`${styles['filter-panel__item']} ${isActive ? styles.active : styles.inactive}`}
          >
            <input
              type="checkbox"
              checked={isActive}
              onChange={() => toggleItem(item.id)}
            />
            <span>{item.title}</span>
          </label>
        );
      })}

      <div className={styles['filter-panel__actions']}>
        <button className={styles['reset-btn']} onClick={handleReset}>
          Сбросить
        </button>
        <button className={styles['apply-btn']} onClick={handleApply}>
          Применить
        </button>
      </div>
    </div>
  );
};

export default TableFilterPanel;
