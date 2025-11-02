import { useState, useMemo, type FC } from 'react';
import Button from '@/shared/ui/button/Button';
import PopUp from '@/shared/ui/pop-up/PopUp';
import styles from './styles.module.scss';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { AddBankModalProps } from './types';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';

export const AddBankModal: FC<AddBankModalProps> = ({
  isOpen,
  onClose,
  onAddBanks,
  allBanks,
  selectedBanks,
  popularBankBics = [],
}) => {
  const [search, setSearch] = useState<string>('');
  const [selectedForAdd, setSelectedForAdd] = useLocalStorage<BankIndicator[]>(
    'selected-banks',
    []
  );

  const popularBanks = useMemo(
    () =>
      allBanks.filter(
        (b) =>
          popularBankBics.includes(b.bic) &&
          !selectedBanks.some((s) => s.bic === b.bic)
      ),
    [allBanks, selectedBanks, popularBankBics]
  );

  const filteredBanks = useMemo(() => {
    const filtered = allBanks.filter(
      (b) =>
        !selectedBanks.some((s) => s.bic === b.bic) &&
        (b.name.toLowerCase().includes(search.toLowerCase()) ||
          b.reg_number.includes(search))
    );

    const selectedBics = selectedForAdd.map((b) => b.bic);
    const sorted = filtered.sort((a, b) => {
      if (selectedBics.includes(a.bic)) return -1;
      if (selectedBics.includes(b.bic)) return 1;
      return 0;
    });

    return sorted;
  }, [allBanks, search, selectedBanks, selectedForAdd]);

  const toggleSelectBank = (bank: BankIndicator) => {
    setSelectedForAdd((prev) =>
      prev.some((b) => b.bic === bank.bic)
        ? prev.filter((b) => b.bic !== bank.bic)
        : [...prev, bank]
    );
  };

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
                className={`${styles.bankItem} ${
                  selectedForAdd.some((b) => b.bic === bank.bic)
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
                className={`${styles.bankItem} ${
                  selectedForAdd.some((b) => b.bic === bank.bic)
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
