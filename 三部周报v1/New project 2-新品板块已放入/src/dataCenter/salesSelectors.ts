import {
  buildSalesFactsDimensionRows,
  buildSalesFactsOverview,
  buildSalesFactsTrendSeries,
  type SalesFactsDimension,
  type SalesFactsDimensionRow,
  type SalesFactsOverview,
  type SalesFactsTrendDimension,
  type SalesFactsTrendPoint,
} from './metrics/salesFactsMetrics';
import type { DataCenterState, DataSourceState, ProductDimension, SalesFact, UnifiedPeriod } from './types';

export type SalesSourceStatus = DataSourceState & {
  rowCount: number;
  periodCount: number;
  warningCount: number;
};

export const selectSalesOverviewFromFacts = (
  salesFacts: SalesFact[],
  selectedPeriodId: string,
  previousPeriodId?: string,
): SalesFactsOverview => buildSalesFactsOverview(salesFacts, selectedPeriodId, previousPeriodId);

export const selectSalesOverview = (state: DataCenterState): SalesFactsOverview | null => {
  if (!state.selectedPeriodId) return null;
  return selectSalesOverviewFromFacts(
    state.salesFacts,
    state.selectedPeriodId,
    state.previousPeriod?.id,
  );
};

export const selectSalesDimensionRowsFromFacts = (
  salesFacts: SalesFact[],
  productDimensions: ProductDimension[],
  selectedPeriodId: string,
  previousPeriodId: string | undefined,
  dimension: SalesFactsDimension,
): SalesFactsDimensionRow[] => buildSalesFactsDimensionRows(
  salesFacts,
  productDimensions,
  selectedPeriodId,
  previousPeriodId,
  dimension,
);

export const selectSalesDimensionRows = (
  state: DataCenterState,
  dimension: SalesFactsDimension,
): SalesFactsDimensionRow[] => {
  if (!state.selectedPeriodId) return [];
  return selectSalesDimensionRowsFromFacts(
    state.salesFacts,
    state.productDimensions,
    state.selectedPeriodId,
    state.previousPeriod?.id,
    dimension,
  );
};

export const selectSalesTrendSeriesFromFacts = (
  salesFacts: SalesFact[],
  productDimensions: ProductDimension[],
  periods: UnifiedPeriod[],
  selectedPeriodId: string,
  dimension: SalesFactsTrendDimension,
  dimensionValue?: string,
): SalesFactsTrendPoint[] => buildSalesFactsTrendSeries(
  salesFacts,
  productDimensions,
  periods,
  selectedPeriodId,
  dimension,
  dimensionValue,
);

export const selectSalesTrendSeries = (
  state: DataCenterState,
  dimension: SalesFactsTrendDimension,
  dimensionValue?: string,
): SalesFactsTrendPoint[] => {
  if (!state.selectedPeriodId) return [];
  return selectSalesTrendSeriesFromFacts(
    state.salesFacts,
    state.productDimensions,
    state.periods,
    state.selectedPeriodId,
    dimension,
    dimensionValue,
  );
};

export const selectSalesSourceStatus = (state: DataCenterState): SalesSourceStatus => {
  const source = state.sources.sales;
  return {
    ...source,
    rowCount: state.productDimensions.length,
    periodCount: state.periods.length,
    warningCount: source.warnings.length,
    sourceName: source.sourceName,
  };
};
