import { useState, useEffect } from 'react';
import { useGetAllBanks } from '@/shared/api/hooks/indicators/useGetAllBanks';
import Section from '@/shared/ui/section/Section';
import Title from '@/shared/ui/title/Title';
import Button from '@/shared/ui/button/Button';
import { TableLoader } from '../table-loader/TableLoader';
import styles from './styles.module.scss';
import { DEFAULT_BANKS_REGS, INDICATORS } from './constants';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import AddBankModal from '../add-bank-modal/AddBankModal';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';

export const BanksComparison = () => {
  const { data } = useGetAllBanks();
  const allBanks = data?.banks;

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedBanks, setSelectedBanks] = useLocalStorage<BankIndicator[]>(
    'banks-list',
    []
  );

  const handleAddBanks = (banks: BankIndicator[]) => {
    setSelectedBanks((prev) => [...(prev || []), ...banks]);
  };

  const handleRemoveBank = (bic: string) => {
    setSelectedBanks((prev) => prev?.filter((bank) => bank.bic !== bic));
  };

  useEffect(() => {
    if (allBanks && selectedBanks.length === 0) {
      const defaultBanks = allBanks.filter((bank) =>
        DEFAULT_BANKS_REGS.includes(bank.reg_number)
      );
      setSelectedBanks(defaultBanks);
    }
  }, [allBanks, selectedBanks, setSelectedBanks]);

  if (!data?.banks) return <TableLoader />;

  return (
    <>
      <Section
        padding="medium"
        background="secondary"
        className={styles.container}
        withBorder
      >
        <Title size="large" className={styles.title}>
          Сравнение банков
        </Title>

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
              {INDICATORS.map((indicator) => (
                <tr key={indicator.key}>
                  <td className={styles['sticky-col']}>{indicator.label}</td>
                  {selectedBanks.map((bank) => (
                    <td key={bank.bic + indicator.key}>
                      {indicator.key === 'registration_date'
                        ? new Date(bank[indicator.key]).toLocaleDateString()
                        : bank[indicator.key]}
                    </td>
                  ))}
                  <td></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <AddBankModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        allBanks={allBanks || []}
        selectedBanks={selectedBanks || []}
        popularBankBics={DEFAULT_BANKS_REGS}
        onAddBanks={handleAddBanks}
      />
    </>
  );
};
