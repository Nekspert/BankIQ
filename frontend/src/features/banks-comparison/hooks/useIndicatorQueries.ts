import { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import { indicatorsApi } from '@/shared/api/indicatorsApi';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { Indicator } from '../../settings-modal/types';

/**
 * ��� ��� ���������� ������������ �������� � API ����������� ������.
 * ���������� `react-query` ��� �������� ������ �� ������� ��������� ����� � ����������.
 * ������������� ��������� ������������ � ���������� �����������.
 *
 * @hook
 * @param {BankIndicator[]} selectedBanks � ������ ��������� ������.
 * @param {Indicator[]} selectedIndicators � ������ ��������� �����������.
 * @param {string | null} dateFrom � ������ ������� (������ YYYY-MM).
 * @param {string | null} dateTo � ����� ������� (������ YYYY-MM).
 *
 * @returns {{
 *   indicatorData: Record<string, Record<string, { iitg: number | null; vitg: number | null }>>;
 *   rawResults: ReturnType<typeof useQueries>;
 * }}
 * ������ � ������������:
 * - `indicatorData` � �������������� ������ �� ������ � �����������;
 * - `rawResults` � ������������ ���������� �������� `react-query`.
 *
 * @see {@link indicatorsApi.getIndicatorData} � ��������� �������� ������ �� ����������� ����������.
 * @see {@link useQueries} � ��������� �������������� ������������ ���������.
 * @see {@link useBanksComparison} � �������� ���, ������������ ������ ��� ��������� ������.
 *
 * @example
 * ```tsx
 * const { indicatorData, rawResults } = useIndicatorQueries(
 *   selectedBanks,
 *   selectedIndicators,
 *   '2024-01',
 *   '2024-06'
 * );
 * ```
 */
export const useIndicatorQueries = (
  selectedBanks: BankIndicator[],
  selectedIndicators: Indicator[],
  dateFrom: string | null,
  dateTo: string | null
) => {
  /**
   * @hook useMemo
   * ��������� ������ ������������ �������� ��� react-query.
   * ������ ������ �������� �� ���������� (���. �����, ��� ����������, ������).
   */
  const queries = useMemo(() => {
    if (!selectedBanks?.length || !selectedIndicators?.length) return [];
    if (!dateFrom || !dateTo) return [];

    return selectedBanks.flatMap((bank) =>
      selectedIndicators.map((indicator) => {
        const reg = Number(bank.reg_number);
        const ind = indicator.ind_code;

        return {
          queryKey: ['indicator-data', reg, ind, dateFrom, dateTo],
          /** @function queryFn � ��������� ������ ������ �� ���������� ����� */
          queryFn: async () => {
            const data = await indicatorsApi.getIndicatorData({
              reg_number: reg,
              ind_code: ind,
              date_from: dateFrom,
              date_to: dateTo,
            });
            return data;
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

  /**
   * @hook useQueries
   * ��������� ��� ������� ����������� � ���������� ������ �����������.
   */
  const results = useQueries({ queries });

  /**
   * @hook useMemo
   * ����������� ������ ����������� � ������ � ������� [���.�����][���_����������].
   */
  const indicatorData = useMemo(() => {
    const out: Record<
      string,
      Record<string, { iitg: number | null; vitg: number | null }>
    > = {};

    if (!results || results.length === 0) return out;
    let idx = 0;
    for (const bank of selectedBanks) {
      const reg = bank.reg_number;
      for (const indicator of selectedIndicators) {
        if (idx >= results.length) break;
        const res = results[idx].data;
        const first = res?.[0]?.iitg;
        const last = res?.[res?.length - 2]?.iitg;
        const value = { iitg: first ?? null, vitg: last ?? null };

        if (!out[reg]) out[reg] = {};
        out[reg][indicator.ind_code] = value;

        idx++;
      }
    }

    return out;
  }, [results, selectedBanks, selectedIndicators]);

  return { indicatorData, rawResults: results };
};
