import type { ReactNode } from 'react';
import ModulePeriodInfo from './ModulePeriodInfo';
import StatusTag from './StatusTag';

type ModulePageLayoutProps = {
  title: string;
  subtitle?: string;
  status?: string;
  riskLevel?: 'low' | 'medium' | 'high' | 'unknown';
  dataPeriod?: string;
  periodTypeLabel?: string;
  sourceStatusLabel?: string;
  children: ReactNode;
};

export default function ModulePageLayout({
  title,
  subtitle,
  status = '待接入',
  riskLevel = 'unknown',
  dataPeriod,
  periodTypeLabel,
  sourceStatusLabel,
  children,
}: ModulePageLayoutProps) {
  return (
    <main className="page-main module-page">
      <div className="module-page-header">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <StatusTag label={status} riskLevel={riskLevel} />
      </div>
      {dataPeriod && periodTypeLabel && <ModulePeriodInfo dataPeriod={dataPeriod} periodTypeLabel={periodTypeLabel} sourceStatusLabel={sourceStatusLabel} />}
      {children}
    </main>
  );
}
