import type { BankIndicator } from '@/shared/api/indicatorsApi';

export interface AddBankModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddBanks: (banks: BankIndicator[]) => void;
  allBanks: BankIndicator[];
  selectedBanks: BankIndicator[];
  popularBankBics?: string[];
}
