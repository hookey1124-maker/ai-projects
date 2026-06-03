import type { NewProductStatusData, NewProductAnomaly } from './newProductStatusAdapter';

// 异常规则ID列表
export const newProductStatusRuleIds = [
  'new_product_low_share_high_risk',  // 低占比高风险
  'new_product_no_sales',            // 新品未出单
  'new_product_ramp_slow',            // 爬坡缓慢
  'new_product_analysis_delay',       // 分析延迟
  'new_product_competitor_pressure',  // 竞品压力
] as const;

/**
 * 评估新品状态异常
 * @param data 新品状态数据
 * @returns 异常列表
 */
export function evaluateNewProductStatusAnomalies(
  data: NewProductStatusData
): NewProductAnomaly[] {
  const anomalies: NewProductAnomaly[] = [];

  // 1. 低占比高风险新品
  const lowShareHighRisk = evaluateLowShareHighRisk(data);
  if (lowShareHighRisk) {
    anomalies.push(lowShareHighRisk);
  }

  // 2. 有对手未出单
  const noSalesWithCompetitor = evaluateNoSalesWithCompetitor(data);
  if (noSalesWithCompetitor) {
    anomalies.push(noSalesWithCompetitor);
  }

  // 3. 爬坡缓慢
  const rampSlow = evaluateRampSlow(data);
  if (rampSlow) {
    anomalies.push(rampSlow);
  }

  // 4. 分析延迟
  const analysisDelay = evaluateAnalysisDelay(data);
  if (analysisDelay) {
    anomalies.push(analysisDelay);
  }

  // 5. 竞品压力
  const competitorPressure = evaluateCompetitorPressure(data);
  if (competitorPressure) {
    anomalies.push(competitorPressure);
  }

  return anomalies;
}

/**
 * 评估低占比高风险新品
 * 定义：市占比 < 75% 且有竞品订单
 */
function evaluateLowShareHighRisk(data: NewProductStatusData): NewProductAnomaly | null {
  const unsold = data.unsoldReason.hasCompetitor;
  
  if (unsold.total > 0) {
    return {
      ruleId: 'new_product_low_share_high_risk',
      severity: 'high',
      message: `有 ${unsold.total} 个低占比新品存在竞品压力（上期 ${unsold.prevTotal} 个）`,
      affectedItems: [],
      recommendation: '建议开启 PLP 广告或进行链接优化，提升市场竞争力',
    };
  }

  return null;
}

/**
 * 评估有对手未出单新品
 */
function evaluateNoSalesWithCompetitor(data: NewProductStatusData): NewProductAnomaly | null {
  const noSales = data.salesSituation.overall.noSaleCount;
  
  if (noSales > 0) {
    return {
      ruleId: 'new_product_no_sales',
      severity: 'medium',
      message: `本期有 ${noSales} 个有对手新品未出单（上期 ${data.salesSituation.overall.prevNoSaleCount} 个）`,
      affectedItems: [],
      recommendation: '分析未出单原因，调整定价策略或开启广告推广',
    };
  }

  return null;
}

/**
 * 评估爬坡缓慢新品
 * 定义：8日外出单（N）占比过高
 */
function evaluateRampSlow(data: NewProductStatusData): NewProductAnomaly | null {
  const { nCount, hasCompetitorSku } = data.salesSituation.overall;
  
  // 8日外占比超过 50% 视为爬坡缓慢
  const nRatio = hasCompetitorSku > 0 ? nCount / hasCompetitorSku : 0;
  
  if (nRatio > 0.5) {
    return {
      ruleId: 'new_product_ramp_slow',
      severity: 'low',
      message: `${nCount} 个新品爬坡缓慢，8日外出单占比 ${(nRatio * 100).toFixed(1)}%`,
      affectedItems: [],
      recommendation: '关注爬坡期新品，优化 listing 和价格策略',
    };
  }

  return null;
}

/**
 * 评估分析延迟
 * 定义：及时率低于 60% 或某分析人及时率低于 30%
 */
function evaluateAnalysisDelay(data: NewProductStatusData): NewProductAnomaly | null {
  const timelyRate = parseFloat(data.overall.timeliness.timelyRate);
  
  // 总体及时率低于 60%
  if (timelyRate < 60) {
    const delayedAnalysts = data.timelinessData.analysts
      .filter((a: any) => parseFloat(a.timelyRate) < 50)
      .map((a: any) => `${a.analyst}(${a.timelyRate})`);
    
    return {
      ruleId: 'new_product_analysis_delay',
      severity: 'medium',
      message: `分析及时率 ${data.overall.timeliness.timelyRate}，低于 60% 警戒线`,
      affectedItems: delayedAnalysts,
      recommendation: '加快新品分析节奏，确保 8 日内完成首次分析',
    };
  }

  return null;
}

/**
 * 评估竞品压力
 * 定义：有竞品的新品中，8 日内出单率下降
 */
function evaluateCompetitorPressure(data: NewProductStatusData): NewProductAnomaly | null {
  const { yCount, prevYCount, hasCompetitorSku, prevHasCompetitorSku } = data.salesSituation.overall;
  
  // 出单率下降超过 10%
  const currRate = hasCompetitorSku > 0 ? (yCount / hasCompetitorSku) * 100 : 100;
  const prevRate = prevHasCompetitorSku > 0 ? (prevYCount / prevHasCompetitorSku) * 100 : 100;
  
  if (currRate < prevRate - 10) {
    return {
      ruleId: 'new_product_competitor_pressure',
      severity: 'low',
      message: `新品 8 日内出单率下降 ${(prevRate - currRate).toFixed(1)}pp（${currRate.toFixed(1)}% vs ${prevRate.toFixed(1)}%）`,
      affectedItems: [],
      recommendation: '关注竞品动态，评估价格和 listing 竞争力',
    };
  }

  return null;
}

/**
 * 获取总体风险等级
 */
export function getOverallRiskLevel(
  anomalies: NewProductAnomaly[]
): 'low' | 'medium' | 'high' | 'unknown' {
  if (anomalies.length === 0) {
    return 'unknown';
  }
  
  if (anomalies.some(a => a.severity === 'high')) {
    return 'high';
  }
  
  if (anomalies.some(a => a.severity === 'medium')) {
    return 'medium';
  }
  
  return 'low';
}
