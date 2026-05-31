import type { ModuleStatusSummary } from '../../dataCenter/types';

export const emptyAdsStatusSummary: ModuleStatusSummary = {
  moduleKey: 'adsStatus',
  moduleName: '广告状态',
  currentStatus: '待接入',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: [],
  nextActions: [],
};
