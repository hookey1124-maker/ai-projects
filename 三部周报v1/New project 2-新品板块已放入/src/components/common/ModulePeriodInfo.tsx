type ModulePeriodInfoProps = {
  dataPeriod: string;
  periodTypeLabel: string;
  sourceStatusLabel?: string;
};

export default function ModulePeriodInfo({ dataPeriod, periodTypeLabel, sourceStatusLabel }: ModulePeriodInfoProps) {
  return (
    <div className="module-period-info">
      <span><b>数据周期：</b>{dataPeriod}</span>
      <span><b>周期口径：</b>{periodTypeLabel}</span>
      {sourceStatusLabel && <span><b>数据来源状态：</b>{sourceStatusLabel}</span>}
    </div>
  );
}
