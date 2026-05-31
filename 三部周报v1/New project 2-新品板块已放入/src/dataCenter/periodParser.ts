export {
  convertWeeklyPeriodsToUnifiedPeriods,
  getCurrentPeriod,
  getPreviousPeriod,
  getVisiblePeriods,
} from './periodEngine';

import type { PeriodType, UnifiedPeriod } from './periodTypes';

const oneDayMs = 24 * 60 * 60 * 1000;

const pad = (value: number) => String(value).padStart(2, '0');

const toIsoDate = (date: Date) =>
  `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`;

const fromIsoDate = (value: string) => {
  const [year, month, day] = value.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day));
};

const addDays = (value: string, days: number) => toIsoDate(new Date(fromIsoDate(value).getTime() + days * oneDayMs));

const dayOfWeek = (value: string) => fromIsoDate(value).getUTCDay();

const mondayOfWeek = (value: string) => {
  const day = dayOfWeek(value);
  const offset = day === 0 ? -6 : 1 - day;
  return addDays(value, offset);
};

const thursdayOfSalesWeek = (value: string) => {
  const day = dayOfWeek(value);
  const offset = day >= 4 ? 4 - day : -3 - day;
  return addDays(value, offset);
};

const shortDate = (value: string) => {
  const date = fromIsoDate(value);
  return `${date.getUTCMonth() + 1}/${date.getUTCDate()}`;
};

const periodId = (type: PeriodType, startDate: string, endDate: string, sourceModule?: string) =>
  `${sourceModule ?? 'period'}-${type}-${startDate}-${endDate}`;

export const periodLabelFromIsoRange = (period: Pick<UnifiedPeriod, 'startDate' | 'endDate'>) =>
  period.startDate === period.endDate
    ? shortDate(period.startDate)
    : `${shortDate(period.startDate)}-${shortDate(period.endDate)}`;

export const createBusinessPeriod = ({
  type,
  startDate,
  endDate,
  reportDate,
  sourceModule,
}: {
  type: PeriodType;
  startDate: string;
  endDate: string;
  reportDate?: string;
  sourceModule?: string;
}): UnifiedPeriod => ({
  id: periodId(type, startDate, endDate, sourceModule),
  type,
  label: periodLabelFromIsoRange({ startDate, endDate }),
  startDate,
  endDate,
  reportDate,
  sourceModule,
});

export const createPeriodForType = (
  type: PeriodType,
  reportDate: string,
  sourceModule?: string,
): UnifiedPeriod => {
  if (type === 'NATURAL_WEEK_MON_TO_SUN') {
    const currentWeekMonday = mondayOfWeek(reportDate);
    const startDate = addDays(currentWeekMonday, -7);
    return createBusinessPeriod({
      type,
      startDate,
      endDate: addDays(startDate, 6),
      reportDate,
      sourceModule,
    });
  }

  if (type === 'DATE_SNAPSHOT') {
    return createBusinessPeriod({
      type,
      startDate: reportDate,
      endDate: reportDate,
      reportDate,
      sourceModule,
    });
  }

  if (type === 'FORECAST_WEEK') {
    const startDate = addDays(reportDate, 1);
    return createBusinessPeriod({
      type,
      startDate,
      endDate: addDays(startDate, 6),
      reportDate,
      sourceModule,
    });
  }

  if (type === 'MONTHLY') {
    const date = fromIsoDate(reportDate);
    const startDate = `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-01`;
    const nextMonth = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 1));
    const endDate = toIsoDate(new Date(nextMonth.getTime() - oneDayMs));
    return createBusinessPeriod({ type, startDate, endDate, reportDate, sourceModule });
  }

  const startDate = thursdayOfSalesWeek(reportDate);
  return createBusinessPeriod({
    type,
    startDate,
    endDate: addDays(startDate, 6),
    reportDate,
    sourceModule,
  });
};

export const getPreviousBusinessPeriod = (period: UnifiedPeriod): UnifiedPeriod => {
  if (period.type === 'DATE_SNAPSHOT') {
    const snapshotDate = addDays(period.startDate, -1);
    return createBusinessPeriod({
      type: period.type,
      startDate: snapshotDate,
      endDate: snapshotDate,
      reportDate: period.reportDate,
      sourceModule: period.sourceModule,
    });
  }

  if (period.type === 'MONTHLY') {
    const date = fromIsoDate(period.startDate);
    const previousMonth = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() - 1, 1));
    const startDate = toIsoDate(previousMonth);
    const endDate = toIsoDate(new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1) - oneDayMs));
    return createBusinessPeriod({
      type: period.type,
      startDate,
      endDate,
      reportDate: period.reportDate,
      sourceModule: period.sourceModule,
    });
  }

  const startDate = addDays(period.startDate, -7);
  return createBusinessPeriod({
    type: period.type,
    startDate,
    endDate: addDays(period.endDate, -7),
    reportDate: period.reportDate,
    sourceModule: period.sourceModule,
  });
};

export const canComparePeriods = (current: UnifiedPeriod, previous: UnifiedPeriod) =>
  current.type === previous.type;

export const assertComparablePeriods = (current: UnifiedPeriod, previous: UnifiedPeriod) => {
  if (!canComparePeriods(current, previous)) {
    throw new Error(`Cannot compare different period types: ${current.type} vs ${previous.type}`);
  }
};

export type { PeriodType, UnifiedPeriod } from './periodTypes';
