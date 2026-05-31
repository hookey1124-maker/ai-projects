import type { TrendDimension } from '../types/weeklyReport';

type TrendFilterBarProps = {
  dimension: TrendDimension;
  value: string;
  values: string[];
  onDimensionChange: (dimension: TrendDimension) => void;
  onValueChange: (value: string) => void;
};

const dimensions: TrendDimension[] = ['总盘', '分析人', '产品分类', '产品等级', '三级类目'];

export default function TrendFilterBar({ dimension, value, values, onDimensionChange, onValueChange }: TrendFilterBarProps) {
  return (
    <section className="trend-filter">
      <div className="segmented">
        {dimensions.map((item) => (
          <button
            key={item}
            type="button"
            className={item === dimension ? 'active' : ''}
            onClick={() => onDimensionChange(item)}
          >
            {item}
          </button>
        ))}
      </div>
      <label className="select-label">
        趋势对象
        <select value={value} onChange={(event) => onValueChange(event.target.value)} disabled={dimension === '总盘'}>
          {values.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>
      </label>
    </section>
  );
}
