// import React, { useEffect, useMemo, useState } from 'react';
// import styles from './styles.module.scss';

// export interface TableItem {
//   id: string;
//   title: string;
//   requestData: {
//     publication_id: number;
//     dataset_id: number;
//     measure_id: number;
//     from_year: number;
//     to_year: number;
//     [k: string]: any;
//   };
//   endpoint: string
// }

// interface ApplyPayload {
//   selectedIds: string[];
//   from_year: number;
//   to_year: number;
// }

// interface Props {
//   items: TableItem[];
//   initialSelectedIds?: string[];
//   initialFromYear?: number;
//   initialToYear?: number;
//   onApply: (payload: ApplyPayload) => void;
//   onCancel?: () => void;
// }

// export const TableFilterPanel: React.FC<Props> = ({
//   items,
//   initialSelectedIds = [],
//   initialFromYear,
//   initialToYear,
//   onApply,
//   onCancel,
// }) => {
//   const itemIds = useMemo(() => items.map((it) => it.id), [items]);

//   const [query, setQuery] = useState('');
//   const [selectedMap, setSelectedMap] = useState<Record<string, boolean>>(() =>
//     itemIds.reduce(
//       (acc, id) => {
//         acc[id] =
//           initialSelectedIds.length > 0
//             ? initialSelectedIds.includes(id)
//             : true;
//         return acc;
//       },
//       {} as Record<string, boolean>
//     )
//   );
//   const [fromYear, setFromYear] = useState<number | ''>(initialFromYear ?? '');
//   const [toYear, setToYear] = useState<number | ''>(initialToYear ?? '');

//   useEffect(() => {
//     setSelectedMap(
//       itemIds.reduce(
//         (acc, id) => {
//           acc[id] =
//             selectedMap[id] ??
//             (initialSelectedIds.length > 0
//               ? initialSelectedIds.includes(id)
//               : true);
//           return acc;
//         },
//         {} as Record<string, boolean>
//       )
//     );
//   }, [items.join?.('|') ?? items.map((i) => i.id).join('|')]);

//   const filtered = useMemo(() => {
//     const q = query.trim().toLowerCase();
//     if (!q) return items;
//     return items.filter(
//       (it) =>
//         it.title.toLowerCase().includes(q) || it.id.toLowerCase().includes(q)
//     );
//   }, [items, query]);

//   const toggle = (id: string) =>
//     setSelectedMap((s) => ({ ...s, [id]: !s[id] }));

//   const selectAll = () =>
//     setSelectedMap(
//       itemIds.reduce(
//         (acc, id) => ((acc[id] = true), acc),
//         {} as Record<string, boolean>
//       )
//     );
//   const clearAll = () =>
//     setSelectedMap(
//       itemIds.reduce(
//         (acc, id) => ((acc[id] = false), acc),
//         {} as Record<string, boolean>
//       )
//     );

//   const handleApply = () => {
//     const chosen = itemIds.filter((id) => selectedMap[id]);
//     const fy =
//       typeof fromYear === 'number'
//         ? fromYear
//         : (initialFromYear ?? items[0]?.requestData?.from_year ?? 0);
//     const ty =
//       typeof toYear === 'number'
//         ? toYear
//         : (initialToYear ?? items[0]?.requestData?.to_year ?? 0);
//     onApply({ selectedIds: chosen, from_year: fy, to_year: ty });
//   };

//   return (
//     <div
//       className={styles['filter-panel']}
//       role="region"
//       aria-label="Панель фильтров таблиц"
//     >
//       <div className={styles['filter-panel__controls']}>
//         <div className={styles['filter-panel__search']}>
//           <input
//             type="search"
//             placeholder="Поиск отчёта..."
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             aria-label="Поиск отчёта"
//           />
//         </div>

//         <div className={styles['filter-panel__quick-actions']}>
//           <button
//             className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--ghost']}`}
//             type="button"
//             onClick={selectAll}
//           >
//             Все
//           </button>
//           <button
//             className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--ghost']}`}
//             type="button"
//             onClick={clearAll}
//           >
//             Снять
//           </button>
//         </div>
//       </div>

//       <div style={{ display: 'flex', gap: 8 }}>
//         <label
//           style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}
//         >
//           <span style={{ fontSize: 12, color: '#6b7280' }}>От</span>
//           <input
//             type="number"
//             value={fromYear}
//             onChange={(e) =>
//               setFromYear(e.target.value === '' ? '' : Number(e.target.value))
//             }
//             placeholder="Год от"
//             aria-label="Год от"
//           />
//         </label>

//         <label
//           style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}
//         >
//           <span style={{ fontSize: 12, color: '#6b7280' }}>До</span>
//           <input
//             type="number"
//             value={toYear}
//             onChange={(e) =>
//               setToYear(e.target.value === '' ? '' : Number(e.target.value))
//             }
//             placeholder="Год до"
//             aria-label="Год до"
//           />
//         </label>
//       </div>

//       <div className={styles['filter-panel__list']}>
//         {filtered.length === 0 && (
//           <div className={styles['filter-panel__empty']}>Ничего не найдено</div>
//         )}
//         {filtered.map((it) => (
//           <label
//             key={it.id}
//             className={styles['filter-panel__item']}
//             title={it.title}
//           >
//             <input
//               type="checkbox"
//               checked={!!selectedMap[it.id]}
//               onChange={() => toggle(it.id)}
//               aria-checked={!!selectedMap[it.id]}
//             />
//             <span>{it.title}</span>
//           </label>
//         ))}
//       </div>

//       <div className={styles['filter-panel__footer']}>
//         {onCancel && (
//           <button
//             className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--ghost']}`}
//             type="button"
//             onClick={onCancel}
//           >
//             Отмена
//           </button>
//         )}
//         <button
//           className={`${styles['filter-panel__btn']} ${styles['filter-panel__btn--primary']}`}
//           type="button"
//           onClick={handleApply}
//         >
//           Применить
//         </button>
//       </div>
//     </div>
//   );
// };

// export default TableFilterPanel;
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

const TableFilterPanel: React.FC<Props> = ({ items, initialSelectedIds = [], onApply }) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelectedIds);

  const toggleItem = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleApply = () => onApply(selectedIds);

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
        <button className="reset-btn" onClick={() => setSelectedIds([])}>Сбросить</button>
        <button className="apply-btn" onClick={handleApply}>Применить</button>
      </div>
    </div>
  );
};

export default TableFilterPanel;
