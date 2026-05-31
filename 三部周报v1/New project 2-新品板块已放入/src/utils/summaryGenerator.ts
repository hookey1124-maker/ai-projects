import type { DimensionMetrics, TrendDimension, TrendPoint } from '../types/weeklyReport';
import { formatAmount, formatBp, formatInteger, formatPercent, formatRate } from './formatters';

const rateText = (value: number | null, status: 'normal' | 'new' | 'none') => formatRate(value, status);

const pickTop = (items: DimensionMetrics[], predicate: (item: DimensionMetrics) => boolean, limit = 3) =>
  items
    .filter(predicate)
    .sort((a, b) => Math.abs(b.salesQtyChange) - Math.abs(a.salesQtyChange))
    .slice(0, limit)
    .map((item) => item.dimensionName)
    .join('、') || '暂无明显项';

const pickTopBy = (items: DimensionMetrics[], selector: (item: DimensionMetrics) => number, positive: boolean, limit = 3) =>
  [...items]
    .filter((item) => positive ? selector(item) > 0 : selector(item) < 0)
    .sort((a, b) => positive ? selector(b) - selector(a) : selector(a) - selector(b))
    .slice(0, limit)
    .map((item) => item.dimensionName)
    .join('、') || '暂无明显项';

const isDown = (value: number | null) => value != null && value < -0.000001;
const isUp = (value: number | null) => value != null && value > 0.000001;

const gradeOrder = ['A', 'B', 'C', 'D'];

const gradeRank = (name: string) => {
  const index = gradeOrder.findIndex((grade) => name.toUpperCase().includes(grade));
  return index === -1 ? 99 : index;
};

const directionText = (qtyRate: number | null, amountRate: number | null) => {
  if (isUp(qtyRate) && isUp(amountRate)) return '销量和销售额均增长';
  if (isDown(qtyRate) && isDown(amountRate)) return '销量和销售额均下滑';
  if (isUp(qtyRate) && isDown(amountRate)) return '销量增长但销售额下滑';
  if (isDown(qtyRate) && isUp(amountRate)) return '销量下滑但销售额增长';
  if (isDown(qtyRate)) return '销量下滑、销售额基本稳定';
  if (isDown(amountRate)) return '销量基本稳定、销售额下滑';
  return '销量和销售额整体稳定';
};

const metricIssue = (item: DimensionMetrics) => {
  const amountWeak = item.salesAmountRate != null && item.salesQtyRate != null && item.salesAmountRate < item.salesQtyRate - 0.05;
  if (amountWeak) return '销售额表现弱于销量，需关注成交均价或产品结构';
  if (item.marketShareBpChange != null && item.salesQtyRate != null && item.salesQtyRate < 0 && item.marketShareBpChange > 0) return '销量下降但市占提升，更偏市场同步走弱';
  if (item.marketShareBpChange != null && item.salesQtyRate != null && item.salesQtyRate < 0 && item.marketShareBpChange < 0) return '销量下降且市占下降，自身竞争力需要排查';
  if (item.soldAvgPriceRate != null && item.soldAvgPriceRate < -0.03) return '出单均价下滑，需要复核成交结构';
  return item.insightTags.includes('明显增长') || item.insightTags.includes('稳定增长') ? '当前表现偏正向，可继续跟进放量' : '当前变化处于可观察区间';
};

const describeDimension = (item: DimensionMetrics) =>
  `${item.dimensionName}：${directionText(item.salesQtyRate, item.salesAmountRate)}，销量环比 ${rateText(item.salesQtyRate, item.salesQtyRateStatus)}，销售额环比 ${rateText(item.salesAmountRate, item.salesAmountRateStatus)}，${metricIssue(item)}。`;

const buildGradeComparison = (gradeMetrics: DimensionMetrics[]) => {
  const grades = [...gradeMetrics].sort((a, b) => gradeRank(a.dimensionName) - gradeRank(b.dimensionName));
  if (!grades.length) return '产品等级字段缺失或暂无可对比数据，A/B/C/D 横向判断暂不可用。';
  const overview = grades.map((item) => `${item.dimensionName}${directionText(item.salesQtyRate, item.salesAmountRate)}`).join('；');
  const details = grades.map(describeDimension).join('');
  return `从产品等级看，${overview}。具体来看，${details}`;
};

const buildDimensionComparison = (
  categoryMetrics: DimensionMetrics[],
  gradeMetrics: DimensionMetrics[],
  analystMetrics: DimensionMetrics[],
) => {
  const categoryGrowth = pickTop(categoryMetrics, (item) => item.salesQtyChange > 0, 3);
  const categoryDrag = pickTop(categoryMetrics, (item) => item.salesQtyChange < 0, 3);
  const analystDrag = pickTopBy(analystMetrics, (item) => item.salesAmountChange, false, 3);
  const analystGrowth = pickTopBy(analystMetrics, (item) => item.salesAmountChange, true, 3);
  return [
    buildGradeComparison(gradeMetrics),
    `从产品分类看，${categoryGrowth}贡献增长；${categoryDrag}形成主要拖累。分类层面建议优先排查拖累项的销售额跌幅、成交均价和市占变化。`,
    `从分析人看，${analystGrowth}负责范围贡献增长；${analystDrag}负责范围形成拖累。该结论用于横向定位责任范围，不代表个人绩效，需要结合类目结构和 SKU 组合复核。`,
  ];
};

const trendSentence = (series: TrendPoint[]) => {
  const recent = series.slice(-4);
  if (recent.length < 2) return '历史周期不足，近几周趋势暂不判断。';
  const first = recent[0];
  const last = recent.at(-1)!;
  const qtyDirection = last.salesQty > first.salesQty ? '走高' : last.salesQty < first.salesQty ? '走低' : '基本持平';
  const amountDirection = last.salesAmount > first.salesAmount ? '走高' : last.salesAmount < first.salesAmount ? '走低' : '基本持平';
  return `近 ${recent.length} 周看，销量整体${qtyDirection}，销售额整体${amountDirection}。`;
};

export const generateSummary = (
  periodLabel: string,
  totalMetric: DimensionMetrics,
  currentMetric: DimensionMetrics,
  trendDimension: TrendDimension,
  categoryMetrics: DimensionMetrics[],
  gradeMetrics: DimensionMetrics[],
  analystMetrics: DimensionMetrics[],
  trendSeries: TrendPoint[] = [],
  selectedPeriodIndex?: number,
) => {
  const amountDropsMore =
    totalMetric.salesAmountRate != null &&
    totalMetric.salesQtyRate != null &&
    totalMetric.salesAmountRate < totalMetric.salesQtyRate - 0.02;
  const growth = pickTop(categoryMetrics, (item) => item.salesQtyChange > 0);
  const drag = pickTop(categoryMetrics, (item) => item.salesQtyChange < 0);
  const concern = [...categoryMetrics, ...gradeMetrics]
    .filter((item) => item.insightTags.some((tag) => !['正常波动', '稳定增长', '明显增长'].includes(tag)))
    .slice(0, 4)
    .map((item) => item.dimensionName)
    .join('、') || '暂无突出异常';
  const marketJudgement = totalMetric.marketShare == null || totalMetric.marketShareBpChange == null
    ? '市占或对手字段缺失，市场同步走弱和竞争力判断暂不可用。'
    : isDown(totalMetric.salesQtyRate) && totalMetric.marketShareBpChange > 0
      ? '销量下降但市占提升，更像市场或对手同步走弱，并不一定是自身竞争力下降。'
      : isDown(totalMetric.salesQtyRate) && totalMetric.marketShareBpChange < 0
        ? '销量下降且市占下降，自身竞争力存在下滑风险，需要排查价格、广告和链接转化。'
        : '市占变化未显示明显竞争力恶化信号。';
  const priceStructureJudgement = amountDropsMore
    ? '销售额跌幅大于销量跌幅，说明出单均价或产品结构存在下滑压力。'
    : totalMetric.soldAvgPriceRate != null && totalMetric.soldAvgPriceRate < -0.03
      ? '出单均价明显下滑，需要关注低价 SKU 出单占比是否提升。'
      : '销量与销售额变化整体相对匹配。';

  const total = [
    `${periodLabel} 期间，总销量为 ${formatInteger(totalMetric.salesQty)}，环比 ${rateText(totalMetric.salesQtyRate, totalMetric.salesQtyRateStatus)}；销售额为 ${formatAmount(totalMetric.salesAmount)}，环比 ${rateText(totalMetric.salesAmountRate, totalMetric.salesAmountRateStatus)}。${priceStructureJudgement}`,
    `市占比为 ${formatPercent(totalMetric.marketShare)}，较上期变化 ${formatBp(totalMetric.marketShareBpChange)}；直接对手出单为 ${formatInteger(totalMetric.competitorOrders)}，环比 ${rateText(totalMetric.competitorRate, totalMetric.competitorRateStatus)}。${marketJudgement}`,
    `从产品分类看，${growth}贡献增长；${drag}为主要拖累项。需要重点关注：${concern}。`,
  ];

  const comparison = buildDimensionComparison(categoryMetrics, gradeMetrics, analystMetrics);

  if (trendDimension === '总盘') return { total, comparison, detail: [] };

  const detailAmountWeak =
    currentMetric.salesAmountRate != null &&
    currentMetric.salesQtyRate != null &&
    currentMetric.salesAmountRate < currentMetric.salesQtyRate - 0.05;
  const priceDivergence =
    currentMetric.listingAvgPriceRate != null &&
    currentMetric.soldAvgPriceRate != null &&
    currentMetric.listingAvgPriceRate >= -0.005 &&
    currentMetric.soldAvgPriceRate < -0.03;
  const trendPoint = selectedPeriodIndex == null ? trendSeries.at(-1) : trendSeries[selectedPeriodIndex];
  const prevTrendPoint = selectedPeriodIndex != null && selectedPeriodIndex > 0 ? trendSeries[selectedPeriodIndex - 1] : undefined;
  const shareSentence = trendPoint?.salesQtyShare == null || trendPoint?.salesAmountShare == null
    ? '该对象对总盘的贡献占比暂不可判断。'
    : `本期销量贡献占比为 ${formatPercent(trendPoint.salesQtyShare)}，销售额贡献占比为 ${formatPercent(trendPoint.salesAmountShare)}${prevTrendPoint?.salesQtyShare != null && prevTrendPoint?.salesAmountShare != null ? `；较上期分别变化 ${formatBp((trendPoint.salesQtyShare - prevTrendPoint.salesQtyShare) * 10000)}、${formatBp((trendPoint.salesAmountShare - prevTrendPoint.salesAmountShare) * 10000)}。` : '。'}`;
  const detailJudgements = [
    detailAmountWeak ? '销量增长或降幅较小但销售额表现偏弱，需要关注增长是否集中在低价 SKU。' : '',
    isDown(currentMetric.salesQtyRate) && currentMetric.marketShareBpChange != null && currentMetric.marketShareBpChange > 0 ? '销量下降但市占上升，更像市场同步走弱或对手出单下降。' : '',
    isDown(currentMetric.salesQtyRate) && currentMetric.marketShareBpChange != null && currentMetric.marketShareBpChange < 0 ? '销量下降且市占下降，当前对象自身竞争力需要重点排查。' : '',
    priceDivergence ? '在售均价和出单均价背离，低价成交结构可能上升。' : '',
    currentMetric.soldAvgPriceRate != null && currentMetric.soldAvgPriceRate < -0.03 ? '出单均价明显下滑，需要复核成交 SKU 结构。' : '',
    trendDimension === '产品等级' && currentMetric.dimensionName.includes('D') ? 'D档增长需要关注是否只是低价动销，还是具备稳定销售额贡献。' : '',
    trendDimension === '产品等级' && currentMetric.dimensionName.includes('A') && currentMetric.salesAmountRate != null && currentMetric.salesAmountRate < -0.05 ? 'A档销售额下滑需要重点排查高货值 SKU 和成交均价变化。' : '',
  ].filter(Boolean).join('');

  const detail = [
    `${currentMetric.dimensionName}本期销量为 ${formatInteger(currentMetric.salesQty)}，环比 ${rateText(currentMetric.salesQtyRate, currentMetric.salesQtyRateStatus)}；销售额为 ${formatAmount(currentMetric.salesAmount)}，环比 ${rateText(currentMetric.salesAmountRate, currentMetric.salesAmountRateStatus)}。`,
    `该对象市占比为 ${formatPercent(currentMetric.marketShare)}，较上期变化 ${formatBp(currentMetric.marketShareBpChange)}。${currentMetric.marketShare == null ? '市占或对手字段缺失，竞争判断暂不可用。' : ''}${shareSentence}`,
    `${trendSentence(trendSeries)}${detailJudgements || '当前对象销量、销售额和价格结构未出现突出的额外风险。'}异常标签为「${currentMetric.insightTags.join('、')}」，建议动作：${currentMetric.action}。`,
  ];

  return { total, comparison, detail };
};
