import type { CSSProperties } from 'react';

type KpiCardProps = {
  label: string;
  value?: string | number;
  helper?: string;
  style?: CSSProperties;
};

export default function KpiCard({ label, value = '--', helper, style }: KpiCardProps) {
  return (
    <article className="kpi-card common-kpi-card" style={style}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {helper && <p>{helper}</p>}
    </article>
  );
}
