import { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import { indicatorsApi } from '@/shared/api/indicatorsApi';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { Indicator } from '../../settings-modal/types';

export const useIndicatorQueries = (
  selectedBanks: BankIndicator[],
  selectedIndicators: Indicator[],
  dateFrom: string | null,
  dateTo: string | null
) => {
  const queries = useMemo(() => {
    if (!selectedBanks?.length || !selectedIndicators?.length) return [];
    if (!dateFrom || !dateTo) return [];

    return selectedBanks.flatMap((bank) =>
      selectedIndicators.map((indicator) => {
        const reg = Number(bank.reg_number);
        const ind = indicator.ind_code;

        return {
          queryKey: ['indicator-data', reg, ind, dateFrom, dateTo],
          queryFn: async () => {
            const { iitg, vitg } = await indicatorsApi.getIndicatorData({
              reg_number: reg,
              ind_code: ind,
              date_from: dateFrom,
              date_to: dateTo,
            });
            return { iitg, vitg };
          },
          enabled: true,
          staleTime: 1000 * 60 * 5,
          cacheTime: 1000 * 60 * 30,
          refetchOnWindowFocus: false,
          retry: false,
        };
      })
    );
  }, [selectedBanks, selectedIndicators, dateFrom, dateTo]);

  const results = useQueries({ queries });

  const indicatorData = useMemo(() => {
    const out: Record<string, Record<string, { iitg: number | null; vitg: number | null }>> = {};

    if (!results || results.length === 0) return out;

    let idx = 0;
    for (const bank of selectedBanks) {
      const reg = bank.reg_number;
      for (const indicator of selectedIndicators) {
        if (idx >= results.length) break;
        const res = results[idx];
        const value = res?.data ?? { iitg: null, vitg: null };

        if (!out[reg]) out[reg] = {};
        out[reg][indicator.ind_code] = value;

        idx++;
      }
    }

    return out;
  }, [results, selectedBanks, selectedIndicators]);

  return { indicatorData, rawResults: results };
};
