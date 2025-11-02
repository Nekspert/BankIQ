export interface TableLink {
  id: string;
  title: string;
  icon?: string;
  badge?: number;
}

export interface SideMenuProps {
  tableList: TableLink[];
  isOpen: boolean;
  activeId?: string;
  onLinkClick?: (id: string) => void;
  handleClose: () => void
}