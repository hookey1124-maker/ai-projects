import type { BaseSkuRecord } from '../../dataCenter/types';

export type AccountTrafficStatusRecord = BaseSkuRecord & {
  sessions?: number;
  pageViews?: number;
  conversionRate?: number | null;
};

export const adaptAccountTrafficStatusData = (records: BaseSkuRecord[]): AccountTrafficStatusRecord[] => records.map((record) => ({
  ...record,
  conversionRate: null,
}));
