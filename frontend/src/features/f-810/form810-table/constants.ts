export interface F810Column {
  key: string;
  label: string;
}

export const F810_COLUMNS: F810Column[] = [
  { key: 'USTKAP', label: 'Уставный капитал' },
  // { key: 'SOB_AK', label: 'Собственные акции' },
  { key: 'EMIS_DOH', label: 'Эмиссионный доход' },
  { key: 'PER_CB', label: 'Переоценка ценных бумаг' },
  { key: 'PER_OS', label: 'Переоценка основных средств' },
  { key: 'DELTADVR', label: 'Дельта ДВР' },
  // { key: 'PER_IH', label: 'Переоценка инструментов хеджирования' },
  { key: 'REZERVF', label: 'Резервный фонд' },
  // { key: 'VKL_V_IM', label: 'Вклады в имущество' },
  { key: 'NERASP_PU', label: 'Нераспределенная прибыль (убыток)' },
  { key: 'ITOGO_IK', label: 'Итого источники капитала' },
];