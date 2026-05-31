import { modulePeriodConfig } from './periodConfig';
import {
  createBusinessPeriod,
  createPeriodForType,
  getPreviousBusinessPeriod,
  periodLabelFromIsoRange,
} from './periodParser';
import type { UnifiedPeriod, WeeklyReportContext } from './periodTypes';

const todayIso = () => new Date().toISOString().slice(0, 10);

const reportDateFromSalesPeriod = (salesPeriod?: UnifiedPeriod) =>
  salesPeriod?.reportDate ?? salesPeriod?.endDate ?? todayIso();

export const buildWeeklyReportContext = (salesPeriod?: UnifiedPeriod): WeeklyReportContext => {
  const reportDate = reportDateFromSalesPeriod(salesPeriod);
  const sales = salesPeriod ?? createPeriodForType('SALES_THU_TO_WED', reportDate, 'salesStatus');
  const newProducts = createBusinessPeriod({
    type: modulePeriodConfig.newProductStatus.periodType,
    startDate: sales.startDate,
    endDate: sales.endDate,
    reportDate,
    sourceModule: 'newProductStatus',
  });
  const ads = createPeriodForType(modulePeriodConfig.adsStatus.periodType, reportDate, 'adsStatus');
  const pricing = createPeriodForType(modulePeriodConfig.pricingStatus.periodType, reportDate, 'pricingStatus');
  const traffic = createPeriodForType(modulePeriodConfig.accountTrafficStatus.periodType, reportDate, 'accountTrafficStatus');
  const forecast = createPeriodForType(modulePeriodConfig.salesForecast.periodType, reportDate, 'salesForecast');

  return {
    reportId: `weekly-report-${reportDate}`,
    reportDate,
    reportLabel: `周报 ${reportDate}`,
    periods: {
      sales,
      newProducts,
      ads,
      pricing,
      traffic,
      forecast,
    },
  };
};

export const getComparablePeriod = (period: UnifiedPeriod) => getPreviousBusinessPeriod(period);

export const describeReportContext = (context: WeeklyReportContext) => ({
  reportId: context.reportId,
  reportDate: context.reportDate,
  reportLabel: context.reportLabel,
  periods: Object.fromEntries(
    Object.entries(context.periods).map(([key, period]) => [
      key,
      {
        type: period.type,
        label: periodLabelFromIsoRange(period),
      },
    ]),
  ),
});
