/**
 * Универсальный тип для данных таблицы
 */
export interface TableExportData {
  headers: string[];
  rows: Array<Record<string, string | number | null>>;
}

/**
 * Конвертирует данные таблицы в CSV формат
 */
const convertToCSV = (data: TableExportData): string => {
  const { headers, rows } = data;
  
  const escapeCSV = (value: string | number | null): string => {
    if (value === null || value === undefined) return '';
    const stringValue = String(value);
    
    if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
      return `"${stringValue.replace(/"/g, '""')}"`;
    }
    return stringValue;
  };

  const csvHeaders = headers.map(escapeCSV).join(',');
  const csvRows = rows.map(row => 
    headers.map(header => escapeCSV(row[header])).join(',')
  );

  return [csvHeaders, ...csvRows].join('\n');
};

/**
 * Скачивает файл с данными
 */
const downloadFile = (content: string, filename: string, mimeType: string) => {
  const BOM = '\uFEFF';
  const blob = new Blob([BOM + content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Экспортирует таблицу в CSV
 */
export const exportTableToCSV = (
  data: TableExportData,
  filename: string = 'export.csv'
): void => {
  const csv = convertToCSV(data);
  downloadFile(csv, filename, 'text/csv;charset=utf-8;');
};

/**
 * Форматирует число для отображения
 */
export const formatExportNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '—';
  return new Intl.NumberFormat('ru-RU').format(value);
};