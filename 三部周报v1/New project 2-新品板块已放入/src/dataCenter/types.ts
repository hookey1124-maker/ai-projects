import type { UnifiedPeriod, WeeklyReportContext } from './periodTypes';

export type ModuleKey =
  | 'salesStatus'
  | 'newProductStatus'
  | 'adsStatus'
  | 'pricingStatus'
  | 'accountTrafficStatus'
  | 'salesForecast';

export type DataSourceStatus = 'notUploaded' | 'loaded' | 'error';

export type DataSourceKind = 'sales' | 'newProduct' | 'ads' | 'pricing' | 'accountTraffic' | 'salesForecast';

export type RiskLevel = 'low' | 'medium' | 'high' | 'unknown';

export type DataCenterWarning = {
  id: string;
  source: DataSourceKind;
  message: string;
  severity: 'info' | 'warning' | 'error';
  periodId?: string;
  sourcePeriodIndex?: number;
};

export type { PeriodType, UnifiedPeriod, WeeklyReportContext } from './periodTypes';

export type ProductDimension = {
  sku: string;
  salesCode?: string;
  category?: string;
  tertiaryCategory?: string;
  analyst?: string;
  productGrade?: string;
  isLoss?: string;
  inventory?: string | number;
  sellableWeeks?: string | number;
  discontinued?: string;
};

export type SalesFact = {
  periodId: string;
  sourcePeriodIndex: number;
  sku: string;
  salesCode?: string;
  salesQty: number;
  salesAmount: number;
  competitorOrders: number | null;
  marketShare: number | null;
  listingPrice: number | null;
  soldAvgPrice: number | null;
  rawRowIndex: number;
};

export type BaseSkuRecord = {
  sku: string;
  productName: string;
  analyst: string;
  category: string;
  productGrade: string;
  sales: number;
  revenue: number;
  marketShare: number | null;
  currentPrice: number | null;
  avgOrderPrice: number | null;
  periodId: string;
};

export type ModuleStatusSummary = {
  moduleKey: ModuleKey;
  moduleName: string;
  currentStatus: string;
  riskLevel: RiskLevel;
  coreMetrics: Array<{
    label: string;
    value: string | number;
    unit?: string;
    description?: string;
  }>;
  mainFindings: string[];
  nextActions: string[];
};

export type SalesAdapterResult = {
  periods: UnifiedPeriod[];
  productDimensions: ProductDimension[];
  salesFacts: SalesFact[];
  baseSkuRecords: BaseSkuRecord[];
  warnings: DataCenterWarning[];
};

export type DataSourceState = {
  status: DataSourceStatus;
  warnings: DataCenterWarning[];
  sourceName?: string;
};

export type DataSourceRegistry = Record<DataSourceKind, DataSourceState>;

export type DataCenterSources = DataSourceRegistry;

export type DataCenterState = {
  weeklyReportContext: WeeklyReportContext;
  periods: UnifiedPeriod[];
  selectedPeriodId: string | null;
  currentPeriod?: UnifiedPeriod;
  previousPeriod?: UnifiedPeriod;
  visiblePeriods: UnifiedPeriod[];
  productDimensions: ProductDimension[];
  salesFacts: SalesFact[];
  baseSkuRecords: BaseSkuRecord[];
  warnings: DataCenterWarning[];
  sources: DataSourceRegistry;
};
