import Section from '@/shared/ui/section/Section';
import Title from '@/shared/ui/title/Title';
import Button from '@/shared/ui/button/Button';
import { TableLoader } from '../table-loader/TableLoader';
import AddBankModal from '../add-bank-modal/AddBankModal';
import SettingsModal from '../settings-modal/SettingsModal';
import FilterSvg from './icons/filter.svg';
import styles from './styles.module.scss';
import { useBanksComparison } from './hooks/useBanksComparison';
import { formatNumber } from './utils/format';
import MonthPicker from '@/shared/ui/month-picker/MonthPicker';
import ToggleSwitch from '@/shared/ui/toggle-switch/ToggleSwitch';
import type { CSSProperties } from 'react';
/**
 * Компонент **BanksComparison** — основной экран для сравнения финансовых показателей банков.
 *
 * Отображает таблицу с динамикой индикаторов по выбранным банкам за выбранные месяцы.
 * Позволяет:
 * - Добавлять и удалять банки для сравнения;
 * - Выбирать периоды "От" и "На дату";
 * - Переключать режим отображения динамики;
 * - Открывать настройки для выбора показателей и банков.
 *
 * Использует хук `useBanksComparison` для управления состоянием, выбором дат и загрузкой данных.
 * При отсутствии данных отображает компонент-загрузчик `TableLoader`.
 *
 * Внутри применяются:
 * - `AddBankModal` — модальное окно добавления банков;
 * - `SettingsModal` — окно выбора показателей;
 * - `MonthPicker`, `ToggleSwitch` — элементы управления диапазоном дат;
 * - `Button`, `Title`, `Section` — общие UI-компоненты.
 *
 * @component
 * @returns {JSX.Element} Таблица сравнения банков с панелью фильтров и контролами периода.
 *
 * @see {@link useBanksComparison} — управляет состоянием банков, дат и индикаторов.
 * @see {@link AddBankModal} — добавление новых банков в сравнение.
 * @see {@link SettingsModal} — выбор индикаторов и банков.
 * @see {@link TableLoader} — отображается при загрузке данных.
 * @see {@link formatNumber} — форматирует числовые значения показателей.
 */
export const BanksComparison = () => {
  const {
    allBanks,
    selectedBanks,
    selectedIndicators,
    indicatorData,
    handleAddBanks,
    handleRemoveBank,
    setSelectedBanks,
    setSelectedIndicators,
    isModalOpen,
    setIsModalOpen,
    isSettingsOpen,
    setIsSettingsOpen,
    indCodeCounts,
    fromMonth,
    setFromMonth,
    toMonth,
    setToMonth,
    showDynamics,
    setShowDynamics,
  } = useBanksComparison();

  if (!allBanks) return <TableLoader />;

  const indCodeSeen: Record<string, number> = {};

  const toDate = (ym?: string | null) => {
    if (!ym) return;
    const [y, m] = ym.split('-').map(Number);
    if (!y || !m) return;
    return new Date(y, m - 1, 1);
  };

  return (
    <>
      <Section
        padding="medium"
        background="secondary"
        className={styles.container}
        withBorder
      >
        <div className={styles['title-wrapper']}>
          <Title size="large" className={styles.title}>
            Сравнение банков
          </Title>
          <div className={styles['controls']}>
            <Button
              variant="ghost"
              className={styles['filter']}
              onClick={() => setIsSettingsOpen(true)}
            >
              <img src={FilterSvg} alt="filter" />
            </Button>
          </div>
        </div>
        <div className={styles['date-controls']}>
          {showDynamics ? (
            <div className={styles['date-controls-inputs']}>
              <div className={styles['date-label-wrapper']}>
                <span className={styles['date-label-title']}>От</span>
                <MonthPicker
                  value={fromMonth}
                  onChange={(v) => setFromMonth(v)}
                  maxDate={toDate(toMonth)}
                  ariaLabel="Дата с"
                />
              </div>
              <div className={styles['date-label-wrapper']}>
                <span className={styles['date-label-title']}>На дату</span>
                <MonthPicker
                  value={toMonth}
                  onChange={(v) => setToMonth(v)}
                  maxDate={new Date()}
                  minDate={toDate(fromMonth)}
                  ariaLabel="Дата по"
                />
              </div>
            </div>
          ) : (
            <div className={styles['date-label-wrapper']}>
              <span className={styles['date-label-title']}>На дату</span>
              <MonthPicker
                value={toMonth}
                onChange={(v) => setToMonth(v)}
                maxDate={new Date()}
                ariaLabel="Дата на"
              />
            </div>
          )}
          <ToggleSwitch
            checked={showDynamics}
            onChange={setShowDynamics}
            label="Показывать динамику"
          />
        </div>
        <div className={styles['table-container']}>
          <table className={styles['statistic-table']}>
            <thead>
              <tr>
                <th className={styles['sticky-col']}>Показатель</th>
                {selectedBanks.map((bank) => (
                  <th key={bank.bic} className={styles['bank-header-wrapper']}>
                    <div className={styles['bank-header']}>
                      <span>{bank.name}</span>
                      <button
                        className={styles['remove-bank']}
                        onClick={() => handleRemoveBank(bank.bic)}
                        title="Удалить банк"
                      >
                        ×
                      </button>
                    </div>
                  </th>
                ))}
                <th>
                  <Button
                    size="small"
                    variant="primary"
                    onClick={() => setIsModalOpen(true)}
                  >
                    Добавить банк
                  </Button>
                </th>
              </tr>
            </thead>
            <tbody>
              {selectedIndicators.map((indicator) => {
                const code = indicator.ind_code;
                indCodeSeen[code] = (indCodeSeen[code] || 0) + 1;
                const needSuffix = indCodeCounts[code] > 1;
                const rowKey = needSuffix
                  ? `${code}_${indCodeSeen[code] - 1}`
                  : code;
                return (
                  <tr key={rowKey}>
                    <td className={styles['sticky-col']}>{indicator.name}</td>
                    {selectedBanks.map((bank) => {
                      const rawVal =
                        indicatorData[bank.reg_number]?.[code]?.iitg;
                      const startVal =
                        indicatorData[bank.reg_number]?.[code]?.vitg;
                      const delta = startVal
                        ? ((rawVal || 0) - (startVal || 0)) / (startVal || 1)
                        : null;
                      const deltaPercent =
                        delta != null ? Math.round(delta * 100) : null;
                      let cellStyle: CSSProperties = {};
                      if (showDynamics && delta != null) {
                        if (delta > 0) cellStyle.backgroundColor = '#DCFCE7';
                        else if (delta < 0)
                          cellStyle.backgroundColor = '#FEE2E2';
                      }
                      return (
                        <td key={`${bank.bic}_${rowKey}`} style={cellStyle} className={styles['cell']}>
                          {showDynamics && deltaPercent != null && (
                            <span className={styles['cell-delta']}>
                              {deltaPercent > 0
                                ? `+${deltaPercent}%`
                                : `${deltaPercent}%`}
                            </span>
                          )}
                          {formatNumber(rawVal)}
                        </td>
                      );
                    })}
                    <td />
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Section>

      <AddBankModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        allBanks={allBanks}
        selectedBanks={selectedBanks}
        onAddBanks={handleAddBanks}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        allBanks={allBanks}
        selectedBanks={selectedBanks}
        indicators={selectedIndicators}
        onSave={(banks, indicators) => {
          setSelectedBanks(banks);
          setSelectedIndicators(indicators);
        }}
      />
    </>
  );
};

export default BanksComparison;
