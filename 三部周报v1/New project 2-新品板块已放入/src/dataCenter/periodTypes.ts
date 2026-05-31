export type PeriodType =
  | 'SALES_THU_TO_WED'
  | 'NATURAL_WEEK_MON_TO_SUN'
  | 'DATE_SNAPSHOT'
  | 'MONTHLY'
  | 'FORECAST_WEEK';

export interface UnifiedPeriod {
  id: string;
  type: PeriodType;
  label: string;
  startDate: string;
  endDate: string;
  reportDate?: string;
  sourceModule?: string;
  comparePeriodId?: string;
  sourcePeriodIndex?: number;
}

export interface WeeklyReportContext {
  reportId: string;
  reportDate: string;
  reportLabel: string;
  periods: {
    sales: UnifiedPeriod;
    newProducts: UnifiedPeriod;
    ads: UnifiedPeriod;
    pricing: UnifiedPeriod;
    traffic: UnifiedPeriod;
    forecast: UnifiedPeriod;
  };
}
