export interface SectionProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'small' | 'medium' | 'large';
  background?: 'primary' | 'secondary' | 'transparent';
  withBorder?: boolean
}
