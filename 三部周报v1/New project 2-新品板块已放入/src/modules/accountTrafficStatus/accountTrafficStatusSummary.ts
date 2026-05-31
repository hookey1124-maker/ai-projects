import type { ModuleStatusSummary } from '../../dataCenter/types';

export const emptyAccountTrafficStatusSummary: ModuleStatusSummary = {
  moduleKey: 'accountTrafficStatus',
  moduleName: '账号流量状态',
  currentStatus: '待接入',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: [],
  nextActions: [],
};
