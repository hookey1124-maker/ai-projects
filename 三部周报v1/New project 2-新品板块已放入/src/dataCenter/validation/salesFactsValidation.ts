import {
  buildSalesFactsDimensionRows,
  buildSalesFactsOverview,
  buildSalesFactsTrendSeries,
  type SalesFactsDimension,
  type SalesFactsDimensionRow,
  type SalesFactsOverview,
  type SalesFactsTrendDimension,
  type SalesFactsTrendPoint,
} from '../metrics/salesFactsMetrics';

export {
  buildSalesFactsDimensionRows,
  buildSalesFactsOverview,
  buildSalesFactsTrendSeries,
};

export type {
  SalesFactsDimension,
  SalesFactsDimensionRow,
  SalesFactsOverview,
  SalesFactsTrendDimension,
  SalesFactsTrendPoint,
};

export type SalesValidationDifference = {
  metric: string;
  legacyValue: number | null;
  factsValue: number | null;
  diff: number | null;
  tolerance: number;
  level: 'info' | 'warning' | 'error';
};

export type SalesValidationResult = {
  passed: boolean;
  differences: SalesValidationDifference[];
};

const integerTolerance = 0.01;
const moneyTolerance = 0.01;
const rateTolerance = 0.0001;
const maxDifferences = 20;

const toNumberOrNull = (value: unknown) => (typeof value === 'number' && Number.isFinite(value) ? value : null);

const differenceLevel = (metric: string): SalesValidationDifference['level'] =>
  metric.includes('Rate') || metric.includes('marketShare') ? 'warning' : 'error';

const compareMetric = (
  differences: SalesValidationDifference[],
  metric: string,
  legacyValue: unknown,
  factsValue: number | null,
  tolerance: number,
  level?: SalesValidationDifference['level'],
) => {
  if (differences.length >= maxDifferences) return;
  const legacyNumber = toNumberOrNull(legacyValue);
  const valuesMatch =
    legacyNumber == null && factsValue == null
      ? true
      : legacyNumber != null && factsValue != null && Math.abs(legacyNumber - factsValue) <= tolerance;
  if (valuesMatch) return;

  differences.push({
    metric,
    legacyValue: legacyNumber,
    factsValue,
    diff: legacyNumber != null && factsValue != null ? factsValue - legacyNumber : null,
    tolerance,
    level: level ?? differenceLevel(metric),
  });
};

export const compareSalesOverview = (
  legacyOverview: any,
  factsOverview: SalesFactsOverview,
): SalesValidationResult => {
  const differences: SalesValidationDifference[] = [];

  compareMetric(differences, 'salesQty', legacyOverview?.salesQty, factsOverview.salesQty, integerTolerance);
  compareMetric(differences, 'previousSalesQty', legacyOverview?.prevSalesQty, factsOverview.previousSalesQty, integerTolerance);
  compareMetric(differences, 'salesQtyChange', legacyOverview?.salesQtyChange, factsOverview.salesQtyChange, integerTolerance);
  compareMetric(differences, 'salesQtyRate', legacyOverview?.salesQtyRate, factsOverview.salesQtyRate, rateTolerance);
  compareMetric(differences, 'salesAmount', legacyOverview?.salesAmount, factsOverview.salesAmount, moneyTolerance);
  compareMetric(differences, 'previousSalesAmount', legacyOverview?.prevSalesAmount, factsOverview.previousSalesAmount, moneyTolerance);
  compareMetric(differences, 'salesAmountChange', legacyOverview?.salesAmountChange, factsOverview.salesAmountChange, moneyTolerance);
  compareMetric(differences, 'salesAmountRate', legacyOverview?.salesAmountRate, factsOverview.salesAmountRate, rateTolerance);
  compareMetric(differences, 'competitorOrders', legacyOverview?.competitorOrders, factsOverview.competitorOrders, integerTolerance);
  compareMetric(differences, 'previousCompetitorOrders', legacyOverview?.prevCompetitorOrders, factsOverview.previousCompetitorOrders, integerTolerance);
  compareMetric(differences, 'marketShare', legacyOverview?.marketShare, factsOverview.marketShare, rateTolerance);
  compareMetric(differences, 'previousMarketShare', legacyOverview?.prevMarketShare, factsOverview.previousMarketShare, rateTolerance);
  compareMetric(differences, 'marketShareChange', legacyOverview?.marketShareBpChange, factsOverview.marketShareChange == null ? null : factsOverview.marketShareChange * 10000, rateTolerance);
  compareMetric(differences, 'listingAvgPrice', legacyOverview?.listingAvgPrice, factsOverview.listingAvgPrice, moneyTolerance);
  compareMetric(differences, 'previousListingAvgPrice', legacyOverview?.prevListingAvgPrice, factsOverview.previousListingAvgPrice, moneyTolerance);
  compareMetric(differences, 'listingAvgPriceRate', legacyOverview?.listingAvgPriceRate, factsOverview.listingAvgPriceRate, rateTolerance);
  compareMetric(differences, 'soldAvgPrice', legacyOverview?.soldAvgPrice, factsOverview.soldAvgPrice, moneyTolerance);
  compareMetric(differences, 'previousSoldAvgPrice', legacyOverview?.prevSoldAvgPrice, factsOverview.previousSoldAvgPrice, moneyTolerance);
  compareMetric(differences, 'soldAvgPriceRate', legacyOverview?.soldAvgPriceRate, factsOverview.soldAvgPriceRate, rateTolerance);

  return {
    passed: differences.length === 0,
    differences,
  };
};

const compareRowMetrics = (
  differences: SalesValidationDifference[],
  metricPrefix: string,
  legacyRow: any,
  factsRow: SalesFactsDimensionRow,
) => {
  compareMetric(differences, `${metricPrefix}.skuCount`, legacyRow?.skuCount, factsRow.skuCount, integerTolerance);
  compareMetric(differences, `${metricPrefix}.activeSkuCount`, legacyRow?.activeSkuCount, factsRow.activeSkuCount, integerTolerance);
  compareMetric(differences, `${metricPrefix}.salesQty`, legacyRow?.salesQty, factsRow.salesQty, integerTolerance);
  compareMetric(differences, `${metricPrefix}.previousSalesQty`, legacyRow?.prevSalesQty, factsRow.previousSalesQty, integerTolerance);
  compareMetric(differences, `${metricPrefix}.salesQtyChange`, legacyRow?.salesQtyChange, factsRow.salesQtyChange, integerTolerance);
  compareMetric(differences, `${metricPrefix}.salesQtyRate`, legacyRow?.salesQtyRate, factsRow.salesQtyRate, rateTolerance);
  compareMetric(differences, `${metricPrefix}.salesAmount`, legacyRow?.salesAmount, factsRow.salesAmount, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.previousSalesAmount`, legacyRow?.prevSalesAmount, factsRow.previousSalesAmount, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.salesAmountChange`, legacyRow?.salesAmountChange, factsRow.salesAmountChange, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.salesAmountRate`, legacyRow?.salesAmountRate, factsRow.salesAmountRate, rateTolerance);
  compareMetric(differences, `${metricPrefix}.competitorOrders`, legacyRow?.competitorOrders, factsRow.competitorOrders, integerTolerance);
  compareMetric(differences, `${metricPrefix}.previousCompetitorOrders`, legacyRow?.prevCompetitorOrders, factsRow.previousCompetitorOrders, integerTolerance);
  compareMetric(differences, `${metricPrefix}.marketShare`, legacyRow?.marketShare, factsRow.marketShare, rateTolerance);
  compareMetric(differences, `${metricPrefix}.previousMarketShare`, legacyRow?.prevMarketShare, factsRow.previousMarketShare, rateTolerance);
  compareMetric(differences, `${metricPrefix}.marketShareChange`, legacyRow?.marketShareBpChange, factsRow.marketShareChange == null ? null : factsRow.marketShareChange * 10000, rateTolerance);
  compareMetric(differences, `${metricPrefix}.listingAvgPrice`, legacyRow?.listingAvgPrice, factsRow.listingAvgPrice, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.previousListingAvgPrice`, legacyRow?.prevListingAvgPrice, factsRow.previousListingAvgPrice, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.listingAvgPriceRate`, legacyRow?.listingAvgPriceRate, factsRow.listingAvgPriceRate, rateTolerance);
  compareMetric(differences, `${metricPrefix}.soldAvgPrice`, legacyRow?.soldAvgPrice, factsRow.soldAvgPrice, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.previousSoldAvgPrice`, legacyRow?.prevSoldAvgPrice, factsRow.previousSoldAvgPrice, moneyTolerance);
  compareMetric(differences, `${metricPrefix}.soldAvgPriceRate`, legacyRow?.soldAvgPriceRate, factsRow.soldAvgPriceRate, rateTolerance);
};

export const compareSalesDimensionRows = (
  legacyRows: any[],
  factsRows: SalesFactsDimensionRow[],
  dimension: string,
): SalesValidationResult => {
  const differences: SalesValidationDifference[] = [];
  const legacyByName = new Map(legacyRows.map((row) => [String(row.dimensionName), row]));
  const factsByName = new Map(factsRows.map((row) => [row.dimensionName, row]));
  const names = new Set([...legacyByName.keys(), ...factsByName.keys()]);

  for (const name of names) {
    if (differences.length >= maxDifferences) break;
    const legacyRow = legacyByName.get(name);
    const factsRow = factsByName.get(name);
    const metricPrefix = `${dimension}.${name}`;

    if (!legacyRow && factsRow) {
      differences.push({
        metric: `${metricPrefix}.row`,
        legacyValue: null,
        factsValue: null,
        diff: null,
        tolerance: 0,
        level: 'warning',
      });
      continue;
    }

    if (legacyRow && !factsRow) {
      differences.push({
        metric: `${metricPrefix}.row`,
        legacyValue: null,
        factsValue: null,
        diff: null,
        tolerance: 0,
        level: 'error',
      });
      continue;
    }

    if (legacyRow && factsRow) {
      compareRowMetrics(differences, metricPrefix, legacyRow, factsRow);
    }
  }

  return {
    passed: differences.length === 0,
    differences,
  };
};

export const compareSalesTrendSeries = (
  legacyTrend: any[],
  factsTrend: SalesFactsTrendPoint[],
  label: string,
): SalesValidationResult => {
  const differences: SalesValidationDifference[] = [];
  const legacyByPeriod = new Map(legacyTrend.map((point) => [String(point.periodLabel), point]));
  const factsByPeriod = new Map(factsTrend.map((point) => [point.periodLabel, point]));
  const periodLabels = new Set([...legacyByPeriod.keys(), ...factsByPeriod.keys()]);

  for (const periodLabel of periodLabels) {
    if (differences.length >= maxDifferences) break;
    const legacyPoint = legacyByPeriod.get(periodLabel);
    const factsPoint = factsByPeriod.get(periodLabel);
    const metricPrefix = `${label}.${periodLabel}`;

    if (!legacyPoint && factsPoint) {
      differences.push({
        metric: `${metricPrefix}.point`,
        legacyValue: null,
        factsValue: null,
        diff: null,
        tolerance: 0,
        level: 'warning',
      });
      continue;
    }

    if (legacyPoint && !factsPoint) {
      differences.push({
        metric: `${metricPrefix}.point`,
        legacyValue: null,
        factsValue: null,
        diff: null,
        tolerance: 0,
        level: 'error',
      });
      continue;
    }

    if (!legacyPoint || !factsPoint) continue;

    compareMetric(differences, `${metricPrefix}.salesQty`, legacyPoint.salesQty, factsPoint.salesQty, integerTolerance);
    compareMetric(differences, `${metricPrefix}.salesAmount`, legacyPoint.salesAmount, factsPoint.salesAmount, moneyTolerance);
    compareMetric(differences, `${metricPrefix}.competitorOrders`, legacyPoint.competitorOrders, factsPoint.competitorOrders, integerTolerance);
    compareMetric(differences, `${metricPrefix}.marketShare`, legacyPoint.marketShare, factsPoint.marketShare, rateTolerance);
    compareMetric(differences, `${metricPrefix}.listingAvgPrice`, legacyPoint.listingAvgPrice, factsPoint.listingAvgPrice, moneyTolerance);
    compareMetric(differences, `${metricPrefix}.soldAvgPrice`, legacyPoint.soldAvgPrice, factsPoint.soldAvgPrice, moneyTolerance);
    compareMetric(differences, `${metricPrefix}.skuCount`, legacyPoint.skuCount, factsPoint.skuCount, integerTolerance);
    compareMetric(differences, `${metricPrefix}.activeSkuCount`, legacyPoint.activeSkuCount, factsPoint.activeSkuCount, integerTolerance);
    compareMetric(differences, `${metricPrefix}.salesQtyShare`, legacyPoint.salesQtyShare, factsPoint.salesQtyShare, rateTolerance);
    compareMetric(differences, `${metricPrefix}.salesAmountShare`, legacyPoint.salesAmountShare, factsPoint.salesAmountShare, rateTolerance);
  }

  return {
    passed: differences.length === 0,
    differences,
  };
};
