import { useEffect, useMemo, useState } from 'react';
import type { TableData } from '../types';

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
