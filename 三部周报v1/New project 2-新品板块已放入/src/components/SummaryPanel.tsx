import { Check, ClipboardCopy } from 'lucide-react';
import { useState } from 'react';
import type { DimensionMetrics, TrendDimension, TrendPoint } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatPrice, formatRate, signedClass } from '../utils/formatters';
import MetricChip from './MetricChip';

type SummaryPanelProps = {
  comparison: string[];
  detail: string[];
  copyText: string;
  gradeMetrics: DimensionMetrics[];
  currentMetric: DimensionMetrics;
  trendDimension: TrendDimension;
  trendValue: string;
  trendSeries: TrendPoint[];
  selectedPeriodIndex: number;
};

const gradeRank = (name: string) => {
  const index = ['A', 'B', 'C', 'D'].findIndex((grade) => name.toUpperCase().includes(grade));
  return index === -1 ? 99 : index;
};

const gradeLabel = (item: DimensionMetrics) => {
  const risky = item.insightTags.find((tag) => !['正常波动', '稳定增长', '明显增长'].includes(tag));
  if (risky) return risky;
  const name = item.dimensionName.toUpperCase();
  const qtyDown = item.salesQtyRate != null && item.salesQtyRate < 0;
  const amountDown = item.salesAmountRate != null && item.salesAmountRate < 0;
  const amountWeak = item.salesAmountRate != null && item.salesQtyRate != null && item.salesAmountRate < item.salesQtyRate - 0.05;
  if (name.includes('A') && amountWeak) return '高货值均价压力';
  if (name.includes('B') && qtyDown && amountDown) return '主力盘小幅下滑';
  if (name.includes('C') && qtyDown && item.salesAmountRate != null && item.salesQtyRate != null && item.salesAmountRate > item.salesQtyRate) return '成交结构改善';
  if (name.includes('D') && item.salesQtyRate != null && item.salesQtyRate > 0) return '尾部动销改善';
  if (item.dimensionName.toUpperCase().includes('D') && item.salesQtyRate != null && item.salesQtyRate > 0) return '尾部动销改善';
  if (amountWeak) return '成交均价下滑';
  return item.insightTags[0] ?? '观察';
};

const tagTone = (tag: string) => {
  if (['明显增长', '稳定增长', '尾部动销改善', '成交结构改善'].includes(tag)) return 'growth-tag';
  if (tag.includes('缺失') || tag.includes('谨慎')) return 'warning-tag';
  if (tag === '正常波动' || tag === '观察') return 'insight-tag';
  return 'risk-tag';
};

const contributionText = (series: TrendPoint[], selectedPeriodIndex: number) => {
  const point = series[selectedPeriodIndex];
  const previous = selectedPeriodIndex > 0 ? series[selectedPeriodIndex - 1] : undefined;
  if (!point || point.salesQtyShare == null || point.salesAmountShare == null) return '贡献占比暂不可判断';
  const qtyChange = previous?.salesQtyShare == null ? '--' : formatBp((point.salesQtyShare - previous.salesQtyShare) * 10000);
  const amountChange = previous?.salesAmountShare == null ? '--' : formatBp((point.salesAmountShare - previous.salesAmountShare) * 10000);
  return `销量贡献 ${formatPercent(point.salesQtyShare)}（${qtyChange}），销售额贡献 ${formatPercent(point.salesAmountShare)}（${amountChange}）`;
};

export default function SummaryPanel({
  comparison,
  detail,
  copyText,
  gradeMetrics,
  currentMetric,
  trendDimension,
  trendValue,
  trendSeries,
  selectedPeriodIndex,
}: SummaryPanelProps) {
  const [copyState, setCopyState] = useState<'idle' | 'success' | 'error'>('idle');
  const gradeCards = [...gradeMetrics].sort((a, b) => gradeRank(a.dimensionName) - gradeRank(b.dimensionName));
  const showCurrentObject = trendDimension !== '总盘';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(copyText);
      setCopyState('success');
    } catch {
      setCopyState('error');
    }
    window.setTimeout(() => setCopyState('idle'), 1800);
  };

  return (
    <aside className="summary-panel">
      <div className="summary-header">
        <h2>周报文本</h2>
        <button type="button" className="copy-button" onClick={handleCopy}>
          {copyState === 'success' ? <Check size={16} /> : <ClipboardCopy size={16} />}
          {copyState === 'success' ? '已复制' : copyState === 'error' ? '复制失败，请手动复制' : '复制周报总结'}
        </button>
      </div>
      <section>
        <h3>维度对比总结</h3>
        <div className="dimension-compare-grid">
          {gradeCards.map((item) => {
            const label = gradeLabel(item);
            return (
              <article className="dimension-compare-card" key={`${item.dimension}-${item.dimensionName}`}>
                <div className="dimension-card-title">{item.dimensionName}</div>
                <div className="summary-kpi-row compact">
                  <MetricChip compact label="销量环比" value={formatRate(item.salesQtyRate, item.salesQtyRateStatus)} tone={signedClass(item.salesQtyRate, item.salesQtyRateStatus)} />
                  <MetricChip compact label="销售额环比" value={formatRate(item.salesAmountRate, item.salesAmountRateStatus)} tone={signedClass(item.salesAmountRate, item.salesAmountRateStatus)} />
                  <MetricChip compact label="市占变化" value={formatBp(item.marketShareBpChange)} tone={signedClass(item.marketShareBpChange)} />
                </div>
                <span className={`insight-tag ${tagTone(label)}`}>{label}</span>
              </article>
            );
          })}
        </div>
        {comparison.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      </section>
      {showCurrentObject && detail.length > 0 && (
        <section>
          <h3>当前对象总结</h3>
          <div className="current-summary-card">
            <div>
              <span>当前对象</span>
              <strong>{trendDimension} / {trendValue}</strong>
            </div>
            <div className="summary-kpi-row">
              <MetricChip label="销量" value={formatInteger(currentMetric.salesQty)} change={formatRate(currentMetric.salesQtyRate, currentMetric.salesQtyRateStatus)} tone={signedClass(currentMetric.salesQtyRate, currentMetric.salesQtyRateStatus)} />
              <MetricChip label="销售额" value={formatAmount(currentMetric.salesAmount)} change={formatRate(currentMetric.salesAmountRate, currentMetric.salesAmountRateStatus)} tone={signedClass(currentMetric.salesAmountRate, currentMetric.salesAmountRateStatus)} />
              <MetricChip label="市占比" value={formatPercent(currentMetric.marketShare)} change={formatBp(currentMetric.marketShareBpChange)} tone={signedClass(currentMetric.marketShareBpChange)} />
              <MetricChip label="出单均价" value={formatPrice(currentMetric.soldAvgPrice)} change={formatRate(currentMetric.soldAvgPriceRate, currentMetric.soldAvgPriceRateStatus)} tone={signedClass(currentMetric.soldAvgPriceRate, currentMetric.soldAvgPriceRateStatus)} />
            </div>
            <div className="insight-tag-list">
              {currentMetric.insightTags.map((tag) => <span className={`insight-tag ${tagTone(tag)}`} key={tag}>{tag}</span>)}
            </div>
            <p className="contribution-line">{contributionText(trendSeries, selectedPeriodIndex)}</p>
            <div className="action-card">{currentMetric.action}</div>
          </div>
          {detail.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
        </section>
      )}
    </aside>
  );
}
