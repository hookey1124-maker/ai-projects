import type { BaseSkuRecord } from '../../dataCenter/types';

export type AdsStatusRecord = BaseSkuRecord & {
  adSpend?: number;
  acos?: number | null;
  cpc?: number | null;
};

export const adaptAdsStatusData = (records: BaseSkuRecord[]): AdsStatusRecord[] => records.map((record) => ({
  ...record,
  acos: null,
  cpc: null,
}));
