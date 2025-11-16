import type { CSSProperties, RefObject } from 'react';
import { defaultContainerStyles } from '../constants';
/**
 * Функция для вычисления стилей контейнера разворачиваемой таблицы.
 *
 * Возвращает максимальную высоту и прокрутку контейнера в зависимости от
 * состояния {@link isExpanded} и фактической высоты таблицы.
 * Используется в хуке {@link useExpandableTable}.
 *
 * @param {boolean} isExpanded - Флаг, указывающий, развернута ли таблица.
 * @param {RefObject<HTMLTableElement | null>} tableRef - Ссылка на DOM-элемент таблицы.
 *
 * @returns {CSSProperties} Объект стилей для контейнера таблицы.
 *
 * @example
 * ```ts
 * const style = getContainerStyle(isExpanded, tableRef);
 * <div style={style}>
 *   <table ref={tableRef}>...</table>
 * </div>
 * ```
 *
 * @see useExpandableTable
 * @see defaultContainerStyles
 */

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
