/**
 * 新品状态模块 — 数据适配器
 * 从 corrected_data.json（53个数据块，提取自新品板块_4.30-5.27_4weeks_drill.html）加载数据
 */
import correctedData from './corrected_data.json';

// ===== 类型定义（供 Rules / Summary 模块使用） =====
export interface NewProductStatusData { [key: string]: any }
export interface NewProductAnomaly {
  ruleId: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
  affectedItems: string[];
  recommendation: string;
}
export type OverallData = any;
export type CategoryMetrics = any;
export type AnalystMetrics = any;
export type ExpandTypeMetrics = any;
export type TimelinessData = any;
export type LowShareRecord = any;
export type PLPData = any;
export type PLPAdMetrics = any;
export type SalesSituationDetail = any;
export type UnsoldReasonData = any;
export type PLGData = any;
export type PLGRecord = any;

/** @deprecated 旧版兼容，不再使用 */
export const mockNewProductStatusData: any = {};
/** @deprecated 旧版兼容，不再使用 */
export function parseNewProductStatusData(_data: any): any { return {}; }

// ===== 原始数据导出 =====
const CD = correctedData as Record<string, any>;

/** 四三累计原始行（140条） */
export const rawRows: any[] = CD.cum43Data || [];

/** 4周标签 */
export const WEEK_LABELS: string[] = CD.weekLabels4w || ['4.30-5.6', '5.7-5.13', '5.14-5.20', '5.21-5.27'];

// ===== 数据访问器 =====
export function getData() {
  return {
    // 总体统计
    cum43Stats: CD.cum43Stats || {},
    prevWeekKpi: CD.prevWeekKpi || {},

    // 维度数据
    categoryRevenueData: CD.categoryRevenueData || [],
    analystRevenueData: CD.analystRevenueData || [],
    expandTypeData: CD.expandTypeData || [],

    // 4周趋势
    totalSales4w: CD.totalSales4w || [0, 0, 0, 0],
    totalRev4w: CD.totalRev4w || [0, 0, 0, 0],
    totalShare4w: CD.totalShare4w || [0, 0, 0, 0],
    catSales4w: CD.catSales4w || [],
    catRev4w: CD.catRev4w || [],
    catShare4w: CD.catShare4w || [],
    anSales4w: CD.anSales4w || [],
    anRev4w: CD.anRev4w || [],
    anShare4w: CD.anShare4w || [],

    // 及时率
    timelinessData: CD.timelinessData || { analysts: [], total: {} },
    timeliness4w: CD.timeliness4w || { labels: [], analysts: [], totalRates: [] },

    // 低占比
    lowShareData: CD.lowShareData || [],
    lsAdKeys: CD.lsAdKeys || {},
    lsOpKeys: CD.lsOpKeys || {},

    // 市场分布
    mktDistOverall: CD.mktDistOverall || { curTotal: 0, prevTotal: 0, distribution: [] },
    priceOverview: CD.priceOverview || { avgPrice: 0, medianPrice: 0, distribution: [], byAnalyst: {}, byCategory: {} },
    shareTierOverview: CD.shareTierOverview || { tiers: [], byCategory: [] },

    // 未出单原因
    hasCompetitorUnsold: CD.hasCompetitorUnsold || { total: 0, prevTotal: 0, reasons: [], byAnalyst: [], byCategory: [] },
    unsoldNoCompetitor: CD.unsoldNoCompetitor || { total: 0, prevTotal: 0, reasons: [], byAnalyst: [], byCategory: [] },

    // PLP广告
    plpTotal: CD.plpTotal || {},
    plpPrevTotal: CD.plpPrevTotal || {},
    plpAnalysts: CD.plpAnalysts || [],
    plpCategories: CD.plpCategories || [],
    plpExpandTypes: CD.plpExpandTypes || [],
    plpSummaryData: CD.plpSummaryData || [],
    plpDetailData: CD.plpDetailData || [],

    // PLP 4周
    plp4wLabels: CD.plp4wLabels || [],
    plp4wCost: CD.plp4wCost || [0, 0, 0, 0],
    plp4wAdRev: CD.plp4wAdRev || [0, 0, 0, 0],
    plp4wAcos: CD.plp4wAcos || [0, 0, 0, 0],
    plp4wAcoas: CD.plp4wAcoas || [0, 0, 0, 0],
    plp4wAnalysts: CD.plp4wAnalysts || [],
    plpAn4w: CD.plpAn4w || [],
    plpCat4w: CD.plpCat4w || [],
    plpExp4w: CD.plpExp4w || [],

    // PLG
    plgRecords: CD.plgRecords || [],
    plgStats: CD.plgStats || {},
    plgAn4w: CD.plgAn4w || [],

    // 四三累计4周
    cum43_4w: CD.cum43_4w || {},
  };
}

// ===== 派生计算 =====

/** 解析总盘概览 KPI */
export function getOverviewKpi() {
  const d = getData();
  const stats = d.cum43Stats;
  const prev = d.prevWeekKpi;
  const totalSku = stats.total || rawRows.length;

  // cum43Stats uses sales4w/revenue4w arrays: [本周, 上周, 上上周, 上上上周]
  const totalSalesQty = stats.sales4w?.[0] || 0;
  const prevTotalSalesQty = stats.sales4w?.[1] || prev.prevTotalSalesQty || 0;
  const totalRevenue = stats.revenue4w?.[0] || 0;
  const prevTotalRevenue = stats.revenue4w?.[1] || prev.prevTotalRevenue || 0;
  const hasCompetitorSku = stats.hasRivalCount || 0;
  const noCompetitorSku = stats.noRivalCount || 0;
  const yCount = stats.yCount || 0;
  const nCount = stats.nCount || 0;
  const noSaleCount = stats.unCount || 0;
  const soldCount = (yCount + nCount);
  const soldRate = hasCompetitorSku > 0 ? (soldCount / hasCompetitorSku) * 100 : 0;

  const timeliness = (d.timelinessData.total as any) || {};
  const lowShareCount = (d.lowShareData || []).length;

  // 新增/减少SKU数（从prevWeekKpi取）
  const prevTotalSku = prev.prevTotalSku || 0;
  const newSkuDiff = totalSku - prevTotalSku;

  return {
    totalSku,
    curNewSku: newSkuDiff > 0 ? newSkuDiff : 0,
    prevNewSku: prevTotalSku,
    totalSalesQty,
    prevTotalSalesQty,
    totalRevenue,
    prevTotalRevenue,
    hasCompetitorSku,
    noCompetitorSku,
    yCount,
    nCount,
    noSaleCount,
    soldCount,
    soldRate,
    timeliness,
    lowShareCount,
  };
}

/** 品类维度数据（含4周） */
export function getCategoryMetrics() {
  const d = getData();
  return d.categoryRevenueData.map((c: any) => ({
    category: c.category,
    curSku: c.curSku || 0,
    curNewSku: c.curNewSku || 0,
    curSalesQty: c.curSalesQty || 0,
    prevSalesQty: c.prevSalesQty || 0,
    curRevenue: c.curRevenue || 0,
    prevRevenue: c.prevRevenue || 0,
    curHasCompetitor: c.curHasCompetitor || 0,
    curMarketShare: c.curMarketShare,
    prevMarketShare: c.prevMarketShare,
    sales4w: c.sales4w || [0, 0, 0, 0],
    revenue4w: c.revenue4w || [0, 0, 0, 0],
    share4w: c.share4w || [0, 0, 0, 0],
  }));
}

/** 分析人维度数据（含4周） */
export function getAnalystMetrics() {
  const d = getData();
  return d.analystRevenueData.map((a: any) => ({
    analyst: a.analyst,
    curSku: a.curSku || 0,
    curNewSku: a.curNewSku || 0,
    curSalesQty: a.curSalesQty || 0,
    prevSalesQty: a.prevSalesQty || 0,
    curRevenue: a.curRevenue || 0,
    prevRevenue: a.prevRevenue || 0,
    curMarketShare: a.curMarketShare,
    prevMarketShare: a.prevMarketShare,
    sales4w: a.sales4w || [0, 0, 0, 0],
    revenue4w: a.revenue4w || [0, 0, 0, 0],
    share4w: a.share4w || [0, 0, 0, 0],
  }));
}

/** 4周趋势数据（总盘） */
export function get4wTrends() {
  const d = getData();
  return {
    labels: WEEK_LABELS,
    totalSales: d.totalSales4w,
    totalRev: d.totalRev4w,
    totalShare: d.totalShare4w,  // 已是百分数，不要×100
    catSales: d.catSales4w,
    catRev: d.catRev4w,
    catShare: d.catShare4w,
    anSales: d.anSales4w,
    anRev: d.anRev4w,
    anShare: d.anShare4w,
  };
}
