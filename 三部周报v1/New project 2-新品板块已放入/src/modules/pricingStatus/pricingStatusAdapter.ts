import type { BaseSkuRecord } from '../../dataCenter/types';

export type PricingStatusRecord = BaseSkuRecord & {
  priceChange?: number | null;
  priceAction?: string;
};

export const adaptPricingStatusData = (records: BaseSkuRecord[]): PricingStatusRecord[] => records.map((record) => ({
  ...record,
  priceChange: null,
}));
