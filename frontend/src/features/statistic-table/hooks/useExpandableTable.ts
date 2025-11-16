import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import { getContainerStyle } from '../utils/getContainerStyles';
import type { TableData } from '../types';
/**
 * Хук для управления разворачиваемой таблицей с ограничением высоты.
 *
 * Позволяет отображать только часть строк таблицы с возможностью
 * раскрытия/сворачивания для просмотра полного списка данных.
 * Также рассчитывает стили контейнера с помощью {@link getContainerStyle}.
 *
 * @hook
 * @param {TableData | null} data - Данные таблицы (ключ — дата, значение — показатели).
 * @param {React.RefObject<HTMLTableElement | null>} tableRef - Ссылка на DOM-элемент таблицы.
 *
 * @returns {{
 *   isExpanded: boolean;
 *   setIsExpanded: React.Dispatch<React.SetStateAction<boolean>>;
 *   containerStyle: CSSProperties;
 *   displayedRows: [string, Record<string, number | string>][];
 *   showToggle: boolean;
 * }} Объект с состоянием разворота, отображаемыми строками и стилем контейнера.
 *
 * @example
 * ```ts
 * const {
 *   isExpanded,
 *   setIsExpanded,
 *   containerStyle,
 *   displayedRows,
 *   showToggle,
 * } = useExpandableTable(data, tableRef);
 *
 * return (
 *   <div style={containerStyle}>
 *     <table ref={tableRef}>
 *       <tbody>
 *         {displayedRows.map(([date, values]) => (
 *           <tr key={date}>...</tr>
 *         ))}
 *       </tbody>
 *     </table>
 *     {showToggle && (
 *       <button onClick={() => setIsExpanded(!isExpanded)}>
 *         {isExpanded ? 'Свернуть' : 'Показать всё'}
 *       </button>
 *     )}
 *   </div>
 * );
 * ```
 *
 * @see getContainerStyle
 */

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
