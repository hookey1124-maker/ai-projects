import type { DataSourceKind, ModuleKey } from './types';
import type { PeriodType } from './periodTypes';

export type ReportPeriodKey = 'sales' | 'newProducts' | 'ads' | 'pricing' | 'traffic' | 'forecast';

export type ModulePeriodConfig = {
  moduleKey: ModuleKey;
  reportPeriodKey: ReportPeriodKey;
  dataSourceKind: DataSourceKind;
  periodType: PeriodType;
  periodTypeLabel: string;
};

export const periodTypeLabels: Record<PeriodType, string> = {
  SALES_THU_TO_WED: '周四至周三',
  NATURAL_WEEK_MON_TO_SUN: '自然周，周一至周日',
  DATE_SNAPSHOT: '日期快照',
  MONTHLY: '自然月',
  FORECAST_WEEK: '预测周',
};

export const modulePeriodConfig: Record<ModuleKey, ModulePeriodConfig> = {
  salesStatus: {
    moduleKey: 'salesStatus',
    reportPeriodKey: 'sales',
    dataSourceKind: 'sales',
    periodType: 'SALES_THU_TO_WED',
    periodTypeLabel: periodTypeLabels.SALES_THU_TO_WED,
  },
  newProductStatus: {
    moduleKey: 'newProductStatus',
    reportPeriodKey: 'newProducts',
    dataSourceKind: 'newProduct',
    periodType: 'SALES_THU_TO_WED',
    periodTypeLabel: periodTypeLabels.SALES_THU_TO_WED,
  },
  adsStatus: {
    moduleKey: 'adsStatus',
    reportPeriodKey: 'ads',
    dataSourceKind: 'ads',
    periodType: 'NATURAL_WEEK_MON_TO_SUN',
    periodTypeLabel: periodTypeLabels.NATURAL_WEEK_MON_TO_SUN,
  },
  pricingStatus: {
    moduleKey: 'pricingStatus',
    reportPeriodKey: 'pricing',
    dataSourceKind: 'pricing',
    periodType: 'DATE_SNAPSHOT',
    periodTypeLabel: periodTypeLabels.DATE_SNAPSHOT,
  },
  accountTrafficStatus: {
    moduleKey: 'accountTrafficStatus',
    reportPeriodKey: 'traffic',
    dataSourceKind: 'accountTraffic',
    periodType: 'NATURAL_WEEK_MON_TO_SUN',
    periodTypeLabel: periodTypeLabels.NATURAL_WEEK_MON_TO_SUN,
  },
  salesForecast: {
    moduleKey: 'salesForecast',
    reportPeriodKey: 'forecast',
    dataSourceKind: 'salesForecast',
    periodType: 'FORECAST_WEEK',
    periodTypeLabel: periodTypeLabels.FORECAST_WEEK,
  },
};
