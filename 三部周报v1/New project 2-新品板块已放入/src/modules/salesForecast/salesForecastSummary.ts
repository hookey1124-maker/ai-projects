import type { ModuleStatusSummary } from '../../dataCenter/types';

export const emptySalesForecastSummary: ModuleStatusSummary = {
  moduleKey: 'salesForecast',
  moduleName: '销量预估',
  currentStatus: '待接入',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: [],
  nextActions: [],
};
