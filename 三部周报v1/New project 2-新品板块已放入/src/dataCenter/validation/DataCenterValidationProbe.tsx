import { useEffect, useMemo } from 'react';
import type { ParseResult, TableDimension, TrendDimension } from '../../types/weeklyReport';
import { aggregateByDimension, buildTrendSeries, getDimensionValues } from '../../utils/metrics';
import { useDataCenter } from '../DataCenterProvider';
import {
  buildSalesFactsDimensionRows,
  buildSalesFactsOverview,
  buildSalesFactsTrendSeries,
  compareSalesDimensionRows,
  compareSalesOverview,
  compareSalesTrendSeries,
  type SalesFactsDimension,
  type SalesFactsTrendDimension,
} from './salesFactsValidation';

type DataCenterValidationProbeProps = {
  parseResult: ParseResult | null;
};

type ViteImportMeta = ImportMeta & {
  env: {
    DEV: boolean;
  };
};

const validationPeriodIndexes = (periodCount: number) =>
  Array.from(new Set([periodCount - 1, periodCount - 2, periodCount - 3])).filter((index) => index >= 0);

const dimensionValidations: Array<{ label: string; tableDimension: TableDimension; factsDimension: SalesFactsDimension }> = [
  { label: '产品分类', tableDimension: '按产品分类', factsDimension: 'category' },
  { label: '产品等级', tableDimension: '按产品等级', factsDimension: 'productGrade' },
  { label: '分析人', tableDimension: '按分析人', factsDimension: 'analyst' },
];

const trendSamples: Array<{
  label: string;
  legacyDimension: TrendDimension;
  factsDimension: SalesFactsTrendDimension;
  values: string[];
}> = [
  { label: '总盘', legacyDimension: '总盘', factsDimension: 'total', values: ['全部'] },
  { label: '产品分类', legacyDimension: '产品分类', factsDimension: 'category', values: ['车身外扩件', '挡泥板', '车门系统'] },
  { label: '产品等级', legacyDimension: '产品等级', factsDimension: 'productGrade', values: ['A', 'B', 'C', 'D'] },
  { label: '分析人', legacyDimension: '分析人', factsDimension: 'analyst', values: ['张潇', '王偲涵', '俞东旭'] },
];

const trendValidationPeriodIndexes = (periodCount: number) =>
  Array.from(new Set([periodCount - 1, periodCount - 2])).filter((index) => index >= 0);

export default function DataCenterValidationProbe({ parseResult }: DataCenterValidationProbeProps) {
  const dataCenter = useDataCenter();
  const isDev = (import.meta as ViteImportMeta).env.DEV;

  const validationResults = useMemo(() => {
    if (!isDev || !parseResult?.periods.length || !dataCenter.salesFacts.length) return [];

    return validationPeriodIndexes(parseResult.periods.length).flatMap((sourcePeriodIndex) => {
      const period = dataCenter.periods.find((item) => item.sourcePeriodIndex === sourcePeriodIndex);
      if (!period) return [];

      const legacyOverview = aggregateByDimension(
        parseResult.rows,
        parseResult.fields,
        parseResult.periods,
        sourcePeriodIndex,
        '总体',
      )[0];
      const factsOverview = buildSalesFactsOverview(
        dataCenter.salesFacts,
        period.id,
        period.comparePeriodId,
      );
      const result = compareSalesOverview(legacyOverview, factsOverview);
      const dimensionResults = dimensionValidations.map(({ label, tableDimension, factsDimension }) => {
        const legacyRows = aggregateByDimension(
          parseResult.rows,
          parseResult.fields,
          parseResult.periods,
          sourcePeriodIndex,
          tableDimension,
        );
        const factsRows = buildSalesFactsDimensionRows(
          dataCenter.salesFacts,
          dataCenter.productDimensions,
          period.id,
          period.comparePeriodId,
          factsDimension,
        );
        const comparison = compareSalesDimensionRows(legacyRows, factsRows, label);

        return {
          dimension: label,
          passed: comparison.passed,
          differenceCount: comparison.differences.length,
          differences: comparison.differences,
        };
      });

      return [{
        periodLabel: period.label,
        overview: {
          passed: result.passed,
          differenceCount: result.differences.length,
          differences: result.differences.slice(0, 10),
        },
        dimensions: dimensionResults,
      }];
    });
  }, [dataCenter.periods, dataCenter.productDimensions, dataCenter.salesFacts, isDev, parseResult]);

  const trendValidationResults = useMemo(() => {
    if (!isDev || !parseResult?.periods.length || !dataCenter.salesFacts.length) return [];

    return trendValidationPeriodIndexes(parseResult.periods.length).flatMap((sourcePeriodIndex) => {
      const selectedPeriod = dataCenter.periods.find((period) => period.sourcePeriodIndex === sourcePeriodIndex);
      if (!selectedPeriod) return [];

      const chartPeriods = parseResult.periods.slice(Math.max(0, sourcePeriodIndex - 7), sourcePeriodIndex + 1);

      return trendSamples.flatMap((sample) => {
        const availableValues = sample.legacyDimension === '总盘'
          ? ['全部']
          : getDimensionValues(parseResult.rows, parseResult.fields, sample.legacyDimension);

        return sample.values.map((value) => {
          const sampleLabel = sample.legacyDimension === '总盘' ? sample.label : `${sample.label} / ${value}`;
          if (!availableValues.includes(value)) {
            return {
              selectedPeriodLabel: selectedPeriod.label,
              sample: sampleLabel,
              skipped: true,
              info: '样本不存在，已跳过',
              passed: true,
              differenceCount: 0,
              differences: [],
            };
          }

          const legacyTrend = buildTrendSeries(
            parseResult.rows,
            parseResult.fields,
            chartPeriods,
            sample.legacyDimension,
            value,
          );
          const factsTrend = buildSalesFactsTrendSeries(
            dataCenter.salesFacts,
            dataCenter.productDimensions,
            dataCenter.periods,
            selectedPeriod.id,
            sample.factsDimension,
            value,
          );
          const comparison = compareSalesTrendSeries(legacyTrend, factsTrend, sampleLabel);

          return {
            selectedPeriodLabel: selectedPeriod.label,
            sample: sampleLabel,
            skipped: false,
            passed: comparison.passed,
            differenceCount: comparison.differences.length,
            differences: comparison.differences,
          };
        });
      });
    });
  }, [dataCenter.periods, dataCenter.productDimensions, dataCenter.salesFacts, isDev, parseResult]);

  useEffect(() => {
    if (!isDev || !validationResults.length) return;

    const overviewPassed = validationResults.every((result) => result.overview.passed);
    console.info(`[DataCenter 校验] 总盘：${overviewPassed ? '通过' : '存在差异'}`, {
      checkedPeriods: validationResults.map((result) => result.periodLabel),
      results: validationResults.map((result) => ({
        period: result.periodLabel,
        ...result.overview,
      })),
    });

    dimensionValidations.forEach(({ label }) => {
      const results = validationResults.map((periodResult) => {
        const dimensionResult = periodResult.dimensions.find((item) => item.dimension === label);
        return {
          period: periodResult.periodLabel,
          passed: dimensionResult?.passed ?? false,
          differenceCount: dimensionResult?.differenceCount ?? 0,
          differences: dimensionResult?.differences ?? [],
        };
      });
      const passed = results.every((result) => result.passed);
      const differenceCount = results.reduce((sum, result) => sum + result.differenceCount, 0);

      console.info(`[DataCenter 校验] ${label}：${passed ? '通过' : '存在差异'}，差异 ${differenceCount}`, {
        checkedPeriods: results.map((result) => result.period),
        results,
      });
    });
  }, [isDev, validationResults]);

  useEffect(() => {
    if (!isDev || !trendValidationResults.length) return;

    trendValidationResults.forEach((result) => {
      if (result.skipped) {
        console.info(`[DataCenter 趋势校验] ${result.sample}：跳过`, {
          selectedPeriod: result.selectedPeriodLabel,
          info: result.info,
        });
        return;
      }

      console.info(`[DataCenter 趋势校验] ${result.sample}：${result.passed ? '通过' : '存在差异'}，差异 ${result.differenceCount}`, {
        selectedPeriod: result.selectedPeriodLabel,
        differences: result.differences,
      });
    });
  }, [isDev, trendValidationResults]);

  return null;
}
