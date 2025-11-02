import type { ReactNode } from "react";

export interface TitleProps {
  children: ReactNode;
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  align?: 'left' | 'center' | 'right';
  className?: string;
}
