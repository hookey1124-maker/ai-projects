type KpiCardProps = {
  label: string;
  value?: string | number;
  helper?: string;
};

export default function KpiCard({ label, value = '--', helper }: KpiCardProps) {
  return (
    <article className="kpi-card common-kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {helper && <p>{helper}</p>}
    </article>
  );
}
