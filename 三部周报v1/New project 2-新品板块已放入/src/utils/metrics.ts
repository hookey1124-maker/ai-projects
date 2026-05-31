import type {
  DimensionMetrics,
  FieldMap,
  RateStatus,
  RawExcelRow,
  TableDimension,
  TrendDimension,
  TrendPoint,
  WeeklyPeriod,
} from '../types/weeklyReport';
import { classifyInsight } from './insightRules';
import { safeDisplay } from './formatters';

const hiddenDimensionNames = new Set(['无在售', '未分组']);

export const isHiddenDimensionName = (name: string) => hiddenDimensionNames.has(name.trim());

export const toNumber = (value: unknown, fallback = 0) => {
  if (typeof value === 'number') return Number.isFinite(value) ? value : fallback;
  const raw = String(value ?? '').trim();
  if (!raw || raw.startsWith('#')) return fallback;
  const cleaned = raw.replace(/,/g, '').replace(/￥|\$/g, '');
  const parsed = Number(cleaned.endsWith('%') ? Number(cleaned.slice(0, -1)) / 100 : cleaned);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const toNullableNumber = (value: unknown) => {
  const raw = String(value ?? '').trim();
  if (!raw || raw.startsWith('#')) return null;
  const parsed = toNumber(value, Number.NaN);
  if (!Number.isFinite(parsed) || Math.abs(parsed) > 10000000) return null;
  return parsed;
};

const toListingPrice = (value: unknown) => {
  const parsed = toNullableNumber(value);
  return parsed != null && parsed > 0 && parsed < 10000 ? parsed : null;
};

const calcRate = (current: number | null, previous: number | null): { value: number | null; status: RateStatus } => {
  if (current == null || previous == null) return { value: null, status: 'none' };
  const curr = current ?? 0;
  const prev = previous ?? 0;
  if (prev === 0 && curr === 0) return { value: 0, status: 'normal' };
  if (prev === 0 && curr > 0) return { value: null, status: 'new' };
  if (prev === 0) return { value: null, status: 'none' };
  return { value: (curr - prev) / prev, status: 'normal' };
};

const avg = (values: Array<number | null>) => {
  const valid = values.filter((value): value is number => value != null && Number.isFinite(value));
  return valid.length ? valid.reduce((sum, value) => sum + value, 0) / valid.length : null;
};

const dimensionField = (dimension: TableDimension | TrendDimension, fields: FieldMap) => {
  if (dimension === '分析人' || dimension === '按分析人') return fields.analyst;
  if (dimension === '产品分类' || dimension === '按产品分类') return fields.category;
  if (dimension === '产品等级' || dimension === '按产品等级') return fields.productGrade;
  if (dimension === '三级类目') return fields.tertiaryCategory;
  return undefined;
};

export const filterRowsByTrend = (
  rows: RawExcelRow[],
  fields: FieldMap,
  dimension: TrendDimension,
  value: string,
) => {
  const field = dimensionField(dimension, fields);
  if (!field || dimension === '总盘') return rows;
  return rows.filter((row) => safeDisplay(row[field]) === value);
};

const periodAggregate = (rows: RawExcelRow[], period?: WeeklyPeriod) => {
  if (!period) {
    return {
      salesQty: 0,
      salesAmount: 0,
      competitorOrders: null,
      marketShare: null,
      listingAvgPrice: null,
      soldAvgPrice: null,
      activeSkuCount: 0,
    };
  }
  const salesQty = rows.reduce((sum, row) => sum + toNumber(row[period.salesQtyColumn]), 0);
  const salesAmountColumn = period.salesAmountColumn;
  const competitorColumn = period.competitorColumn;
  const listingPriceColumn = period.listingPriceColumn;
  const salesAmount = salesAmountColumn
    ? rows.reduce((sum, row) => sum + toNumber(row[salesAmountColumn]), 0)
    : 0;
  const competitorOrders = competitorColumn
    ? rows.reduce((sum, row) => sum + toNumber(row[competitorColumn]), 0)
    : null;
  const listingAvgPrice = listingPriceColumn
    ? avg(rows.map((row) => toListingPrice(row[listingPriceColumn])))
    : null;
  const soldAvgPrice = salesQty > 0 ? salesAmount / salesQty : null;
  const denominator = competitorOrders == null ? null : salesQty + competitorOrders;
  const marketShare = denominator != null && denominator > 0 ? salesQty / denominator : null;
  const activeSkuCount = rows.filter((row) => toNumber(row[period.salesQtyColumn]) > 0).length;
  return { salesQty, salesAmount, competitorOrders, marketShare, listingAvgPrice, soldAvgPrice, activeSkuCount };
};

const buildMetric = (
  dimension: TableDimension | TrendDimension,
  dimensionName: string,
  rows: RawExcelRow[],
  currentPeriod: WeeklyPeriod | undefined,
  previousPeriod: WeeklyPeriod | undefined,
): DimensionMetrics => {
  const current = periodAggregate(rows, currentPeriod);
  const previous = periodAggregate(rows, previousPeriod);
  const salesQtyRate = calcRate(current.salesQty, previous.salesQty);
  const salesAmountRate = calcRate(current.salesAmount, previous.salesAmount);
  const competitorRate = calcRate(current.competitorOrders, previous.competitorOrders);
  const listingRate = calcRate(current.listingAvgPrice, previous.listingAvgPrice);
  const soldRate = calcRate(current.soldAvgPrice, previous.soldAvgPrice);
  const marketShareBpChange =
    current.marketShare != null && previous.marketShare != null ? (current.marketShare - previous.marketShare) * 10000 : null;

  const base = {
    dimension,
    dimensionName,
    skuCount: rows.length,
    activeSkuCount: current.activeSkuCount,
    salesQty: current.salesQty,
    prevSalesQty: previous.salesQty,
    salesQtyChange: current.salesQty - previous.salesQty,
    salesQtyRate: salesQtyRate.value,
    salesQtyRateStatus: previousPeriod ? salesQtyRate.status : 'none' as RateStatus,
    salesAmount: current.salesAmount,
    prevSalesAmount: previous.salesAmount,
    salesAmountChange: current.salesAmount - previous.salesAmount,
    salesAmountRate: salesAmountRate.value,
    salesAmountRateStatus: previousPeriod ? salesAmountRate.status : 'none' as RateStatus,
    competitorOrders: current.competitorOrders,
    prevCompetitorOrders: previous.competitorOrders,
    competitorRate: competitorRate.value,
    competitorRateStatus: previousPeriod ? competitorRate.status : 'none' as RateStatus,
    marketShare: current.marketShare,
    prevMarketShare: previous.marketShare,
    marketShareBpChange: previousPeriod ? marketShareBpChange : null,
    listingAvgPrice: current.listingAvgPrice,
    prevListingAvgPrice: previous.listingAvgPrice,
    listingAvgPriceRate: listingRate.value,
    listingAvgPriceRateStatus: previousPeriod ? listingRate.status : 'none' as RateStatus,
    soldAvgPrice: current.soldAvgPrice,
    prevSoldAvgPrice: previous.soldAvgPrice,
    soldAvgPriceRate: soldRate.value,
    soldAvgPriceRateStatus: previousPeriod ? soldRate.status : 'none' as RateStatus,
  };
  const insight = classifyInsight(base);
  return { ...base, insightTags: insight.tags, action: insight.actions.join('；') };
};

export const aggregateByDimension = (
  rows: RawExcelRow[],
  fields: FieldMap,
  periods: WeeklyPeriod[],
  selectedPeriodIndex: number,
  dimension: TableDimension,
) => {
  const currentPeriod = periods[selectedPeriodIndex];
  const previousPeriod = selectedPeriodIndex > 0 ? periods[selectedPeriodIndex - 1] : undefined;
  if (dimension === '总体') return [buildMetric('总体', '总盘', rows, currentPeriod, previousPeriod)];

  const field = dimensionField(dimension, fields);
  if (!field) return [];
  const groups = new Map<string, RawExcelRow[]>();
  rows.forEach((row) => {
    const key = safeDisplay(row[field]);
    groups.set(key, [...(groups.get(key) ?? []), row]);
  });
  return [...groups.entries()]
    .filter(([name]) => !isHiddenDimensionName(name))
    .map(([name, groupRows]) => buildMetric(dimension, name, groupRows, currentPeriod, previousPeriod))
    .sort((a, b) => b.salesQty - a.salesQty);
};

export const buildKpiMetric = (
  rows: RawExcelRow[],
  fields: FieldMap,
  periods: WeeklyPeriod[],
  selectedPeriodIndex: number,
  dimension: TrendDimension,
  value: string,
) => {
  const filteredRows = filterRowsByTrend(rows, fields, dimension, value);
  return buildMetric(dimension, dimension === '总盘' ? '总盘' : value, filteredRows, periods[selectedPeriodIndex], selectedPeriodIndex > 0 ? periods[selectedPeriodIndex - 1] : undefined);
};

export const getDimensionValues = (rows: RawExcelRow[], fields: FieldMap, dimension: TrendDimension) => {
  const field = dimensionField(dimension, fields);
  if (!field || dimension === '总盘') return ['全部'];
  return [...new Set(rows.map((row) => safeDisplay(row[field])))]
    .filter((value) => Boolean(value) && !isHiddenDimensionName(value))
    .sort((a, b) => a.localeCompare(b, 'zh-CN'));
};

export const buildTrendSeries = (
  rows: RawExcelRow[],
  fields: FieldMap,
  periods: WeeklyPeriod[],
  selectedTrendDimension: TrendDimension,
  selectedTrendValue: string,
): TrendPoint[] => {
  const filteredRows = filterRowsByTrend(rows, fields, selectedTrendDimension, selectedTrendValue);
  return periods.map((period) => {
    const total = periodAggregate(rows, period);
    const current = periodAggregate(filteredRows, period);
    return {
      periodLabel: period.label,
      salesQty: current.salesQty,
      salesAmount: current.salesAmount,
      competitorOrders: current.competitorOrders,
      marketShare: current.marketShare,
      listingAvgPrice: current.listingAvgPrice,
      soldAvgPrice: current.soldAvgPrice,
      skuCount: filteredRows.length,
      activeSkuCount: current.activeSkuCount,
      salesQtyShare: total.salesQty > 0 ? current.salesQty / total.salesQty : null,
      salesAmountShare: total.salesAmount > 0 ? current.salesAmount / total.salesAmount : null,
    };
  });
};
