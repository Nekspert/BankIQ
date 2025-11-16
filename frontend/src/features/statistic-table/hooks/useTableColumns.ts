import { useEffect, useMemo, useState } from 'react';
import type { TableData } from '../types';
/**
 * ’ук дл€ получени€ списка колонок таблицы и управлени€ выбранными колонками.
 *
 * ѕозвол€ет автоматически определ€ть все колонки из данных {@link TableData},
 * поддерживает внешнее управление выбранными колонками и уведомл€ет о готовности колонок через callback.
 *
 * @hook
 * @param {TableData | null} data - ƒанные таблицы (ключ Ч дата, значение Ч показатели).
 * @param {string[] | null} [externalSelectedColumns] - Ќеоб€зательный массив внешне выбранных колонок.
 * @param {(columns: string[]) => void} [onColumnsReady] - Callback, вызываемый после определени€ всех колонок.
 *
 * @returns {{
 *   columns: string[];
 *   activeColumns: string[];
 * }} ќбъект с полным списком колонок и активными выбранными колонками.
 *
 * @example
 * ```ts
 * const { columns, activeColumns } = useTableColumns(data, ["ROE", "ROA"], (cols) => console.log("¬се колонки:", cols));
 *
 * console.log(columns); // ["ROE", "ROA", "Assets"]
 * console.log(activeColumns); // ["ROE", "ROA"]
 * ```
 *
 * @see TableData
 */

export const useTableColumns = (
  data: TableData | null,
  externalSelectedColumns?: string[] | null,
  onColumnsReady?: (columns: string[]) => void
) => {
  const [internalSelected, setInternalSelected] = useState<string[]>([]);

  const columns = useMemo(() => {
    if (!data) return [];
    const rows = Object.values(data);
    const colsSet = new Set<string>();
    if (rows.length > 0) Object.keys(rows[0]).forEach((k) => colsSet.add(k));
    rows.slice(1).forEach((r) => Object.keys(r).forEach((k) => colsSet.add(k)));
    return Array.from(colsSet);
  }, [data]);

  const activeColumns =
    externalSelectedColumns && externalSelectedColumns.length >= 0
      ? externalSelectedColumns
      : internalSelected;

  useEffect(() => {
    if (!columns.length) return;
    onColumnsReady?.(columns);
    setInternalSelected((prev) => {
      if (!prev.length) return columns;
      return prev.filter((c) => columns.includes(c));
    });
  }, [columns.join('|'), onColumnsReady]);

  useEffect(() => {
    if (externalSelectedColumns?.length) return;
    if (columns.length && !internalSelected.length) {
      setInternalSelected(columns);
    }
  }, [externalSelectedColumns, columns, internalSelected.length]);

  return { columns, activeColumns };
};
