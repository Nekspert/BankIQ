import { useState, useRef, useEffect } from 'react';
import type { UseCustomSelectProps } from '../types';

export const useCustomSelect = ({
  value,
  onChange,
  options,
  placeholder = 'Выберите значение',
}: UseCustomSelectProps) => {
  const selectRef = useRef<HTMLDivElement>(null);

  const [isOpen, setIsOpen] = useState(false);

  const selectedLabel =
    options.find((option) => option.value === value)?.label || placeholder;

  const handleClickOutside = (event: MouseEvent) => {
    if (
      selectRef.current &&
      !selectRef.current.contains(event.target as Node)
    ) {
      setIsOpen(false);
    }
  };

  const handleSelect = (selectedValue: string) => {
    onChange(selectedValue);
    setIsOpen(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent, selectedValue?: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (selectedValue) {
        handleSelect(selectedValue);
      } else {
        setIsOpen((prev) => !prev);
      }
    }
    if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return {
    isOpen,
    setIsOpen,
    selectRef,
    handleSelect,
    handleKeyPress,
    selectedLabel,
  };
};
