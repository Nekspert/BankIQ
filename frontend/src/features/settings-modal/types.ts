import type { BankIndicator } from "@/shared/api/indicatorsApi";
/**
 * Тип описывает экономический показатель, доступный для выбора в настройках таблицы.
 *
 * @typedef {Object} Indicator
 * @property {string} ind_code - Уникальный код показателя.
 * @property {string} name - Отображаемое название показателя.
 *
 * @example
 * ```ts
 * const indicator: Indicator = {
 *   ind_code: "ROE",
 *   name: "Рентабельность капитала",
 * };
 * ```
 */
export type Indicator = {
  ind_code: string;
  name: string;
};
/**
 * Свойства компонента {@link SettingsModal}, управляющего выбором банков и показателей.
 *
 * @typedef {Object} SettingsModalProps
 * @property {boolean} isOpen - Определяет, открыто ли модальное окно.
 * @property {() => void} onClose - Функция для закрытия модального окна.
 * @property {BankIndicator[]} allBanks - Полный список доступных банков.
 * @property {BankIndicator[]} selectedBanks - Текущий список выбранных банков.
 * @property {Indicator[]} indicators - Список выбранных показателей.
 * @property {(banks: BankIndicator[], indicators: Indicator[]) => void} onSave - Callback, вызываемый при сохранении изменений.
 *
 * @example
 * ```ts
 * const props: SettingsModalProps = {
 *   isOpen: true,
 *   onClose: () => console.log("Закрыто"),
 *   allBanks: allBanksData,
 *   selectedBanks: [allBanksData[0]],
 *   indicators: [{ ind_code: "ROA", name: "Рентабельность активов" }],
 *   onSave: (banks, indicators) => console.log("Сохранено", banks, indicators),
 * };
 * ```
 */
export type SettingsModalProps = {
  isOpen: boolean;
  onClose: () => void;
  allBanks: BankIndicator[];
  selectedBanks: BankIndicator[];
  indicators: Indicator[];
  onSave: (banks: BankIndicator[], indicators: Indicator[]) => void;
};