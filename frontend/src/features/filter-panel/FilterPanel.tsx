// components/filters/FilterPanel.tsx
import React, { useEffect, useMemo, useState } from 'react';
import styles from './styles.module.scss';

interface FilterPanelProps {
  columns: string[];
  initialSelected?: string[];
  onApply: (selected: string[]) => void;
  onCancel?: () => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  columns,
  initialSelected = [],
  onApply,
  onCancel,
}) => {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<Record<string, boolean>>(() =>
    columns.reduce(
      (acc, c) => {
        acc[c] =
          initialSelected.length > 0 ? initialSelected.includes(c) : true;
        return acc;
      },
      {} as Record<string, boolean>
    )
  );

  // Keep selection in sync when columns change (preserve previous choices when possible)
  useEffect(() => {
    setSelected((prev) => {
      const next: Record<string, boolean> = {};
      columns.forEach((c) => {
        next[c] =
          prev[c] ??
          (initialSelected.length > 0 ? initialSelected.includes(c) : true);
      });
      return next;
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columns, initialSelected]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return columns;
    return columns.filter((c) => c.toLowerCase().includes(q));
  }, [columns, query]);

  const toggle = (col: string) => {
    setSelected((s) => ({ ...s, [col]: !s[col] }));
  };

  const selectAll = () =>
    setSelected(
      columns.reduce(
        (acc, c) => ((acc[c] = true), acc),
        {} as Record<string, boolean>
      )
    );

  const clearAll = () =>
    setSelected(
      columns.reduce(
        (acc, c) => ((acc[c] = false), acc),
        {} as Record<string, boolean>
      )
    );

  const handleApply = () => {
    const picked = columns.filter((c) => selected[c]);
    onApply(picked);
  };

  return (
    <div
      className={styles['filter-panel']}
      role="region"
      aria-label="Панель фильтров"
    >
      <div className={styles['filter-panel__controls']}>
        <div className={styles['filter-panel__search']}>
          <input
            type="search"
            aria-label="Поиск показателя"
            placeholder="Поиск..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div className={styles['filter-panel__quick-actions']}>
          <button
            type="button"
            className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--ghost']}`}
            onClick={selectAll}
            aria-label="Выбрать все"
          >
            Все
          </button>
          <button
            type="button"
            className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--ghost']}`}
            onClick={clearAll}
            aria-label="Снять все"
          >
            Снять
          </button>
        </div>
      </div>

      <div className={styles['filter-panel__list']}>
        {filtered.length === 0 && (
          <div className={styles['filter-panel__empty']}>Ничего не найдено</div>
        )}

        {filtered.map((col) => (
          <label key={col} className={styles['filter-panel__item']} title={col}>
            <input
              type="checkbox"
              checked={!!selected[col]}
              onChange={() => toggle(col)}
              aria-checked={!!selected[col]}
            />
            <span>{col}</span>
          </label>
        ))}
      </div>

      <div className={styles['filter-panel__footer']}>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--ghost']}`}
          >
            Отмена
          </button>
        )}

        <button
          type="button"
          onClick={handleApply}
          className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--primary']}`}
        >
          Применить
        </button>
      </div>
    </div>
  );
};

export default FilterPanel;
