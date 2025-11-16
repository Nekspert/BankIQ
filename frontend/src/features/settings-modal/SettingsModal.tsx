import { useMemo, useState, type FC } from 'react';
import PopUp from '@/shared/ui/pop-up/PopUp';
import Button from '@/shared/ui/button/Button';
import styles from './styles.module.scss';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';
import type { Indicator, SettingsModalProps } from './types';
import { useGetUniqueIndicators } from '@/shared/api/hooks/indicators/useGetUniqueIndicators';
/**
 * Модальное окно настройки таблицы сравнения банков и показателей.
 *
 * Позволяет пользователю выбирать банки и экономические показатели,
 * а также менять их порядок и сохранять настройки. 
 * Состояние выбора сохраняется в localStorage.
 *
 * Использует хук {@link useGetUniqueIndicators} для загрузки доступных показателей
 * и {@link useLocalStorage} для сохранения выбранных значений между сессиями.
 *
 * @component
 * @param {SettingsModalProps} props - Свойства компонента.
 * @param {boolean} props.isOpen - Флаг открытия модального окна.
 * @param {() => void} props.onClose - Обработчик закрытия окна.
 * @param {BankIndicator[]} props.allBanks - Полный список доступных банков.
 * @param {BankIndicator[]} props.selectedBanks - Текущий список выбранных банков.
 * @param {Indicator[]} props.indicators - Текущий список выбранных показателей.
 * @param {(banks: BankIndicator[], indicators: Indicator[]) => void} props.onSave - Callback, вызываемый при сохранении настроек.
 *
 * @returns {JSX.Element} Компонент модального окна с формой выбора банков и показателей.
 *
 * @example
 * ```tsx
 * <SettingsModal
 *   isOpen={true}
 *   onClose={() => setOpen(false)}
 *   allBanks={banksList}
 *   selectedBanks={selectedBanks}
 *   indicators={indicators}
 *   onSave={(banks, inds) => console.log('Сохранено:', banks, inds)}
 * />
 * ```
 *
 * @see useGetUniqueIndicators
 * @see useLocalStorage
 */

const SettingsModal: FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  allBanks,
  selectedBanks,
  indicators,
  onSave,
}) => {
  const { data: DEFAULT_INDICATOR_OPTIONS } = useGetUniqueIndicators();

  const [bankSearch, setBankSearch] = useState('');
  const [selectedForBanks, setSelectedForBanks] = useLocalStorage<
    BankIndicator[]
  >('settings-selected-banks', selectedBanks);

  const [localIndicators, setLocalIndicators] = useLocalStorage<Indicator[]>(
    'selected-indicators',
    indicators
  );

  const filteredBanks = useMemo(() => {
    const q = bankSearch.trim().toLowerCase();
    return allBanks
      .filter(
        (b) =>
          b.name.toLowerCase().includes(q) ||
          b.reg_number.toLowerCase().includes(q) ||
          b.bic.toLowerCase().includes(q)
      )
      .sort((a, b) => {
        const aSelected = selectedForBanks.some((s) => s.bic === a.bic);
        const bSelected = selectedForBanks.some((s) => s.bic === b.bic);
        if (aSelected && !bSelected) return -1;
        if (!aSelected && bSelected) return 1;
        return a.name.localeCompare(b.name, 'ru');
      });
  }, [allBanks, bankSearch, selectedForBanks]);

  const toggleBank = (bank: BankIndicator) => {
    setSelectedForBanks((prev) =>
      prev.some((b) => b.bic === bank.bic)
        ? prev.filter((b) => b.bic !== bank.bic)
        : [...(prev || []), bank]
    );
  };

  const moveIndicator = (index: number, dir: 'up' | 'down') => {
    setLocalIndicators((prev) => {
      if (!prev) return prev;
      const arr = [...prev];
      const newIndex = dir === 'up' ? index - 1 : index + 1;
      if (newIndex < 0 || newIndex >= arr.length) return arr;
      const tmp = arr[newIndex];
      arr[newIndex] = arr[index];
      arr[index] = tmp;
      return arr;
    });
  };

  const handleSave = () => {
    onSave(selectedForBanks, localIndicators);
    onClose();
  };

  const handleCancel = () => {
    onClose();
  };

  return (
    <PopUp
      isOpen={isOpen}
      onClose={onClose}
      title="Настройки таблицы"
      size="large"
      footer={
        <div className={styles.footer}>
          <Button variant="secondary" onClick={handleCancel}>
            Отмена
          </Button>
          <Button variant="primary" onClick={handleSave}>
            Сохранить
          </Button>
        </div>
      }
    >
      <div className={styles.settingsRow}>
        <div className={styles.column}>
          <h3 className={styles.sectionTitle}>Банки</h3>
          <div className={styles.searchWrapper}>
            <input
              value={bankSearch}
              onChange={(e) => setBankSearch(e.target.value)}
              placeholder="Поиск по названию, рег. номеру или BIC"
              className={styles.searchInput}
            />
          </div>

          <div className={styles.list}>
            {filteredBanks.map((bank) => {
              const selected = selectedForBanks.some((b) => b.bic === bank.bic);
              return (
                <div
                  key={bank.bic}
                  className={`${styles.item} ${selected ? styles.selected : ''}`}
                  onClick={() => toggleBank(bank)}
                >
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={() => toggleBank(bank)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div className={styles.itemLabel}>
                    <div className={styles.name}>{bank.name}</div>
                    <div className={styles.meta}>{bank.reg_number}</div>
                  </div>
                </div>
              );
            })}
            {filteredBanks.length === 0 && (
              <div className={styles.noResults}>Ничего не найдено</div>
            )}
          </div>
        </div>

        <div className={styles.column}>
          <h3 className={styles.sectionTitle}>Показатели</h3>

          <div className={styles.hint}>
            Выберите показатели и упорядочьте их (верхний – первый в таблице)
          </div>

          <div className={styles.indicatorsList}>
            {localIndicators.map((ind, idx) => (
              <div key={ind.ind_code} className={styles.indicatorRow}>
                <div className={styles.indicatorLeft}>
                  <input
                    type="checkbox"
                    checked={true}
                    onChange={() =>
                      setLocalIndicators((prev) =>
                        prev.filter((p) => p.ind_code !== ind.ind_code)
                      )
                    }
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div className={styles.indLabel}>{ind.name}</div>
                </div>

                <div className={styles.controls}>
                  <button
                    className={styles.iconBtn}
                    onClick={() => moveIndicator(idx, 'up')}
                    title="Вверх"
                    disabled={idx === 0}
                  >
                    ↑
                  </button>
                  <button
                    className={styles.iconBtn}
                    onClick={() => moveIndicator(idx, 'down')}
                    title="Вниз"
                    disabled={idx === localIndicators.length - 1}
                  >
                    ↓
                  </button>
                  <button
                    className={styles.removeBtn}
                    onClick={() =>
                      setLocalIndicators((prev) =>
                        prev.filter((p) => p.ind_code !== ind.ind_code)
                      )
                    }
                    title="Удалить"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}

            {localIndicators.length === 0 && (
              <div className={styles.noResults}>Показатели не выбраны</div>
            )}
          </div>

          <div className={styles.addSection}>
            <div className={styles.subTitle}>Добавить показатель</div>
            <div className={styles.addList}>
              {DEFAULT_INDICATOR_OPTIONS?.filter(
                (d) => !localIndicators.some((l) => l.ind_code === d.ind_code)
              ).map((d) => (
                <div key={d.ind_code} className={styles.addItem}>
                  <button
                    className={styles.addBtn}
                    onClick={() =>
                      setLocalIndicators((prev) => [...(prev || []), d])
                    }
                  >
                    + {d.name}
                  </button>
                </div>
              ))}
              {DEFAULT_INDICATOR_OPTIONS?.filter(
                (d) => !localIndicators.some((l) => l.ind_code === d.ind_code)
              ).length === 0 && (
                <div className={styles.noResults}>
                  Нет доступных показателей
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </PopUp>
  );
};

export default SettingsModal;
