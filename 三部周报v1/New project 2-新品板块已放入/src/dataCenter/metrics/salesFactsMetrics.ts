import type { ProductDimension, SalesFact, UnifiedPeriod } from '../types';

export type SalesFactsOverview = {
  salesQty: number;
  previousSalesQty: number;
  salesQtyChange: number;
  salesQtyRate: number | null;
  salesAmount: number;
  previousSalesAmount: number;
  salesAmountChange: number;
  salesAmountRate: number | null;
  competitorOrders: number | null;
  previousCompetitorOrders: number | null;
  marketShare: number | null;
  previousMarketShare: number | null;
  marketShareChange: number | null;
  listingAvgPrice: number | null;
  previousListingAvgPrice: number | null;
  listingAvgPriceRate: number | null;
  soldAvgPrice: number | null;
  previousSoldAvgPrice: number | null;
  soldAvgPriceRate: number | null;
};

export type SalesFactsDimension = 'category' | 'productGrade' | 'analyst';

export type SalesFactsTrendDimension = 'total' | SalesFactsDimension;

export type SalesFactsDimensionRow = SalesFactsOverview & {
  dimensionName: string;
  skuCount: number;
  activeSkuCount: number;
};

export type SalesFactsTrendPoint = {
  periodId: string;
  periodLabel: string;
  salesQty: number;
  salesAmount: number;
  competitorOrders: number | null;
  marketShare: number | null;
  listingAvgPrice: number | null;
  soldAvgPrice: number | null;
  skuCount: number;
  activeSkuCount: number;
  salesQtyShare: number | null;
  salesAmountShare: number | null;
};

const hiddenDimensionNames = new Set(['无在售', '未分组']);

const safeDimensionName = (value: unknown) => {
  const text = String(value ?? '').trim();
  return text && text !== '#N/A' && text !== '#REF!' && text !== 'undefined' ? text : '未分组';
};

const avg = (values: Array<number | null | undefined>) => {
  const valid = values.filter((value): value is number => value != null && Number.isFinite(value) && value > 0 && value < 10000);
  return valid.length ? valid.reduce((sum, value) => sum + value, 0) / valid.length : null;
};

const calcRate = (current: number | null, previous: number | null) => {
  if (current == null || previous == null) return null;
  if (previous === 0 && current === 0) return 0;
  if (previous === 0 && current > 0) return null;
  if (previous === 0) return null;
  return (current - previous) / previous;
};

const periodAggregate = (salesFacts: SalesFact[], periodId?: string) => {
  const facts = periodId ? salesFacts.filter((fact) => fact.periodId === periodId) : [];
  const salesQty = facts.reduce((sum, fact) => sum + fact.salesQty, 0);
  const salesAmount = facts.reduce((sum, fact) => sum + fact.salesAmount, 0);
  const validCompetitorOrders = facts
    .map((fact) => fact.competitorOrders)
    .filter((value): value is number => value != null && Number.isFinite(value));
  const competitorOrders = validCompetitorOrders.length
    ? validCompetitorOrders.reduce((sum, value) => sum + value, 0)
    : null;
  const denominator = competitorOrders == null ? null : salesQty + competitorOrders;
  const marketShare = denominator != null && denominator > 0 ? salesQty / denominator : null;
  const listingAvgPrice = avg(facts.map((fact) => fact.listingPrice));
  const soldAvgPrice = salesQty > 0 ? salesAmount / salesQty : null;

  return {
    salesQty,
    salesAmount,
    competitorOrders,
    marketShare,
    listingAvgPrice,
    soldAvgPrice,
  };
};

const buildDimensionLookup = (productDimensions: ProductDimension[]) => {
  const bySku = new Map<string, ProductDimension>();
  const bySalesCode = new Map<string, ProductDimension>();
  productDimensions.forEach((dimension) => {
    if (dimension.sku && !bySku.has(dimension.sku)) bySku.set(dimension.sku, dimension);
    if (dimension.salesCode && !bySalesCode.has(dimension.salesCode)) bySalesCode.set(dimension.salesCode, dimension);
  });
  return { bySku, bySalesCode };
};

const dimensionValue = (dimension: ProductDimension | undefined, key: SalesFactsDimension) => {
  if (!dimension) return '未分组';
  return safeDimensionName(dimension[key]);
};

const resolveDimensionName = (
  fact: SalesFact,
  lookup: ReturnType<typeof buildDimensionLookup>,
  dimension: SalesFactsDimension,
) => {
  const productDimension = lookup.bySku.get(fact.sku) ?? (fact.salesCode ? lookup.bySalesCode.get(fact.salesCode) : undefined);
  return dimensionValue(productDimension, dimension);
};

const filterFactsByTrendDimension = (
  salesFacts: SalesFact[],
  productDimensions: ProductDimension[],
  dimension: SalesFactsTrendDimension,
  dimensionValue?: string,
) => {
  if (dimension === 'total') return salesFacts;

  const lookup = buildDimensionLookup(productDimensions);
  return salesFacts.filter((fact) => resolveDimensionName(fact, lookup, dimension) === dimensionValue);
};

export const buildSalesFactsOverview = (
  salesFacts: SalesFact[],
  periodId: string,
  previousPeriodId?: string,
): SalesFactsOverview => {
  const current = periodAggregate(salesFacts, periodId);
  const previous = periodAggregate(salesFacts, previousPeriodId);
  const marketShareChange = current.marketShare != null && previous.marketShare != null
    ? current.marketShare - previous.marketShare
    : null;

  return {
    salesQty: current.salesQty,
    previousSalesQty: previous.salesQty,
    salesQtyChange: current.salesQty - previous.salesQty,
    salesQtyRate: calcRate(current.salesQty, previous.salesQty),
    salesAmount: current.salesAmount,
    previousSalesAmount: previous.salesAmount,
    salesAmountChange: current.salesAmount - previous.salesAmount,
    salesAmountRate: calcRate(current.salesAmount, previous.salesAmount),
    competitorOrders: current.competitorOrders,
    previousCompetitorOrders: previous.competitorOrders,
    marketShare: current.marketShare,
    previousMarketShare: previous.marketShare,
    marketShareChange,
    listingAvgPrice: current.listingAvgPrice,
    previousListingAvgPrice: previous.listingAvgPrice,
    listingAvgPriceRate: calcRate(current.listingAvgPrice, previous.listingAvgPrice),
    soldAvgPrice: current.soldAvgPrice,
    previousSoldAvgPrice: previous.soldAvgPrice,
    soldAvgPriceRate: calcRate(current.soldAvgPrice, previous.soldAvgPrice),
  };
};

export const buildSalesFactsDimensionRows = (
  salesFacts: SalesFact[],
  productDimensions: ProductDimension[],
  periodId: string,
  previousPeriodId: string | undefined,
  dimension: SalesFactsDimension,
): SalesFactsDimensionRow[] => {
  const lookup = buildDimensionLookup(productDimensions);
  const currentFacts = salesFacts.filter((fact) => fact.periodId === periodId);
  const previousFacts = previousPeriodId ? salesFacts.filter((fact) => fact.periodId === previousPeriodId) : [];
  const groups = new Map<string, { current: SalesFact[]; previous: SalesFact[] }>();

  currentFacts.forEach((fact) => {
    const name = resolveDimensionName(fact, lookup, dimension);
    const group = groups.get(name) ?? { current: [], previous: [] };
    group.current.push(fact);
    groups.set(name, group);
  });

  previousFacts.forEach((fact) => {
    const name = resolveDimensionName(fact, lookup, dimension);
    const group = groups.get(name) ?? { current: [], previous: [] };
    group.previous.push(fact);
    groups.set(name, group);
  });

  return [...groups.entries()]
    .filter(([dimensionName]) => !hiddenDimensionNames.has(dimensionName.trim()))
    .map(([dimensionName, group]) => {
      const current = periodAggregate(group.current, periodId);
      const previous = periodAggregate(group.previous, previousPeriodId);
      const marketShareChange = current.marketShare != null && previous.marketShare != null
        ? current.marketShare - previous.marketShare
        : null;

      return {
        dimensionName,
        skuCount: group.current.length,
        activeSkuCount: group.current.filter((fact) => fact.salesQty > 0).length,
        salesQty: current.salesQty,
        previousSalesQty: previous.salesQty,
        salesQtyChange: current.salesQty - previous.salesQty,
        salesQtyRate: calcRate(current.salesQty, previous.salesQty),
        salesAmount: current.salesAmount,
        previousSalesAmount: previous.salesAmount,
        salesAmountChange: current.salesAmount - previous.salesAmount,
        salesAmountRate: calcRate(current.salesAmount, previous.salesAmount),
        competitorOrders: current.competitorOrders,
        previousCompetitorOrders: previous.competitorOrders,
        marketShare: current.marketShare,
        previousMarketShare: previous.marketShare,
        marketShareChange,
        listingAvgPrice: current.listingAvgPrice,
        previousListingAvgPrice: previous.listingAvgPrice,
        listingAvgPriceRate: calcRate(current.listingAvgPrice, previous.listingAvgPrice),
        soldAvgPrice: current.soldAvgPrice,
        previousSoldAvgPrice: previous.soldAvgPrice,
        soldAvgPriceRate: calcRate(current.soldAvgPrice, previous.soldAvgPrice),
      };
    })
    .sort((a, b) => b.salesQty - a.salesQty);
};

export const buildSalesFactsTrendSeries = (
  salesFacts: SalesFact[],
  productDimensions: ProductDimension[],
  periods: UnifiedPeriod[],
  selectedPeriodId: string,
  dimension: SalesFactsTrendDimension,
  dimensionValue?: string,
): SalesFactsTrendPoint[] => {
  const selectedIndex = periods.findIndex((period) => period.id === selectedPeriodId);
  if (selectedIndex < 0) return [];

  const visiblePeriods = periods.slice(Math.max(0, selectedIndex - 7), selectedIndex + 1);
  const filteredFacts = filterFactsByTrendDimension(salesFacts, productDimensions, dimension, dimensionValue);

  return visiblePeriods.map((period) => {
    const total = periodAggregate(salesFacts, period.id);
    const current = periodAggregate(filteredFacts, period.id);
    const currentFacts = filteredFacts.filter((fact) => fact.periodId === period.id);

    return {
      periodId: period.id,
      periodLabel: period.label,
      salesQty: current.salesQty,
      salesAmount: current.salesAmount,
      competitorOrders: current.competitorOrders,
      marketShare: current.marketShare,
      listingAvgPrice: current.listingAvgPrice,
      soldAvgPrice: current.soldAvgPrice,
      skuCount: currentFacts.length,
      activeSkuCount: currentFacts.filter((fact) => fact.salesQty > 0).length,
      salesQtyShare: total.salesQty > 0 ? current.salesQty / total.salesQty : null,
      salesAmountShare: total.salesAmount > 0 ? current.salesAmount / total.salesAmount : null,
    };
  });
};
