import { BarChart3 } from 'lucide-react';
import type { ReactNode } from 'react';

type HeaderProps = {
  controls: ReactNode;
  statusText: string;
  moduleTitle: string;
};

export default function Header({ controls, statusText, moduleTitle }: HeaderProps) {
  return (
    <header className="main-header app-header">
      <div className="brand-block">
        <div className="brand-icon"><BarChart3 size={22} /></div>
        <div>
          <h1>周报自动生成看板</h1>
          <div className="current-module-title">{moduleTitle}</div>
        </div>
      </div>
      <div className="header-right">
        <div className="header-controls">{controls}</div>
        <div className="data-status">{statusText}</div>
      </div>
    </header>
  );
}
