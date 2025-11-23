import { useState, type FC } from 'react';
import Section from '@/shared/ui/section/Section';
import Title from '@/shared/ui/title/Title';
import Button from '@/shared/ui/button/Button';
import FilterSvg from '@/shared/icons/filter.svg?react';
import styles from './styles.module.scss';
import { useGetAllBanks } from '@/shared/api/hooks/indicators/useGetAllBanks';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';
import MonthPicker from '@/shared/ui/month-picker/MonthPicker';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import { TableLoader } from '@/features/table-loader/TableLoader';
import { useF123Queries } from './hooks/useF123Queries';
import { formatNumber } from '@/features/banks-comparison/utils/format';
import AddBankModal from '@/features/add-bank-modal/AddBankModal';
import { F123_ROWS } from './constants';
import ExportSvg from '@/shared/icons/DownloadIcon.svg?react'

export const Form123Table: FC = () => {
  const { data: allBanksData } = useGetAllBanks();
  const allBanks = allBanksData?.banks ?? [];
  const now = new Date();
  const defaultMonth = `${now.getFullYear()}-${String(now.getMonth()).padStart(2, '0')}`;

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [month, setMonth] = useLocalStorage<string | null>(
    'f123-month',
    defaultMonth
  );
  const [selectedBanks, setSelectedBanks] = useLocalStorage<BankIndicator[]>(
    'f123-banks-list',
    allBanks.slice(0, 3)
  );

  const { indicatorData, rawResults } = useF123Queries(
    selectedBanks || [],
    month
  );

  const handleAddBanks = (banks: BankIndicator[]) => {
    setSelectedBanks((prev) => [...(prev || []), ...banks]);
  };

  const handleRemoveBank = (bic: string) => {
    setSelectedBanks((prev) => prev?.filter((b) => b.bic !== bic));
  };

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
              Сравнение банков (Форма 123)
            </Title>
            <Title level={3} size="medium" className={styles.warning}>
              * все показатели указаны в тысячах ₽
            </Title>
            <div className={styles['subtitle']}>
              Три агрегированных показателя по банку
            </div>
          </div>

          <div className={styles['controls']}>
            <Button
              variant="ghost"
              className={styles['filter']}
              // onClick={() => setIsSettingsOpen(true)}
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
              {F123_ROWS.map((rowName) => (
                <tr key={rowName}>
                  <td className={styles['sticky-col']}>{rowName}</td>

                  {selectedBanks.map((bank) => {
                    const val =
                      indicatorData?.[bank.reg_number]?.[rowName] ?? null;
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

export default Form123Table;
