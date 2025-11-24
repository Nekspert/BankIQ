import { useState, useRef, useEffect, type FC } from 'react';
import type { ExportFormat } from '@/shared/utils/export/tableExport';
import Button from '@/shared/ui/button/Button';
import ExportSvg from '@/shared/icons/DownloadIcon.svg?react';
import styles from './styles.module.scss';
import classNames from 'classnames';
import type { ExportMenuProps } from './types';

export const ExportMenu: FC<ExportMenuProps> = ({
  onExport,
  className,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const handleExport = (format: ExportFormat) => {
    onExport(format);
    setIsOpen(false);
  };

  const exportOptions = [
    { format: 'csv' as ExportFormat, label: 'CSV', icon: '📄' },
    { format: 'xlsx' as ExportFormat, label: 'Excel (XLSX)', icon: '📊' },
    { format: 'pdf' as ExportFormat, label: 'PDF', icon: '📑' },
  ];

  return (
    <div className={classNames(styles.wrapper, className)} ref={menuRef}>
      <Button
        variant="ghost"
        className={styles.button}
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <ExportSvg />
      </Button>

      {isOpen && (
        <div className={styles.menu}>
          <div className={styles.menuTitle}>Экспортировать как:</div>
          {exportOptions.map((option) => (
            <button
              key={option.format}
              className={styles.menuItem}
              onClick={() => handleExport(option.format)}
            >
              <span className={styles.menuIcon}>{option.icon}</span>
              <span className={styles.menuLabel}>{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExportMenu;
