import React, {
  forwardRef,
  useCallback,
  useEffect,
  useRef,
  useState,
  type InputHTMLAttributes,
} from 'react';
import styles from './styles.module.scss';

type Props = InputHTMLAttributes<HTMLInputElement> & {
  className?: string;
  isEditing?: boolean;
  value?: string | number;
  options?: string[];
};

export const Input = forwardRef<HTMLInputElement, Props>(
  (props, forwardedRef) => {
    const {
      className = '',
      isEditing = true,
      value,
      placeholder = '',
      type = 'text',
      options = [],
      onChange,
      defaultValue,
      ...rest
    } = props;

    const wrapperRef = useRef<HTMLDivElement | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
      if (!forwardedRef) return;
      if (typeof forwardedRef === 'function') {
        forwardedRef(inputRef.current);
      } else {
        forwardedRef.current = inputRef.current;
      }
    }, [forwardedRef]);

    const isControlled = value !== undefined;

    const [inputValue, setInputValue] = useState<string>(() =>
      isControlled ? String(value) : String(defaultValue ?? '')
    );

    useEffect(() => {
      if (isControlled) {
        setInputValue(String(value ?? ''));
      }
    }, [value, isControlled]);

    const [isOpen, setIsOpen] = useState(false);
    const [highlighted, setHighlighted] = useState<number>(-1);

    const inputLower = (inputValue || '').toLowerCase();
    const opts = options || [];

    const isExactOption = opts.some((opt) => opt.toLowerCase() === inputLower);

    const filtered = opts.filter((opt) => {
      if (inputLower === '' || isExactOption) return true;
      return opt.toLowerCase().includes(inputLower);
    });

    const handleFocus = () => {
      if (filtered.length > 0) setIsOpen(true);
    };

    const handleBlurOutside = useCallback((e: MouseEvent) => {
      if (!wrapperRef.current) return;
      const target = e.target as Node | null;
      if (target && !wrapperRef.current.contains(target)) {
        setIsOpen(false);
        setHighlighted(-1);
      }
    }, []);

    useEffect(() => {
      document.addEventListener('mousedown', handleBlurOutside);
      return () => document.removeEventListener('mousedown', handleBlurOutside);
    }, [handleBlurOutside]);

    const triggerOnChange = (val: string) => {
      setInputValue(val);

      if (onChange) {
        const synthetic = {
          target: { value: val, name: rest.name },
        } as unknown as React.ChangeEvent<HTMLInputElement>;

        onChange(synthetic);
      }
    };

    const handleInputChange: React.ChangeEventHandler<HTMLInputElement> = (
      e
    ) => {
      const val = e.target.value;
      if (isControlled) {
        if (onChange) onChange(e);
        setInputValue(val);
      } else {
        setInputValue(val);
        if (onChange) onChange(e);
      }

      setIsOpen(Boolean(val && options && options.length > 0));
      setHighlighted(-1);
    };

    const handleSelect = (option: string) => {
      triggerOnChange(option);
      setIsOpen(false);
      inputRef.current?.focus();
    };

    const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
      if (!isOpen && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
        if (filtered.length > 0) {
          setIsOpen(true);
          setHighlighted(0);
          e.preventDefault();
        }
        return;
      }

      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        setHighlighted((prev) => Math.min(prev + 1, filtered.length - 1));
        e.preventDefault();
      } else if (e.key === 'ArrowUp') {
        setHighlighted((prev) => Math.max(prev - 1, 0));
        e.preventDefault();
      } else if (e.key === 'Enter') {
        if (highlighted >= 0 && highlighted < filtered.length) {
          handleSelect(filtered[highlighted]);
          e.preventDefault();
        }
      } else if (e.key === 'Escape') {
        setIsOpen(false);
        setHighlighted(-1);
      }
    };

    useEffect(() => {
      if (!filtered.length) {
        setIsOpen(false);
        setHighlighted(-1);
      }
    }, [filtered.length]);

    if (!isEditing) {
      return (
        <div className={`${styles.input} ${className}`}>
          {String(value ?? defaultValue ?? '') || placeholder}
        </div>
      );
    }

    return (
      <div className={styles.inputWrapper} ref={wrapperRef}>
        <input
          ref={inputRef}
          className={`${styles.input} ${className}`}
          type={type}
          placeholder={placeholder}
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          {...rest}
        />
        {isOpen && filtered.length > 0 && (
          <ul className={styles.dropdown} role="listbox" aria-label="options">
            {filtered.map((opt, idx) => (
              <li
                key={opt + idx}
                role="option"
                aria-selected={highlighted === idx}
                className={`${styles.option} ${
                  highlighted === idx ? styles.optionActive : ''
                }`}
                onMouseDown={(e) => {
                  e.preventDefault();
                  handleSelect(opt);
                }}
                onMouseEnter={() => setHighlighted(idx)}
              >
                {opt}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
