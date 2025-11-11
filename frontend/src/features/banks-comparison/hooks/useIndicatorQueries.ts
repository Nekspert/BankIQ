import { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import { indicatorsApi } from '@/shared/api/indicatorsApi';
import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { Indicator } from '../../settings-modal/types';

/**
 * ’ук дл€ выполнени€ параллельных запросов к API показателей банков.
 * »спользует `react-query` дл€ загрузки данных по каждому сочетанию банка и индикатора.
 * јвтоматически управл€ет кэшированием и агрегацией результатов.
 *
 * @hook
 * @param {BankIndicator[]} selectedBanks Ч —писок выбранных банков.
 * @param {Indicator[]} selectedIndicators Ч —писок выбранных индикаторов.
 * @param {string | null} dateFrom Ч Ќачало периода (формат YYYY-MM).
 * @param {string | null} dateTo Ч  онец периода (формат YYYY-MM).
 *
 * @returns {{
 *   indicatorData: Record<string, Record<string, { iitg: number | null; vitg: number | null }>>;
 *   rawResults: ReturnType<typeof useQueries>;
 * }}
 * ќбъект с результатами:
 * - `indicatorData` Ч агрегированные данные по банкам и индикаторам;
 * - `rawResults` Ч оригинальные результаты запросов `react-query`.
 *
 * @see {@link indicatorsApi.getIndicatorData} Ч ¬ыполн€ет загрузку данных по конкретному показателю.
 * @see {@link useQueries} Ч ”правл€ет множественными асинхронными запросами.
 * @see {@link useBanksComparison} Ч ќсновной хук, использующий данный дл€ сравнени€ банков.
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
     * ‘ормирует массив конфигураций запросов дл€ react-query.
     *  аждый запрос уникален по комбинации (рег. номер, код индикатора, период).
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
                    /** @function queryFn Ч ¬ыполн€ет запрос данных по индикатору банка */
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

    /** 
     * @hook useQueries
     * ¬ыполн€ет все запросы параллельно и возвращает массив результатов.
     */
    const results = useQueries({ queries });

    /**
     * @hook useMemo
     * ѕреобразует массив результатов в объект с ключами [рег.номер][код_индикатора].
     */
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
