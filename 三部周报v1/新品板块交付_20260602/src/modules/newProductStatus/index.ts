// 页面组件
export { default as NewProductStatusPage } from './NewProductStatusPage';
export {
  type NewProductStatusData,
  type NewProductAnomaly,
  type OverallData,
  type CategoryMetrics,
  type AnalystMetrics,
  type ExpandTypeMetrics,
  type TimelinessData,
  type LowShareRecord,
  type PLPData,
  type PLPAdMetrics,
  type SalesSituationDetail,
  type UnsoldReasonData,
  type PLGData,
  type PLGRecord,
  mockNewProductStatusData,
  parseNewProductStatusData,
} from './newProductStatusAdapter';

// 规则 - 异常检测
export {
  newProductStatusRuleIds,
  evaluateNewProductStatusAnomalies,
  getOverallRiskLevel,
} from './newProductStatusRules';

// 汇总 - 周报文案
export {
  emptyNewProductStatusSummary,
  generateNewProductStatusSummary,
  type ReportText,
} from './newProductStatusSummary';
