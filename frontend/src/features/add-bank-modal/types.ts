import type { BankIndicator } from '@/shared/api/indicatorsApi';

/**
 * Свойства (props) для компонента {@link AddBankModal}.
 * Используются для управления состоянием и поведением модального окна добавления банков.
 *
 * @interface AddBankModalProps
 * @see {@link AddBankModal} — Компонент модального окна для выбора и добавления банков.
 * @see {@link BankIndicator} — Тип, описывающий данные о банке.
 */
export interface AddBankModalProps {
    /**
     * Флаг, определяющий, открыто ли модальное окно.
     * @default false
     */
    isOpen: boolean;

    /**
     * Обработчик закрытия модального окна.
     * @returns void
     */
    onClose: () => void;

    /**
     * Колбэк, вызываемый при подтверждении добавления выбранных банков.
     * @param {BankIndicator[]} banks — Список выбранных пользователем банков.
     */
    onAddBanks: (banks: BankIndicator[]) => void;

    /**
     * Полный список доступных банков, из которых можно выбрать.
     */
    allBanks: BankIndicator[];

    /**
     * Банки, которые уже добавлены пользователем.
     */
    selectedBanks: BankIndicator[];

    /**
     * Массив BIC популярных банков, которые отображаются в отдельной секции.
     * @optional
     */
    popularBankBics?: string[];
}
