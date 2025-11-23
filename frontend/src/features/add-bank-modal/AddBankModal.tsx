import { useState, useMemo, type FC } from 'react';
import Button from '@/shared/ui/button/Button';
import PopUp from '@/shared/ui/pop-up/PopUp';
import styles from './styles.module.scss';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { AddBankModalProps } from './types';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';

/**
 * Компонент модального окна для добавления банков в список пользователя.
 * Позволяет искать банки, выбирать популярные и добавлять их в общий список.
 *
 * @component
 * @param {AddBankModalProps} props - Свойства модального окна.
 * @param {boolean} props.isOpen - Флаг, открыто ли модальное окно.
 * @param {() => void} props.onClose - Колбэк закрытия окна.
 * @param {(banks: BankIndicator[]) => void} props.onAddBanks - Функция добавления выбранных банков.
 * @param {BankIndicator[]} props.allBanks - Список всех доступных банков.
 * @param {BankIndicator[]} props.selectedBanks - Уже выбранные банки.
 * @param {string[]} [props.popularBankBics] - BIC популярных банков.
 *
 * @hook useState - Управляет состоянием поисковой строки.
 * @hook useMemo - Оптимизирует фильтрацию и сортировку банков.
 * @hook useLocalStorage - Сохраняет выбранные банки между сессиями.
 *
 * @function toggleSelectBank - Добавляет или удаляет банк из выбранных.
 * @function handleAdd - Добавляет выбранные банки и закрывает модальное окно.
 *
 * @see {@link Button} - Используется для кнопок "Отмена" и "Добавить".
 * @see {@link PopUp} - Компонент модального окна.
 * @see {@link useLocalStorage} - Хук для хранения состояния в localStorage.
 *
 * @returns JSX.Element — Интерфейс модального окна для выбора банков.
 */
export const AddBankModal: FC<AddBankModalProps> = ({
    isOpen,
    onClose,
    onAddBanks,
    allBanks,
    selectedBanks,
    popularBankBics = [],
}) => {
    /** @hook useState — Управление строкой поиска */
    const [search, setSearch] = useState<string>('');

    /** @hook useLocalStorage — Список банков, выбранных для добавления */
    const [selectedForAdd, setSelectedForAdd] = useLocalStorage<BankIndicator[]>(
        'selected-banks',
        []
    );

    /** 
     * @hook useMemo 
     * Отбирает популярные банки, не добавленные в список пользователя.
     */
    const popularBanks = useMemo(
        () =>
            allBanks.filter(
                (b) =>
                    popularBankBics.includes(b.bic) &&
                    !selectedBanks.some((s) => s.bic === b.bic)
            ),
        [allBanks, selectedBanks, popularBankBics]
    );

    /**
     * @hook useMemo
     * Фильтрует и сортирует банки по поисковой строке и выбранным банкам.
     */
    const filteredBanks = useMemo(() => {
        const filtered = allBanks?.filter(
            (b) =>
                !selectedBanks?.some((s) => s.bic === b.bic) &&
                (b.name.toLowerCase().includes(search.toLowerCase()) ||
                    b.reg_number?.toString().includes(search))
        );

        const selectedBics = selectedForAdd.map((b) => b.bic);

        const sorted = filtered.sort((a, b) => {
            if (selectedBics.includes(a.bic)) return -1;
            if (selectedBics.includes(b.bic)) return 1;
            return 0;
        });

        return sorted;
    }, [allBanks, search, selectedBanks, selectedForAdd]);

    /**
     * Переключает выбор банка: добавляет или убирает его из списка выбранных.
     * @param {BankIndicator} bank - Объект банка для добавления или удаления.
     * @see {@link useLocalStorage} - Обновляет сохранённое состояние выбранных банков.
     */
    const toggleSelectBank = (bank: BankIndicator) => {
        setSelectedForAdd((prev) =>
            prev.some((b) => b.bic === bank.bic)
                ? prev.filter((b) => b.bic !== bank.bic)
                : [...prev, bank]
        );
    };

    /**
     * Добавляет выбранные банки, очищает состояние и закрывает окно.
     * @see {@link onAddBanks} - Передаёт список выбранных банков в родительский компонент.
     * @see {@link onClose} - Закрывает модальное окно после добавления.
     */
    const handleAdd = () => {
        onAddBanks(selectedForAdd);
        setSelectedForAdd([]);
        setSearch('');
        onClose();
    };

    return (
        <PopUp
            isOpen={isOpen}
            onClose={onClose}
            title="Добавить банки"
            size="medium"
            footer={
                <div className={styles.footer}>
                    <Button variant="secondary" onClick={onClose}>
                        Отмена
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleAdd}
                        disabled={selectedForAdd.length === 0}
                    >
                        Добавить ({selectedForAdd.length})
                    </Button>
                </div>
            }
        >
            <div className={styles.searchWrapper}>
                <input
                    type="text"
                    placeholder="Название банка или рег. номер"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className={styles.searchInput}
                />
            </div>

            <div className={styles.bankList}>
                {!search.trim() && popularBanks.length > 0 && (
                    <>
                        <div className={styles.sectionTitle}>Популярные банки</div>
                        {popularBanks.map((bank) => (
                            <div
                                key={bank.bic}
                                className={`${styles.bankItem} ${selectedForAdd.some((b) => b.bic === bank.bic)
                                        ? styles.selected
                                        : ''
                                    }`}
                                onClick={() => toggleSelectBank(bank)}
                            >
                                {bank.name} ({bank.reg_number})
                            </div>
                        ))}
                    </>
                )}

                {filteredBanks.length > 0 && (
                    <>
                        {search.trim() !== '' && (
                            <div className={styles.sectionTitle}>Результаты поиска</div>
                        )}
                        {filteredBanks.map((bank) => (
                            <div
                                key={bank.bic}
                                className={`${styles.bankItem} ${selectedForAdd.some((b) => b.bic === bank.bic)
                                        ? styles.selected
                                        : ''
                                    }`}
                                onClick={() => toggleSelectBank(bank)}
                            >
                                {bank.name} ({bank.reg_number})
                            </div>
                        ))}
                    </>
                )}
                {!search.trim() && filteredBanks.length === 0 && (
                    <div className={styles.noResults}>Банки не найдены</div>
                )}
            </div>
        </PopUp>
    );
};

export default AddBankModal;
