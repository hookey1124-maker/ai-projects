import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { ParseResult } from '../types/weeklyReport';
import { adaptSalesParseResult } from './adapters/salesAdapter';
import { getCurrentPeriod, getPreviousPeriod, getVisiblePeriods } from './periodEngine';
import { buildWeeklyReportContext } from './reportContext';
import type { DataSourceRegistry, DataCenterState } from './types';

type DataCenterContextValue = DataCenterState & {
  setSelectedPeriodId: (periodId: string | null) => void;
};

type DataCenterProviderProps = {
  children: ReactNode;
  salesParseResult?: ParseResult | null;
  selectedSourcePeriodIndex?: number;
};

const emptySources = (): DataSourceRegistry => ({
  sales: { status: 'notUploaded', warnings: [] },
  newProduct: { status: 'notUploaded', warnings: [] },
  ads: { status: 'notUploaded', warnings: [] },
  pricing: { status: 'notUploaded', warnings: [] },
  accountTraffic: { status: 'notUploaded', warnings: [] },
  salesForecast: { status: 'notUploaded', warnings: [] },
});

const emptyPeriods: DataCenterState['periods'] = [];

const DataCenterContext = createContext<DataCenterContextValue | null>(null);

export function DataCenterProvider({ children, salesParseResult, selectedSourcePeriodIndex }: DataCenterProviderProps) {
  const salesAdapterResult = useMemo(
    () => salesParseResult ? adaptSalesParseResult(salesParseResult) : null,
    [salesParseResult],
  );
  const periods = salesAdapterResult?.periods ?? emptyPeriods;
  const [selectedPeriodId, setSelectedPeriodId] = useState<string | null>(null);

  useEffect(() => {
    setSelectedPeriodId(
      selectedSourcePeriodIndex == null
        ? periods.at(-1)?.id ?? null
        : periods[selectedSourcePeriodIndex]?.id ?? periods.at(-1)?.id ?? null,
    );
  }, [periods, selectedSourcePeriodIndex]);

  const sources = useMemo<DataSourceRegistry>(() => {
    const next = emptySources();
    if (salesParseResult && salesAdapterResult) {
      next.sales = {
        status: 'loaded',
        warnings: salesAdapterResult.warnings,
        sourceName: salesParseResult.sourceName,
      };
    }
    return next;
  }, [salesAdapterResult, salesParseResult]);

  const value = useMemo<DataCenterContextValue>(() => {
    const currentPeriod = getCurrentPeriod(periods, selectedPeriodId);
    const previousPeriod = getPreviousPeriod(periods, selectedPeriodId);
    const visiblePeriods = getVisiblePeriods(periods, selectedPeriodId);
    const weeklyReportContext = buildWeeklyReportContext(currentPeriod);
    return {
      weeklyReportContext,
      periods,
      selectedPeriodId,
      currentPeriod,
      previousPeriod,
      visiblePeriods,
      productDimensions: salesAdapterResult?.productDimensions ?? [],
      salesFacts: salesAdapterResult?.salesFacts ?? [],
      baseSkuRecords: salesAdapterResult?.baseSkuRecords ?? [],
      warnings: sources.sales.warnings,
      sources,
      setSelectedPeriodId,
    };
  }, [periods, salesAdapterResult, selectedPeriodId, sources]);

  return <DataCenterContext.Provider value={value}>{children}</DataCenterContext.Provider>;
}

export const useDataCenter = () => {
  const context = useContext(DataCenterContext);
  if (!context) {
    throw new Error('useDataCenter must be used within DataCenterProvider');
  }
  return context;
};
