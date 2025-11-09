import { useState, useEffect, useMemo } from 'react';
import { useGetAllBanks } from '@/shared/api/hooks/indicators/useGetAllBanks';
import { useLocalStorage } from '@/shared/hooks/useLocalStorage';
import { DEFAULT_BANKS_REGS, BANK_TOP_INDICATORS } from '../constants';
import { useIndicatorQueries } from './useIndicatorQueries';
import { getMonthRange } from '../utils/date';
import { useDebounce } from '@/shared/hooks/useDebounce';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { Indicator } from '../../settings-modal/types';
import { dateToYYYYMM, monthToDate } from '../helpers';
import { getPrevMonth } from '../utils/getPrevMonth';

export const useBanksComparison = () => {
  const { data: allBanksData } = useGetAllBanks();
  const allBanks = allBanksData?.banks;

  const [selectedBanks, setSelectedBanks] = useLocalStorage<BankIndicator[]>(
    'banks-list',
    []
  );
  const [selectedIndicators, setSelectedIndicators] = useLocalStorage<
    Indicator[]
  >('selected-indicators', BANK_TOP_INDICATORS);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const today = new Date();
  const defaultToMonth = dateToYYYYMM(today);
  const prev = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const defaultFromMonth = dateToYYYYMM(prev);

  const [fromMonth, setFromMonth] = useLocalStorage<string | null>(
    'banks-from-month',
    defaultFromMonth
  );
  const [toMonth, setToMonth] = useLocalStorage<string | null>(
    'banks-to-month',
    defaultToMonth
  );

  const [showDynamics, setShowDynamics] = useLocalStorage<boolean>(
    'banks-show-dynamics',
    true
  );

  const debouncedFrom = useDebounce(fromMonth, 350);
  const debouncedTo = useDebounce(toMonth, 350);

  useEffect(() => {
    if (toMonth) {
      const parsedTo = monthToDate(toMonth);
      if (parsedTo && parsedTo > today) {
        setToMonth(defaultToMonth);
      }
    } else setToMonth(defaultToMonth);

    if (!fromMonth) {
      setFromMonth(defaultFromMonth);
    }
    if (fromMonth && toMonth) {
      const pFrom = monthToDate(fromMonth);
      const pTo = monthToDate(toMonth);
      if (pFrom && pTo && pFrom > pTo) {
        setFromMonth(toMonth);
      }
    }
  }, [fromMonth, toMonth]);

  const { from: dateFrom } = useMemo(
    () => getMonthRange(showDynamics ? debouncedFrom : null),
    [showDynamics, debouncedFrom]
  );
  const { to: dateTo } = useMemo(
    () => getMonthRange(debouncedTo),
    [debouncedTo]
  );

  const { indicatorData, rawResults } = useIndicatorQueries(
    selectedBanks,
    selectedIndicators,
    dateFrom ?? getPrevMonth(new Date(dateTo || new Date())),
    dateTo ?? null
    // fromMonth ? getMonthStartDate(fromMonth) : null,
    // toMonth ? getMonthEndDate(toMonth) : null
  );

  const handleAddBanks = (banks: BankIndicator[]) =>
    setSelectedBanks((prev) => [...(prev || []), ...banks]);
  const handleRemoveBank = (bic: string) =>
    setSelectedBanks((prev) => prev?.filter((b) => b.bic !== bic));

  useEffect(() => {
    if (allBanks && selectedBanks.length === 0) {
      const defaults = allBanks.filter((b) =>
        DEFAULT_BANKS_REGS.includes(b.reg_number)
      );
      if (defaults.length) setSelectedBanks(defaults);
    }
  }, [allBanks, selectedBanks.length, setSelectedBanks]);

  const indCodeCounts = useMemo(
    () =>
      selectedIndicators.reduce<Record<string, number>>((acc, ind) => {
        acc[ind.ind_code] = (acc[ind.ind_code] || 0) + 1;
        return acc;
      }, {}),
    [selectedIndicators]
  );

  const formatNumber = (value: number | null | undefined) =>
    value != null ? new Intl.NumberFormat('ru-RU').format(value) : '—';

  return {
    allBanks,
    selectedBanks,
    selectedIndicators,
    indicatorData,
    rawResults,
    isModalOpen,
    setIsModalOpen,
    isSettingsOpen,
    setIsSettingsOpen,
    setSelectedBanks,
    setSelectedIndicators,
    handleAddBanks,
    handleRemoveBank,
    indCodeCounts,
    formatNumber,
    fromMonth,
    toMonth,
    setFromMonth,
    setToMonth,
    showDynamics,
    setShowDynamics,
    effectiveFrom: dateFrom ?? null,
    effectiveTo: dateTo ?? null,
  };
};
