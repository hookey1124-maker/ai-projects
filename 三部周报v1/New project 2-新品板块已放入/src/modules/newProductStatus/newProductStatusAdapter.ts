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

// ===== 多周期支持 =====
export const ALL_PERIODS: Array<{label: string, index: number}> = CD.allPeriods || [];
export const ALL_WEEK_LABELS: string[] = CD.allWeekLabels || [];
const _NWEEKS = ALL_WEEK_LABELS.length || 4;

function slice4w(arr: number[], endIdx: number): number[] {
  if (!arr || arr.length === 0) return [0,0,0,0];
  const start = Math.max(0, endIdx - 3);
  const result: number[] = [];
  for (let i = start; i <= endIdx && i < arr.length; i++) result.push(arr[i] ?? 0);
  while (result.length < 4) result.unshift(0);
  return result;
}

function sliceLabels(endIdx: number): string[] {
  const start = Math.max(0, endIdx - 3);
  return ALL_WEEK_LABELS.slice(start, endIdx + 1);
}

function toDateKey(d: string): number {
  if (!d) return 0;
  if (d.includes('-')) {
    const parts = d.split('-');
    return parseInt(parts[0]) * 10000 + parseInt(parts[1]) * 100 + parseInt(parts[2]);
  }
  const parts2 = d.split('.');
  if (parts2.length === 2) {
    return 20260000 + parseInt(parts2[0]) * 100 + parseInt(parts2[1]);
  }
  return 0;
}

function buildSkuRowForPeriod(sku: any, idx: number, periodEndStr?: string): any | null {
  // 剔除在周期结束后上架的SKU
  if (periodEndStr) {
    const listKey = toDateKey(sku.listDate || '');
    const endKey = toDateKey(periodEndStr);
    if (listKey > 0 && endKey > 0 && listKey > endKey) return null;
  }
  return {
    sku: sku.sku, saleNo: sku.saleNo, listDate: sku.listDate,
    firstOrderDate: sku.firstOrderDate, analyst: sku.analyst,
    category: sku.category, expandType: sku.expandType,
    curSalesQty: sku.salesAll?.[idx] || 0,
    prevSalesQty: sku.salesAll?.[idx-1] || 0,
    curRevenue: sku.revenueAll?.[idx] || 0,
    prevRevenue: sku.revenueAll?.[idx-1] || 0,
    curRivalQty: sku.rivalAll?.[idx] || 0,
    prevRivalQty: sku.rivalAll?.[idx-1] || 0,
    curMarketShare: sku.shareAll?.[idx] || 0,
    prevMarketShare: sku.shareAll?.[idx-1] || 0,
    curMarketStatus: sku.mktAll?.[idx] || '',
    cur8dStatus: sku.ord8All?.[idx] || '',
    plpEnabled: sku.plpAll?.[idx] || 'N',
    plgFee: (sku.plgFeeAll?.[idx] || 0) + '%',
  };
}

function getDefaultPeriodIndex(): number {
  return ALL_PERIODS.length > 0 ? ALL_PERIODS[ALL_PERIODS.length - 1].index : _NWEEKS - 1;
}

/** 四三累计原始行（默认最新周期，静态快照） */
export const rawRows: any[] = CD.cum43Data || [];

/** 获取指定周期的四三累计行（剔除周期后上架的SKU） */
export function getRawRows(periodEndIndex?: number): any[] {
  const idx = periodEndIndex ?? getDefaultPeriodIndex();
  const periodEndStr = ALL_WEEK_LABELS[idx]?.split('-').pop() || '';
  const skuAll: any[] = CD.skuAll || [];
  if (skuAll.length === 0) return CD.cum43Data || [];
  return skuAll
    .map((sku: any) => buildSkuRowForPeriod(sku, idx, periodEndStr))
    .filter((r: any) => r !== null);
}

/** 4周标签（默认最新周期） */
export const WEEK_LABELS: string[] = CD.weekLabels4w || ['4.30-5.6', '5.7-5.13', '5.14-5.20', '5.21-5.27'];

/** 动态获取4周标签 */
export function getWeekLabels(periodEndIndex?: number): string[] {
  const idx = periodEndIndex ?? getDefaultPeriodIndex();
  return ALL_WEEK_LABELS.length >= 4 ? sliceLabels(idx) : WEEK_LABELS;
}

function buildUnsoldDetail(rows: any[], analysts: string[], categories: string[]) {
  const mktReasons = ['竞争无优势', '站内无价格优势'];
  const noMktReasons = ['无市场', '站外出单'];
  const unsold = rows.filter((r: any) => r.cur8dStatus !== 'Y' && r.cur8dStatus !== 'N');
  const byAn: any[] = [];
  const byCat: any[] = [];
  analysts.forEach(an => {
    const anRows = unsold.filter((r: any) => r.analyst === an);
    if (anRows.length === 0) return;
    const entry: any = { analyst: an, total: anRows.length };
    mktReasons.forEach(m => { entry[m] = anRows.filter((r: any) => r.curMarketStatus === m).length; });
    noMktReasons.forEach(m => { entry[m] = anRows.filter((r: any) => r.curMarketStatus === m).length; });
    byAn.push(entry);
  });
  categories.forEach(cat => {
    const catRows = unsold.filter((r: any) => r.category === cat);
    if (catRows.length === 0) return;
    const entry: any = { category: cat, total: catRows.length };
    mktReasons.forEach(m => { entry[m] = catRows.filter((r: any) => r.curMarketStatus === m).length; });
    noMktReasons.forEach(m => { entry[m] = catRows.filter((r: any) => r.curMarketStatus === m).length; });
    byCat.push(entry);
  });
  return { total: unsold.length, prevTotal: 0, change: 0, byAnalyst: byAn, byCategory: byCat };
}

// ===== 数据访问器 =====
export function getData(periodEndIndex?: number) {
  const idx = periodEndIndex ?? getDefaultPeriodIndex();
  const skuAll: any[] = CD.skuAll || [];

  // 为选定周期重建 cum43Data（剔除周期后上架的SKU）
  const periodEndStr = ALL_WEEK_LABELS[idx]?.split('-').pop() || '';
  const cum43Data = skuAll.length > 0
    ? skuAll.map((sku: any) => buildSkuRowForPeriod(sku, idx, periodEndStr)).filter((r: any) => r !== null)
    : (CD.cum43Data || []);

  // 重建 cum43Stats
  const totalSku = cum43Data.length;
  const yCount = cum43Data.filter((r: any) => r.cur8dStatus === 'Y').length;
  const nCount = cum43Data.filter((r: any) => r.cur8dStatus === 'N').length;
  const hasRivalRows = cum43Data.filter((r: any) => r.curRivalQty > 0);
  const noRivalRows = cum43Data.filter((r: any) => r.curRivalQty === 0);
  const normalCount = cum43Data.filter((r: any) => r.curMarketStatus === '正常').length;
  const competitiveCount = cum43Data.filter((r: any) => r.curMarketStatus === '竞争无优势').length;
  const noMarketCount = cum43Data.filter((r: any) => r.curMarketStatus === '无市场').length;
  const stationOutCount = cum43Data.filter((r: any) => r.curMarketStatus === '站外出单').length;
  const noRivalSold = noRivalRows.filter((r: any) => r.cur8dStatus === 'Y' || r.cur8dStatus === 'N').length;
  const totalSalesW = cum43Data.reduce((s: number, r: any) => s + r.curSalesQty, 0);
  const totalRivalW = cum43Data.reduce((s: number, r: any) => s + r.curRivalQty, 0);
  const totalShareW = (totalSalesW + totalRivalW) > 0 ? Math.round(totalSalesW / (totalSalesW + totalRivalW) * 1000) / 10 : 0;

  // Previous week (idx-1)
  const prevIdx = Math.max(0, idx - 1);
  const prevRows = skuAll.length > 0
    ? skuAll.map((sku: any) => buildSkuRowForPeriod(sku, prevIdx))
    : [];
  const prevTotalSalesW = prevRows.reduce((s: number, r: any) => s + r.curSalesQty, 0);
  const prevTotalRevW = prevRows.reduce((s: number, r: any) => s + r.curRevenue, 0);
  const prevTotalRivalW = prevRows.reduce((s: number, r: any) => s + r.curRivalQty, 0);
  const prevTotalShareW = (prevTotalSalesW + prevTotalRivalW) > 0 ? Math.round(prevTotalSalesW / (prevTotalSalesW + prevTotalRivalW) * 1000) / 10 : 0;

  const cum43Stats = {
    total: totalSku, yCount, nCount, unCount: totalSku - yCount - nCount,
    noRivalSold, noRivalUnsold: noRivalRows.length - noRivalSold,
    normalCount, competitiveCount, noMarketCount, stationOutCount,
    hasRivalCount: hasRivalRows.length, noRivalCount: noRivalRows.length,
    totalMarketShare: totalShareW, totalMarketSharePrev: prevTotalShareW,
    sales4w: [totalSalesW, prevTotalSalesW, 0, 0],
    revenue4w: [cum43Data.reduce((s: number, r: any) => s + r.curRevenue, 0), prevTotalRevW, 0, 0],
  };

  // 4周切片
  const totalSalesAll: number[] = CD.totalSalesAll || [];
  const totalRevAll: number[] = CD.totalRevAll || [];
  const totalShareAll: number[] = CD.totalShareAll || [];

  // Compute SKU counts per category/analyst for this period
  const periodStartStr = ALL_WEEK_LABELS[idx]?.split('-')[0] || '';
  const skuByCat: Record<string, any[]> = {};
  const skuByAn: Record<string, any[]> = {};
  skuAll.forEach((sku: any) => {
    const cat = sku.category || '未分类';
    const an = sku.analyst || '未知';
    if (!skuByCat[cat]) skuByCat[cat] = [];
    if (!skuByAn[an]) skuByAn[an] = [];
    skuByCat[cat].push(sku);
    skuByAn[an].push(sku);
  });
  function countActiveSku(list: any[], weekEnd: string): number {
    if (!weekEnd) return list.length;
    const weKey = toDateKey(weekEnd);
    return list.filter(s => {
      const ldKey = toDateKey(s.listDate || '');
      if (!ldKey) return true; // No date = always active
      return ldKey <= weKey;
    }).length;
  }
  function countNewSku(list: any[], weekStart: string, weekEnd: string): number {
    if (!weekStart || !weekEnd) return 0;
    const wsKey = toDateKey(weekStart);
    const weKey = toDateKey(weekEnd);
    return list.filter(s => {
      const ldKey = toDateKey(s.listDate || '');
      if (!ldKey) return false;
      return ldKey >= wsKey && ldKey <= weKey;
    }).length;
  }

  // Category 4w
  const catSalesAll: any[] = CD.catSalesAll || [];
  const catSales4w = catSalesAll.map((c: any) => {
    const skuList = skuByCat[c.category] || [];
    return {
      category: c.category,
      curSku: countActiveSku(skuList, periodEndStr),
      curNewSku: countNewSku(skuList, periodStartStr, periodEndStr),
      curSalesQty: c.sales?.[idx] || 0, prevSalesQty: c.sales?.[idx-1] || 0,
      curRevenue: c.revenue?.[idx] || 0, prevRevenue: c.revenue?.[idx-1] || 0,
      curHasCompetitor: skuList.filter((s: any) => (s.rivalAll?.[idx] || 0) > 0).length,
      curMarketShare: c.share?.[idx] || 0, prevMarketShare: c.share?.[idx-1] || 0,
      sales4w: slice4w(c.sales || [], idx),
      revenue4w: slice4w(c.revenue || [], idx),
      share4w: slice4w(c.share || [], idx),
    };
  });

  // Analyst 4w
  const anSalesAll: any[] = CD.anSalesAll || [];
  const anSales4w = anSalesAll.map((a: any) => {
    const skuList = skuByAn[a.analyst] || [];
    return {
      analyst: a.analyst,
      curSku: countActiveSku(skuList, periodEndStr),
      curNewSku: countNewSku(skuList, periodStartStr, periodEndStr),
      curSalesQty: a.sales?.[idx] || 0, prevSalesQty: a.sales?.[idx-1] || 0,
      curRevenue: a.revenue?.[idx] || 0, prevRevenue: a.revenue?.[idx-1] || 0,
      curHasCompetitor: skuList.filter((s: any) => (s.rivalAll?.[idx] || 0) > 0).length,
      curMarketShare: a.share?.[idx] || 0, prevMarketShare: a.share?.[idx-1] || 0,
      sales4w: slice4w(a.sales || [], idx),
      revenue4w: slice4w(a.revenue || [], idx),
      share4w: slice4w(a.share || [], idx),
    };
  });

  return {
    cum43Stats,
    prevWeekKpi: {
      prevTotalSku: totalSku,
      prevTotalSalesQty: prevTotalSalesW,
      prevTotalRevenue: Math.round(prevTotalRevW * 100) / 100,
      deptRatio: CD.prevWeekKpi?.deptRatio || '--',
      deptTotalRevenue: CD.deptTotalRevenue || 0,
    },
    categoryRevenueData: catSales4w,
    analystRevenueData: anSales4w,
    expandTypeData: CD.expandTypeData || [],
    totalSales4w: slice4w(totalSalesAll, idx),
    totalRev4w: slice4w(totalRevAll, idx),
    totalShare4w: slice4w(totalShareAll, idx),
    catSales4w,
    catRev4w: catSales4w,
    catShare4w: catSales4w,
    anSales4w,
    anRev4w: anSales4w,
    anShare4w: anSales4w,
    timelinessData: CD.timelinessData || { analysts: [], total: {} },
    timeliness4w: CD.timeliness4w || { labels: [], analysts: [], totalRates: [] },
    lowShareData: cum43Data.filter((r: any) => r.curMarketShare < 75 && r.curRivalQty > 0),
    mktDistOverall: {
      curTotal: totalSku, prevTotal: totalSku,
      distribution: ['正常','竞争无优势','无市场','站外出单'].map(st => ({
        status: st, curCount: cum43Data.filter((r: any) => r.curMarketStatus === st).length,
        prevCount: 0, curPct: 0, prevPct: 0, change: 0,
      })),
    },
    priceOverview: CD.priceOverview || { avgPrice: 0, medianPrice: 0, distribution: [], byAnalyst: {}, byCategory: {} },
    shareTierOverview: CD.shareTierOverview || { tiers: [], byCategory: [] },
    hasCompetitorUnsold: buildUnsoldDetail(hasRivalRows, AD_ANALYSTS, AD_CATEGORIES),
    unsoldNoCompetitor: buildUnsoldDetail(noRivalRows, AD_ANALYSTS, AD_CATEGORIES),

    lsAdKeys: CD.lsAdKeys || {},
    lsOpKeys: CD.lsOpKeys || {},
    plpTotal: CD.plpTotal || {},
    plpPrevTotal: CD.plpPrevTotal || {},
    plpAnalysts: CD.plpAnalysts || [],
    plpCategories: CD.plpCategories || [],
    plpExpandTypes: CD.plpExpandTypes || [],
    plpSummaryData: CD.plpSummaryData || [],
    plpDetailData: CD.plpDetailData || [],
    plp4wLabels: CD.plp4wLabels || [],
    plp4wCost: CD.plp4wCost || [0, 0, 0, 0],
    plp4wAdRev: CD.plp4wAdRev || [0, 0, 0, 0],
    plp4wAcos: CD.plp4wAcos || [0, 0, 0, 0],
    plp4wAcoas: CD.plp4wAcoas || [0, 0, 0, 0],
    plp4wAnalysts: CD.plp4wAnalysts || [],
    plpAn4w: CD.plpAn4w || [],
    plpCat4w: CD.plpCat4w || [],
    plpExp4w: CD.plpExp4w || [],
    plgRecords: CD.plgRecords || [],
    plgStats: CD.plgStats || {},
    plgAn4w: CD.plgAn4w || [],
    cum43_4w: CD.cum43_4w || {},
    deptTotalSales: CD.deptTotalSales || 0,
    deptTotalRevenue: CD.deptTotalRevenue || 0,
    pwShare: CD.pwShare || 0,
    pwTotalLinks: CD.pwTotalLinks || 0,
  };
}

// ===== 派生计算 =====

/** 解析总盘概览 KPI */
export function getOverviewKpi(periodEndIndex?: number) {
  const d = getData(periodEndIndex);
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
    totalMarketShare: stats.totalMarketShare || 0,
    totalMarketSharePrev: stats.totalMarketSharePrev || 0,
  };
}

/** 部门对比 + PW爬虫市占 KPI */
export function getDeptKpi(periodEndIndex?: number) {
  const d = getData(periodEndIndex);
  const rows = getRawRows(periodEndIndex);
  const stats = d.cum43Stats;
  const totalRevenue = stats.revenue4w?.[0] || 0;
  const totalSales = stats.sales4w?.[0] || 0;
  const deptTotalSales = d.deptTotalSales || 0;
  const deptTotalRev = d.deptTotalRevenue || 0;
  const salesPct = deptTotalSales > 0 ? (totalSales / deptTotalSales * 100).toFixed(1) : '--';
  const revPct = deptTotalRev > 0 ? (totalRevenue / deptTotalRev * 100).toFixed(1) : '--';

  // 新品加权市占：只算有对手的SKU（按选定周期）
  const skuWR = rows.filter((r: any) => (r.curRivalQty || 0) > 0);
  const newSalesW = skuWR.reduce((s: number, r: any) => s + (r.curSalesQty || 0), 0);
  const rivalSalesW = skuWR.reduce((s: number, r: any) => s + (r.curRivalQty || 0), 0);
  const newShareW = (newSalesW + rivalSalesW) > 0 ? Math.round(newSalesW / (newSalesW + rivalSalesW) * 1000) / 10 : 0;

  const pwShare = d.pwShare || 0;
  const diffShare = Math.abs(pwShare - newShareW).toFixed(1);

  return {
    salesPct,
    revPct,
    newSales: totalSales,
    deptSales: deptTotalSales,
    newRevenue: totalRevenue,
    deptRevenue: deptTotalRev,
    pwShare,
    pwTotalLinks: d.pwTotalLinks || 0,
    newShareW,
    newSkuCount: skuWR.length,
    diffShare,
  };
}

/** 品类维度数据（含4周） */
export function getCategoryMetrics(periodEndIndex?: number) {
  const d = getData(periodEndIndex);
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
export function getAnalystMetrics(periodEndIndex?: number) {
  const d = getData(periodEndIndex);
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
export function get4wTrends(periodEndIndex?: number) {
  const d = getData(periodEndIndex);
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

// ==================== 广告构成 & 链接明细 ====================

const AD_ANALYSTS = ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'];
const AD_CATEGORIES = ['车门系统','车身外扩件','挡泥板','机盖及附件','牌照板支架','其他','饰条'];

/** 市占比分档 */
export function getShareTier(share: number, rivalQty: number): string {
  if (share >= 75) return '高';
  if (share >= 50) return '中';
  if (share > 0 || rivalQty > 0) return '低';
  return '无市场';
}

/** 是否出单（上架后是否出过单） */
export function getHasOrder(cur8dStatus: string, curSalesQty: number): '是' | '否' {
  return (cur8dStatus === 'Y' || cur8dStatus === 'N' || curSalesQty > 0) ? '是' : '否';
}

/** 广告分类标签 */
export function getAdClassLabel(plpEnabled: string, plgFee: number): string {
  const hasPlp = plpEnabled === 'Y' || plpEnabled === '是';
  const hasPlg = plgFee > 0;
  if (hasPlp && hasPlg) return 'PLP+PLG';
  if (hasPlp) return '单PLP';
  if (hasPlg) return '仅PLG';
  return '无广告';
}

/** PLG费率分档 */
export function getPlgFeeTier(plgFee: number): string {
  if (plgFee === 0) return '无广告';
  if (plgFee <= 2) return '低费率';
  if (plgFee <= 4) return '中费率';
  return '高费率';
}

/** 广告构成分布数据（从选定周期 cum43Data 计算） */
export function getAdCompData(periodEndIndex?: number) {
  const rows = getRawRows(periodEndIndex);
  const comp: Record<string, number> = { 'PLP+PLG': 0, '单PLP': 0, '仅PLG': 0, '无广告': 0 };
  const tierDist: Record<string, number> = { '无广告': 0, '低费率': 0, '中费率': 0, '高费率': 0 };
  const anComp: Record<string, any> = {};
  const catComp: Record<string, any> = {};

  AD_ANALYSTS.forEach(a => { anComp[a] = { 'PLP+PLG':0,'单PLP':0,'仅PLG':0,'无广告':0,total:0,tierNone:0,tierLow:0,tierMid:0,tierHigh:0 }; });
  AD_CATEGORIES.forEach(c => { catComp[c] = { 'PLP+PLG':0,'单PLP':0,'仅PLG':0,'无广告':0,total:0 }; });

  rows.forEach((r: any) => {
    const an = r.analyst || '未知';
    const cat = r.category || '未分类';
    const plpEnabled = r.plpEnabled || 'N';
    const feeStr = String(r.plgFee || '0%').replace('%', '');
    const feePct = parseFloat(feeStr) || 0;
    const label = getAdClassLabel(plpEnabled, feePct);
    const tier = getPlgFeeTier(feePct);

    comp[label] = (comp[label] || 0) + 1;
    tierDist[tier] = (tierDist[tier] || 0) + 1;

    if (anComp[an]) { anComp[an][label]++; anComp[an].total++; }
    if (!catComp[cat]) catComp[cat] = { 'PLP+PLG':0,'单PLP':0,'仅PLG':0,'无广告':0,total:0 };
    catComp[cat][label]++; catComp[cat].total++;

    const tierKey = tier === '无广告' ? 'tierNone' : tier === '低费率' ? 'tierLow' : tier === '中费率' ? 'tierMid' : 'tierHigh';
    if (anComp[an]) anComp[an][tierKey]++;
  });

  return {
    compKpis: (['PLP+PLG', '单PLP', '仅PLG', '无广告'] as const).map(k => ({ label: k, count: comp[k] || 0 })),
    tierKpis: (['无广告', '低费率', '中费率', '高费率'] as const).map(k => ({ label: k, count: tierDist[k] || 0 })),
    byAnalyst: AD_ANALYSTS.filter(a => anComp[a] && anComp[a].total > 0).map(a => ({ analyst: a, ...anComp[a] })),
    byCategory: AD_CATEGORIES.filter(c => catComp[c] && catComp[c].total > 0).map(c => ({ category: c, ...catComp[c] })),
  };
}

/** 链接明细（PLP+PLG同开，链接维度，按选定周期） */
export function getLinkDetail(periodEndIndex?: number) {
  const d = getData(periodEndIndex);
  const rows = getRawRows(periodEndIndex);
  const plpDetail = d.plpDetailData || [];

  // Build SKU info lookup from per-period cum43Data
  const skuMap: Record<string, any> = {};
  rows.forEach((r: any) => {
    const sku = String(r.sku || '').trim();
    if (!sku) return;
    const shareStr = String(r.curMarketShare || '0').replace('%', '');
    skuMap[sku] = {
      analyst: r.analyst || '未知',
      category: r.category || '未分类',
      plgFee: parseFloat(String(r.plgFee || '0%').replace('%', '')) || 0,
      curSalesQty: Number(r.curSalesQty || 0),
      curRevenue: Number(r.curRevenue || 0),
      curMarketShare: parseFloat(shareStr) || 0,
      curRivalQty: Number(r.curRivalQty || 0),
      cur8dStatus: String(r.cur8dStatus || '').trim(),
    };
  });

  // 当期 PLP+PLG同开（链接维度）：plgEnabled === 'Y' 的链接
  const links = plpDetail
    .filter((r: any) => r.plgEnabled === 'Y' || r.plgEnabled === '是')
    .map((r: any) => {
      const sku = String(r.SKU || '').trim();
      const info = skuMap[sku] || {};
      const share = info.curMarketShare || 0;
      const rivalQty = info.curRivalQty || 0;
      const salesQty = info.curSalesQty || 0;
      return {
        sku: sku || r.SKU || '',
        linkId: String(r.id || ''),
        campaign: r.campaign || '',
        analyst: info.analyst || r.analyst || '未知',
        category: info.category || r.category || '未分类',
        hasOrder: getHasOrder(info.cur8dStatus || '', salesQty),
        marketShare: share,
        shareTier: getShareTier(share, rivalQty),
        rivalQty,
        salesQty,
        revenue: info.curRevenue || 0,
        plgFee: info.plgFee || 0,
      };
    });

  return {
    totalLinks: plpDetail.length,
    plpPlgLinks: links,
    plpPlgCount: links.length,
  };
}
