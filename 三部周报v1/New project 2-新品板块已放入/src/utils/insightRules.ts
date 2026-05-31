import type { DimensionMetrics } from '../types/weeklyReport';

const isBadDimension = (name: string) => {
  const value = String(name ?? '').trim();
  return !value || ['#N/A', '#REF!', 'undefined', 'null'].includes(value);
};

const tagPriority = [
  '数据质量异常',
  '竞争力下滑',
  '销售双降',
  '成交均价下滑',
  '涨价影响待排查',
  '市场同步走弱',
  '销量稳定但销售额下滑',
  '明显增长',
  '稳定增长',
  '正常波动',
];

export const classifyInsight = (metric: Omit<DimensionMetrics, 'insightTags' | 'action'>) => {
  const qty = metric.salesQtyRate;
  const amount = metric.salesAmountRate;
  const shareBp = metric.marketShareBpChange;
  const listing = metric.listingAvgPriceRate;
  const sold = metric.soldAvgPriceRate;
  const tags: string[] = [];
  const actions: string[] = [];

  const add = (tag: string, action: string) => {
    if (!tags.includes(tag)) tags.push(tag);
    if (!actions.includes(action)) actions.push(action);
  };

  if (isBadDimension(metric.dimensionName)) {
    add('数据质量异常', '检查基础字段');
  }
  if (qty != null && amount != null && qty < -0.05 && amount < -0.05) {
    add('销售双降', '重点排查');
  }
  if (qty != null && amount != null && qty >= -0.02 && amount < -0.08) {
    add('销量稳定但销售额下滑', '排查成交均价和产品结构');
  }
  if (qty != null && shareBp != null && qty < -0.05 && shareBp < -100) {
    add('竞争力下滑', '排查价格、广告、链接转化');
  }
  if (qty != null && shareBp != null && qty < -0.05 && shareBp >= 0) {
    add('市场同步走弱', '观察市场需求和对手变化');
  }
  if ((sold != null && sold < -0.03) || (qty != null && amount != null && amount < qty - 0.05)) {
    add('成交均价下滑', '关注价格结构');
  }
  if (listing != null && qty != null && listing > 0.02 && qty < -0.05) {
    add('涨价影响待排查', '检查涨价后销量变化');
  }
  if (qty != null && amount != null && qty > 0.1 && amount > 0.1) {
    add('明显增长', '继续放量');
  }
  if (qty != null && amount != null && qty > 0 && amount > 0) {
    add('稳定增长', '持续跟进');
  }
  if (!tags.length) add('正常波动', '观察');
  const actionByTag = new Map(tags.map((tag, index) => [tag, actions[index]]));
  const sortedTags = [...tags].sort((a, b) => tagPriority.indexOf(a) - tagPriority.indexOf(b));
  const sortedActions = sortedTags.map((tag) => actionByTag.get(tag)).filter((action): action is string => Boolean(action));
  return {
    tags: sortedTags,
    primaryTag: sortedTags[0],
    actions: sortedActions,
    primaryAction: sortedActions[0],
  };
};
