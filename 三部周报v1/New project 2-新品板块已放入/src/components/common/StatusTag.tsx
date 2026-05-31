type StatusTagProps = {
  label: string;
  riskLevel?: 'low' | 'medium' | 'high' | 'unknown';
};

export default function StatusTag({ label, riskLevel = 'unknown' }: StatusTagProps) {
  return <span className={`status-tag status-tag-${riskLevel}`}>{label}</span>;
}
