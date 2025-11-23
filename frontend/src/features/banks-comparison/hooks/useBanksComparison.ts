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
import { DEFAULT_BANK_REGS } from '@/shared/config/constants';

/**
 * Кастомный хук для управления логикой сравнения банков и показателей.
 * Сохраняет выбранные банки и индикаторы, управляет диапазоном дат и запросами данных.
 *
 * @hook
 * @returns {{
 *  allBanks: BankIndicator[] | undefined;
 *  selectedBanks: BankIndicator[];
 *  selectedIndicators: Indicator[];
 *  indicatorData: any;
 *  rawResults: any;
 *  isModalOpen: boolean;
 *  setIsModalOpen: (open: boolean) => void;
 *  isSettingsOpen: boolean;
 *  setIsSettingsOpen: (open: boolean) => void;
 *  handleAddBanks: (banks: BankIndicator[]) => void;
 *  handleRemoveBank: (bic: string) => void;
 *  fromMonth: string | null;
 *  toMonth: string | null;
 *  setFromMonth: (month: string | null) => void;
 *  setToMonth: (month: string | null) => void;
 *  showDynamics: boolean;
 *  setShowDynamics: (val: boolean) => void;
 *  effectiveFrom: Date | null;
 *  effectiveTo: Date | null;
 *  indCodeCounts: Record<string, number>;
 *  formatNumber: (value: number | null | undefined) => string;
 * }}
 *
 * @see {@link useGetAllBanks} — Получает список всех банков.
 * @see {@link useIndicatorQueries} — Запрашивает данные по выбранным банкам и показателям.
 * @see {@link useLocalStorage} — Хранит пользовательские настройки и выбор.
 * @see {@link useDebounce} — Снижает частоту обновления дат при вводе.
 * @see {@link getMonthRange} — Преобразует месяцы в диапазон дат.
 * @see {@link getPrevMonth} — Возвращает предыдущий месяц для диапазона по умолчанию.
 *
 * @example
 * ```tsx
 * const {
 *   selectedBanks,
 *   selectedIndicators,
 *   handleAddBanks,
 *   indicatorData,
 * } = useBanksComparison();
 * ```
 */
export const useBanksComparison = () => {
  const { data: allBanksData } = useGetAllBanks();
  const allBanks = allBanksData?.banks;

  /** @hook useLocalStorage — Список выбранных банков */
  const [selectedBanks, setSelectedBanks] = useLocalStorage<BankIndicator[]>(
    'banks-list',
    []
  );

  /** @hook useLocalStorage — Список выбранных показателей */
  const [selectedIndicators, setSelectedIndicators] = useLocalStorage<
    Indicator[]
  >('selected-indicators', BANK_TOP_INDICATORS);

  /** @hook useState — Состояния модальных окон */
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  /** @description Дефолтные месяцы для фильтрации диапазона */
  const today = new Date();
  const defaultToMonth = dateToYYYYMM(today);
  const prev = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const defaultFromMonth = dateToYYYYMM(prev);

  /** @hook useLocalStorage — Диапазон месяцев для отображения данных */
  const [fromMonth, setFromMonth] = useLocalStorage<string | null>(
    'banks-from-month',
    defaultFromMonth
  );
  const [toMonth, setToMonth] = useLocalStorage<string | null>(
    'banks-to-month',
    defaultToMonth
  );

  /** @hook useLocalStorage — Флаг отображения динамики */
  const [showDynamics, setShowDynamics] = useLocalStorage<boolean>(
    'banks-show-dynamics',
    true
  );

  /** @hook useDebounce — Оптимизация обновления периода */
  const debouncedFrom = useDebounce(fromMonth, 350);
  const debouncedTo = useDebounce(toMonth, 350);

  /** Проверка корректности выбранных месяцев */
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

  /** @hook useMemo — Рассчитывает реальные даты для фильтрации */
  const { from: dateFrom } = useMemo(
    () => getMonthRange(showDynamics ? debouncedFrom : null),
    [showDynamics, debouncedFrom]
  );
  const { to: dateTo } = useMemo(
    () => getMonthRange(debouncedTo),
    [debouncedTo]
  );

  /** @hook useIndicatorQueries — Загружает данные индикаторов по выбранным банкам */
  const { indicatorData, rawResults } = useIndicatorQueries(
    selectedBanks,
    selectedIndicators,
    dateFrom ?? getPrevMonth(new Date(dateTo || new Date())),
    dateTo ?? null
    // fromMonth ? getMonthStartDate(fromMonth) : null,
    // toMonth ? getMonthEndDate(toMonth) : null
  );

  /** Добавляет новые банки в список */
  const handleAddBanks = (banks: BankIndicator[]) =>
    setSelectedBanks((prev) => [...(prev || []), ...banks]);

  /** Удаляет банк по BIC */
  const handleRemoveBank = (bic: string) =>
    setSelectedBanks((prev) => prev?.filter((b) => b.bic !== bic));

  /** Автоматически добавляет дефолтные банки при первой загрузке */
  useEffect(() => {
    if (!!allBanks?.length && !selectedBanks.length) {
      const defaultBanks = allBanks!.filter((bank) =>
        DEFAULT_BANK_REGS.includes(bank.reg_number)
      );
      if (defaultBanks.length > 0) {
        setSelectedBanks(defaultBanks);
      }
    }
  }, [allBanks, selectedBanks.length, setSelectedBanks]);

  /** @hook useMemo — Подсчёт количества одинаковых индикаторов */
  const indCodeCounts = useMemo(
    () =>
      selectedIndicators.reduce<Record<string, number>>((acc, ind) => {
        acc[ind.ind_code] = (acc[ind.ind_code] || 0) + 1;
        return acc;
      }, {}),
    [selectedIndicators]
  );

  /** Форматирует числовые значения с разделителями тысяч */
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
