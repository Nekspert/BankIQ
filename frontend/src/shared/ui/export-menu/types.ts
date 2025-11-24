import type { ExportFormat } from '@/shared/utils/export/tableExport';

export interface ExportMenuProps {
  onExport: (format: ExportFormat) => void;
  className?: string;
  disabled?: boolean;
}
