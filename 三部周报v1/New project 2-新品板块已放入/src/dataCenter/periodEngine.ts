import type { WeeklyPeriod } from '../types/weeklyReport';
import type { PeriodType, UnifiedPeriod } from './periodTypes';

const priceDatePattern = /^(\d{4})\/(\d{1,2})\/(\d{1,2})在售价$/;

const pad = (value: number) => String(value).padStart(2, '0');

const toIsoDate = (year: number, month: number, day: number) => `${year}-${pad(month)}-${pad(day)}`;

const inferYear = (periods: WeeklyPeriod[]) => {
  for (const period of periods) {
    const match = period.listingPriceColumn?.match(priceDatePattern);
    if (match) return Number(match[1]);
  }
  return new Date().getFullYear();
};

const parseMonthDay = (value: string) => {
  const [month, day] = value.split('/').map(Number);
  return { month, day };
};

const periodDates = (label: string, defaultYear: number) => {
  const [startLabel, endLabel] = label.split('-');
  const start = parseMonthDay(startLabel);
  const end = parseMonthDay(endLabel);
  const endYear = end.month < start.month ? defaultYear + 1 : defaultYear;
  const startYear = end.month < start.month ? defaultYear : endYear;

  return {
    startDate: toIsoDate(startYear, start.month, start.day),
    endDate: toIsoDate(endYear, end.month, end.day),
  };
};

const reportDate = (period: WeeklyPeriod, fallbackYear: number) => {
  if (!period.reportDateLabel) return undefined;
  const { month, day } = parseMonthDay(period.reportDateLabel);
  return toIsoDate(fallbackYear, month, day);
};

export const convertWeeklyPeriodsToUnifiedPeriods = (
  periods: WeeklyPeriod[],
  periodType: PeriodType = 'SALES_THU_TO_WED',
  sourceModule = 'salesStatus',
): UnifiedPeriod[] => {
  const defaultYear = inferYear(periods);
  return periods.map((period, index) => {
    const dates = periodDates(period.label, defaultYear);
    return {
      id: `period-${index}-${period.label}`,
      type: periodType,
      label: period.label,
      startDate: dates.startDate,
      endDate: dates.endDate,
      reportDate: reportDate(period, Number(dates.endDate.slice(0, 4))),
      sourceModule,
      comparePeriodId: index > 0 ? `period-${index - 1}-${periods[index - 1].label}` : undefined,
      sourcePeriodIndex: index,
    };
  });
};

export const getCurrentPeriod = (periods: UnifiedPeriod[], selectedPeriodId: string | null) =>
  periods.find((period) => period.id === selectedPeriodId);

export const getPreviousPeriod = (periods: UnifiedPeriod[], selectedPeriodId: string | null) => {
  const currentIndex = periods.findIndex((period) => period.id === selectedPeriodId);
  return currentIndex > 0 ? periods[currentIndex - 1] : undefined;
};

export const getVisiblePeriods = (periods: UnifiedPeriod[], selectedPeriodId: string | null, limit = 8) => {
  const currentIndex = periods.findIndex((period) => period.id === selectedPeriodId);
  if (currentIndex < 0) return [];
  return periods.slice(Math.max(0, currentIndex - limit + 1), currentIndex + 1);
};
