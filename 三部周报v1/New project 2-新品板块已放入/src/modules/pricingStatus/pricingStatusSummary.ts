import type { ModuleStatusSummary } from '../../dataCenter/types';

export const emptyPricingStatusSummary: ModuleStatusSummary = {
  moduleKey: 'pricingStatus',
  moduleName: '价格状态',
  currentStatus: '待接入',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: [],
  nextActions: [],
};
