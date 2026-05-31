export type RawExcelRow = Record<string, unknown>;

export type FieldMap = {
  salesCode?: string;
  sku?: string;
  category?: string;
  tertiaryCategory?: string;
  analyst?: string;
  isLoss?: string;
  inventory?: string;
  sellableWeeks?: string;
  productGrade?: string;
  discontinued?: string;
};

export type WeeklyPeriod = {
  label: string;
  salesQtyColumn: string;
  salesAmountColumn?: string;
  marketShareColumn?: string;
  competitorColumn?: string;
  listingPriceColumn?: string;
  endDateLabel?: string;
  reportDateLabel?: string;
  marketShareDateLabel?: string;
  competitorDateLabel?: string;
  listingPriceDateLabel?: string;
};

export type ParseResult = {
  rows: RawExcelRow[];
  headers: string[];
  fields: FieldMap;
  periods: WeeklyPeriod[];
  warnings: string[];
  sourceName: string;
};

export type TrendDimension = '总盘' | '分析人' | '产品分类' | '产品等级' | '三级类目';
export type TableDimension = '总体' | '按分析人' | '按产品分类' | '按产品等级';

export type RateStatus = 'normal' | 'new' | 'none';

export type DimensionMetrics = {
  dimension: TableDimension | TrendDimension;
  dimensionName: string;
  skuCount: number;
  activeSkuCount: number;
  salesQty: number;
  prevSalesQty: number;
  salesQtyChange: number;
  salesQtyRate: number | null;
  salesQtyRateStatus: RateStatus;
  salesAmount: number;
  prevSalesAmount: number;
  salesAmountChange: number;
  salesAmountRate: number | null;
  salesAmountRateStatus: RateStatus;
  competitorOrders: number | null;
  prevCompetitorOrders: number | null;
  competitorRate: number | null;
  competitorRateStatus: RateStatus;
  marketShare: number | null;
  prevMarketShare: number | null;
  marketShareBpChange: number | null;
  listingAvgPrice: number | null;
  prevListingAvgPrice: number | null;
  listingAvgPriceRate: number | null;
  listingAvgPriceRateStatus: RateStatus;
  soldAvgPrice: number | null;
  prevSoldAvgPrice: number | null;
  soldAvgPriceRate: number | null;
  soldAvgPriceRateStatus: RateStatus;
  salesQtyShare?: number | null;
  salesAmountShare?: number | null;
  insightTags: string[];
  action: string;
};

export type TrendPoint = {
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

export type SortKey =
  | 'salesQty'
  | 'salesAmount'
  | 'salesQtyRate'
  | 'salesAmountRate'
  | 'marketShareBpChange';
