import type { CSSProperties, RefObject } from 'react';
import { defaultContainerStyles } from '../constants';

export const getContainerStyle = (
  isExpanded: boolean,
  tableRef: RefObject<HTMLTableElement | null>
): CSSProperties => {
  return isExpanded && tableRef.current
    ? {
        maxHeight: `${tableRef.current.scrollHeight + 30}px`,
        overflowY: 'auto',
      }
    : defaultContainerStyles;
};
