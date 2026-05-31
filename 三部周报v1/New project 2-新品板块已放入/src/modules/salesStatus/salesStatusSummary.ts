import type { ModuleStatusSummary } from '../../dataCenter/types';
import {
  buildWeeklyConclusion,
  buildWeeklyReportText,
  describeTrendPoint,
  type WeeklyConclusion,
} from '../../utils/reportGenerator';
import { generateSummary } from '../../utils/summaryGenerator';

export const emptySalesStatusSummary: ModuleStatusSummary = {
  moduleKey: 'salesStatus',
  moduleName: '总销售状态',
  currentStatus: '已接入主销售数据源',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: [],
  nextActions: [],
};

export {
  buildWeeklyConclusion,
  buildWeeklyReportText,
  describeTrendPoint,
  generateSummary,
};

export type { WeeklyConclusion };
