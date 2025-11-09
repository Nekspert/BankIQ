/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />

declare module '*.svg?react' {
  import { FC, SVGProps } from 'react';
  const content: FC<SVGProps<SVGSVGElement>>;
  export default content;
}

declare module '*.svg' {
  const content: string;
  export default content;
}