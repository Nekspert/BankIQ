import { useState, useMemo } from 'react';
import type { UseTableFilterPanelProps } from '../types';

export const useTableFilterPanel = ({
  items,
  initialSelectedIds = [],
  onApply,
}: UseTableFilterPanelProps) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelectedIds);

  const selectedItems = useMemo(
    () => items.filter((item) => selectedIds.includes(item.id)),
    [items, selectedIds]
  );

  const availableItems = useMemo(
    () => items.filter((item) => !selectedIds.includes(item.id)),
    [items, selectedIds]
  );

  const addItem = (id: string) => {
    setSelectedIds((prev) => [...prev, id]);
  };

  const removeItem = (id: string) => {
    setSelectedIds((prev) => prev.filter((i) => i !== id));
  };

  const handleReset = () => {
    setSelectedIds([]);
  };

  const handleApply = () => {
    onApply(selectedIds);
  };

  return {
    selectedItems,
    availableItems,
    addItem,
    removeItem,
    handleReset,
    handleApply,
  };
};
