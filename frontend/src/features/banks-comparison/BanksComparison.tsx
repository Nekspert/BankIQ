import { useState, useEffect } from 'react';
import { useGetAllBanks } from '@/shared/api/hooks/indicators/useGetAllBanks';
import Section from '@/shared/ui/section/Section';
import Title from '@/shared/ui/title/Title';
import Button from '@/shared/ui/button/Button';
import { TableLoader } from '../table-loader/TableLoader';
import styles from './styles.module.scss';
import { BANK_TOP_INDICATORS, DEFAULT_BANKS_REGS } from './constants';
import { indicatorsApi, type BankIndicator } from '@/shared/api/indicatorsApi';
import AddBankModal from '../add-bank-modal/AddBankModal';
import SettingsModal, { type Indicator } from '../settings-modal/SettingsModal';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';
import { useGetSupportedIndicators } from '@/shared/api/hooks/indicators/useGetSupportedIndicators';
import FilterSvg from './icons/filter.svg';

export const BanksComparison = () => {
  const { data: allBanksData } = useGetAllBanks();
  const allBanks = allBanksData?.banks;

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const [selectedBanks, setSelectedBanks] = useLocalStorage<BankIndicator[]>(
    'banks-list',
    []
  );

  const [selectedIndicators, setSelectedIndicators] = useLocalStorage<
    Indicator[]
  >('selected-indicators', BANK_TOP_INDICATORS);

  const [indicatorData, setIndicatorData] = useState<
    Record<string, Record<string, number | null>>
  >({});

  const dateFrom = '2024-01-01T00:00:00';
  const dateTo = '2024-10-31T23:59:59';

  // useGetSupportedIndicators({
  //   reg_number: 1000,
  //   dt: '2024-07-01T00:00:00Z',
  // });

  const fetchData = async () => {
    if (!selectedBanks?.length) return;

    const requests = selectedBanks.flatMap((bank) =>
      selectedIndicators.map((indicator) =>
        indicatorsApi
          .getIndicatorData({
            reg_number: Number(bank.reg_number),
            ind_code: indicator.ind_code,
            date_from: dateFrom,
            date_to: dateTo,
          })
          .then((res) => ({
            bankReg: bank.reg_number,
            ind_code: indicator.ind_code,
            value: res?.iitg ?? null,
          }))
      )
    );

    const results = await Promise.allSettled(requests);

    const indicatorValues: Record<string, Record<string, number | null>> = {};

    for (const r of results) {
      if (r.status === 'fulfilled') {
        const { bankReg, ind_code, value } = r.value;
        if (!indicatorValues[bankReg]) indicatorValues[bankReg] = {};
        indicatorValues[bankReg][ind_code] = value;
      } else {
        console.warn('Ошибка запроса индикатора:', r.reason);
      }
    }

    setIndicatorData(indicatorValues);
  };

  useEffect(() => {
    if (!selectedBanks?.length) return;
    fetchData();
  }, [selectedBanks, selectedIndicators]);

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

  if (!allBanks) return <TableLoader />;

  const indCodeCounts = selectedIndicators.reduce<Record<string, number>>(
    (acc, ind) => {
      acc[ind.ind_code] = (acc[ind.ind_code] || 0) + 1;
      return acc;
    },
    {}
  );

  const indCodeSeen: Record<string, number> = {};

  const formatNumber = (value: number | null | undefined) =>
    value != null ? new Intl.NumberFormat('ru-RU').format(value) : '—';

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
                    {selectedBanks.map((bank) => (
                      <td key={`${bank.bic}_${rowKey}`}>
                        {formatNumber(indicatorData[bank.reg_number]?.[code])}
                      </td>
                    ))}
                    <td></td>
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
        popularBankBics={DEFAULT_BANKS_REGS}
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
