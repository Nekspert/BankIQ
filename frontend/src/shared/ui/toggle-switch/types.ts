export type ToggleSwitchProps = {
  checked: boolean;
  onChange: (v: boolean) => void;
  label?: string;
  className?: string;
  disabled?: boolean;
};