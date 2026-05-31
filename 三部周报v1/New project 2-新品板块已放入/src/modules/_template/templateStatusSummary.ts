import type { ModuleKey, ModuleStatusSummary } from '../../dataCenter/types';

export const buildTemplateStatusSummary = (moduleKey: ModuleKey, moduleName = '模板模块'): ModuleStatusSummary => ({
  moduleKey,
  moduleName,
  currentStatus: '待接入',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: ['当前模板不包含真实业务判断。'],
  nextActions: ['复制模板目录后，按模块 README 接入 Adapter、Rules 和 Summary。'],
});
