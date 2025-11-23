import { AppRoutes } from './routes';

export interface HeaderLink {
  link: string;
  name: string;
}

export const headerNavList: HeaderLink[] = [
  {
    link: AppRoutes.home,
    name: 'Главная',
  },
  {
    link: AppRoutes.generalStatisticPage,
    name: 'Общее',
  },
];

export const DEFAULT_BANK_REGS = [1481, 2673, 1000, 1326];