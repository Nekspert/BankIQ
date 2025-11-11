import type { CSSProperties } from 'react';
/**
 * Стандартные стили контейнера для разворачиваемой таблицы.
 *
 * Используются по умолчанию, когда таблица свернута или высота не рассчитана динамически.
 *
 * @constant {CSSProperties} defaultContainerStyles
 *
 * @example
 * ```ts
 * <div style={defaultContainerStyles}>
 *   <table>...</table>
 * </div>
 * ```
 */

export const defaultContainerStyles: CSSProperties = {
  maxHeight: '300px',
  overflowY: 'hidden',
};
