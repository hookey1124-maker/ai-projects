import type { WeeklyPeriod } from '../types/weeklyReport';

const qtyPattern = /^(\d{1,2}\/\d{1,2}-\d{1,2}\/\d{1,2})销量$/;
const amountPattern = /^(\d{1,2}\/\d{1,2}-\d{1,2}\/\d{1,2})销售额$/;
const marketSharePattern = /^(\d{1,2}\/\d{1,2})市占比$/;
const competitorPattern = /^(\d{1,2}\/\d{1,2})直接对手出单$/;
const pricePattern = /^(\d{4})\/(\d{1,2})\/(\d{1,2})在售价$/;

const toDateLabel = (month: number, day: number) => `${month}/${day}`;
const toFullDateLabel = (year: number, month: number, day: number) => `${year}/${month}/${day}`;

const inferYear = (headers: string[]) => {
  for (const header of headers) {
    const match = header.match(pricePattern);
    if (match) return Number(match[1]);
  }
  return new Date().getFullYear();
};

const periodEndDate = (periodLabel: string, year: number) => {
  const end = periodLabel.split('-')[1];
  const [month, day] = end.split('/').map(Number);
  return new Date(year, month - 1, day);
};

const candidateDateLabels = (periodLabel: string, year: number) => {
  const endDate = periodEndDate(periodLabel, year);
  const endDateLabel = toDateLabel(endDate.getMonth() + 1, endDate.getDate());
  const candidates = Array.from({ length: 4 }, (_, offset) => {
    const date = new Date(endDate);
    date.setDate(date.getDate() + offset);
    return {
      dateLabel: toDateLabel(date.getMonth() + 1, date.getDate()),
      fullDateLabel: toFullDateLabel(date.getFullYear(), date.getMonth() + 1, date.getDate()),
    };
  });
  return {
    endDateLabel,
    candidates,
  };
};

const firstMatched = (candidates: ReturnType<typeof candidateDateLabels>['candidates'], map: Map<string, string>, key: 'dateLabel' | 'fullDateLabel') =>
  candidates.find((candidate) => map.has(candidate[key]));

export const buildPeriods = (headers: string[]): { periods: WeeklyPeriod[]; warnings: string[] } => {
  const year = inferYear(headers);
  const amountByLabel = new Map<string, string>();
  const marketShareByDate = new Map<string, string>();
  const competitorByDate = new Map<string, string>();
  const listingPriceByDate = new Map<string, string>();

  headers.forEach((header) => {
    const amount = header.match(amountPattern);
    if (amount) amountByLabel.set(amount[1], header);

    const marketShare = header.match(marketSharePattern);
    if (marketShare) marketShareByDate.set(marketShare[1], header);

    const competitor = header.match(competitorPattern);
    if (competitor) competitorByDate.set(competitor[1], header);

    const price = header.match(pricePattern);
    if (price) listingPriceByDate.set(`${Number(price[1])}/${Number(price[2])}/${Number(price[3])}`, header);
  });

  const warnings: string[] = [];
  const periods = headers.flatMap((header) => {
    const qty = header.match(qtyPattern);
    if (!qty) return [];
    const label = qty[1];
    const { endDateLabel, candidates } = candidateDateLabels(label, year);
    const marketShareDate = firstMatched(candidates, marketShareByDate, 'dateLabel');
    const competitorDate = firstMatched(candidates, competitorByDate, 'dateLabel');
    const listingPriceDate = firstMatched(candidates, listingPriceByDate, 'fullDateLabel');
    if (!marketShareDate) warnings.push(`${label} 缺失市占比列`);
    if (!competitorDate) warnings.push(`${label} 缺失直接对手出单列`);
    if (!listingPriceDate) warnings.push(`${label} 缺失在售价列`);
    const matchedDates = [
      marketShareDate ? `市占为 ${marketShareDate.dateLabel}` : null,
      competitorDate ? `对手为 ${competitorDate.dateLabel}` : null,
      listingPriceDate ? `在售价为 ${listingPriceDate.dateLabel}` : null,
    ].filter((item): item is string => Boolean(item));
    const uniqueDates = new Set([
      marketShareDate?.dateLabel,
      competitorDate?.dateLabel,
      listingPriceDate?.dateLabel,
    ].filter(Boolean));
    if (uniqueDates.size > 1) {
      warnings.push(`周期 ${label} 的辅助字段日期不一致：${matchedDates.join('，')}。`);
    }
    return [
      {
        label,
        salesQtyColumn: header,
        salesAmountColumn: amountByLabel.get(label),
        marketShareColumn: marketShareDate ? marketShareByDate.get(marketShareDate.dateLabel) : undefined,
        competitorColumn: competitorDate ? competitorByDate.get(competitorDate.dateLabel) : undefined,
        listingPriceColumn: listingPriceDate ? listingPriceByDate.get(listingPriceDate.fullDateLabel) : undefined,
        endDateLabel,
        reportDateLabel: competitorDate?.dateLabel ?? marketShareDate?.dateLabel ?? listingPriceDate?.dateLabel,
        marketShareDateLabel: marketShareDate?.dateLabel,
        competitorDateLabel: competitorDate?.dateLabel,
        listingPriceDateLabel: listingPriceDate?.dateLabel,
      },
    ];
  }).sort((a, b) => periodEndDate(a.label, year).getTime() - periodEndDate(b.label, year).getTime());

  return { periods, warnings };
};
