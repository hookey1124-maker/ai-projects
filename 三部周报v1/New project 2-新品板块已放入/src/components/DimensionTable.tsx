import { ArrowDownUp } from 'lucide-react';
import type { DimensionMetrics, SortKey, TableDimension, TrendDimension } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatPrice, formatRate, signedClass } from '../utils/formatters';

type DimensionTableProps = {
  metrics: DimensionMetrics[];
  activeTab: TableDimension;
  selectedDimension: TrendDimension;
  selectedValue: string;
  sortKey: SortKey;
  sortDirection: 'asc' | 'desc';
  onSort: (key: SortKey) => void;
  onDrill: (dimension: TrendDimension, value: string) => void;
  state?: 'loading' | 'error' | 'ready';
  emptyMessage?: string;
};

const tabToTrendDimension = (tab: TableDimension): TrendDimension => {
  if (tab === '按分析人') return '分析人';
  if (tab === '按产品分类') return '产品分类';
  if (tab === '按产品等级') return '产品等级';
  return '总盘';
};

const SortButton = ({ label, sortKey, onSort }: { label: string; sortKey: SortKey; onSort: (key: SortKey) => void }) => (
  <button className="sort-button" type="button" onClick={() => onSort(sortKey)}>
    {label}<ArrowDownUp size={13} />
  </button>
);

export default function DimensionTable({
  metrics,
  activeTab,
  selectedDimension,
  selectedValue,
  sortKey,
  sortDirection,
  onSort,
  onDrill,
  state = 'ready',
  emptyMessage,
}: DimensionTableProps) {
  const sorted = [...metrics].sort((a, b) => {
    const av = a[sortKey] ?? -Infinity;
    const bv = b[sortKey] ?? -Infinity;
    return sortDirection === 'desc' ? Number(bv) - Number(av) : Number(av) - Number(bv);
  });
  const drillDimension = tabToTrendDimension(activeTab);

  return (
    <div className="table-shell">
      <table className="dimension-table">
        <thead>
          <tr>
            <th>维度</th>
            <th>SKU数</th>
            <th>动销SKU数</th>
            <th><SortButton label="本期销量" sortKey="salesQty" onSort={onSort} /></th>
            <th><SortButton label="销量环比" sortKey="salesQtyRate" onSort={onSort} /></th>
            <th><SortButton label="本期销售额" sortKey="salesAmount" onSort={onSort} /></th>
            <th><SortButton label="销售额环比" sortKey="salesAmountRate" onSort={onSort} /></th>
            <th>市占比</th>
            <th><SortButton label="市占变化" sortKey="marketShareBpChange" onSort={onSort} /></th>
            <th>在售均价</th>
            <th>出单均价</th>
            <th>异常标签</th>
            <th>建议动作</th>
          </tr>
        </thead>
        <tbody>
          {state !== 'ready' || sorted.length === 0 ? (
            <tr className="table-empty-row">
              <td colSpan={13}>
                {state === 'loading'
                  ? '数据加载中...'
                  : state === 'error'
                    ? '表格数据加载失败。'
                    : emptyMessage || '当前维度暂无可展示数据。'}
              </td>
            </tr>
          ) : sorted.map((item) => {
            const selected = selectedDimension === drillDimension && (drillDimension === '总盘' || selectedValue === item.dimensionName);
            return (
              <tr
                key={`${item.dimension}-${item.dimensionName}`}
                className={selected ? 'selected-row' : ''}
                onClick={() => onDrill(drillDimension, drillDimension === '总盘' ? '全部' : item.dimensionName)}
              >
                <td className="dimension-name">{item.dimensionName}</td>
                <td>{formatInteger(item.skuCount)}</td>
                <td>{formatInteger(item.activeSkuCount)}</td>
                <td>{formatInteger(item.salesQty)}</td>
                <td className={signedClass(item.salesQtyRate, item.salesQtyRateStatus)}>{formatRate(item.salesQtyRate, item.salesQtyRateStatus)}</td>
                <td>{formatAmount(item.salesAmount)}</td>
                <td className={signedClass(item.salesAmountRate, item.salesAmountRateStatus)}>{formatRate(item.salesAmountRate, item.salesAmountRateStatus)}</td>
                <td>{formatPercent(item.marketShare)}</td>
                <td className={signedClass(item.marketShareBpChange)}>{formatBp(item.marketShareBpChange)}</td>
                <td>{formatPrice(item.listingAvgPrice)}</td>
                <td>{formatPrice(item.soldAvgPrice)}</td>
                <td>
                  <div className="tag-list">
                    {item.insightTags.map((tag) => <span className={`tag tag-${tag}`} key={tag}>{tag}</span>)}
                  </div>
                </td>
                <td className="action-cell">{item.action}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
