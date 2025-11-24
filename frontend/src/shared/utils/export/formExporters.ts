import type { BankIndicator } from '@/shared/api/indicatorsApi';
import type { Indicator } from '@/features/settings-modal/types';
import { exportTableToCSV, formatExportNumber } from './tableExport';

/**
 * Экспорт для формы 101
 */
export const exportForm101 = (
  selectedBanks: BankIndicator[],
  selectedIndicators: Indicator[],
  indicatorData: Record<
    string,
    Record<string, { iitg: number | null; vitg: number | null }>
  >,
  fromMonth: string | null,
  toMonth: string | null,
  showDynamics: boolean
) => {
  const headers = ['Показатель', ...selectedBanks.map((bank) => bank.name)];

  const rows = selectedIndicators.map((indicator) => {
    const row: Record<string, string | number | null> = {
      Показатель: indicator.name,
    };

    selectedBanks.forEach((bank) => {
      const data = indicatorData[bank.reg_number]?.[indicator.ind_code];
      const value = data?.vitg ?? null;

      if (showDynamics && data?.iitg !== null && data?.vitg !== null) {
        const delta = ((data.vitg - data.iitg) / data.iitg) * 100;
        row[bank.name] =
          `${formatExportNumber(value)} (${delta > 0 ? '+' : ''}${delta.toFixed(1)}%)`;
      } else {
        row[bank.name] = formatExportNumber(value);
      }
    });

    return row;
  });

  const period =
    showDynamics && fromMonth && toMonth
      ? `_${fromMonth}_to_${toMonth}`
      : toMonth
        ? `_${toMonth}`
        : '';

  const filename = `form_101_export${period}_${new Date().toISOString().split('T')[0]}.csv`;

  exportTableToCSV({ headers, rows }, filename);
};

/**
 * Экспорт для формы 123
 */
export const exportForm123 = (
  selectedBanks: BankIndicator[],
  indicatorData: Record<string, Record<string, number | null>>,
  month: string | null,
  rowNames: string[]
) => {
  const headers = ['Показатель', ...selectedBanks.map((bank) => bank.name)];

  const rows = rowNames.map((rowName) => {
    const row: Record<string, string | number | null> = {
      Показатель: rowName,
    };

    selectedBanks.forEach((bank) => {
      const value = indicatorData[bank.reg_number]?.[rowName] ?? null;
      row[bank.name] = formatExportNumber(value);
    });

    return row;
  });

  const period = month ? `_${month}` : '';
  const filename = `form_123_export${period}_${new Date().toISOString().split('T')[0]}.csv`;

  exportTableToCSV({ headers, rows }, filename);
};

/**
 * Экспорт для формы 810
 */
export const exportForm810 = (
  selectedBanks: BankIndicator[],
  indicatorData: Record<string, Record<string, number | null>>,
  month: string | null,
  columns: Array<{ key: string; label: string }>
) => {
  const headers = ['Показатель', ...selectedBanks.map((bank) => bank.name)];

  const rows = columns.map((column) => {
    const row: Record<string, string | number | null> = {
      Показатель: column.label,
    };

    selectedBanks.forEach((bank) => {
      const value = indicatorData[bank.reg_number]?.[column.key] ?? null;
      row[bank.name] = formatExportNumber(value);
    });

    return row;
  });

  const period = month ? `_${month}` : '';
  const filename = `form_810_export${period}_${new Date().toISOString().split('T')[0]}.csv`;

  exportTableToCSV({ headers, rows }, filename);
};
