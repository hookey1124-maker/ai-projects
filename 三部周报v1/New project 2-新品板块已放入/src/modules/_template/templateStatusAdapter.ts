import type { BaseSkuRecord } from '../../dataCenter/types';

export type TemplateStatusRecord = BaseSkuRecord & {
  moduleSpecificMetric?: number | null;
};

export const adaptTemplateStatusData = (records: BaseSkuRecord[]): TemplateStatusRecord[] =>
  records.map((record) => ({
    ...record,
    moduleSpecificMetric: null,
  }));
