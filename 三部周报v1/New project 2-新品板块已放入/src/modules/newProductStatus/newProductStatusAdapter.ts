import type { ModuleStatusSummary } from '../../dataCenter/types';

// ==================== 总体数据 ====================
/** 总体概况 KPI */
export interface OverallKPI {
  totalSku: number;            // 累计SKU数
  curNewSku: number;           // 本周新上架SKU
  prevNewSku: number;          // 上周新上架SKU
  totalSalesQty: number;        // 总销量
  prevTotalSalesQty: number;   // 上周总销量
  salesQtyChange: string;      // 销量环比
  totalRevenue: number;        // 总销售额(USD)
  prevTotalRevenue: number;    // 上周总销售额
  revenueChange: string;       // 销售额环比
  hasCompetitorSku: number;   // 有对手SKU数
  prevHasCompetitorSku: number;
  noCompetitorSku: number;    // 无对手SKU数
  prevNoCompetitorSku: number;
}

/** 分析及时率 */
export interface TimelinessMetrics {
  timelyCount: number;          // 及时分析产品数
  noAnalysis8dCount: number;     // 8日内新品无分析数
  noAnalysis7dCount: number;    // 超7日低占比未分析数
  totalCount: number;           // 统计总数
  timelyRate: string;           // 及时分析率
  prevTimelyCount: number;
  prevTimelyRate: string;
  change: string;
}

/** 出单情况汇总 */
export interface SalesSituationMetrics {
  hasCompetitorSku: number;      // 有对手总SKU
  prevHasCompetitorSku: number;
  change: number;
  yCount: number;                // 8日内出单（Y）
  prevYCount: number;
  yChange: number;
  nCount: number;                // 8日外出单（N）
  prevNCount: number;
  nChange: number;
  noSaleCount: number;          // 真正未出单
  prevNoSaleCount: number;
  noSaleChange: number;
  soldCount: number;            // 已出单合计(Y+N)
  prevSoldCount: number;
  soldChange: number;
  soldRate: string;             // 出单率
  prevSoldRate: string;
}

/** 总体数据 */
export interface OverallData {
  kpi: OverallKPI;
  timeliness: TimelinessMetrics;
  salesSituation: SalesSituationMetrics;
}

// ==================== 品线维度 ====================
export interface CategoryMetrics {
  category: string;
  curSku: number;
  curNewSku: number;
  curSalesQty: number;
  prevSalesQty: number;
  salesQtyChange: string;
  curRevenue: number;
  prevRevenue: number;
  revenueChange: string;
  curHasCompetitor: number;
  prevHasCompetitor: number;
}

// ==================== 分析人维度 ====================
export interface AnalystMetrics {
  analyst: string;
  curSku: number;
  curNewSku: number;
  curSalesQty: number;
  prevSalesQty: number;
  salesQtyChange: string;
  curRevenue: number;
  prevRevenue: number;
  revenueChange: string;
}

// ==================== 拓展类型 ====================
export interface ExpandTypeMetrics {
  expandType: string;
  curSku: number;
  prevSku: number;
  curSalesCount: number;
  curSalesRate: string;
  prevSalesCount: number;
  prevSalesRate: string;
  salesRateChange: string;
  curSalesQty: number;
  prevSalesQty: number;
  salesQtyChange: string;
  curRevenue: number;
  prevRevenue: number;
  revenueChange: string;
}

// ==================== 分析及时率 ====================
export interface AnalystTimeliness {
  analyst: string;
  curSku: number;
  timelyCount: number;
  noAnalysis8dCount: number;
  noAnalysis7dCount: number;
  timelyRate: string;
  prevSku: number;
  prevTimelyCount: number;
  prevTimelyRate: string;
  change: string;
}

export interface TimelinessData {
  analysts: AnalystTimeliness[];
  total: AnalystTimeliness;
}

// ==================== 低占比新品 ====================
export interface LowShareRecord {
  salesCode: string;
  sku: string;
  launchDate: string;
  analyst: string;
  category: string;
  expandType: string;
  curSalesQty: number;
  salesQtyChange: string;
  curRevenue: number;
  revenueChange: string;
  prevCompetitorQty: number;
  curCompetitorQty: number;
  competitorQtyChange: string;
  prevMarketShare: string;
  curMarketShare: string;
  marketShareChange: string;
  cur8dStatus: string;
  cur7dFreqTag: string;
  prevMarketStatus: string;
  curOperation: string;
  curMarketStatus: string;
  plpEnabled: string;
  plgFee: string;
}

// ==================== 新品PLP ====================
export interface PLPAdMetrics {
  campaignCount: number;
  linkCount: number;
  impression: number;
  click: number;
  sold: number;
  cost: number;
  revenue: number;
  prevRevenue: number;
  revenueChange: string;
  roas: string;
  cvr: string;
  ctr: string;
  cpc: string;
  cpa: string;
  acos: string;
  acoas: string;
}

export interface PLPAnalystMetrics extends PLPAdMetrics {
  analyst: string;
}

export interface PLPCategoryMetrics extends PLPAdMetrics {
  category: string;
}

export interface PLPExpandTypeMetrics extends PLPAdMetrics {
  expandType: string;
}

export interface PLPDetailRecord {
  period: string;
  campaign: string;
  sku: string;
  id: string;
  store: string;
  plpStartDate: string;
  actualListDate: string;
  firstOrderDate: string;
  analyst: string;
  category: string;
  productExpansion: string;
  impressions: number;
  clicks: number;
  salesQty: number;
  spend: number;
  adRevenue: number;
  totalRevenue: number;
  roas: number;
  cvr: number;
  ctr: number;
  cpc: number;
  cpa: number;
  acos: number;
  acoas: number;
}

export interface PLPData {
  total: PLPAdMetrics;
  prevTotal: PLPAdMetrics;
  analysts: PLPAnalystMetrics[];
  categories: PLPCategoryMetrics[];
  expandTypes: PLPExpandTypeMetrics[];
  detailRecords: PLPDetailRecord[];
}

// ==================== 新品出单情况 ====================
export interface SalesSituationDetail {
  /** 总体出单情况 */
  overall: SalesSituationMetrics;
  
  /** 8日外出单统计 */
  outside8dSku: number;
  prevOutside8dSku: number;
  outside8dChange: number;
  
  /** 按分析人维度 */
  byAnalyst: {
    analyst: string;
    hasCompetitorSku: number;
    yCount: number;
    nCount: number;
    noSaleCount: number;
    soldCount: number;
    soldRate: string;
    prevSoldRate: string;
    change: string;
  }[];
  
  /** 按品线维度 */
  byCategory: {
    category: string;
    hasCompetitorSku: number;
    yCount: number;
    nCount: number;
    noSaleCount: number;
    soldCount: number;
    soldRate: string;
    prevSoldRate: string;
    change: string;
  }[];
}

// ==================== 新品未出单原因 ====================
/** 有对手未出单新品 */
export interface HasCompetitorUnsold {
  total: number;
  prevTotal: number;
  change: number;
  reasons: {
    reason: string;
    curCount: number;
    curRatio: string;
    prevCount: number;
    prevRatio: string;
    change: number;
  }[];
  byAnalyst: {
    analyst: string;
    competitiveWeak: number;
    noMarket: number;
    noPriceAdv: number;
    overseas: number;
    normal: number;
    na: number;
    unknown: number;
    total: number;
  }[];
  byCategory: {
    category: string;
    competitiveWeak: number;
    noMarket: number;
    noPriceAdv: number;
    overseas: number;
    normal: number;
    na: number;
    unknown: number;
    total: number;
  }[];
}

/** 无对手未出单新品 */
export interface NoCompetitorUnsold {
  total: number;
  prevTotal: number;
  change: number;
  reasons: {
    reason: string;
    curCount: number;
    curRatio: string;
    prevCount: number;
    prevRatio: string;
    change: number;
  }[];
  byAnalyst: {
    analyst: string;
    noMarket: number;
    unknown: number;
    competitiveWeak: number;
    na: number;
    other: number;
    total: number;
  }[];
  byCategory: {
    category: string;
    noMarket: number;
    unknown: number;
    competitiveWeak: number;
    na: number;
    other: number;
    total: number;
  }[];
}

export interface UnsoldReasonData {
  hasCompetitor: HasCompetitorUnsold;
  noCompetitor: NoCompetitorUnsold;
}

// ==================== 新品PLG维度 ====================
export interface PLGRecord {
  salesCode: string;
  sku: string;
  launchDate: string;
  firstSaleDate: string;
  analyst: string;
  category: string;
  expandType: string;
  curSalesQty: number;
  prevSalesQty: number;
  curRevenue: number;
  curCompetitorQty: number;
  curMarketShare: string;
  curMarketStatus: string;
  curOperation: string;
  plpEnabled: string;
  plgFee: string;
}

export interface PLGData {
  records: PLGRecord[];
  /** PLP=Y且PLG费率>0% */
  plpAndPlgBothCount: number;
  /** PLP未开但PLG费率>0% */
  plgOnlyCount: number;
  /** PLP=Y且PLG费率=0% */
  plpOnlyCount: number;
  /** PLP未开且PLG费率=0% */
  noAdCount: number;
  /** PLP未开且未出单 */
  plpDisabledNoSaleCount: number;
  /** PLP开启数 */
  plpEnabledCount?: number;
  /** 新品总数 */
  totalNewProducts?: number;
  /** @deprecated */
  totalLowShare?: number;
  /** 按分析人拆分 */
  byAnalyst?: { analyst: string; total: number; plpAndPlgBoth: number; plgOnly: number; plpOnly: number; noAd: number; plpDisabledNoSale: number }[];
}

// ==================== 新品状态异常 ====================
export interface NewProductAnomaly {
  ruleId: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
  affectedItems: string[];
  recommendation: string;
}

// ==================== 完整数据 ====================
export interface NewProductStatusData {
  currentPeriod: string;
  previousPeriod: string;
  overall: OverallData;
  categoryMetrics: CategoryMetrics[];
  analystMetrics: AnalystMetrics[];
  expandTypeMetrics: ExpandTypeMetrics[];
  timelinessData: TimelinessData;
  lowShareRecords: LowShareRecord[];
  plpData: PLPData;
  salesSituation: SalesSituationDetail;
  unsoldReason: UnsoldReasonData;
  plgData: PLGData;
}

export type NewProductStatusAdapterResult = {
  data: NewProductStatusData | null;
  anomalies: NewProductAnomaly[];
  summary: ModuleStatusSummary;
  isEmpty: boolean;
};

// ==================== 数据转换函数 ====================

/**
 * 从JSON数据转换为新品状态数据
 * @param jsonData 从 sheets_{周期}.json 读取的数据
 */
export function parseNewProductStatusData(jsonData: Record<string, unknown[][]>): NewProductStatusData {
  // 周期信息
  const currentPeriod = '4.30-5.6';
  const previousPeriod = '4.23-4.29';
  
  // 解析总体数据
  const overallData = parseOverallData(jsonData['总体数据'] || []);
  
  // 解析品线维度
  const categoryMetrics = parseCategoryMetrics(jsonData['品线维度'] || []);
  
  // 解析分析人维度
  const analystMetrics = parseAnalystMetrics(jsonData['分析人维度'] || []);
  
  // 解析拓展类型
  const expandTypeMetrics = parseExpandTypeMetrics(jsonData['拓展类型'] || []);
  
  // 解析分析及时率
  const timelinessData = parseTimelinessData(jsonData['分析及时率'] || []);
  
  // 解析低占比新品
  const lowShareRecords = parseLowShareRecords(jsonData['低占比新品'] || []);
  
  // 解析新品PLP
  const plpData = parsePLPData(jsonData['新品PLP'] || []);
  
  // 解析新品出单情况
  const salesSituation = parseSalesSituation(jsonData['新品出单情况'] || []);
  
  // 解析新品未出单原因
  const unsoldReason = parseUnsoldReason(jsonData['新品未出单原因'] || []);
  
  // 解析新品PLG维度
  const plgData = parsePLGData(jsonData['新品PLG维度'] || []);
  
  return {
    currentPeriod,
    previousPeriod,
    overall: overallData,
    categoryMetrics,
    analystMetrics,
    expandTypeMetrics,
    timelinessData,
    lowShareRecords,
    plpData,
    salesSituation,
    unsoldReason,
    plgData,
  };
}

function parseOverallData(rows: unknown[][]): OverallData {
  // 总体数据结构: [指标, 本周值, 上周值, 环比]
  const kpi: OverallKPI = {
    totalSku: 0,
    curNewSku: 0,
    prevNewSku: 0,
    totalSalesQty: 0,
    prevTotalSalesQty: 0,
    salesQtyChange: '',
    totalRevenue: 0,
    prevTotalRevenue: 0,
    revenueChange: '',
    hasCompetitorSku: 0,
    prevHasCompetitorSku: 0,
    noCompetitorSku: 0,
    prevNoCompetitorSku: 0,
  };
  
  const timeliness: TimelinessMetrics = {
    timelyCount: 0,
    noAnalysis8dCount: 0,
    noAnalysis7dCount: 0,
    totalCount: 0,
    timelyRate: '',
    prevTimelyCount: 0,
    prevTimelyRate: '',
    change: '',
  };
  
  const salesSituation: SalesSituationMetrics = {
    hasCompetitorSku: 0,
    prevHasCompetitorSku: 0,
    change: 0,
    yCount: 0,
    prevYCount: 0,
    yChange: 0,
    nCount: 0,
    prevNCount: 0,
    nChange: 0,
    noSaleCount: 0,
    prevNoSaleCount: 0,
    noSaleChange: 0,
    soldCount: 0,
    prevSoldCount: 0,
    soldChange: 0,
    soldRate: '',
    prevSoldRate: '',
  };
  
  // 解析每一行
  for (const row of rows) {
    if (!row || row.length < 2) continue;
    const label = String(row[0] || '');
    
    // 一、总体概况
    if (label === '累计SKU数') {
      kpi.totalSku = Number(row[1]) || 0;
    } else if (label === '本周新上架SKU') {
      kpi.curNewSku = Number(row[1]) || 0;
      kpi.prevNewSku = Number(row[2]) || 0;
    } else if (label === '总销量') {
      kpi.totalSalesQty = Number(row[1]) || 0;
      kpi.prevTotalSalesQty = Number(row[2]) || 0;
      kpi.salesQtyChange = String(row[3] || '');
    } else if (label === '总销售额(USD)') {
      kpi.totalRevenue = Number(row[1]) || 0;
      kpi.prevTotalRevenue = Number(row[2]) || 0;
      kpi.revenueChange = String(row[3] || '');
    } else if (label === '有对手SKU数') {
      kpi.hasCompetitorSku = Number(row[1]) || 0;
      kpi.prevHasCompetitorSku = Number(row[2]) || 0;
    } else if (label === '无对手SKU数') {
      kpi.noCompetitorSku = Number(row[1]) || 0;
      kpi.prevNoCompetitorSku = Number(row[2]) || 0;
    }
    // 二、分析及时率
    else if (label === '及时分析产品数') {
      timeliness.timelyCount = Number(row[1]) || 0;
      timeliness.prevTimelyCount = Number(row[2]) || 0;
    } else if (label === '8日内新品无分析数') {
      timeliness.noAnalysis8dCount = Number(row[1]) || 0;
    } else if (label === '超7日低占比未分析数') {
      timeliness.noAnalysis7dCount = Number(row[1]) || 0;
    } else if (label === '统计总数') {
      timeliness.totalCount = Number(row[1]) || 0;
    } else if (label === '及时分析率') {
      timeliness.timelyRate = String(row[1] || '');
      timeliness.prevTimelyRate = String(row[2] || '');
      timeliness.change = String(row[3] || '');
    }
    // 三、新品出单情况
    else if (label === '有对手总SKU') {
      salesSituation.hasCompetitorSku = Number(row[1]) || 0;
      salesSituation.prevHasCompetitorSku = Number(row[2]) || 0;
      salesSituation.change = Number(row[3]) || 0;
    } else if (label === '8日内出单（Y）') {
      salesSituation.yCount = Number(row[1]) || 0;
      salesSituation.prevYCount = Number(row[2]) || 0;
      salesSituation.yChange = Number(row[3]) || 0;
    } else if (label === '8日外出单（N）') {
      salesSituation.nCount = Number(row[1]) || 0;
      salesSituation.prevNCount = Number(row[2]) || 0;
      salesSituation.nChange = Number(row[3]) || 0;
    } else if (label === '真正未出单') {
      salesSituation.noSaleCount = Number(row[1]) || 0;
      salesSituation.prevNoSaleCount = Number(row[2]) || 0;
      salesSituation.noSaleChange = Number(row[3]) || 0;
    } else if (label === '已出单合计(Y+N)') {
      salesSituation.soldCount = Number(row[1]) || 0;
      salesSituation.prevSoldCount = Number(row[2]) || 0;
      salesSituation.soldChange = Number(row[3]) || 0;
    } else if (label === '出单率') {
      salesSituation.soldRate = String(row[1] || '');
      salesSituation.prevSoldRate = String(row[2] || '');
    }
  }
  
  return { kpi, timeliness, salesSituation };
}

function parseCategoryMetrics(rows: unknown[][]): CategoryMetrics[] {
  const result: CategoryMetrics[] = [];
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 2) continue;
    const category = String(row[0] || '');
    if (!category || category === '合计') continue;
    
    result.push({
      category,
      curSku: Number(row[1]) || 0,
      curNewSku: Number(row[2]) || 0,
      curSalesQty: Number(row[3]) || 0,
      prevSalesQty: Number(row[4]) || 0,
      salesQtyChange: String(row[5] || ''),
      curRevenue: Number(row[6]) || 0,
      prevRevenue: Number(row[7]) || 0,
      revenueChange: String(row[8] || ''),
      curHasCompetitor: Number(row[9]) || 0,
      prevHasCompetitor: Number(row[10]) || 0,
    });
  }
  return result;
}

function parseAnalystMetrics(rows: unknown[][]): AnalystMetrics[] {
  const result: AnalystMetrics[] = [];
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 2) continue;
    const analyst = String(row[0] || '');
    if (!analyst || analyst === '合计') continue;
    
    result.push({
      analyst,
      curSku: Number(row[1]) || 0,
      curNewSku: Number(row[2]) || 0,
      curSalesQty: Number(row[3]) || 0,
      prevSalesQty: Number(row[4]) || 0,
      salesQtyChange: String(row[5] || ''),
      curRevenue: Number(row[6]) || 0,
      prevRevenue: Number(row[7]) || 0,
      revenueChange: String(row[8] || ''),
    });
  }
  return result;
}

function parseExpandTypeMetrics(rows: unknown[][]): ExpandTypeMetrics[] {
  const result: ExpandTypeMetrics[] = [];
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 2) continue;
    const expandType = String(row[0] || '');
    if (!expandType) continue;
    
    result.push({
      expandType,
      curSku: Number(row[1]) || 0,
      prevSku: Number(row[2]) || 0,
      curSalesCount: Number(row[3]) || 0,
      curSalesRate: String(row[4] || ''),
      prevSalesCount: Number(row[5]) || 0,
      prevSalesRate: String(row[6] || ''),
      salesRateChange: String(row[7] || ''),
      curSalesQty: Number(row[8]) || 0,
      prevSalesQty: Number(row[9]) || 0,
      salesQtyChange: String(row[10] || ''),
      curRevenue: Number(row[11]) || 0,
      prevRevenue: Number(row[12]) || 0,
      revenueChange: String(row[13] || ''),
    });
  }
  return result;
}

function parseTimelinessData(rows: unknown[][]): TimelinessData {
  const analysts: AnalystTimeliness[] = [];
  let total: AnalystTimeliness | null = null;
  
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 2) continue;
    const analyst = String(row[0] || '');
    if (!analyst) continue;
    
    const item: AnalystTimeliness = {
      analyst,
      curSku: Number(row[1]) || 0,
      timelyCount: Number(row[2]) || 0,
      noAnalysis8dCount: Number(row[3]) || 0,
      noAnalysis7dCount: Number(row[4]) || 0,
      timelyRate: String(row[5] || ''),
      prevSku: Number(row[6]) || 0,
      prevTimelyCount: Number(row[7]) || 0,
      prevTimelyRate: String(row[8] || ''),
      change: String(row[9] || ''),
    };
    
    if (analyst === '合计') {
      total = item;
    } else {
      analysts.push(item);
    }
  }
  
  return { analysts, total: total || analysts[analysts.length - 1] || {
    analyst: '合计',
    curSku: 0, timelyCount: 0, noAnalysis8dCount: 0, noAnalysis7dCount: 0,
    timelyRate: '', prevSku: 0, prevTimelyCount: 0, prevTimelyRate: '', change: ''
  }};
}

function parseLowShareRecords(rows: unknown[][]): LowShareRecord[] {
  const result: LowShareRecord[] = [];
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 5) continue;
    const salesCode = String(row[0] || '');
    if (!salesCode || salesCode.includes('销售编号')) continue;
    
    result.push({
      salesCode,
      sku: String(row[1] || ''),
      launchDate: String(row[2] || ''),
      analyst: String(row[3] || ''),
      category: String(row[4] || ''),
      expandType: String(row[5] || ''),
      curSalesQty: Number(row[6]) || 0,
      salesQtyChange: String(row[7] || ''),
      curRevenue: Number(row[8]) || 0,
      revenueChange: String(row[9] || ''),
      prevCompetitorQty: Number(row[10]) || 0,
      curCompetitorQty: Number(row[11]) || 0,
      competitorQtyChange: String(row[12] || ''),
      prevMarketShare: String(row[13] || ''),
      curMarketShare: String(row[14] || ''),
      marketShareChange: String(row[15] || ''),
      cur8dStatus: String(row[16] || ''),
      cur7dFreqTag: String(row[17] || ''),
      prevMarketStatus: String(row[18] || ''),
      curOperation: String(row[19] || ''),
      curMarketStatus: String(row[20] || ''),
      plpEnabled: String(row[21] || ''),
      plgFee: String(row[22] || ''),
    });
  }
  return result;
}

function parsePLPData(rows: unknown[][]): PLPData {
  const result: PLPData = {
    total: createEmptyPLPMetrics(),
    prevTotal: createEmptyPLPMetrics(),
    analysts: [],
    categories: [],
    expandTypes: [],
    detailRecords: [],
  };
  
  let section = '';
  for (const row of rows) {
    if (!row || row.length < 2) continue;
    const firstCell = String(row[0] || '').trim();
    
    if (firstCell.includes('【总数据】')) {
      section = 'total';
    } else if (firstCell.includes('【分析人维度】')) {
      section = 'analyst';
    } else if (firstCell.includes('【品线维度】')) {
      section = 'category';
    } else if (firstCell.includes('【拓展类型维度】')) {
      section = 'expandType';
    } else if (firstCell === '总计') {
      result.total = parsePLPRow(row);
    } else if (firstCell === '上周') {
      result.prevTotal = parsePLPRow(row);
    } else if (section === 'analyst' && firstCell && !firstCell.includes('维度')) {
      result.analysts.push({ ...parsePLPRow(row), analyst: firstCell });
    } else if (section === 'category' && firstCell) {
      result.categories.push({ ...parsePLPRow(row), category: firstCell });
    } else if (section === 'expandType' && firstCell) {
      result.expandTypes.push({ ...parsePLPRow(row), expandType: firstCell });
    }
  }
  
  return result;
}

function createEmptyPLPMetrics(): PLPAdMetrics {
  return {
    campaignCount: 0, linkCount: 0, impression: 0, click: 0, sold: 0,
    cost: 0, revenue: 0, prevRevenue: 0, revenueChange: '', roas: '', cvr: '', ctr: '', cpc: '', cpa: '', acos: '', acoas: '',
  };
}

function parsePLPRow(row: unknown[]): PLPAdMetrics {
  return {
    campaignCount: Number(row[1]) || 0,
    linkCount: Number(row[2]) || 0,
    impression: Number(row[3]) || 0,
    click: Number(row[4]) || 0,
    sold: Number(row[5]) || 0,
    cost: Number(row[6]) || 0,
    revenue: Number(row[7]) || 0,
    prevRevenue: 0,
    revenueChange: '',
    roas: String(row[8] || ''),
    cvr: String(row[9] || ''),
    ctr: String(row[10] || ''),
    cpc: String(row[11] || ''),
    cpa: String(row[12] || ''),
    acos: String(row[13] || ''),
    acoas: String(row[14] || ''),
  };
}

function parseSalesSituation(rows: unknown[][]): SalesSituationDetail {
  const overall: SalesSituationMetrics = {
    hasCompetitorSku: 0, prevHasCompetitorSku: 0, change: 0,
    yCount: 0, prevYCount: 0, yChange: 0,
    nCount: 0, prevNCount: 0, nChange: 0,
    noSaleCount: 0, prevNoSaleCount: 0, noSaleChange: 0,
    soldCount: 0, prevSoldCount: 0, soldChange: 0,
    soldRate: '', prevSoldRate: '',
  };
  
  const byAnalyst: SalesSituationDetail['byAnalyst'] = [];
  const byCategory: SalesSituationDetail['byCategory'] = [];
  
  let outside8dSku = 0, prevOutside8dSku = 0, outside8dChange = 0;
  let section = '';
  
  for (const row of rows) {
    if (!row || row.length < 2) continue;
    const firstCell = String(row[0] || '').trim();
    
    if (firstCell.includes('【总体出单情况】')) {
      section = 'overall';
    } else if (firstCell.includes('8日外（4.29前上架）')) {
      section = 'outside8d';
    } else if (firstCell.includes('【按分析人维度】')) {
      section = 'byAnalyst';
    } else if (firstCell.includes('【按品线维度】')) {
      section = 'byCategory';
    } else if (section === 'overall') {
      if (firstCell === '有对手总SKU') {
        overall.hasCompetitorSku = Number(row[1]) || 0;
        overall.prevHasCompetitorSku = Number(row[2]) || 0;
        overall.change = Number(row[3]) || 0;
      } else if (firstCell === '8日内出单（Y）') {
        overall.yCount = Number(row[1]) || 0;
        overall.prevYCount = Number(row[2]) || 0;
        overall.yChange = Number(row[3]) || 0;
      } else if (firstCell === '8日外出单（N）') {
        overall.nCount = Number(row[1]) || 0;
        overall.prevNCount = Number(row[2]) || 0;
        overall.nChange = Number(row[3]) || 0;
      } else if (firstCell === '真正未出单') {
        overall.noSaleCount = Number(row[1]) || 0;
        overall.prevNoSaleCount = Number(row[2]) || 0;
        overall.noSaleChange = Number(row[3]) || 0;
      } else if (firstCell === '已出单合计(Y+N)') {
        overall.soldCount = Number(row[1]) || 0;
        overall.prevSoldCount = Number(row[2]) || 0;
        overall.soldChange = Number(row[3]) || 0;
      } else if (firstCell === '出单率') {
        overall.soldRate = String(row[1] || '');
        overall.prevSoldRate = String(row[2] || '');
      }
    } else if (section === 'outside8d') {
      if (firstCell === '8日外SKU') {
        outside8dSku = Number(row[1]) || 0;
        prevOutside8dSku = Number(row[2]) || 0;
        outside8dChange = Number(row[3]) || 0;
      }
    } else if (section === 'byAnalyst' && firstCell && !firstCell.includes('分析人')) {
      byAnalyst.push({
        analyst: firstCell,
        hasCompetitorSku: Number(row[1]) || 0,
        yCount: Number(row[2]) || 0,
        nCount: Number(row[3]) || 0,
        noSaleCount: Number(row[4]) || 0,
        soldCount: Number(row[5]) || 0,
        soldRate: String(row[6] || ''),
        prevSoldRate: String(row[7] || ''),
        change: String(row[8] || ''),
      });
    } else if (section === 'byCategory' && firstCell && !firstCell.includes('品线')) {
      byCategory.push({
        category: firstCell,
        hasCompetitorSku: Number(row[1]) || 0,
        yCount: Number(row[2]) || 0,
        nCount: Number(row[3]) || 0,
        noSaleCount: Number(row[4]) || 0,
        soldCount: Number(row[5]) || 0,
        soldRate: String(row[6] || ''),
        prevSoldRate: String(row[7] || ''),
        change: String(row[8] || ''),
      });
    }
  }
  
  return { overall, outside8dSku, prevOutside8dSku, outside8dChange, byAnalyst, byCategory };
}

function parseUnsoldReason(rows: unknown[][]): UnsoldReasonData {
  const hasCompetitor: HasCompetitorUnsold = {
    total: 0, prevTotal: 0, change: 0,
    reasons: [], byAnalyst: [], byCategory: [],
  };
  
  const noCompetitor: NoCompetitorUnsold = {
    total: 0, prevTotal: 0, change: 0,
    reasons: [], byAnalyst: [], byCategory: [],
  };
  
  let section = '';
  
  for (const row of rows) {
    if (!row || row.length < 2) continue;
    const firstCell = String(row[0] || '').trim();
    
    if (firstCell.includes('【A. 有对手未出单新品】')) {
      section = 'hasCompetitorTotal';
    } else if (firstCell.includes('【A1】')) {
      section = 'hasCompetitorReason';
    } else if (firstCell.includes('【A2】')) {
      section = 'hasCompetitorByAnalyst';
    } else if (firstCell.includes('【A3】')) {
      section = 'hasCompetitorByCategory';
    } else if (firstCell.includes('【B. 无对手未出单新品】')) {
      section = 'noCompetitorTotal';
    } else if (firstCell.includes('【B1】')) {
      section = 'noCompetitorReason';
    } else if (firstCell.includes('【B2】')) {
      section = 'noCompetitorByAnalyst';
    } else if (firstCell.includes('【B3】')) {
      section = 'noCompetitorByCategory';
    } else if (section === 'hasCompetitorTotal') {
      const match = firstCell.match(/本周:\s*(\d+).*上周:\s*(\d+)/);
      if (match) {
        hasCompetitor.total = Number(match[1]);
        hasCompetitor.prevTotal = Number(match[2]);
        hasCompetitor.change = hasCompetitor.total - hasCompetitor.prevTotal;
      }
    } else if (section === 'hasCompetitorReason') {
      const reason = firstCell;
      if (reason && !reason.includes('市场状态')) {
        hasCompetitor.reasons.push({
          reason,
          curCount: Number(row[1]) || 0,
          curRatio: String(row[2] || ''),
          prevCount: Number(row[3]) || 0,
          prevRatio: String(row[4] || ''),
          change: Number(row[5]) || 0,
        });
      }
    } else if (section === 'noCompetitorTotal') {
      const match = firstCell.match(/本周:\s*(\d+).*上周:\s*(\d+)/);
      if (match) {
        noCompetitor.total = Number(match[1]);
        noCompetitor.prevTotal = Number(match[2]);
        noCompetitor.change = noCompetitor.total - noCompetitor.prevTotal;
      }
    } else if (section === 'noCompetitorReason') {
      const reason = firstCell;
      if (reason && !reason.includes('市场状态')) {
        noCompetitor.reasons.push({
          reason,
          curCount: Number(row[1]) || 0,
          curRatio: String(row[2] || ''),
          prevCount: Number(row[3]) || 0,
          prevRatio: String(row[4] || ''),
          change: Number(row[5]) || 0,
        });
      }
    }
  }
  
  return { hasCompetitor, noCompetitor };
}

function parsePLGData(rows: unknown[][]): PLGData {
  const records: PLGRecord[] = [];
  let plgEnabledCount = 0;
  let plpDisabledNoSaleCount = 0;
  let plpDisabledPlgActiveCount = 0;
  
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 5) continue;
    const salesCode = String(row[0] || '');
    if (!salesCode || isNaN(Number(salesCode))) continue;
    
    const plpEnabled = String(row[14] || '');
    const plgFee = String(row[15] || '');
    const firstSaleDate = String(row[3] || '');
    
    // 统计
    if (plpEnabled === 'Y' && parseFloat(plgFee) > 0) {
      plgEnabledCount++;
    }
    if (plpEnabled === 'N' && firstSaleDate === '未出单') {
      plpDisabledNoSaleCount++;
    }
    if (plpEnabled === 'N' && parseFloat(plgFee) > 0) {
      plpDisabledPlgActiveCount++;
    }
    
    records.push({
      salesCode,
      sku: String(row[1] || ''),
      launchDate: String(row[2] || ''),
      firstSaleDate,
      analyst: String(row[4] || ''),
      category: String(row[5] || ''),
      expandType: String(row[6] || ''),
      curSalesQty: Number(row[7]) || 0,
      prevSalesQty: Number(row[8]) || 0,
      curRevenue: Number(row[9]) || 0,
      curCompetitorQty: Number(row[10]) || 0,
      curMarketShare: String(row[11] || ''),
      curMarketStatus: String(row[12] || ''),
      curOperation: String(row[13] || ''),
      plpEnabled,
      plgFee,
    });
  }
  
  return { records, plpAndPlgBothCount: plgEnabledCount, plgOnlyCount: plpDisabledPlgActiveCount, plpOnlyCount: 0, noAdCount: 0, plpDisabledNoSaleCount };
}

// ==================== Demo 数据 ====================
export const mockNewProductStatusData: NewProductStatusData = {
  currentPeriod: '5.14-5.20',
  previousPeriod: '5.7-5.13',
  overall: {
    kpi: {
      totalSku: 134,
      curNewSku: 18,
      prevNewSku: 15,
      totalSalesQty: 185,
      prevTotalSalesQty: 184,
      salesQtyChange: '+0.5%',
      totalRevenue: 17618.93,
      prevTotalRevenue: 18897.55,
      revenueChange: '-6.8%',
      hasCompetitorSku: 48,
      prevHasCompetitorSku: 45,
      noCompetitorSku: 86,
      prevNoCompetitorSku: 81,
    },
    timeliness: {
      timelyCount: 88,
      noAnalysis8dCount: 5,
      noAnalysis7dCount: 41,
      totalCount: 134,
      timelyRate: '65.7%',
      prevTimelyCount: 86,
      prevTimelyRate: '68.3%',
      change: '-2.6%',
    },
    salesSituation: {
      hasCompetitorSku: 48,
      prevHasCompetitorSku: 45,
      change: 3,
      yCount: 29,
      prevYCount: 27,
      yChange: 2,
      nCount: 14,
      prevNCount: 13,
      nChange: 1,
      noSaleCount: 5,
      prevNoSaleCount: 5,
      noSaleChange: 0,
      soldCount: 43,
      prevSoldCount: 40,
      soldChange: 3,
      soldRate: '89.6%',
      prevSoldRate: '88.9%',
    },
  },
  categoryMetrics: [
    { category: '其他', curSku: 11, curNewSku: 3, curSalesQty: 36, prevSalesQty: 19, salesQtyChange: '+89.5%', curRevenue: 2349.47, prevRevenue: 1261.42, revenueChange: '+86.3%', curHasCompetitor: 2, prevHasCompetitor: 3 },
    { category: '挡泥板', curSku: 4, curNewSku: 0, curSalesQty: 19, prevSalesQty: 3, salesQtyChange: '+533.3%', curRevenue: 1079, prevRevenue: 135, revenueChange: '+699.3%', curHasCompetitor: 4, prevHasCompetitor: 3 },
    { category: '机盖及附件', curSku: 7, curNewSku: 2, curSalesQty: 38, prevSalesQty: 24, salesQtyChange: '+58.3%', curRevenue: 2639, prevRevenue: 1721, revenueChange: '+53.3%', curHasCompetitor: 7, prevHasCompetitor: 4 },
    { category: '牌照板支架', curSku: 1, curNewSku: 1, curSalesQty: 1, prevSalesQty: 0, salesQtyChange: '-', curRevenue: 45, prevRevenue: 0, revenueChange: '-', curHasCompetitor: 1, prevHasCompetitor: 0 },
    { category: '车身外扩件', curSku: 6, curNewSku: 1, curSalesQty: 8, prevSalesQty: 3, salesQtyChange: '+166.7%', curRevenue: 682, prevRevenue: 210, revenueChange: '+224.8%', curHasCompetitor: 6, prevHasCompetitor: 5 },
    { category: '车门系统', curSku: 17, curNewSku: 4, curSalesQty: 82, prevSalesQty: 40, salesQtyChange: '+105.0%', curRevenue: 14170.02, prevRevenue: 6906.5, revenueChange: '+105.2%', curHasCompetitor: 17, prevHasCompetitor: 14 },
    { category: '饰条', curSku: 6, curNewSku: 0, curSalesQty: 11, prevSalesQty: 4, salesQtyChange: '+175.0%', curRevenue: 530.51, prevRevenue: 178, revenueChange: '+198.0%', curHasCompetitor: 6, prevHasCompetitor: 3 },
  ],
  analystMetrics: [
    { analyst: '俞东旭', curSku: 12, curNewSku: 3, curSalesQty: 38, prevSalesQty: 23, salesQtyChange: '+65.2%', curRevenue: 6379.53, prevRevenue: 3953.92, revenueChange: '+61.3%' },
    { analyst: '张潇', curSku: 16, curNewSku: 4, curSalesQty: 58, prevSalesQty: 37, salesQtyChange: '+56.8%', curRevenue: 4920, prevRevenue: 3131, revenueChange: '+57.1%' },
    { analyst: '朱培源', curSku: 8, curNewSku: 0, curSalesQty: 34, prevSalesQty: 10, salesQtyChange: '+240.0%', curRevenue: 2158, prevRevenue: 575, revenueChange: '+275.3%' },
    { analyst: '王偲涵', curSku: 10, curNewSku: 2, curSalesQty: 21, prevSalesQty: 13, salesQtyChange: '+61.5%', curRevenue: 1830, prevRevenue: 1338, revenueChange: '+36.8%' },
    { analyst: '章鹏', curSku: 1, curNewSku: 1, curSalesQty: 1, prevSalesQty: 0, salesQtyChange: '-', curRevenue: 45, prevRevenue: 0, revenueChange: '-' },
    { analyst: '胡煜星', curSku: 15, curNewSku: 1, curSalesQty: 43, prevSalesQty: 10, salesQtyChange: '+330.0%', curRevenue: 6162.47, prevRevenue: 1514.5, revenueChange: '+306.9%' },
  ],
  expandTypeMetrics: [
    { expandType: '原开品', curSku: 32, prevSku: 32, curSalesCount: 24, curSalesRate: '75.0%', prevSalesCount: 22, prevSalesRate: '68.8%', salesRateChange: '+9.0%', curSalesQty: 116, prevSalesQty: 55, salesQtyChange: '+110.9%', curRevenue: 13505.6, prevRevenue: 8750.22, revenueChange: '+54.3%' },
    { expandType: '拓展品', curSku: 13, prevSku: 13, curSalesCount: 11, curSalesRate: '84.6%', prevSalesCount: 9, prevSalesRate: '69.2%', salesRateChange: '+22.2%', curSalesQty: 68, prevSalesQty: 28, salesQtyChange: '+142.9%', curRevenue: 6989.25, prevRevenue: 4938.17, revenueChange: '+41.5%' },
    { expandType: '组合件', curSku: 4, prevSku: 4, curSalesCount: 2, curSalesRate: '50.0%', prevSalesCount: 2, prevSalesRate: '50.0%', salesRateChange: '+0.0%', curSalesQty: 11, prevSalesQty: 6, salesQtyChange: '+83.3%', curRevenue: 0, prevRevenue: 0, revenueChange: '-' },
    { expandType: '配件', curSku: 3, prevSku: 3, curSalesCount: 2, curSalesRate: '66.7%', prevSalesCount: 1, prevSalesRate: '33.3%', salesRateChange: '+100.0%', curSalesQty: 0, prevSalesQty: 0, salesQtyChange: '-', curRevenue: 0, prevRevenue: 0, revenueChange: '-' },
  ],
  timelinessData: {
    analysts: [
      { analyst: '俞东旭', curSku: 12, timelyCount: 10, noAnalysis8dCount: 2, noAnalysis7dCount: 0, timelyRate: '83.3%', prevSku: 12, prevTimelyCount: 9, prevTimelyRate: '73.9%', change: '+9.4%' },
      { analyst: '张潇', curSku: 16, timelyCount: 13, noAnalysis8dCount: 2, noAnalysis7dCount: 1, timelyRate: '81.3%', prevSku: 16, prevTimelyCount: 11, prevTimelyRate: '70.3%', change: '+11.0%' },
      { analyst: '朱培源', curSku: 8, timelyCount: 6, noAnalysis8dCount: 2, noAnalysis7dCount: 0, timelyRate: '75.0%', prevSku: 8, prevTimelyCount: 6, prevTimelyRate: '70.0%', change: '+5.0%' },
      { analyst: '王偲涵', curSku: 10, timelyCount: 7, noAnalysis8dCount: 2, noAnalysis7dCount: 1, timelyRate: '70.0%', prevSku: 10, prevTimelyCount: 8, prevTimelyRate: '76.9%', change: '-6.9%' },
      { analyst: '章鹏', curSku: 1, timelyCount: 0, noAnalysis8dCount: 0, noAnalysis7dCount: 1, timelyRate: '0%', prevSku: 1, prevTimelyCount: 0, prevTimelyRate: '0%', change: '-' },
      { analyst: '胡煜星', curSku: 15, timelyCount: 11, noAnalysis8dCount: 2, noAnalysis7dCount: 2, timelyRate: '73.3%', prevSku: 15, prevTimelyCount: 10, prevTimelyRate: '70.0%', change: '+3.3%' },
    ],
    total: { analyst: '合计', curSku: 101, timelyCount: 71, noAnalysis8dCount: 16, noAnalysis7dCount: 15, timelyRate: '70.3%', prevSku: 90, prevTimelyCount: 58, prevTimelyRate: '64.4%', change: '+9.2%' },
  },
  lowShareRecords: [
    { salesCode:'12252', sku:'LYAP-X1800-1', launchDate:'2026-03-04', analyst:'胡煜星', category:'车门系统', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:40, revenueChange:'N/A', prevCompetitorQty:7, curCompetitorQty:7, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'12.5%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'Y', plgFee:'0.5%' },
    { salesCode:'12165', sku:'LYAP-X1877', launchDate:'2026-03-04', analyst:'朱培源', category:'挡泥板', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:169, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'11102', sku:'LYAM-X2254-L', launchDate:'2026-03-04', analyst:'张潇', category:'车门系统', expandType:'原开品', curSalesQty:5, salesQtyChange:'N/A', curRevenue:140.95, revenueChange:'N/A', prevCompetitorQty:5, curCompetitorQty:5, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'58.3%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12205', sku:'LYAP-X1800S-1L', launchDate:'2026-03-05', analyst:'胡煜星', category:'车门系统', expandType:'原开品', curSalesQty:10, salesQtyChange:'N/A', curRevenue:220, revenueChange:'N/A', prevCompetitorQty:20, curCompetitorQty:20, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'35.5%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12206', sku:'LYAP-X1800S-1R', launchDate:'2026-03-05', analyst:'胡煜星', category:'车门系统', expandType:'原开品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:44, revenueChange:'N/A', prevCompetitorQty:6, curCompetitorQty:6, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'25.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12244', sku:'LYAP-X2190-L', launchDate:'2026-03-10', analyst:'张潇', category:'饰条', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'无市场', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12243', sku:'LYAP-X2190-R', launchDate:'2026-03-10', analyst:'张潇', category:'饰条', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:38, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12304', sku:'LYAP-X1642-GR', launchDate:'2026-03-11', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12085', sku:'LYAP-X1911-BK', launchDate:'2026-03-11', analyst:'张潇', category:'机盖及附件', expandType:'拓展品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:170, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'66.7%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12258', sku:'LYAP-X1927', launchDate:'2026-03-11', analyst:'张潇', category:'机盖及附件', expandType:'原开品', curSalesQty:13, salesQtyChange:'N/A', curRevenue:364, revenueChange:'N/A', prevCompetitorQty:17, curCompetitorQty:17, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'34.6%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'Y', plgFee:'1.2%' },
    { salesCode:'12210', sku:'LYAP-X1934', launchDate:'2026-03-11', analyst:'张潇', category:'饰条', expandType:'原开品', curSalesQty:6, salesQtyChange:'N/A', curRevenue:69.04, revenueChange:'N/A', prevCompetitorQty:20, curCompetitorQty:20, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'16.7%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12250', sku:'LYAP-X2148-1L', launchDate:'2026-03-11', analyst:'王偲涵', category:'饰条', expandType:'拓展品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:78, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12332', sku:'LYAP-X2289', launchDate:'2026-03-11', analyst:'张潇', category:'饰条', expandType:'原开品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:228, revenueChange:'N/A', prevCompetitorQty:3, curCompetitorQty:3, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12309', sku:'MD-002-FL', launchDate:'2026-03-11', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12310', sku:'MD-002-FR', launchDate:'2026-03-11', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:483, revenueChange:'N/A', prevCompetitorQty:4, curCompetitorQty:4, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'33.3%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12311', sku:'MD-002-RL', launchDate:'2026-03-11', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12312', sku:'MD-002-RR', launchDate:'2026-03-11', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:478, revenueChange:'N/A', prevCompetitorQty:4, curCompetitorQty:4, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'33.3%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12441', sku:'LYAM-X2862', launchDate:'2026-03-12', analyst:'张潇', category:'机盖及附件', expandType:'原开品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:278, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12271', sku:'LYAP-X1651-1L', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'无市场', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12270', sku:'LYAP-X1651-1R', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:270, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12318', sku:'LYAP-X1676', launchDate:'2026-03-16', analyst:'胡煜星', category:'车门系统', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:460, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12320', sku:'LYAP-X2417', launchDate:'2026-03-16', analyst:'朱培源', category:'挡泥板', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:75, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12305', sku:'MD-001-FL', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:3, salesQtyChange:'N/A', curRevenue:1770, revenueChange:'N/A', prevCompetitorQty:3, curCompetitorQty:3, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'40.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12321', sku:'LYAP-X1788-GR', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:4, salesQtyChange:'N/A', curRevenue:143.6, revenueChange:'N/A', prevCompetitorQty:3, curCompetitorQty:3, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12272', sku:'LYAP-X1808', launchDate:'2026-03-16', analyst:'胡煜星', category:'车门系统', expandType:'原开品', curSalesQty:5, salesQtyChange:'N/A', curRevenue:340, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12292', sku:'LYAP-X1879', launchDate:'2026-03-16', analyst:'朱培源', category:'挡泥板', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:95, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12333', sku:'LYAP-X2429', launchDate:'2026-03-16', analyst:'朱培源', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12334', sku:'LYAP-X2523', launchDate:'2026-03-16', analyst:'朱培源', category:'车门系统', expandType:'原开品', curSalesQty:4, salesQtyChange:'N/A', curRevenue:396, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12368', sku:'LYAP-X2530', launchDate:'2026-03-16', analyst:'胡煜星', category:'其他', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:95, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12306', sku:'MD-001-FR', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:3, salesQtyChange:'N/A', curRevenue:1794, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12307', sku:'MD-001-RL', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12308', sku:'MD-001-RR', launchDate:'2026-03-16', analyst:'俞东旭', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12293', sku:'LYAP-X2144-1', launchDate:'2026-03-18', analyst:'朱培源', category:'车门系统', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'无市场', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12298', sku:'LYAP-X2144-1L', launchDate:'2026-03-18', analyst:'朱培源', category:'车门系统', expandType:'拓展品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:3, curCompetitorQty:3, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'未出单', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12299', sku:'LYAP-X2144-1R', launchDate:'2026-03-18', analyst:'朱培源', category:'车门系统', expandType:'拓展品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12391', sku:'LYAP-X2130-1', launchDate:'2026-03-23', analyst:'张潇', category:'其他', expandType:'原开品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:278, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12398', sku:'LYAP-X2130-2', launchDate:'2026-03-23', analyst:'张潇', category:'其他', expandType:'拓展品', curSalesQty:3, salesQtyChange:'N/A', curRevenue:147, revenueChange:'N/A', prevCompetitorQty:0, curCompetitorQty:0, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'100.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'正常', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12387', sku:'LYAP-X2077', launchDate:'2026-03-24', analyst:'俞东旭', category:'车身外扩件', expandType:'原开品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:70, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'50.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12388', sku:'LYAP-X2085', launchDate:'2026-03-24', analyst:'俞东旭', category:'车身外扩件', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12386', sku:'LYAP-X1788-BN', launchDate:'2026-03-27', analyst:'俞东旭', category:'车门系统', expandType:'拓展品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:30.59, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'33.3%', marketShareChange:'N/A', cur8dStatus:'N', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12461', sku:'LYAM-X2428-BK', launchDate:'2026-04-07', analyst:'俞东旭', category:'车身外扩件', expandType:'拓展品', curSalesQty:3, salesQtyChange:'N/A', curRevenue:357, revenueChange:'N/A', prevCompetitorQty:3, curCompetitorQty:3, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'62.5%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12489', sku:'LYAP-X2504', launchDate:'2026-04-10', analyst:'俞东旭', category:'挡泥板', expandType:'原开品', curSalesQty:7, salesQtyChange:'N/A', curRevenue:315, revenueChange:'N/A', prevCompetitorQty:6, curCompetitorQty:6, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'60.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12480', sku:'LYAM-X2804', launchDate:'2026-04-23', analyst:'张潇', category:'牌照板支架', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:45, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'33.3%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12651', sku:'LYAP-X2210-C', launchDate:'2026-04-28', analyst:'张潇', category:'机盖及附件', expandType:'原开品', curSalesQty:3, salesQtyChange:'N/A', curRevenue:267, revenueChange:'N/A', prevCompetitorQty:6, curCompetitorQty:6, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'25.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12590', sku:'LYAM-X2450-SL', launchDate:'2026-04-29', analyst:'王偲涵', category:'车身外扩件', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:125, revenueChange:'N/A', prevCompetitorQty:4, curCompetitorQty:4, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'20.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12586', sku:'LYAP-X1909', launchDate:'2026-04-29', analyst:'朱培源', category:'机盖及附件', expandType:'原开品', curSalesQty:2, salesQtyChange:'N/A', curRevenue:140, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'33.3%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12615', sku:'LYAP-X2042-FL', launchDate:'2026-04-29', analyst:'王偲涵', category:'其他', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'未出单', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12587', sku:'LYAP-X1360-1L', launchDate:'2026-04-30', analyst:'章鹏', category:'饰条', expandType:'拓展品', curSalesQty:4, salesQtyChange:'N/A', curRevenue:152.89, revenueChange:'N/A', prevCompetitorQty:2, curCompetitorQty:2, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'60.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12629', sku:'LYAP-X2412', launchDate:'2026-04-30', analyst:'王偲涵', category:'车身外扩件', expandType:'原开品', curSalesQty:1, salesQtyChange:'N/A', curRevenue:35, revenueChange:'N/A', prevCompetitorQty:9, curCompetitorQty:9, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'10.0%', marketShareChange:'N/A', cur8dStatus:'Y', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
    { salesCode:'12591', sku:'LYAM-X2452-SL', launchDate:'2026-04-30', analyst:'王偲涵', category:'车身外扩件', expandType:'原开品', curSalesQty:0, salesQtyChange:'N/A', curRevenue:0, revenueChange:'N/A', prevCompetitorQty:1, curCompetitorQty:1, competitorQtyChange:'N/A', prevMarketShare:'N/A', curMarketShare:'0.0%', marketShareChange:'N/A', cur8dStatus:'未出单', cur7dFreqTag:'N/A', prevMarketStatus:'N/A', curOperation:'N/A', curMarketStatus:'竞争无优势', plpEnabled:'N', plgFee:'0%' },
  ],
  plpData: {
    total: { campaignCount: 42, linkCount: 53, impression: 119686, click: 429, sold: 27, cost: 272.56, revenue: 1754.44, prevRevenue: 3401.59, revenueChange: '-48.4%', roas: '14.28', cvr: '6.3%', ctr: '0.36%', cpc: '$0.64', cpa: '$10.09', acos: '23.94%', acoas: '5.61%' },
    prevTotal: { campaignCount: 38, linkCount: 48, impression: 98654, click: 386, sold: 22, cost: 245.32, revenue: 3401.59, prevRevenue: 0, revenueChange: '-', roas: '12.56', cvr: '5.7%', ctr: '0.39%', cpc: '$0.64', cpa: '$11.15', acos: '26.12%', acoas: '5.81%' },
    analysts: [
      { analyst: '俞东旭', campaignCount: 4, linkCount: 5, impression: 64667, click: 121, sold: 0, cost: 99.94, revenue: 0, prevRevenue: 878.62, revenueChange: '-100%', roas: '0', cvr: '0.0%', ctr: '0.19%', cpc: '$0.83', cpa: '$0', acos: '0%', acoas: '-' },
      { analyst: '张潇', campaignCount: 16, linkCount: 18, impression: 9629, click: 121, sold: 21, cost: 48.15, revenue: 1265.11, prevRevenue: 1768, revenueChange: '-28.4%', roas: '26.27', cvr: '17.36%', ctr: '1.26%', cpc: '$0.40', cpa: '$2.29', acos: '3.81%', acoas: '3.51%' },
      { analyst: '朱培源', campaignCount: 4, linkCount: 5, impression: 1015, click: 9, sold: 1, cost: 6.4, revenue: 82.44, prevRevenue: 0, revenueChange: '-', roas: '11.81', cvr: '11.11%', ctr: '0.89%', cpc: '$0.71', cpa: '$6.40', acos: '8.47%', acoas: '7.82%' },
      { analyst: '王偲涵', campaignCount: 8, linkCount: 10, impression: 5131, click: 74, sold: 1, cost: 52.31, revenue: 39, prevRevenue: 0, revenueChange: '-', roas: '2.59', cvr: '1.35%', ctr: '1.44%', cpc: '$0.71', cpa: '$52.31', acos: '38.66%', acoas: '12.44%' },
      { analyst: '章鹏', campaignCount: 2, linkCount: 3, impression: 2224, click: 12, sold: 3, cost: 3.99, revenue: 119.42, prevRevenue: 0, revenueChange: '-', roas: '29.93', cvr: '25.0%', ctr: '0.54%', cpc: '$0.33', cpa: '$1.33', acos: '3.34%', acoas: '3.21%' },
      { analyst: '胡煜星', campaignCount: 9, linkCount: 12, impression: 37020, click: 92, sold: 1, cost: 61.77, revenue: 248.47, prevRevenue: 755.07, revenueChange: '-67.1%', roas: '2.57', cvr: '1.09%', ctr: '0.25%', cpc: '$0.67', cpa: '$61.77', acos: '38.85%', acoas: '8.72%' },
    ],
    categories: [
      { category: '车门系统', campaignCount: 6, linkCount: 8, impression: 64284, click: 94, sold: 2, cost: 65.31, revenue: 115.14, prevRevenue: 0, revenueChange: '-', roas: '1.21', cvr: '2.13%', ctr: '0.15%', cpc: '$0.69', cpa: '$32.65', acos: '82.34%', acoas: '15.27%' },
      { category: '车身外扩件', campaignCount: 7, linkCount: 9, impression: 36778, click: 138, sold: 1, cost: 115.38, revenue: 345.29, prevRevenue: 0, revenueChange: '-', roas: '1.17', cvr: '0.72%', ctr: '0.38%', cpc: '$0.84', cpa: '$115.38', acos: '85.27%', acoas: '14.33%' },
      { category: '挡泥板', campaignCount: 5, linkCount: 6, impression: 1259, click: 12, sold: 1, cost: 8.81, revenue: 80.14, prevRevenue: 0, revenueChange: '-', roas: '14.64', cvr: '8.33%', ctr: '0.95%', cpc: '$0.73', cpa: '$8.81', acos: '6.83%', acoas: '6.21%' },
      { category: '机盖及附件', campaignCount: 5, linkCount: 6, impression: 1788, click: 49, sold: 12, cost: 17.21, revenue: 720.98, prevRevenue: 0, revenueChange: '-', roas: '41.89', cvr: '24.49%', ctr: '2.74%', cpc: '$0.35', cpa: '$1.43', acos: '2.39%', acoas: '2.18%' },
      { category: '牌照板支架', campaignCount: 1, linkCount: 2, impression: 527, click: 6, sold: 1, cost: 2.32, revenue: 69.04, prevRevenue: 0, revenueChange: '-', roas: '21', cvr: '16.67%', ctr: '1.14%', cpc: '$0.39', cpa: '$2.32', acos: '4.76%', acoas: '4.52%' },
      { category: '其他', campaignCount: 10, linkCount: 12, impression: 6674, click: 80, sold: 2, cost: 45.52, revenue: 423.43, prevRevenue: 0, revenueChange: '-', roas: '7.03', cvr: '2.5%', ctr: '1.2%', cpc: '$0.57', cpa: '$22.76', acos: '14.22%', acoas: '6.34%' },
      { category: '饰条', campaignCount: 8, linkCount: 10, impression: 8376, click: 50, sold: 8, cost: 18.01, revenue: 319.42, prevRevenue: 0, revenueChange: '-', roas: '17.83', cvr: '16.0%', ctr: '0.6%', cpc: '$0.36', cpa: '$2.25', acos: '5.61%', acoas: '5.12%' },
    ],
    expandTypes: [],
    detailRecords: [],
  },
  salesSituation: {
    overall: {
      hasCompetitorSku: 43, prevHasCompetitorSku: 32, change: 11,
      yCount: 27, prevYCount: 21, yChange: 6,
      nCount: 13, prevNCount: 11, nChange: 2,
      noSaleCount: 3, prevNoSaleCount: 0, noSaleChange: 3,
      soldCount: 40, prevSoldCount: 32, soldChange: 8,
      soldRate: '93.0%', prevSoldRate: '100.0%',
    },
    outside8dSku: 37, prevOutside8dSku: 30, outside8dChange: 7,
    byAnalyst: [
      { analyst: '俞东旭', hasCompetitorSku: 12, yCount: 10, nCount: 1, noSaleCount: 1, soldCount: 11, soldRate: '91.7%', prevSoldRate: '90.9%', change: '+0.8%' },
      { analyst: '张潇', hasCompetitorSku: 16, yCount: 9, nCount: 5, noSaleCount: 2, soldCount: 14, soldRate: '87.5%', prevSoldRate: '83.8%', change: '+3.7%' },
      { analyst: '朱培源', hasCompetitorSku: 8, yCount: 3, nCount: 5, noSaleCount: 0, soldCount: 8, soldRate: '100.0%', prevSoldRate: '80.0%', change: '+20.0%' },
      { analyst: '王偲涵', hasCompetitorSku: 10, yCount: 5, nCount: 2, noSaleCount: 3, soldCount: 7, soldRate: '70.0%', prevSoldRate: '69.2%', change: '+0.8%' },
      { analyst: '章鹏', hasCompetitorSku: 1, yCount: 0, nCount: 0, noSaleCount: 1, soldCount: 0, soldRate: '0%', prevSoldRate: '0%', change: '-' },
      { analyst: '胡煜星', hasCompetitorSku: 15, yCount: 9, nCount: 6, noSaleCount: 0, soldCount: 15, soldRate: '100.0%', prevSoldRate: '100.0%', change: '+0.0%' },
    ],
    byCategory: [
      { category: '其他', hasCompetitorSku: 11, yCount: 6, nCount: 5, noSaleCount: 0, soldCount: 11, soldRate: '100.0%', prevSoldRate: '100.0%', change: '+0.0%' },
      { category: '挡泥板', hasCompetitorSku: 4, yCount: 2, nCount: 2, noSaleCount: 0, soldCount: 4, soldRate: '100.0%', prevSoldRate: '100.0%', change: '+0.0%' },
      { category: '机盖及附件', hasCompetitorSku: 7, yCount: 5, nCount: 1, noSaleCount: 1, soldCount: 6, soldRate: '85.7%', prevSoldRate: '80.0%', change: '+5.7%' },
      { category: '牌照板支架', hasCompetitorSku: 1, yCount: 0, nCount: 0, noSaleCount: 1, soldCount: 0, soldRate: '0%', prevSoldRate: '0%', change: '-' },
      { category: '车身外扩件', hasCompetitorSku: 6, yCount: 3, nCount: 2, noSaleCount: 1, soldCount: 5, soldRate: '83.3%', prevSoldRate: '80.0%', change: '+3.3%' },
      { category: '车门系统', hasCompetitorSku: 17, yCount: 11, nCount: 5, noSaleCount: 1, soldCount: 16, soldRate: '94.1%', prevSoldRate: '92.3%', change: '+1.8%' },
      { category: '饰条', hasCompetitorSku: 6, yCount: 4, nCount: 2, noSaleCount: 0, soldCount: 6, soldRate: '100.0%', prevSoldRate: '100.0%', change: '+0.0%' },
    ],
  },
  unsoldReason: {
    hasCompetitor: { 
      total: 3, prevTotal: 0, change: 3, 
      reasons: [
        { reason: '竞争无优势', curCount: 3, curRatio: '7.0%', prevCount: 0, prevRatio: '0.0%', change: 3 },
      ], 
      byAnalyst: [
        { analyst: '俞东旭', competitiveWeak: 1, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 1 },
        { analyst: '张潇', competitiveWeak: 2, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 2 },
        { analyst: '朱培源', competitiveWeak: 0, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 0 },
        { analyst: '王偲涵', competitiveWeak: 0, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 0 },
        { analyst: '章鹏', competitiveWeak: 0, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 0 },
        { analyst: '胡煜星', competitiveWeak: 0, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 0 },
      ],
      byCategory: [
        { category: '车门系统', competitiveWeak: 1, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 1 },
        { category: '机盖及附件', competitiveWeak: 2, noMarket: 0, noPriceAdv: 0, overseas: 0, normal: 0, na: 0, unknown: 0, total: 2 },
      ],
    },
    noCompetitor: { 
      total: 19, prevTotal: 16, change: 3, 
      reasons: [
        { reason: '无市场', curCount: 19, curRatio: '100.0%', prevCount: 16, prevRatio: '100.0%', change: 3 },
      ], 
      byAnalyst: [
        { analyst: '俞东旭', noMarket: 3, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 3 },
        { analyst: '张潇', noMarket: 4, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 4 },
        { analyst: '朱培源', noMarket: 2, unknown: 0, competitiveWeak: 1, na: 0, other: 0, total: 3 },
        { analyst: '王偲涵', noMarket: 3, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 3 },
        { analyst: '章鹏', noMarket: 1, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 1 },
        { analyst: '胡煜星', noMarket: 6, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 6 },
      ],
      byCategory: [
        { category: '其他', noMarket: 8, unknown: 0, competitiveWeak: 1, na: 0, other: 0, total: 9 },
        { category: '挡泥板', noMarket: 3, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 3 },
        { category: '机盖及附件', noMarket: 1, unknown: 0, competitiveWeak: 0, na: 0, other: 0, total: 1 },
        { category: '车身外扩件', noMarket: 3, unknown: 0, competitiveWeak: 1, na: 0, other: 0, total: 4 },
        { category: '车门系统', noMarket: 4, unknown: 0, competitiveWeak: 1, na: 0, other: 0, total: 5 },
      ],
    },
  },
  plgData: { records: [], plpAndPlgBothCount: 0, plgOnlyCount: 0, plpOnlyCount: 0, noAdCount: 0, plpDisabledNoSaleCount: 0 },
};

// ==================== 从 corrected_data.json 加载真实数据 ====================
import correctedData from './corrected_data.json';

/** 直接暴露原始行数据，供页面 Tab 使用 */
export const rawRows: any[] = (correctedData as any).cum43Data || [];

/**
 * 从 corrected_data.json 加载并转换为 NewProductStatusData 格式
 */
export function loadCorrectedNewProductData(): NewProductStatusData {
  const corrected = correctedData as {
    cum43Data: any[];
    cum43Stats: any;
    lowShareData: any[];
    plgRecords: any[];
    plpTotal: any;
    plpPrevTotal: any;
    plpCategories: any[];
    plpExpandTypes: any[];
    plpAnalysts: any[];
    expandTypeData: any[];
    timelinessData: any;
    hasCompetitorUnsold: any;
    unsoldNoCompetitor: any;
    prevWeekKpi: any;
    plgStats: any;
    prevWeekAnalysts: any;
    categoryRevenueData?: any[];
    analystRevenueData?: any[];
    plpSummaryData?: any[];
    plpDetailData?: any[];
  };

  const cum43Data = corrected.cum43Data || [];
  const lowShareData = corrected.lowShareData || [];
  const plpTotal = corrected.plpTotal || {};
  const plpPrevTotal = corrected.plpPrevTotal || {};
  const plpCategories = corrected.plpCategories || [];
  const plpExpandTypes = corrected.plpExpandTypes || [];
  const plpAnalysts = corrected.plpAnalysts || [];
  const expandTypeData = corrected.expandTypeData || [];
  const timelinessData = corrected.timelinessData || { analysts: [], total: {} };
  const hasCompetitorUnsold = corrected.hasCompetitorUnsold || {};
  const unsoldNoCompetitor = corrected.unsoldNoCompetitor || {};
  const prevWeekKpi = corrected.prevWeekKpi || {};
  const plgStats = corrected.plgStats || {};
  const plgRecords = corrected.plgRecords || [];
  const categoryRevenueData = corrected.categoryRevenueData || [];
  const analystRevenueData = corrected.analystRevenueData || [];
  const plpSummaryData = corrected.plpSummaryData || [];
  const plpDetailData = corrected.plpDetailData || [];

  // 计算总体数据 — 兼容新旧两种 JSON 字段名
  const getField = (item: any, newKey: string, oldKey: string): any =>
    item[newKey] !== undefined ? item[newKey] : item[oldKey];

  const totalSku = cum43Data.length;
  const lowShareCount = lowShareData.length;
  const hasCompetitorSku = cum43Data.filter((item: any) => getField(item, 'rivalCurr', '5.6对手销量') > 0).length;
  const noCompetitorSku = totalSku - hasCompetitorSku;
  const ord8Field = getField(cum43Data[0] || {}, 'ord8Curr', '') ? 'ord8Curr' : '5.6 8日出单情况';
  const soldSku = cum43Data.filter((item: any) => item[ord8Field] === 'Y' || item[ord8Field] === 'N').length;
  const yCount = cum43Data.filter((item: any) => item[ord8Field] === 'Y').length;
  const nCount = cum43Data.filter((item: any) => item[ord8Field] === 'N').length;
  const noSaleCount = cum43Data.filter((item: any) => item[ord8Field] !== 'Y' && item[ord8Field] !== 'N').length;

  // 本周新上架: 上架日期在当期起始日或之后 (兼容新旧字段)
  const listDateField = getField(cum43Data[0] || {}, 'listDate', '') ? 'listDate' : '实际上架日期';
  const curNewSku = cum43Data.filter((item: any) => {
    const date = item[listDateField];
    return date && date >= '2026-05-14';
  }).length;

  // 按分析人汇总 - 从 Excel 真实数据读取
  const analystMetrics: AnalystMetrics[] = (analystRevenueData || [])
    .filter((item: any) => item.analyst !== '合计')
    .map((item: any) => ({
      analyst: item.analyst,
      curSku: Number(item.curSku) || 0,
      curNewSku: Number(item.curNewSku) || 0,
      curSalesQty: Number(item.curSalesQty) || 0,
      prevSalesQty: Number(item.prevSalesQty) || 0,
      salesQtyChange: String(item.salesQtyChange || '-'),
      curRevenue: Number(item.curRevenue) || 0,
      prevRevenue: Number(item.prevRevenue) || 0,
      revenueChange: String(item.revenueChange || '-'),
    }));

  // 按品类汇总 - 从 Excel 真实数据读取
  const categoryMetrics: CategoryMetrics[] = (categoryRevenueData || [])
    .filter((item: any) => item.category !== '合计')
    .map((item: any) => ({
      category: item.category,
      curSku: Number(item.curSku) || 0,
      curNewSku: Number(item.curNewSku) || 0,
      curSalesQty: Number(item.curSalesQty) || 0,
      prevSalesQty: Number(item.prevSalesQty) || 0,
      salesQtyChange: String(item.salesQtyChange || '-'),
      curRevenue: Number(item.curRevenue) || 0,
      prevRevenue: Number(item.prevRevenue) || 0,
      revenueChange: String(item.revenueChange || '-'),
      curHasCompetitor: Number(item.curHasCompetitor) || 0,
      prevHasCompetitor: 0,
    }));

  // 转换低占比数据 - 兼容新旧 JSON 字段名
  const lowShareRecords: any[] = lowShareData.map((item: any) => ({
    salesCode: item.salesCode || item.saleNo || item['SKU'] || '',
    sku: item.sku || item['SKU'] || '',
    launchDate: item.launchDate || item.listDate || item['实际上架日期'] || '',
    analyst: item.analyst || item['4月分析人'] || '',
    category: item.category || item['品类'] || '',
    expandType: item.expandType || item['产品拓展'] || '',
    curSalesQty: Number(item.curSalesQty || item.salesCurr || item['4.30-5.6销量'] || 0),
    salesQtyChange: item.salesQtyChange || '-',
    curRevenue: Number(item.curRevenue || item.revenueCurr || item['4.30-5.6销售额'] || 0),
    revenueChange: item.revenueChange || '-',
    prevCompetitorQty: Number(item.prevCompetitorQty || item.rivalPrev || 0),
    curCompetitorQty: Number(item.curCompetitorQty || item.rivalCurr || item['5.6对手销量'] || 0),
    competitorQtyChange: item.competitorQtyChange || '-',
    prevMarketShare: item.prevMarketShare || (item.sharePrev !== undefined ? item.sharePrev + '%' : '0%'),
    curMarketShare: item.curMarketShare || (item.shareCurr !== undefined ? item.shareCurr + '%' : item['5.6市占比']?.toString()) || '0%',
    marketShareChange: item.marketShareChange || '-',
    cur8dStatus: item.cur8dStatus || item.ord8Curr || item['5.6 8日出单情况'] || '',
    cur7dFreqTag: item.cur7dFreqTag || item.freq7Curr || '正常',
    prevMarketStatus: item.prevMarketStatus || item.mktStatusPrev || '',
    curOperation: item.curOperation || item.opJudge || '',
    curMarketStatus: item.curMarketStatus || item.mktStatus || item['5.6市场状态'] || '',
    plpEnabled: item.plpEnabled || item.plpCurr || 'N',
    plgFee: item.plgFee || (item.plgCurr !== undefined ? item.plgCurr + '%' : '0%'),
    riskLevel: 'high' as const,
  }));

  // PLP 数据 - 从 plpSummaryData 读取
  const plpTotalRow = plpSummaryData.find((r: any) => r.dimensionType === '总计') || {};
  const plpPrevRow = {};
  // 提取各维度数据
  const plpAnalystsSectionStart = plpSummaryData.findIndex((r: any) => r.dimensionType === '【分析人维度】');
  const plpCategorySectionStart = plpSummaryData.findIndex((r: any) => r.dimensionType === '【品线维度】');
  const plpExpandSectionStart = plpSummaryData.findIndex((r: any) => r.dimensionType === '【拓展类型维度】');

  // 从总计行获取上周数据
  const prevRevenue = Number(plpTotalRow.prevRevenue) || 0;
  const curRevenue = Number(plpTotalRow.revenue) || 0;
  const revenueChange = prevRevenue > 0
    ? ((curRevenue - prevRevenue) / prevRevenue * 100).toFixed(1) + '%'
    : (prevRevenue === 0 && curRevenue > 0 ? '+100%' : '0%');

  const plpAnalystsData: PLPAnalystMetrics[] = [];
  if (plpAnalystsSectionStart >= 0) {
    for (let i = plpAnalystsSectionStart + 1; i < plpSummaryData.length; i++) {
      const r = plpSummaryData[i];
      if (!r.dimensionType || r.dimensionType.startsWith('【')) break;
      const pRev = Number(r.prevRevenue) || 0;
      const cRev = Number(r.revenue) || 0;
      plpAnalystsData.push({
        analyst: r.dimensionType,
        campaignCount: Number(r.campaign) || 0,
        linkCount: Number(r.link) || 0,
        impression: Number(r.impressions) || 0,
        click: Number(r.clicks) || 0,
        sold: Number(r.salesQty) || 0,
        cost: Number(r.spend) || 0,
        revenue: cRev,
        prevRevenue: pRev,
        revenueChange: pRev > 0 ? ((cRev - pRev) / pRev * 100).toFixed(1) + '%' : '-',
        roas: Number(r.roas) ? Number(r.roas).toFixed(2) : '-',
        cvr: String(r.cvr || '-'),
        ctr: String(r.ctr || '-'),
        cpc: Number(r.cpc) ? '$' + Number(r.cpc).toFixed(2) : '-',
        cpa: Number(r.cpa) ? '$' + Number(r.cpa).toFixed(2) : '-',
        acos: String(r.acos || '-'),
        acoas: Number(r.acoas) ? (Number(r.acoas) * 100).toFixed(2) + '%' : '-',
      });
    }
  }

  // 品线维度PLP
  const plpCategoriesData: PLPCategoryMetrics[] = [];
  if (plpCategorySectionStart >= 0) {
    for (let i = plpCategorySectionStart + 1; i < plpSummaryData.length; i++) {
      const r = plpSummaryData[i];
      if (!r.dimensionType || r.dimensionType.startsWith('【')) break;
      const pRev = Number(r.prevRevenue) || 0;
      const cRev = Number(r.revenue) || 0;
      plpCategoriesData.push({
        category: r.dimensionType,
        campaignCount: Number(r.campaign) || 0,
        linkCount: Number(r.link) || 0,
        impression: Number(r.impressions) || 0,
        click: Number(r.clicks) || 0,
        sold: Number(r.salesQty) || 0,
        cost: Number(r.spend) || 0,
        revenue: cRev,
        prevRevenue: pRev,
        revenueChange: pRev > 0 ? ((cRev - pRev) / pRev * 100).toFixed(1) + '%' : '-',
        roas: Number(r.roas) ? Number(r.roas).toFixed(2) : '-',
        cvr: String(r.cvr || '-'),
        ctr: String(r.ctr || '-'),
        cpc: Number(r.cpc) ? '$' + Number(r.cpc).toFixed(2) : '-',
        cpa: Number(r.cpa) ? '$' + Number(r.cpa).toFixed(2) : '-',
        acos: String(r.acos || '-'),
        acoas: Number(r.acoas) ? (Number(r.acoas) * 100).toFixed(2) + '%' : '-',
      });
    }
  }

  // 拓展类型PLP
  const plpExpandTypesData: PLPExpandTypeMetrics[] = [];
  if (plpExpandSectionStart >= 0) {
    for (let i = plpExpandSectionStart + 1; i < plpSummaryData.length; i++) {
      const r = plpSummaryData[i];
      if (!r.dimensionType || r.dimensionType.startsWith('【')) break;
      const pRev = Number(r.prevRevenue) || 0;
      const cRev = Number(r.revenue) || 0;
      plpExpandTypesData.push({
        expandType: r.dimensionType,
        campaignCount: Number(r.campaign) || 0,
        linkCount: Number(r.link) || 0,
        impression: Number(r.impressions) || 0,
        click: Number(r.clicks) || 0,
        sold: Number(r.salesQty) || 0,
        cost: Number(r.spend) || 0,
        revenue: cRev,
        prevRevenue: pRev,
        revenueChange: pRev > 0 ? ((cRev - pRev) / pRev * 100).toFixed(1) + '%' : '-',
        roas: Number(r.roas) ? Number(r.roas).toFixed(2) : '-',
        cvr: String(r.cvr || '-'),
        ctr: String(r.ctr || '-'),
        cpc: Number(r.cpc) ? '$' + Number(r.cpc).toFixed(2) : '-',
        cpa: Number(r.cpa) ? '$' + Number(r.cpa).toFixed(2) : '-',
        acos: String(r.acos || '-'),
        acoas: Number(r.acoas) ? (Number(r.acoas) * 100).toFixed(2) + '%' : '-',
      });
    }
  }

  // PLP 明细数据
  const plpDetailRecords: PLPDetailRecord[] = (plpDetailData || []).map((r: any) => ({
    period: r.period || '',
    campaign: r.campaign || '',
    sku: r.sku || '',
    id: String(r.id || ''),
    store: r.store || '',
    plpStartDate: r.plpStartDate || '',
    actualListDate: r.actualListDate || '',
    firstOrderDate: r.firstOrderDate || '',
    analyst: r.analyst || '',
    category: r.category || '',
    productExpansion: r.productExpansion || '',
    impressions: Number(r.impressions) || 0,
    clicks: Number(r.clicks) || 0,
    salesQty: Number(r.salesQty) || 0,
    spend: Number(r.spend) || 0,
    adRevenue: Number(r.adRevenue) || 0,
    totalRevenue: Number(r.totalRevenue) || 0,
    roas: Number(r.roas) || 0,
    cvr: Number(r.cvr) || 0,
    ctr: Number(r.ctr) || 0,
    cpc: Number(r.cpc) || 0,
    cpa: Number(r.cpa) || 0,
    acos: Number(r.acos) || 0,
    acoas: Number(r.acoas) || 0,
  }));

  const plpData = {
    total: {
      campaignCount: Number(plpTotalRow.campaign) || 0,
      linkCount: Number(plpTotalRow.link) || 0,
      impression: Number(plpTotalRow.impressions) || 0,
      click: Number(plpTotalRow.clicks) || 0,
      sold: Number(plpTotalRow.salesQty) || 0,
      cost: Number(plpTotalRow.spend) || 0,
      revenue: curRevenue,
      prevRevenue,
      revenueChange,
      roas: Number(plpTotalRow.roas) ? Number(plpTotalRow.roas).toFixed(2) : '-',
      cvr: String(plpTotalRow.cvr || '-'),
      ctr: String(plpTotalRow.ctr || '-'),
      cpc: Number(plpTotalRow.cpc) ? '$' + Number(plpTotalRow.cpc).toFixed(2) : '-',
      cpa: Number(plpTotalRow.cpa) ? '$' + Number(plpTotalRow.cpa).toFixed(2) : '-',
      acos: String(plpTotalRow.acos || '-'),
      acoas: Number(plpTotalRow.acoas) ? (Number(plpTotalRow.acoas) * 100).toFixed(2) + '%' : '-',
    } as PLPAdMetrics,
    prevTotal: {
      campaignCount: Number(plpTotalRow.prevCampaign) || 0,
      linkCount: Number(plpTotalRow.prevLink) || 0,
      impression: Number(plpTotalRow.prevImpressions) || 0,
      click: Number(plpTotalRow.prevClicks) || 0,
      sold: Number(plpTotalRow.prevSalesQty) || 0,
      cost: Number(plpTotalRow.prevSpend) || 0,
      revenue: prevRevenue,
      prevRevenue: 0,
      revenueChange: '-',
      roas: Number(plpTotalRow.prevRoas) ? Number(plpTotalRow.prevRoas).toFixed(2) : '-',
      cvr: String(plpTotalRow.prevCvr || '-'),
      ctr: String(plpTotalRow.prevCtr || '-'),
      cpc: Number(plpTotalRow.prevCpc) ? '$' + Number(plpTotalRow.prevCpc).toFixed(2) : '-',
      cpa: Number(plpTotalRow.prevCpa) ? '$' + Number(plpTotalRow.prevCpa).toFixed(2) : '-',
      acos: String(plpTotalRow.prevAcos || '-'),
      acoas: '',
    } as PLPAdMetrics,
    analysts: plpAnalystsData,
    categories: plpCategoriesData,
    expandTypes: plpExpandTypesData,
    detailRecords: plpDetailRecords,
  };

  // 从 Excel 合计行获取总体数据 — 兼容新旧 JSON 格式
  const totalRow = categoryRevenueData.find((r: any) => r.category === '合计') || null;
  const totalRevenueVal = totalRow?.curRevenue
    || cum43Data.reduce((sum: number, item: any) => sum + (Number(item.revenueCurr) || Number(item['4.30-5.6销售额']) || 0), 0);
  const prevTotalRevenueVal = totalRow?.prevRevenue
    || cum43Data.reduce((sum: number, item: any) => sum + (Number(item.revenuePrev) || 0), 0);
  const revenueChangeVal = totalRow?.revenueChange || '-';
  const prevTotalSalesQtyVal = totalRow?.prevSalesQty || 0;
  const salesQtyChangeVal = totalRow?.salesQtyChange || '-';

  // 自动检测实际周期（从第一条数据的 listDate 范围推断）
  const firstItem = cum43Data[0] || {};
  const listDates = cum43Data.map((r: any) => r.listDate || r['实际上架日期'] || '').filter(Boolean).sort();

  return {
    _rawRows: cum43Data as any[],
    currentPeriod: '5.14-5.20',
    previousPeriod: '5.7-5.13',
    overall: {
      kpi: {
        totalSku,
        curNewSku: Number(totalRow.curNewSku) || curNewSku,
        prevNewSku: prevWeekKpi.prevTotalSku ? totalSku - prevWeekKpi.prevTotalSku : 0,
        totalSalesQty: Number(totalRow.curSalesQty) || cum43Data.reduce((sum: number, item: any) => sum + Number(item['4.30-5.6销量']) || 0, 0),
        prevTotalSalesQty: prevTotalSalesQtyVal,
        salesQtyChange: salesQtyChangeVal,
        totalRevenue: totalRevenueVal,
        prevTotalRevenue: prevTotalRevenueVal,
        revenueChange: revenueChangeVal,
        hasCompetitorSku,
        prevHasCompetitorSku: prevWeekKpi.prevTotalSku ? prevWeekKpi.prevTotalSku - (totalSku - hasCompetitorSku) : 0,
        noCompetitorSku,
        prevNoCompetitorSku: prevWeekKpi.prevTotalSku ? prevWeekKpi.prevTotalSku - (hasCompetitorSku) : 0,
      },
      timeliness: {
        timelyCount: prevWeekKpi.timelyChange ? timelinessData.total?.timelyCount || soldSku : soldSku,
        noAnalysis8dCount: prevWeekKpi.timelyChange ? timelinessData.total?.noAnalysis8dCount || noSaleCount : noSaleCount,
        noAnalysis7dCount: prevWeekKpi.timelyChange ? timelinessData.total?.noAnalysis7dCount || 0 : 0,
        totalCount: totalSku,
        timelyRate: prevWeekKpi.timelyChange ? (timelinessData.total?.timelyRate || '0%') : (totalSku > 0 ? ((soldSku / totalSku) * 100).toFixed(1) + '%' : '0%'),
        prevTimelyCount: prevWeekKpi.prevTimelyCount || 0,
        prevTimelyRate: prevWeekKpi.prevTimelyRate || '0%',
        change: prevWeekKpi.timelyChange || '-',
      },
      salesSituation: {
        hasCompetitorSku,
        prevHasCompetitorSku: 0,
        change: hasCompetitorSku,
        yCount,
        prevYCount: 0,
        yChange: yCount,
        nCount,
        prevNCount: 0,
        nChange: nCount,
        noSaleCount,
        prevNoSaleCount: 0,
        noSaleChange: noSaleCount,
        soldCount: soldSku,
        prevSoldCount: prevWeekKpi.prevSoldCount || 0,
        soldChange: soldSku,
        soldRate: hasCompetitorSku > 0 ? ((soldSku / hasCompetitorSku) * 100).toFixed(1) + '%' : '0%',
        prevSoldRate: prevWeekKpi.prevSoldRate || '0%',
      },
    },
    categoryMetrics,
    analystMetrics,
    expandTypeMetrics: expandTypeData.map((item: any) => ({
      expandType: item.expandType,
      curSku: item.curSku || 0,
      prevSku: item.prevSku || 0,
      curSalesCount: item.curSalesCount || 0,
      curSalesRate: item.curSalesRate || '0%',
      prevSalesCount: item.prevSalesCount || 0,
      prevSalesRate: item.prevSalesRate || '0%',
      salesRateChange: item.salesRateChange || '-',
      curSalesQty: item.curSalesQty || 0,
      prevSalesQty: item.prevSalesQty || 0,
      salesQtyChange: item.salesQtyChange || '-',
      curRevenue: item.curRevenue || 0,
      prevRevenue: item.prevRevenue || 0,
      revenueChange: item.revenueChange || '-',
    })),
    timelinessData: {
      analysts: (timelinessData.analysts || []).map((item: any) => ({
        analyst: item.analyst,
        curSku: item.curSku || 0,
        timelyCount: item.timelyCount || 0,
        noAnalysis8dCount: item.noAnalysis8dCount || 0,
        noAnalysis7dCount: item.noAnalysis7dCount || 0,
        timelyRate: item.timelyRate || '0%',
        prevSku: item.prevSku || 0,
        prevTimelyCount: item.prevTimelyCount || 0,
        prevTimelyRate: item.prevTimelyRate || '0%',
        change: item.change || '-',
      })),
      total: {
        analyst: '合计',
        curSku: timelinessData.total?.curSku || totalSku,
        timelyCount: timelinessData.total?.timelyCount || 0,
        noAnalysis8dCount: timelinessData.total?.noAnalysis8dCount || 0,
        noAnalysis7dCount: timelinessData.total?.noAnalysis7dCount || 0,
        timelyRate: timelinessData.total?.timelyRate || '0%',
        prevSku: timelinessData.total?.prevSku || 0,
        prevTimelyCount: timelinessData.total?.prevTimelyCount || 0,
        prevTimelyRate: timelinessData.total?.prevTimelyRate || '0%',
        change: timelinessData.total?.change || '-',
      },
    },
    lowShareRecords,
    plpData,
    salesSituation: {
      overall: {
        hasCompetitorSku,
        prevHasCompetitorSku: 0,
        change: hasCompetitorSku,
        yCount,
        prevYCount: 0,
        yChange: yCount,
        nCount,
        prevNCount: 0,
        nChange: nCount,
        noSaleCount,
        prevNoSaleCount: 0,
        noSaleChange: noSaleCount,
        soldCount: soldSku,
        prevSoldCount: 0,
        soldChange: soldSku,
        soldRate: hasCompetitorSku > 0 ? ((soldSku / hasCompetitorSku) * 100).toFixed(1) + '%' : '0%',
        prevSoldRate: '0%',
      },
      outside8dSku: nCount,
      prevOutside8dSku: 0,
      outside8dChange: nCount,
      byAnalyst: [],
      byCategory: [],
    },
    unsoldReason: {
      hasCompetitor: hasCompetitorUnsold,
      noCompetitor: unsoldNoCompetitor,
    },
    plgData: {
      records: (plgRecords || []).map((r: any) => ({
        salesCode: r.salesCode || '',
        sku: r.sku,
        launchDate: r.launchDate,
        firstSaleDate: r.firstSaleDate || '未出单',
        analyst: r.analyst,
        category: r.category,
        expandType: r.expandType,
        curSalesQty: r.curSalesQty || 0,
        prevSalesQty: 0,
        curRevenue: r.curRevenue || 0,
        curCompetitorQty: r.curCompetitorQty || 0,
        curMarketShare: r.curMarketShare || '0%',
        curMarketStatus: r.curMarketStatus || '',
        curOperation: r.curOperation || '',
        plpEnabled: r.plpEnabled || 'N',
        plgFee: r.plgFee || '0%',
      })) as PLGRecord[],
      plpAndPlgBothCount: plgStats.plpAndPlgBothCount || 0,
      plgOnlyCount: plgStats.plgOnlyCount || 0,
      plpOnlyCount: plgStats.plpOnlyCount || 0,
      noAdCount: plgStats.noAdCount || 0,
      plpDisabledNoSaleCount: plgStats.plpDisabledNoSaleCount || 0,
      plpEnabledCount: plgStats.plpEnabledCount || 0,
      totalNewProducts: plgStats.totalNewProducts || 0,
      totalLowShare: plgStats.totalNewProducts || 0,
      byAnalyst: plgStats.byAnalyst || [],
    },
  } as any;
}
