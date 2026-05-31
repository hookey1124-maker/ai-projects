import type { BaseSkuRecord } from '../../dataCenter/types';

export type SalesForecastRecord = BaseSkuRecord & {
  forecastSales?: number;
  forecastRevenue?: number;
  confidence?: number | null;
};

export const adaptSalesForecastData = (records: BaseSkuRecord[]): SalesForecastRecord[] => records.map((record) => ({
  ...record,
  confidence: null,
}));
