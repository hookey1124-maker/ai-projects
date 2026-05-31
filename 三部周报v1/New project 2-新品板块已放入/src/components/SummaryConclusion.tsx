import type { ReactNode } from 'react';
import type { DimensionMetrics } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatPrice, formatRate, signedClass } from '../utils/formatters';
import type { WeeklyConclusion } from '../utils/reportGenerator';
import MetricChip from './MetricChip';

type SummaryConclusionProps = {
  conclusion: WeeklyConclusion;
  totalMetric: DimensionMetrics;
  categoryMetrics: DimensionMetrics[];
  gradeMetrics: DimensionMetrics[];
  expanded: boolean;
  onToggle: () => void;
};

const Section = ({ title, children }: { title: string; children: ReactNode }) => (
  <div className="conclusion-section">
    <span>{title}</span>
    {children}
  </div>
);

const tagTone = (tag: string) => {
  if (['明显增长', '稳定增长'].includes(tag)) return 'growth-tag';
  if (tag.includes('缺失') || tag.includes('谨慎') || tag.includes('数据')) return 'warning-tag';
  if (['正常波动', '市场同步走弱'].includes(tag)) return 'insight-tag';
  return 'risk-tag';
};

const topMovers = (items: DimensionMetrics[], positive: boolean) =>
  [...items]
    .filter((item) => positive ? item.salesQtyChange > 0 : item.salesQtyChange < 0)
    .sort((a, b) => positive ? b.salesQtyChange - a.salesQtyChange : a.salesQtyChange - b.salesQtyChange)
    .slice(0, 4);

const buildJudgementTags = (metric: DimensionMetrics, warningNote?: string) => {
  const tags = new Set<string>();
  metric.insightTags.forEach((tag) => tags.add(tag));
  if (metric.salesAmountRate != null && metric.salesQtyRate != null && metric.salesAmountRate < metric.salesQtyRate - 0.02) {
    tags.add('成交均价/产品结构下滑');
  }
  if (metric.marketShareBpChange == null) tags.add('数据字段缺失，判断需谨慎');
  if (metric.salesQtyRate != null && metric.salesQtyRate < 0 && metric.marketShareBpChange != null && metric.marketShareBpChange > 0) {
    tags.add('市场同步走弱');
  }
  if (metric.salesQtyRate != null && metric.salesQtyRate < 0 && metric.marketShareBpChange != null && metric.marketShareBpChange < 0) {
    tags.add('自身竞争力下滑');
  }
  if (warningNote) tags.add('数据字段缺失，判断需谨慎');
  return [...tags].slice(0, 7);
};

export default function SummaryConclusion({
  conclusion,
  totalMetric,
  categoryMetrics,
  gradeMetrics,
  expanded,
  onToggle,
}: SummaryConclusionProps) {
  const generatedCount = 5;
  const growthItems = topMovers([...categoryMetrics, ...gradeMetrics], true);
  const dragItems = topMovers([...categoryMetrics, ...gradeMetrics], false);
  const judgementTags = buildJudgementTags(totalMetric, conclusion.warningNote);

  return (
    <section className={`conclusion-card ${expanded ? '' : 'collapsed'}`}>
      <div className="conclusion-header">
        <div>
          <h2>本周核心结论</h2>
          {expanded
            ? conclusion.warningNote && <p>{conclusion.warningNote}</p>
            : <p>已生成 {generatedCount} 条核心判断，点击展开查看。</p>}
        </div>
        <button type="button" className="secondary-button" onClick={onToggle}>
          {expanded ? '收起' : '展开'}
        </button>
      </div>
      {expanded && (
        <div className="summary-grid">
          <Section title="总盘表现">
            <div className="summary-kpi-row">
              <MetricChip label="销量" value={formatInteger(totalMetric.salesQty)} change={formatRate(totalMetric.salesQtyRate, totalMetric.salesQtyRateStatus)} tone={signedClass(totalMetric.salesQtyRate, totalMetric.salesQtyRateStatus)} />
              <MetricChip label="销售额" value={formatAmount(totalMetric.salesAmount)} change={formatRate(totalMetric.salesAmountRate, totalMetric.salesAmountRateStatus)} tone={signedClass(totalMetric.salesAmountRate, totalMetric.salesAmountRateStatus)} />
              <MetricChip label="市占比" value={formatPercent(totalMetric.marketShare)} change={formatBp(totalMetric.marketShareBpChange)} tone={signedClass(totalMetric.marketShareBpChange)} />
              <MetricChip label="直接对手出单" value={formatInteger(totalMetric.competitorOrders)} change={formatRate(totalMetric.competitorRate, totalMetric.competitorRateStatus)} tone={signedClass(totalMetric.competitorRate, totalMetric.competitorRateStatus)} />
              <MetricChip label="出单均价" value={formatPrice(totalMetric.soldAvgPrice)} change={formatRate(totalMetric.soldAvgPriceRate, totalMetric.soldAvgPriceRateStatus)} tone={signedClass(totalMetric.soldAvgPriceRate, totalMetric.soldAvgPriceRateStatus)} />
            </div>
            <p>{conclusion.totalPerformance}</p>
          </Section>
          <Section title="核心判断">
            <div className="insight-tag-list">
              {judgementTags.map((tag) => <span className={`insight-tag ${tagTone(tag)}`} key={tag}>{tag}</span>)}
            </div>
          </Section>
          <Section title="主要增长来源">
            <div className="summary-chip-list">
              {growthItems.length ? growthItems.map((item) => (
                <MetricChip key={`${item.dimension}-${item.dimensionName}`} compact label={item.dimensionName} value={formatInteger(item.salesQty)} change={formatRate(item.salesQtyRate, item.salesQtyRateStatus)} tone={signedClass(item.salesQtyRate, item.salesQtyRateStatus)} />
              )) : <p>暂无明确增长来源。</p>}
            </div>
          </Section>
          <Section title="主要拖累来源">
            <div className="summary-chip-list">
              {dragItems.length ? dragItems.map((item) => (
                <MetricChip key={`${item.dimension}-${item.dimensionName}`} compact label={item.dimensionName} value={formatInteger(item.salesQty)} change={formatRate(item.salesQtyRate, item.salesQtyRateStatus)} tone={signedClass(item.salesQtyRate, item.salesQtyRateStatus)} />
              )) : <p>暂无明显拖累项。</p>}
            </div>
          </Section>
          <Section title="重点异常对象">
            <ul>{conclusion.riskObjects.map((item) => <li key={item}>{item}</li>)}</ul>
          </Section>
          <Section title="下周建议动作">
            <div className="action-card-list">
              {conclusion.nextActions.map((item) => <div className="action-card" key={item}>{item}</div>)}
            </div>
          </Section>
        </div>
      )}
    </section>
  );
}
