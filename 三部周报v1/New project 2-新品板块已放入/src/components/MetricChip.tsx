type MetricChipProps = {
  label: string;
  value: string;
  change?: string;
  tone?: 'positive' | 'negative' | 'neutral';
  compact?: boolean;
};

const arrow = (tone: MetricChipProps['tone']) => {
  if (tone === 'positive') return '↑';
  if (tone === 'negative') return '↓';
  return '—';
};

export default function MetricChip({ label, value, change, tone = 'neutral', compact = false }: MetricChipProps) {
  return (
    <div className={`metric-chip ${compact ? 'compact' : ''}`}>
      <span>{label}</span>
      <strong className={`highlight-value ${change ? '' : `change-${tone}`}`}>{value}</strong>
      {change && (
        <em className={`change-${tone}`}>
          {arrow(tone)} {change}
        </em>
      )}
    </div>
  );
}
