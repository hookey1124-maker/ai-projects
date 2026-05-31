import type { WeeklyPeriod } from '../types/weeklyReport';

type PeriodSelectorProps = {
  periods: WeeklyPeriod[];
  selectedIndex: number;
  onChange: (index: number) => void;
};

export default function PeriodSelector({ periods, selectedIndex, onChange }: PeriodSelectorProps) {
  const previous = selectedIndex > 0 ? periods[selectedIndex - 1]?.label : '--';
  return (
    <>
      <label className="select-label">
        汇报周期
        <select value={selectedIndex} onChange={(event) => onChange(Number(event.target.value))}>
          {periods.map((period, index) => (
            <option key={period.label} value={index}>{period.label}</option>
          ))}
        </select>
      </label>
      <div className="compare-pill">对比：{previous}</div>
    </>
  );
}
