import { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import { indicatorsF123Api } from '@/shared/api/form-123/indicatorsApi';
import { monthToApiDate } from '../utils/monthToApiDate';
import { parseF123Response } from '../utils/parseF123Response';

export const useF123Queries = (
  selectedBanks: BankIndicator[],
  monthYYYYMM: string | null
) => {
  const apiDate = monthToApiDate(monthYYYYMM);

  const queries = useMemo(() => {
    if (!selectedBanks?.length) return [];
    if (!apiDate) return [];

    return selectedBanks.map((bank) => {
      const regNum = Number(bank.reg_number);
      return {
        queryKey: ['f123-indicator', regNum, apiDate],
        queryFn: async () => {
          const data = await indicatorsF123Api.getIndicator({
            regNum,
            date: apiDate,
          });
          return data;
        },
        enabled: true,
        staleTime: 1000 * 60 * 5,
        cacheTime: 1000 * 60 * 30,
        refetchOnWindowFocus: false,
        retry: false,
      };
    });
  }, [selectedBanks, apiDate]);

  const results = useQueries({ queries });

  const indicatorData = useMemo(() => {
    const out: Record<string, Record<string, number | null>> = {};
    if (!results || results.length === 0) return out;
    for (let i = 0; i < selectedBanks.length; i++) {
      const bank = selectedBanks[i];
      const res = results[i];
      const raw = res?.data ?? null;
      out[bank.reg_number] = parseF123Response(raw);
    }
    return out;
  }, [results, selectedBanks]);

  return { indicatorData, rawResults: results };
};
