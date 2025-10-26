import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import { getContainerStyle } from '../utils/getContainerStyles';
import type { TableData } from '../types';

export const useExpandableTable = (
  data: TableData | null,
  tableRef: React.RefObject<HTMLTableElement | null>
) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [containerStyle, setContainerStyle] = useState<CSSProperties>({
    maxHeight: '300px',
    overflow: 'hidden',
  });

  const rows = data ? Object.entries(data) : [];
  const displayedRows = isExpanded ? rows : rows.slice(0, 5);
  const showToggle = rows.length > 5;

  useEffect(() => {
    setContainerStyle(getContainerStyle(isExpanded, tableRef));
  }, [isExpanded, data]);

  return {
    isExpanded,
    setIsExpanded,
    containerStyle,
    displayedRows,
    showToggle,
  };
};
