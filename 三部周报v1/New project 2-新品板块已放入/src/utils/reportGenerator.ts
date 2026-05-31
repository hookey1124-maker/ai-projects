import type { DimensionMetrics, TrendPoint } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatRate } from './formatters';

export type WeeklyConclusion = {
  totalPerformance: string;
  growthSources: string[];
  dragSources: string[];
  riskObjects: string[];
  nextActions: string[];
  warningNote?: string;
};

const positiveTags = ['明显增长', '稳定增长'];
const normalTags = ['正常波动', ...positiveTags];

const rateText = (metric: DimensionMetrics, key: 'salesQtyRate' | 'salesAmountRate') =>
  key === 'salesQtyRate'
    ? formatRate(metric.salesQtyRate, metric.salesQtyRateStatus)
    : formatRate(metric.salesAmountRate, metric.salesAmountRateStatus);

const topNames = (items: DimensionMetrics[], selector: (item: DimensionMetrics) => number, positive: boolean) =>
  [...items]
    .filter((item) => positive ? selector(item) > 0 : selector(item) < 0)
    .sort((a, b) => positive ? selector(b) - selector(a) : selector(a) - selector(b))
    .slice(0, 3);

const hasRisk = (item: DimensionMetrics) => item.insightTags.some((tag) => !normalTags.includes(tag));

export const buildWeeklyConclusion = (
  periodLabel: string,
  total: DimensionMetrics,
  categoryMetrics: DimensionMetrics[],
  gradeMetrics: DimensionMetrics[],
  analystMetrics: DimensionMetrics[],
  warnings: string[],
): WeeklyConclusion => {
  const amountWeak = total.salesAmountRate != null && total.salesQtyRate != null && total.salesAmountRate < total.salesQtyRate - 0.02;
  const competitionUnavailable = total.marketShare == null || total.marketShareBpChange == null;
  const marketShareBpChange = total.marketShareBpChange;
  const marketJudgement = competitionUnavailable
    ? '市占或对手字段缺失，市场竞争判断暂不可用'
    : total.salesQtyRate != null && total.salesQtyRate < 0 && marketShareBpChange != null && marketShareBpChange > 0
      ? '销量下降但市占提升，更偏市场或对手同步走弱'
      : total.salesQtyRate != null && total.salesQtyRate < 0 && marketShareBpChange != null && marketShareBpChange < 0
        ? '销量下降且市占下降，自身竞争力存在下滑风险'
        : '市占变化未显示明显竞争力恶化';
  const totalPerformance = `${periodLabel} 总销量 ${formatInteger(total.salesQty)}，环比 ${rateText(total, 'salesQtyRate')}；销售额 ${formatAmount(total.salesAmount)}，环比 ${rateText(total, 'salesAmountRate')}。${amountWeak ? '销售额表现弱于销量，成交均价或产品结构存在压力。' : '销量与销售额变化整体匹配。'}${marketJudgement}。`;

  const growth = topNames(categoryMetrics, (item) => item.salesQtyChange, true);
  const drags = topNames(categoryMetrics, (item) => item.salesQtyChange, false);
  const risks = [...categoryMetrics, ...gradeMetrics, ...analystMetrics]
    .filter(hasRisk)
    .sort((a, b) => Math.abs(b.salesAmountChange) - Math.abs(a.salesAmountChange))
    .slice(0, 5);
  const riskActions = [...new Set(risks.flatMap((item) => item.action.split('；')).filter(Boolean))];

  return {
    totalPerformance,
    growthSources: growth.length
      ? growth.map((item) => `${item.dimensionName}贡献增长，销量变化 ${formatInteger(item.salesQtyChange)}，销售额变化 ${formatAmount(item.salesAmountChange)}。`)
      : ['暂无明确增长来源。'],
    dragSources: drags.length
      ? drags.map((item) => `${item.dimensionName}形成拖累，销量变化 ${formatInteger(item.salesQtyChange)}，销售额变化 ${formatAmount(item.salesAmountChange)}。`)
      : ['暂无明显拖累项。'],
    riskObjects: risks.length
      ? risks.map((item) => `${item.dimensionName}命中「${item.insightTags.join('、')}」，${item.action}。`)
      : ['暂无突出异常对象。'],
    nextActions: riskActions.length
      ? riskActions.slice(0, 5)
      : ['持续观察销量、销售额、市占和成交均价变化。'],
    warningNote: warnings.length ? '部分周期字段存在缺失或日期不一致，相关判断需谨慎。' : undefined,
  };
};

export const buildRankingText = (items: DimensionMetrics[], selector: (item: DimensionMetrics) => number | null, valueFormatter: (item: DimensionMetrics) => string) =>
  items.slice(0, 5).map((item, index) => `${index + 1}. ${item.dimensionName}：${valueFormatter(item)}，${item.insightTags.join('、')}，${item.action}`);

export const buildWeeklyReportText = (
  periodLabel: string,
  previousLabel: string,
  conclusion: WeeklyConclusion,
  dimensionSummary: string[],
  detailSummary: string[],
  warningCount: number,
  total?: DimensionMetrics,
) => [
  '【总销售数据周报】',
  `周期：${periodLabel}`,
  `对比：${previousLabel}`,
  '',
  '【总盘表现】',
  ...(total ? [
    `销量：${formatInteger(total.salesQty)}（环比 ${formatRate(total.salesQtyRate, total.salesQtyRateStatus)}）`,
    `销售额：${formatAmount(total.salesAmount)}（环比 ${formatRate(total.salesAmountRate, total.salesAmountRateStatus)}）`,
    `市占比：${formatPercent(total.marketShare)}（${formatBp(total.marketShareBpChange)}）`,
    `直接对手出单：${formatInteger(total.competitorOrders)}（环比 ${formatRate(total.competitorRate, total.competitorRateStatus)}）`,
    `出单均价：${formatAmount(total.soldAvgPrice)}（环比 ${formatRate(total.soldAvgPriceRate, total.soldAvgPriceRateStatus)}）`,
    '',
    '【核心判断】',
  ] : []),
  conclusion.totalPerformance,
  '',
  '【主要增长来源】',
  ...conclusion.growthSources.map((item, index) => `${index + 1}. ${item}`),
  '',
  '【主要拖累项】',
  ...conclusion.dragSources.map((item, index) => `${index + 1}. ${item}`),
  '',
  '【重点异常】',
  ...conclusion.riskObjects.map((item, index) => `${index + 1}. ${item}`),
  '',
  '【维度对比总结】',
  ...dimensionSummary.map((item, index) => `${index + 1}. ${item}`),
  ...(detailSummary.length ? ['', '【当前对象总结】', ...detailSummary.map((item, index) => `${index + 1}. ${item}`)] : []),
  '',
  '【下周建议动作】',
  ...conclusion.nextActions.map((item, index) => `${index + 1}. ${item}`),
  warningCount ? '\n数据提示：当前数据源存在 warning，部分字段判断需谨慎。' : '',
].filter(Boolean).join('\n');

export const describeTrendPoint = (point?: TrendPoint) => point
  ? `销量 ${formatInteger(point.salesQty)}，销售额 ${formatAmount(point.salesAmount)}，市占 ${formatPercent(point.marketShare)}`
  : '--';
