import type { BankIndicator } from "@/shared/api/indicatorsApi";

export type Indicator = {
  ind_code: string;
  name: string;
};

export type SettingsModalProps = {
  isOpen: boolean;
  onClose: () => void;
  allBanks: BankIndicator[];
  selectedBanks: BankIndicator[];
  indicators: Indicator[];
  onSave: (banks: BankIndicator[], indicators: Indicator[]) => void;
};