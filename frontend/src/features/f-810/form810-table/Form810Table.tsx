import { useEffect, useState, type FC } from 'react';
import Section from '@/shared/ui/section/Section';
import Title from '@/shared/ui/title/Title';
import Button from '@/shared/ui/button/Button';
import FilterSvg from '@/shared/icons/filter.svg?react';
import ExportSvg from '@/shared/icons/DownloadIcon.svg?react';
import styles from './styles.module.scss';
import { useGetAllBanks } from '@/shared/api/hooks/indicators/useGetAllBanks';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';
import MonthPicker from '@/shared/ui/month-picker/MonthPicker';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import { TableLoader } from '@/features/table-loader/TableLoader';
import { formatNumber } from '@/features/banks-comparison/utils/format';
import AddBankModal from '@/features/add-bank-modal/AddBankModal';
import { F810_COLUMNS } from './constants';
import { useF810Queries } from './hooks/useF810Queries';
import { DEFAULT_BANK_REGS } from '@/shared/config/constants';
import { exportForm810 } from '@/shared/utils/export/formExporters';

export const Form810Table: FC = () => {
  const { data: allBanksData } = useGetAllBanks();
  const allBanks = allBanksData?.banks ?? [];
  const defaultMonth = `2025-04`;

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [month, setMonth] = useLocalStorage<string | null>(
    'f810-month',
    defaultMonth
  );
  const [selectedBanks, setSelectedBanks] = useLocalStorage<BankIndicator[]>(
    'f810-banks-list',
    allBanks.slice(0, 3)
  );

  const { indicatorData, rawResults } = useF810Queries(
    selectedBanks || [],
    month
  );

  const handleAddBanks = (banks: BankIndicator[]) => {
    setSelectedBanks((prev) => [...(prev || []), ...banks]);
  };

  const handleRemoveBank = (bic: string) => {
    setSelectedBanks((prev) => prev?.filter((b) => b.bic !== bic));
  };

  const handleExport = () => {
    exportForm810(selectedBanks, indicatorData, month, F810_COLUMNS);
  };

  useEffect(() => {
    if (allBanks.length > 0 && selectedBanks.length === 0) {
      const defaultBanks = allBanks.filter((bank) =>
        DEFAULT_BANK_REGS.includes(bank.reg_number)
      );
      if (defaultBanks.length > 0) {
        setSelectedBanks(defaultBanks);
      }
    }
  }, [allBanks, selectedBanks.length, setSelectedBanks]);

  if (!allBanks) return <TableLoader />;

  return (
    <>
      <Section
        padding="medium"
        background="secondary"
        className={styles.container}
        withBorder
      >
        <div className={styles['title-wrapper']}>
          <div>
            <Title size="large" className={styles.title}>
              Сравнение банков (Форма 810)
            </Title>
            <Title level={3} size="medium" className={styles.warning}>
              * все показатели указаны в тысячах ₽
            </Title>
            <div className={styles['subtitle']}>
              Отчет об изменениях в капитале кредитной организации
            </div>
          </div>

          <div className={styles['controls']}>
            <Button
              variant="ghost"
              className={styles['filter']}
              onClick={handleExport}
            >
              <ExportSvg />
            </Button>
            <Button
              variant="ghost"
              className={styles['filter']}
              onClick={() => setIsModalOpen(true)}
            >
              <FilterSvg />
            </Button>
          </div>
        </div>

        <div className={styles['date-controls']}>
          <div className={styles['date-label-wrapper']}>
            <span className={styles['date-label-title']}>На дату</span>
            <MonthPicker
              value={month}
              onChange={(v) => setMonth(v)}
              maxDate={new Date()}
              ariaLabel="Дата на"
            />
          </div>
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
              {F810_COLUMNS.map((column) => (
                <tr key={column.key}>
                  <td className={styles['sticky-col']}>{column.label}</td>

                  {selectedBanks.map((bank) => {
                    const val =
                      indicatorData?.[bank.reg_number]?.[column.key] ?? null;
                    const bankIndex = selectedBanks.findIndex(
                      (b) => b.reg_number === bank.reg_number
                    );
                    const res = rawResults?.[bankIndex];
                    const isLoading =
                      !!res && (res.isFetching || res.isLoading);
                    const isError = !!res && res.isError;

                    return (
                      <td key={bank.bic} className={styles['cell']}>
                        {isLoading ? (
                          <div className={styles['cell-skeleton']}>…</div>
                        ) : isError ? (
                          <div className={styles['cell-error']}>—</div>
                        ) : (
                          formatNumber(val)
                        )}
                      </td>
                    );
                  })}

                  <td />
                </tr>
              ))}
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
        popularBankBics={[]}
      />
    </>
  );
};
