export const formatNumber = (value?: number | null) =>
  value != null ? new Intl.NumberFormat('ru-RU').format(value) : '—';
