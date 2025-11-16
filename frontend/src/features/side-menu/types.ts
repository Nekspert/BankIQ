/**
 * Элемент списка навигации бокового меню.
 *
 * Используется для отображения ссылки на раздел (таблицу, график и т.п.)
 * в компоненте {@link SideMenu}.
 *
 * @interface TableLink
 * @property {string} id - Уникальный идентификатор раздела (используется для якорной ссылки).
 * @property {string} title - Заголовок раздела, отображаемый в списке.
 * @property {string} [icon] - Необязательная иконка, отображаемая рядом с заголовком.
 * @property {number} [badge] - Необязательный числовой индикатор (например, количество элементов).
 *
 * @example
 * ```ts
 * const link: TableLink = {
 *   id: "profit",
 *   title: "Прибыль банков",
 *   icon: "chart",
 *   badge: 12,
 * };
 * ```
 */
 export interface TableLink {
  id: string;
  title: string;
  icon?: string;
  badge?: number;
}
/**
 * Свойства компонента {@link SideMenu}, управляющего навигацией по разделам страницы.
 *
 * @interface SideMenuProps
 * @property {TableLink[]} tableList - Список ссылок для навигации.
 * @property {boolean} isOpen - Флаг отображения меню.
 * @property {string} [activeId] - Идентификатор активного раздела, подсвечивается в меню.
 * @property {(id: string) => void} [onLinkClick] - Callback при клике на пункт меню.
 * @property {() => void} handleClose - Обработчик закрытия меню.
 *
 * @example
 * ```ts
 * const props: SideMenuProps = {
 *   tableList: [
 *     { id: "assets", title: "Активы" },
 *     { id: "profit", title: "Прибыль" },
 *   ],
 *   isOpen: true,
 *   activeId: "assets",
 *   onLinkClick: (id) => console.log("Переход к:", id),
 *   handleClose: () => console.log("Меню закрыто"),
 * };
 * ```
 */
export interface SideMenuProps {
  tableList: TableLink[];
  isOpen: boolean;
  activeId?: string;
  onLinkClick?: (id: string) => void;
  handleClose: () => void
}