import type { FieldMap, ParseResult, RawExcelRow } from '../../types/weeklyReport';
import { modulePeriodConfig } from '../periodConfig';
import { convertWeeklyPeriodsToUnifiedPeriods } from '../periodEngine';
import type { BaseSkuRecord, DataCenterWarning, ProductDimension, SalesAdapterResult, SalesFact, UnifiedPeriod } from '../types';

const toNumber = (value: unknown, fallback = 0) => {
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

const readField = (row: RawExcelRow, field?: string) => {
  if (!field) return undefined;
  const value = row[field];
  return value == null || value === '' ? undefined : value;
};

const toStringField = (value: unknown) => (value == null ? undefined : String(value));

const buildProductDimensions = (rows: RawExcelRow[], fields: FieldMap): ProductDimension[] =>
  rows.flatMap((row) => {
    const sku = toStringField(readField(row, fields.sku));
    const salesCode = toStringField(readField(row, fields.salesCode));
    if (!sku && !salesCode) return [];
    return [{
      sku: sku ?? '',
      salesCode,
      category: toStringField(readField(row, fields.category)),
      tertiaryCategory: toStringField(readField(row, fields.tertiaryCategory)),
      analyst: toStringField(readField(row, fields.analyst)),
      productGrade: toStringField(readField(row, fields.productGrade)),
      isLoss: toStringField(readField(row, fields.isLoss)),
      inventory: readField(row, fields.inventory) as string | number | undefined,
      sellableWeeks: readField(row, fields.sellableWeeks) as string | number | undefined,
      discontinued: toStringField(readField(row, fields.discontinued)),
    }];
  });

const buildProductDimensionLookup = (productDimensions: ProductDimension[]) => {
  const bySku = new Map<string, ProductDimension>();
  const bySalesCode = new Map<string, ProductDimension>();

  productDimensions.forEach((dimension) => {
    if (dimension.sku && !bySku.has(dimension.sku)) bySku.set(dimension.sku, dimension);
    if (dimension.salesCode && !bySalesCode.has(dimension.salesCode)) bySalesCode.set(dimension.salesCode, dimension);
  });

  return { bySku, bySalesCode };
};

const buildWarnings = (messages: string[], periods: UnifiedPeriod[]): DataCenterWarning[] =>
  messages.map((message, index) => {
    const matchedPeriod = periods.find((period) => message.includes(period.label));
    return {
      id: `sales-warning-${index}`,
      source: 'sales',
      message,
      severity: message.includes('未找到') || message.includes('未识别到') ? 'error' : 'warning',
      periodId: matchedPeriod?.id,
      sourcePeriodIndex: matchedPeriod?.sourcePeriodIndex,
    };
  });

const buildSalesFacts = (parseResult: ParseResult, periods: UnifiedPeriod[]): SalesFact[] =>
  parseResult.rows.flatMap((row, rawRowIndex) => {
    const sku = toStringField(readField(row, parseResult.fields.sku)) ?? '';
    const salesCode = toStringField(readField(row, parseResult.fields.salesCode));

    return parseResult.periods.map((period, sourcePeriodIndex) => {
      const unifiedPeriod = periods[sourcePeriodIndex];
      const salesQty = toNumber(row[period.salesQtyColumn]);
      const salesAmount = period.salesAmountColumn ? toNumber(row[period.salesAmountColumn]) : 0;
      const competitorOrders = period.competitorColumn ? toNumber(row[period.competitorColumn]) : null;
      const denominator = competitorOrders == null ? null : salesQty + competitorOrders;
      const marketShare = denominator != null && denominator > 0 ? salesQty / denominator : null;
      const listingPrice = period.listingPriceColumn ? toListingPrice(row[period.listingPriceColumn]) : null;
      const soldAvgPrice = salesQty > 0 ? salesAmount / salesQty : null;

      return {
        periodId: unifiedPeriod.id,
        sourcePeriodIndex,
        sku,
        salesCode,
        salesQty,
        salesAmount,
        competitorOrders,
        marketShare,
        listingPrice,
        soldAvgPrice,
        rawRowIndex,
      };
    });
  });

const buildBaseSkuRecords = (salesFacts: SalesFact[], productDimensions: ProductDimension[]): BaseSkuRecord[] => {
  const lookup = buildProductDimensionLookup(productDimensions);

  return salesFacts.map((fact) => {
    const dimension = lookup.bySku.get(fact.sku) ?? (fact.salesCode ? lookup.bySalesCode.get(fact.salesCode) : undefined);
    const sku = fact.sku || fact.salesCode || '';

    return {
      sku,
      productName: '',
      analyst: dimension?.analyst ?? '未分组',
      category: dimension?.category ?? '未分组',
      productGrade: dimension?.productGrade ?? '未分组',
      sales: fact.salesQty,
      revenue: fact.salesAmount,
      marketShare: fact.marketShare,
      currentPrice: fact.listingPrice,
      avgOrderPrice: fact.soldAvgPrice,
      periodId: fact.periodId,
    };
  });
};

export const adaptSalesParseResult = (parseResult: ParseResult): SalesAdapterResult => {
  const periods = convertWeeklyPeriodsToUnifiedPeriods(
    parseResult.periods,
    modulePeriodConfig.salesStatus.periodType,
    modulePeriodConfig.salesStatus.moduleKey,
  );
  const productDimensions = buildProductDimensions(parseResult.rows, parseResult.fields);
  const salesFacts = buildSalesFacts(parseResult, periods);

  return {
    periods,
    productDimensions,
    salesFacts,
    baseSkuRecords: buildBaseSkuRecords(salesFacts, productDimensions),
    warnings: buildWarnings(parseResult.warnings, periods),
  };
};
