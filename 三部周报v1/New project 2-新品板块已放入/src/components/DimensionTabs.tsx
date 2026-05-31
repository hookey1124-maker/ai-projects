import type { TableDimension } from '../types/weeklyReport';

type DimensionTabsProps = {
  active: TableDimension;
  onChange: (tab: TableDimension) => void;
};

const tabs: TableDimension[] = ['总体', '按分析人', '按产品分类', '按产品等级'];

export default function DimensionTabs({ active, onChange }: DimensionTabsProps) {
  return (
    <div className="dimension-tabs">
      {tabs.map((tab) => (
        <button
          key={tab}
          type="button"
          className={active === tab ? 'active' : ''}
          onClick={() => onChange(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}
