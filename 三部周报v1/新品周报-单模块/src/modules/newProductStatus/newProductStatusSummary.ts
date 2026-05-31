import type { ModuleStatusSummary } from '../../dataCenter/types';
import type { NewProductStatusData, NewProductAnomaly } from './newProductStatusAdapter';
import { getOverallRiskLevel } from './newProductStatusRules';

/** 空状态汇总 */
export const emptyNewProductStatusSummary: ModuleStatusSummary = {
  moduleKey: 'newProductStatus',
  moduleName: '新品状态',
  currentStatus: '待接入',
  riskLevel: 'unknown',
  coreMetrics: [],
  mainFindings: [],
  nextActions: [],
};

/**
 * 生成新品状态汇总
 */
export const generateNewProductStatusSummary = (
  data: NewProductStatusData,
  anomalies: NewProductAnomaly[]
): ModuleStatusSummary => {
  const riskLevel = getOverallRiskLevel(anomalies);

  // 核心指标
  const coreMetrics = [
    {
      label: '累计SKU',
      value: data.overall.kpi.totalSku,
      unit: '个',
      description: `本期新上架 ${data.overall.kpi.curNewSku}`,
    },
    {
      label: '总销量',
      value: data.overall.kpi.totalSalesQty,
      unit: '件',
      description: `${data.overall.kpi.salesQtyChange}`,
    },
    {
      label: '出单率',
      value: data.overall.salesSituation.soldRate,
      description: `上期 ${data.overall.salesSituation.prevSoldRate}`,
    },
    {
      label: '分析及时率',
      value: data.overall.timeliness.timelyRate,
      description: `${data.overall.timeliness.change}`,
    },
  ];

  // 主要发现
  const mainFindings: string[] = [];

  // 出单率情况
  const currRate = parseFloat(data.overall.salesSituation.soldRate);
  const prevRate = parseFloat(data.overall.salesSituation.prevSoldRate);
  if (currRate >= prevRate) {
    mainFindings.push(`新品出单率 ${data.overall.salesSituation.soldRate}，较上期 ${data.overall.salesSituation.prevSoldRate} 保持稳定`);
  } else {
    mainFindings.push(`新品出单率 ${data.overall.salesSituation.soldRate}，较上期 ${data.overall.salesSituation.prevSoldRate} 有所下降`);
  }

  // 未出单情况
  if (data.unsoldReason.hasCompetitor.total > 0) {
    mainFindings.push(`${data.unsoldReason.hasCompetitor.total} 个有对手新品未出单，100% 为竞争无优势，需重点关注`);
  }

  // 分析及时率
  const timelyRate = parseFloat(data.overall.timeliness.timelyRate);
  const prevTimelyRate = parseFloat(data.overall.timeliness.prevTimelyRate);
  if (timelyRate >= prevTimelyRate) {
    mainFindings.push(`分析及时率 ${data.overall.timeliness.timelyRate}，较上期 ${data.overall.timeliness.prevTimelyRate} 提升 ${data.overall.timeliness.change}`);
  } else {
    mainFindings.push(`分析及时率 ${data.overall.timeliness.timelyRate}，较上期 ${data.overall.timeliness.prevTimelyRate} 有所下降，需加强分析跟进`);
  }

  // 销量情况
  if (data.overall.kpi.totalSalesQty > data.overall.kpi.prevTotalSalesQty) {
    mainFindings.push(`新品总销量 ${data.overall.kpi.totalSalesQty} 件，环比增长 ${data.overall.kpi.salesQtyChange}，表现良好`);
  }

  // 下周动作
  const nextActions: string[] = [];

  // 基于异常的动议
  anomalies.forEach((anomaly) => {
    if (anomaly.recommendation) {
      nextActions.push(anomaly.recommendation);
    }
  });

  // 通用建议
  if (nextActions.length === 0) {
    nextActions.push('新品整体表现正常，持续观察并优化广告策略');
  }

  // 风险状态
  let currentStatus = '正常';
  if (riskLevel === 'high') {
    currentStatus = '高风险';
  } else if (riskLevel === 'medium') {
    currentStatus = '中风险';
  } else if (riskLevel === 'low') {
    currentStatus = '低风险';
  }

  return {
    moduleKey: 'newProductStatus',
    moduleName: '新品状态',
    currentStatus,
    riskLevel,
    coreMetrics,
    mainFindings,
    nextActions,
  };
};

/** 汇报文案类型 */
export type ReportText = {
  full: string;
  summary: string;
};
