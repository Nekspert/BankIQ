export interface UseTableFilterPanelProps {
  items: TableItem[];
  initialSelectedIds?: string[];
  onApply: (selectedIds: string[]) => void;
}

export interface TableItem {
  id: string;
  title: string;
}

export interface TableFilterPanelProps {
  items: TableItem[];
  initialSelectedIds?: string[];
  onApply: (selectedIds: string[]) => void;
}
