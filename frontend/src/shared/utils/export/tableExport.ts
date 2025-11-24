/**
 * Универсальный тип для данных таблицы
 */
export interface TableExportData {
  headers: string[];
  rows: Array<Record<string, string | number | null>>;
  title?: string;
}

/**
 * Форматы экспорта
 */
export type ExportFormat = 'csv' | 'xlsx' | 'pdf';

/**
 * Конвертирует данные таблицы в CSV формат
 */
const convertToCSV = (data: TableExportData): string => {
  const { headers, rows } = data;

  const escapeCSV = (value: string | number | null): string => {
    if (value === null || value === undefined) return '';
    const stringValue = String(value);

    if (
      stringValue.includes(',') ||
      stringValue.includes('"') ||
      stringValue.includes('\n')
    ) {
      return `"${stringValue.replace(/"/g, '""')}"`;
    }
    return stringValue;
  };

  const csvHeaders = headers.map(escapeCSV).join(',');
  const csvRows = rows.map((row) =>
    headers.map((header) => escapeCSV(row[header])).join(',')
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
 * Экспортирует таблицу в XLSX (Excel)
 * Использует простой XML-подход без внешних библиотек
 */
export const exportTableToXLSX = (
  data: TableExportData,
  filename: string = 'export.xlsx'
): void => {
  const { headers, rows } = data;

  let html = '<table>';

  html += '<thead><tr>';
  headers.forEach((header) => {
    html += `<th>${escapeHTML(String(header))}</th>`;
  });
  html += '</tr></thead>';

  html += '<tbody>';
  rows.forEach((row) => {
    html += '<tr>';
    headers.forEach((header) => {
      const value = row[header];
      html += `<td>${escapeHTML(String(value ?? ''))}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';

  const blob = new Blob(['\uFEFF' + html], {
    type: 'application/vnd.ms-excel;charset=utf-8;',
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename.replace('.xlsx', '.xls');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Экспортирует таблицу в PDF
 */
export const exportTableToPDF = (data: TableExportData, fileName: string): void => {
  const { headers, rows, title } = data;

  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    alert('Пожалуйста, разрешите всплывающие окна для экспорта в PDF');
    return;
  }

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>${title || 'Экспорт таблицы'}</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: Arial, sans-serif;
          padding: 20px;
          font-size: 10pt;
        }
        
        h1 {
          font-size: 16pt;
          margin-bottom: 20px;
          color: #1f2937;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 20px;
        }
        
        th, td {
          border: 1px solid #e5e7eb;
          padding: 8px;
          text-align: left;
        }
        
        th {
          background-color: #f3f4f6;
          font-weight: 600;
          color: #1f2937;
        }
        
        tbody tr:nth-child(even) {
          background-color: #f9fafb;
        }
        
        @media print {
          body {
            padding: 0;
          }
          
          @page {
            size: A4 landscape;
            margin: 15mm;
          }
        }
      </style>
    </head>
    <body>
      ${title ? `<h1>${escapeHTML(title)}</h1>` : ''}
      <table>
        <thead>
          <tr>
            ${headers.map((h) => `<th>${escapeHTML(String(h))}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
            <tr>
              ${headers.map((h) => `<td>${escapeHTML(String(row[h] ?? ''))}</td>`).join('')}
            </tr>
          `
            )
            .join('')}
        </tbody>
      </table>
      <script>
        window.onload = function() {
          window.print();
          setTimeout(function() { window.close(); }, 100);
        };
      </script>
    </body>
    </html>
  `;

  printWindow.document.write(html);
};

/**
 * Экранирует HTML
 */
const escapeHTML = (str: string): string => {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
};

/**
 * Форматирует число для отображения
 */
export const formatExportNumber = (
  value: number | null | undefined
): string => {
  if (value === null || value === undefined) return '—';
  return new Intl.NumberFormat('ru-RU').format(value);
};
