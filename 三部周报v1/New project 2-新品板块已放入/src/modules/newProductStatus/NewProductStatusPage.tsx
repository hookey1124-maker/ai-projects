import { useState, useMemo } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadialBarChart, RadialBar,
} from 'recharts';
import KpiCard from '../../components/common/KpiCard';
import ModulePageLayout from '../../components/common/ModulePageLayout';
import StatusTag from '../../components/common/StatusTag';
import { useModulePeriodInfo } from '../useModulePeriodInfo';
import {
  mockNewProductStatusData,
  loadCorrectedNewProductData,
  type NewProductStatusData,
} from './newProductStatusAdapter';

// ===== 颜色常量 =====
const COLORS = {
  blue: '#0f3460', green: '#08845a', orange: '#e07b24', red: '#c0392b',
  purple: '#8e44ad', info: '#2980b9', gray: '#6c757d',
};
const CHART_COLORS = ['#0f3460','#08845a','#e07b24','#c0392b','#8e44ad','#2980b9','#16a085','#d35400','#2c3e50'];

// ===== 工具函数 =====
type TabId = 'overview' | 'marketDist' | 'performance' | 'lowShare' | 'ads' | 'cum43' | 'report';

const fmtPct = (v: number): string => `${v.toFixed(1)}%`;
const fmtUsd = (v: number): string => `$${v.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
const fmtNum = (v: number): string => v.toLocaleString('en-US');
const hbStr = (curr: number, prev: number): string => {
  if (!prev) return '-';
  const r = ((curr - prev) / Math.abs(prev)) * 100;
  return `${r > 0 ? '+' : ''}${r.toFixed(1)}%`;
};
const hbClass = (curr: number, prev: number): 'up' | 'down' | 'flat' => {
  if (!prev || curr === prev) return 'flat';
  return curr > prev ? 'up' : 'down';
};

// 安全取字段（兼容新旧 JSON）
const gf = (r: any, newKey: string, oldKey: string): any =>
  r[newKey] !== undefined ? r[newKey] : r[oldKey];

// ===== 数据加载 =====
const demoData: NewProductStatusData = (() => {
  try {
    const real = loadCorrectedNewProductData();
    if (real?.overall?.kpi?.totalSku > 0) return real;
  } catch {}
  return mockNewProductStatusData;
})();

export default function NewProductStatusPage() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const { periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo('newProductStatus');

  const dataPeriod = '5/14 - 5/20';
  const prevDataPeriod = '5/7 - 5/13';

  // 原始行数据（从 demoData._rawRows 获取；mock 数据无此字段则为空）
  const rawRows = useMemo(() => (demoData as any)._rawRows || [], []);
  const hasRawData = rawRows.length > 0;

  // ===== 派生统计 =====
  const kpi = useMemo(() => demoData.overall.kpi, []);
  const timeliness = useMemo(() => demoData.overall.timeliness, []);
  const salesSit = useMemo(() => demoData.overall.salesSituation, []);

  // 品类维度
  const catData = useMemo(() =>
    (demoData.categoryMetrics || []).map((c: any) => ({
      name: c.category, salesCurr: c.curSalesQty, salesPrev: c.prevSalesQty,
      revCurr: c.curRevenue, revPrev: c.prevRevenue, sku: c.curSku,
    })), [demoData]);

  // 分析人维度
  const anData = useMemo(() =>
    (demoData.analystMetrics || []).map((a: any) => ({
      name: a.analyst, salesCurr: a.curSalesQty, salesPrev: a.prevSalesQty,
      revCurr: a.curRevenue, revPrev: a.prevRevenue, sku: a.curSku,
    })), [demoData]);

  // 拓展类型
  const expData = useMemo(() =>
    (demoData.expandTypeMetrics || []).map((e: any) => ({
      name: e.expandType, sku: e.curSku, salesCurr: e.curSalesQty,
      soldRate: e.curSalesRate, prevSoldRate: e.prevSalesRate,
      revCurr: e.curRevenue,
    })), [demoData]);

  // 及时率数据
  const timelyData = useMemo(() => {
    const analysts = (demoData.timelinessData?.analysts || []).map((t: any) => ({
      name: t.analyst, rate: parseFloat(t.timelyRate) || 0, sku: t.curSku,
    }));
    const total = demoData.timelinessData?.total;
    return { analysts, total };
  }, [demoData]);

  // 低占比数据
  const lowShareData = useMemo(() => demoData.lowShareRecords || [], [demoData]);

  // PLP 数据
  const plpData = useMemo(() => demoData.plpData || { total: {}, analysts: [], categories: [], expandTypes: [], detailRecords: [] }, [demoData]);

  // ===== Tab 1: 总盘概览 KPI =====
  const overviewKpi = [
    { label: '累计在跟SKU', value: fmtNum(kpi.totalSku), helper: `新上架 +${kpi.curNewSku}` },
    { label: '本周销量', value: fmtNum(kpi.totalSalesQty), helper: `环比 ${hbStr(kpi.totalSalesQty, kpi.prevTotalSalesQty)}` },
    { label: '本周销售额', value: fmtUsd(kpi.totalRevenue), helper: `环比 ${hbStr(kpi.totalRevenue, kpi.prevTotalRevenue)}` },
    { label: '有对手SKU', value: fmtNum(kpi.hasCompetitorSku), helper: `无对手 ${kpi.noCompetitorSku}` },
    { label: '出单率', value: fmtPct(salesSit.soldRate ? parseFloat(salesSit.soldRate) : 0), helper: `已出单 ${salesSit.soldCount}/${salesSit.hasCompetitorSku}` },
    { label: '分析及时率', value: fmtPct(timeliness.timelyRate ? parseFloat(timeliness.timelyRate) : 0), helper: `超7日 ${timeliness.noAnalysis7dCount}` },
    { label: '低占比新品', value: fmtNum((kpi as any).lowShareSku ?? demoData.lowShareRecords?.length ?? 0), helper: `市占比<75%` },
  ];

  // ===== Tab 1 图表数据 =====
  const ord8ChartData = useMemo(() => [
    { name: '8日内出单(Y)', value: salesSit.yCount, color: '#08845a' },
    { name: '8日外出单(N)', value: salesSit.nCount, color: '#2980b9' },
    { name: '未出单', value: salesSit.noSaleCount, color: '#c0392b' },
  ], [salesSit]);

  // ===== Tab 2: 市场分布数据 =====
  const mktStatusData = useMemo(() => {
    if (!rawRows.length) return { curr: [], prev: [] };
    const curr = new Map<string, number>();
    const prev = new Map<string, number>();
    rawRows.forEach((r: any) => {
      const cs = gf(r, 'mktStatus', 'curMarketStatus') || gf(r, 'mktStatus', '5.6市场状态') || '未知';
      const ps = gf(r, 'mktStatusPrev', 'prevMarketStatus') || cs;
      curr.set(cs, (curr.get(cs) || 0) + 1);
      prev.set(ps, (prev.get(ps) || 0) + 1);
    });
    const allKeys = [...new Set([...curr.keys(), ...prev.keys()])];
    return {
      curr: allKeys.map(k => ({ name: k, value: curr.get(k) || 0 })),
      prevMap: Object.fromEntries(prev),
      barData: allKeys.map(k => ({ name: k, 本周: curr.get(k) || 0, 上周: prev.get(k) || 0 })),
    };
  }, [rawRows]);

  // 货值分布
  const priceDistData = useMemo(() => {
    if (!rawRows.length) return { dist: [], byAn: [] };
    const buckets = [
      { label: '$0-50', min: 0, max: 50 },
      { label: '$50-100', min: 50, max: 100 },
      { label: '$100-200', min: 100, max: 200 },
      { label: '$200-500', min: 200, max: 500 },
      { label: '$500+', min: 500, max: Infinity },
    ];
    const dist = buckets.map(b => {
      const skus = rawRows.filter((r: any) => {
        const v = gf(r, 'revenueCurr', 'curRevenue') || 0;
        return v >= b.min && v < b.max;
      });
      return { name: b.label, SKU数: skus.length };
    });
    // 按分析人
    const analysts = ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'];
    const byAn = buckets.map(b => {
      const row: any = { name: b.label };
      analysts.forEach(an => {
        row[an] = rawRows.filter((r: any) => {
          const v = gf(r, 'revenueCurr', 'curRevenue') || 0;
          return v >= b.min && v < b.max && (gf(r, 'analyst', '4月分析人') || '') === an;
        }).length;
      });
      return row;
    });
    return { dist, byAn };
  }, [rawRows]);

  // 市占比分布
  const shareTierData = useMemo(() => {
    const categories = ['车门系统','车身外扩件','挡泥板','机盖及附件','其他','饰条','牌照板支架'];
    return categories.map(cat => {
      const skus = rawRows.filter((r: any) => (gf(r, 'category', '品类') || '') === cat);
      const high = skus.filter((r: any) => (gf(r, 'shareCurr', 'curMarketShare') || 0) >= 75).length;
      const mid = skus.filter((r: any) => {
        const s = gf(r, 'shareCurr', 'curMarketShare') || 0;
        return s >= 50 && s < 75;
      }).length;
      const low = skus.filter((r: any) => {
        const s = gf(r, 'shareCurr', 'curMarketShare') || 0;
        return s < 50;
      }).length;
      return { name: cat, '高(≥75%)': high, '中(50-75%)': mid, '低(<50%)': low };
    });
  }, [rawRows]);

  // ===== Tab 3: 品效分析 =====
  const cohortData = useMemo(() => {
    if (!rawRows.length) return [];
    const months = ['2026-01','2026-02','2026-03','2026-04','2026-05'];
    return months.map(m => {
      const skus = rawRows.filter((r: any) => (gf(r, 'listDate', '实际上架日期') || '').startsWith(m));
      const totalRev = skus.reduce((s: number, r: any) => s + (gf(r, 'revenueCurr', 'curRevenue') || 0), 0);
      return {
        month: m.replace('2026-', ''),
        SKU数: skus.length,
        总销售额: Math.round(totalRev),
        品效: skus.length ? Math.round(totalRev / skus.length) : 0,
      };
    });
  }, [rawRows]);

  // ===== Tab 4: 低占比 KPI =====
  const lowShareKpi = useMemo(() => {
    const hasRival = lowShareData.filter((r: any) => (r.curCompetitorQty || gf(r, 'rivalCurr', 'curRivalQty') || 0) > 0);
    const noRival = lowShareData.filter((r: any) => (r.curCompetitorQty || gf(r, 'rivalCurr', 'curRivalQty') || 0) === 0);
    return [
      { label: '低占比总数', value: fmtNum(lowShareData.length), helper: '市占比<75%' },
      { label: '有对手未出单', value: fmtNum(hasRival.length), helper: '竞争无优势等' },
      { label: '无对手未出单', value: fmtNum(noRival.length), helper: '无市场等' },
    ];
  }, [lowShareData]);

  // ===== Tab 5: 广告追踪 KPI =====
  const adsKpi = useMemo(() => {
    const t = plpData.total || {};
    return [
      { label: 'PLP广告活动', value: fmtNum((t as any).campaignCount || 0) },
      { label: '曝光量', value: fmtNum((t as any).impression || 0) },
      { label: '花费', value: fmtUsd((t as any).cost || 0) },
      { label: '广告销售额', value: fmtUsd((t as any).revenue || 0) },
      { label: 'ROAS', value: String((t as any).roas || '-') },
      { label: 'ACOS', value: String((t as any).acos || '-') },
    ];
  }, [plpData]);

  // ===== 汇报输出 =====
  const findings = useMemo(() => {
    const f: string[] = [];
    const soldRate = salesSit.soldRate ? parseFloat(salesSit.soldRate) : 0;
    if (soldRate < 90) f.push(`出单率 ${fmtPct(soldRate)}，需关注有对手未出单的 ${salesSit.noSaleCount} 个SKU`);
    const tr = timeliness.timelyRate ? parseFloat(timeliness.timelyRate) : 0;
    if (tr < 70) f.push(`分析及时率 ${fmtPct(tr)}，超7日未分析产品 ${timeliness.noAnalysis7dCount} 个`);
    const ls = (kpi as any).lowShareSku ?? lowShareData.length;
    if (ls > 30) f.push(`低占比新品 ${ls} 个，竞争压力显著，需排查定价与竞争力`);
    if (f.length === 0) f.push('本周各维度指标均在正常范围内');
    return f;
  }, [salesSit, timeliness, kpi, lowShareData]);

  const actions = useMemo(() => {
    const a: string[] = [];
    if ((timeliness.noAnalysis7dCount || 0) > 15) a.push('集中处理超7日未分析的低占比产品');
    if ((salesSit.noSaleCount || 0) > 0) a.push('对有对手但未出单的SKU做竞品对标分析');
    a.push('持续关注新品爬坡与广告ROAS表现');
    return a;
  }, [timeliness, salesSit]);

  // ===== 筛选器状态 =====
  const [lsFilter, setLsFilter] = useState({ ord8: '', analyst: '', category: '', adClass: '' });
  const filteredLowShare = useMemo(() => {
    return lowShareData.filter((r: any) => {
      if (lsFilter.ord8 && gf(r, 'cur8dStatus', '5.6 8日出单情况') !== lsFilter.ord8) return false;
      if (lsFilter.analyst && gf(r, 'analyst', '4月分析人') !== lsFilter.analyst) return false;
      if (lsFilter.category && gf(r, 'category', '品类') !== lsFilter.category) return false;
      return true;
    });
  }, [lowShareData, lsFilter]);

  const [cum43Filter, setCum43Filter] = useState({ analyst: '', category: '', ord8: '' });
  const filteredCum43 = useMemo(() => {
    return rawRows.filter((r: any) => {
      if (cum43Filter.analyst && gf(r, 'analyst', '4月分析人') !== cum43Filter.analyst) return false;
      if (cum43Filter.category && gf(r, 'category', '品类') !== cum43Filter.category) return false;
      if (cum43Filter.ord8 && gf(r, 'ord8Curr', 'cur8dStatus') !== cum43Filter.ord8) return false;
      return true;
    });
  }, [rawRows, cum43Filter]);

  // ===== 通用 KPI 渲染 =====
  const renderKpiGrid = (items: any[]) => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
      {items.map((item, i) => (
        <KpiCard key={i} label={item.label} value={item.value} helper={item.helper} />
      ))}
    </div>
  );

  // ===== 通用表格渲染 =====
  const renderTable = (columns: string[], rows: any[], getRow: (r: any) => any[], total?: any) => (
    <div className="table-scroll-wrap" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
      <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr style={{ background: COLORS.blue, color: '#fff' }}>
            {columns.map((c, i) => <th key={i} style={{ padding: '8px 10px', whiteSpace: 'nowrap' }}>{c}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
              {getRow(r).map((v: any, j: number) => (
                <td key={j} style={{ padding: '6px 10px', textAlign: 'center' }}>{v}</td>
              ))}
            </tr>
          ))}
        </tbody>
        {total && (
          <tfoot>
            <tr style={{ fontWeight: 700, background: '#e8f0fe' }}>
              {getRow(total).map((v: any, j: number) => (
                <td key={j} style={{ padding: '6px 10px', textAlign: 'center' }}>{v}</td>
              ))}
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );

  // ===== Tab 1: 总盘概览 =====
  const renderOverview = () => (
    <>
      {renderKpiGrid(overviewKpi)}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📈 出单分布</h4>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={ord8ChartData} cx="50%" cy="50%" innerRadius={55} outerRadius={100} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {ord8ChartData.map((d, i) => <Cell key={i} fill={d.color} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📊 品线销量对比</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={catData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="salesCurr" name="本周" fill={COLORS.blue} radius={[4,4,0,0]} />
              <Bar dataKey="salesPrev" name="上周" fill="#ccc" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>👤 分析人销量对比</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={anData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="salesCurr" name="本周" fill={COLORS.green} radius={[4,4,0,0]} />
              <Bar dataKey="salesPrev" name="上周" fill="#ccc" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>⏰ 分析及时率对比</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={timelyData.analysts}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)}%` : String(v)} />
              <Bar dataKey="rate" name="及时率" fill={COLORS.purple} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>💰 品线销售额对比</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={catData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? fmtUsd(v) : String(v)} />
              <Legend />
              <Bar dataKey="revCurr" name="本周" fill={COLORS.blue} radius={[4,4,0,0]} />
              <Bar dataKey="revPrev" name="上周" fill="#ccc" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>👤 分析人销售额对比</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={anData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? fmtUsd(v) : String(v)} />
              <Legend />
              <Bar dataKey="revCurr" name="本周" fill={COLORS.green} radius={[4,4,0,0]} />
              <Bar dataKey="revPrev" name="上周" fill="#ccc" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 出单情况表 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>📈 新品出单情况</h3>
        {renderTable(
          ['指标', '本周', '上周'],
          [
            { label: '有对手SKU', curr: salesSit.hasCompetitorSku, prev: salesSit.prevHasCompetitorSku },
            { label: '8日内出单(Y)', curr: salesSit.yCount, prev: salesSit.prevYCount },
            { label: '8日外出单(N)', curr: salesSit.nCount, prev: salesSit.prevNCount },
            { label: '未出单', curr: salesSit.noSaleCount, prev: salesSit.prevNoSaleCount },
            { label: '出单率', curr: salesSit.soldRate, prev: salesSit.prevSoldRate },
          ],
          (r: any) => [r.label, r.curr, r.prev],
        )}
      </div>

      {/* 品类维度 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>🔍 品线维度</h3>
        {renderTable(
          ['品线', 'SKU数', '本周销量', '上周销量', '环比', '本周销售额', '上周销售额'],
          catData,
          (r: any) => [r.name, r.sku, r.salesCurr, r.salesPrev, hbStr(r.salesCurr, r.salesPrev), fmtUsd(r.revCurr), fmtUsd(r.revPrev)],
        )}
      </div>

      {/* 分析人维度 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>👤 分析人维度</h3>
        {renderTable(
          ['分析人', 'SKU数', '本周销量', '上周销量', '环比', '本周销售额', '上周销售额'],
          anData,
          (r: any) => [r.name, r.sku, r.salesCurr, r.salesPrev, hbStr(r.salesCurr, r.salesPrev), fmtUsd(r.revCurr), fmtUsd(r.revPrev)],
        )}
      </div>

      {/* 拓展类型 + 及时率 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>📊 拓展类型 & 及时率</h3>
        <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 8 }}>拓展类型</h4>
        {renderTable(
          ['类型', 'SKU', '销量', '出单率', '上期出单率', '销售额'],
          expData,
          (r: any) => [r.name, r.sku, r.salesCurr, r.soldRate, r.prevSoldRate, fmtUsd(r.revCurr || 0)],
        )}
        <h4 style={{ fontSize: 13, color: COLORS.blue, margin: '16px 0 8px' }}>分析及时率</h4>
        {renderTable(
          ['分析人', '在跟SKU', '及时数', '8日内无分析', '超7日', '及时率'],
          timelyData.analysts,
          (r: any) => [r.name, r.sku, r.timelyCount || '-', r.noAnalysis8dCount || '-', r.noAnalysis7dCount || '-', r.timelyRate || '-'],
        )}
      </div>
    </>
  );

  // ===== Tab 2: 市场分布 =====
  const renderMarketDist = () => {
    if (!hasRawData) return <p style={{ color: '#888', padding: 40, textAlign: 'center' }}>需要上传 Excel 或加载 corrected_data.json 后才能查看市场分布数据</p>;
    return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
        {[
          { label: '正常市场', value: fmtNum(mktStatusData.curr.find(d => d.name === '正常')?.value || 0) },
          { label: '竞争无优势', value: fmtNum(mktStatusData.curr.find(d => d.name === '竞争无优势')?.value || 0) },
          { label: '无市场', value: fmtNum(mktStatusData.curr.find(d => d.name === '无市场')?.value || 0) },
          { label: '站外出单', value: fmtNum(mktStatusData.curr.find(d => d.name === '站外出单')?.value || 0) },
        ].map((item, i) => <KpiCard key={i} label={item.label} value={item.value} />)}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📊 本周市场状态占比</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={mktStatusData.curr} cx="50%" cy="50%" innerRadius={60} outerRadius={110} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {mktStatusData.curr.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📊 本周vs上周各状态SKU数</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mktStatusData.barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="本周" fill={COLORS.blue} radius={[4,4,0,0]} />
              <Bar dataKey="上周" fill="#ccc" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 市场状态明细 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>📋 市场状态明细</h3>
        {renderTable(
          ['状态', '本周SKU数', '上周SKU数'],
          mktStatusData.barData || [],
          (r: any) => [r.name, r.本周, r.上周],
        )}
      </div>

      {/* 货值分布 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>💰 货值分布</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16 }}>
            <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📊 价格区间SKU数分布</h4>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={priceDistData.dist}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="SKU数" fill={COLORS.green} radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16 }}>
            <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📊 按分析人-各价格区间SKU数</h4>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={priceDistData.byAn}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                {['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'].map((an, i) => (
                  <Bar key={an} dataKey={an} fill={CHART_COLORS[i % CHART_COLORS.length]} radius={[4,4,0,0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        {renderTable(
          ['区间', ...['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星']],
          priceDistData.byAn,
          (r: any) => [r.name, ...['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'].map(an => r[an] || 0)],
        )}
      </div>

      {/* 市占比分布 */}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>🎯 市占比分布（品线 x 高中低）</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16, marginBottom: 20 }}>
          <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16 }}>
            <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📊 各品线高中低市占比SKU分布</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={shareTierData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="高(≥75%)" fill={COLORS.green} stackId="a" radius={[0,0,0,0]} />
                <Bar dataKey="中(50-75%)" fill={COLORS.orange} stackId="a" />
                <Bar dataKey="低(<50%)" fill={COLORS.red} stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        {renderTable(
          ['品线', '高(≥75%)', '中(50-75%)', '低(<50%)'],
          shareTierData,
          (r: any) => [r.name, r['高(≥75%)'], r['中(50-75%)'], r['低(<50%)']],
        )}
      </div>
    </>
  );
  };

  // ===== Tab 3: 品效分析 =====
  const renderPerformance = () => (
    <>
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>📊 品效Cohort分析（按上架月份）</h3>
        {renderTable(
          ['上架月份', 'SKU数', '总销售额', '品效($/SKU)'],
          cohortData,
          (r: any) => [r.month + '月', r.SKU数, fmtUsd(r.总销售额), fmtUsd(r.品效)],
        )}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📈 月度销售额趋势</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={cohortData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? fmtUsd(v) : String(v)} />
              <Bar dataKey="总销售额" fill={COLORS.blue} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box" style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 12 }}>📈 品效趋势（$/SKU）</h4>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={cohortData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? fmtUsd(v) : String(v)} />
              <Line type="monotone" dataKey="品效" stroke={COLORS.green} strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );

  // ===== Tab 4: 低占比分析 =====
  const renderLowShare = () => {
    // 拆分有对手 vs 无对手
    const hasRivalRows = filteredLowShare.filter((r: any) => (r.curCompetitorQty || gf(r, 'rivalCurr', 'curRivalQty') || 0) > 0);
    const noRivalRows = filteredLowShare.filter((r: any) => (r.curCompetitorQty || gf(r, 'rivalCurr', 'curRivalQty') || 0) === 0);

    // 按分析人聚合
    const aggByAn = (rows: any[]) => {
      const m = new Map<string, number>();
      rows.forEach((r: any) => {
        const an = gf(r, 'analyst', '4月分析人') || '未知';
        m.set(an, (m.get(an) || 0) + 1);
      });
      return Array.from(m.entries()).map(([name, count]) => ({ name, count }));
    };
    // 按品线聚合
    const aggByCat = (rows: any[]) => {
      const m = new Map<string, number>();
      rows.forEach((r: any) => {
        const cat = gf(r, 'category', '品类') || '未分类';
        m.set(cat, (m.get(cat) || 0) + 1);
      });
      return Array.from(m.entries()).map(([name, count]) => ({ name, count }));
    };

    return (
      <>
        {renderKpiGrid(lowShareKpi)}

        <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20, borderLeft: '4px solid #c0392b' }}>
          <h3 style={{ fontSize: 15, color: '#c0392b', marginBottom: 16 }}>🔴 A. 有对手未出单新品 ({hasRivalRows.length})</h3>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 8 }}>按分析人</h4>
          {renderTable(['分析人', 'SKU数'], aggByAn(hasRivalRows), (r: any) => [r.name, r.count])}
          <h4 style={{ fontSize: 13, color: COLORS.blue, margin: '16px 0 8px' }}>按品线</h4>
          {renderTable(['品线', 'SKU数'], aggByCat(hasRivalRows), (r: any) => [r.name, r.count])}
        </div>

        <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20, borderLeft: '4px solid #08845a' }}>
          <h3 style={{ fontSize: 15, color: '#08845a', marginBottom: 16 }}>🟢 B. 无对手未出单新品 ({noRivalRows.length})</h3>
          <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 8 }}>按分析人</h4>
          {renderTable(['分析人', 'SKU数'], aggByAn(noRivalRows), (r: any) => [r.name, r.count])}
          <h4 style={{ fontSize: 13, color: COLORS.blue, margin: '16px 0 8px' }}>按品线</h4>
          {renderTable(['品线', 'SKU数'], aggByCat(noRivalRows), (r: any) => [r.name, r.count])}
        </div>

        {/* 筛选器 + 明细 */}
        <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20 }}>
          <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>👁 低占比新品明细 ({filteredLowShare.length})</h3>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, background: '#f5f7ff', padding: 12, borderRadius: 8 }}>
            <select value={lsFilter.ord8} onChange={e => setLsFilter({ ...lsFilter, ord8: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
              <option value="">8日出单: 全部</option>
              <option value="Y">Y - 8日内出单</option>
              <option value="N">N - 8日外出单</option>
              <option value="未出单">未出单</option>
            </select>
            <select value={lsFilter.analyst} onChange={e => setLsFilter({ ...lsFilter, analyst: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
              <option value="">分析人: 全部</option>
              {['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'].map(a => <option key={a} value={a}>{a}</option>)}
            </select>
            <select value={lsFilter.category} onChange={e => setLsFilter({ ...lsFilter, category: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
              <option value="">品线: 全部</option>
              {['车门系统','车身外扩件','挡泥板','机盖及附件','其他','饰条','牌照板支架'].map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <span style={{ fontSize: 12, color: '#888', alignSelf: 'center' }}>显示 {filteredLowShare.length} / {lowShareData.length}</span>
          </div>
          {renderTable(
            ['SKU', '分析人', '品类', '销量', '销售额', '市占比', '对手量', '8日出单', '市场状态', 'PLP', 'PLG费率'],
            filteredLowShare,
            (r: any) => [
              gf(r, 'sku', 'SKU') || '-',
              gf(r, 'analyst', '4月分析人') || '-',
              gf(r, 'category', '品类') || '-',
              gf(r, 'curSalesQty', '4.30-5.6销量') || gf(r, 'salesCurr', 'curSalesQty') || 0,
              gf(r, 'curRevenue', '4.30-5.6销售额') || gf(r, 'revenueCurr', 'curRevenue') || 0,
              (gf(r, 'curMarketShare', '5.6市占比') || gf(r, 'shareCurr', 'curMarketShare') || 0) + '%',
              gf(r, 'curCompetitorQty', '5.6对手销量') || gf(r, 'rivalCurr', 'curRivalQty') || 0,
              gf(r, 'cur8dStatus', '5.6 8日出单情况') || gf(r, 'ord8Curr', 'cur8dStatus') || '-',
              gf(r, 'curMarketStatus', '5.6市场状态') || gf(r, 'mktStatus', 'curMarketStatus') || '-',
              gf(r, 'plpEnabled', 'PLP是否开启') || gf(r, 'plpCurr', 'plpEnabled') || 'N',
              gf(r, 'plgFee', 'PLG最高费率') || gf(r, 'plgCurr', 'plgFee') || '0%',
            ],
          )}
        </div>
      </>
    );
  };

  // ===== Tab 5: 广告追踪 =====
  const renderAds = () => (
    <>
      {renderKpiGrid(adsKpi)}
      <div className="section" style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 16 }}>🔍 PLP 维度分析</h3>
        {plpData.analysts?.length > 0 ? (
          <>
            <h4 style={{ fontSize: 13, color: COLORS.blue, marginBottom: 8 }}>按分析人</h4>
            {renderTable(
              ['分析人', '活动', '曝光', '点击', '售出', '花费', '销售额', 'ROAS', 'ACOS'],
              plpData.analysts || [],
              (r: any) => [r.analyst, r.campaignCount, r.impression, r.click, r.sold, fmtUsd(r.cost || 0), fmtUsd(r.revenue || 0), r.roas, r.acos],
            )}
          </>
        ) : (
          <p style={{ color: '#888', fontSize: 13 }}>暂无PLP广告数据（需从Excel PLP明细Sheet加载）</p>
        )}
      </div>
    </>
  );

  // ===== Tab 6: 四三累计 =====
  const renderCum43 = () => (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
        <KpiCard label="累计SKU" value={fmtNum(rawRows.length)} />
        <KpiCard label="已出单" value={fmtNum(rawRows.filter((r: any) => gf(r, 'ord8Curr', 'cur8dStatus') === 'Y' || gf(r, 'ord8Curr', 'cur8dStatus') === 'N').length)} />
        <KpiCard label="未出单" value={fmtNum(rawRows.filter((r: any) => gf(r, 'ord8Curr', 'cur8dStatus') === '未出单').length)} />
        <KpiCard label="显示" value={`${filteredCum43.length} / ${rawRows.length}`} />
      </div>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, background: '#f5f7ff', padding: 12, borderRadius: 8 }}>
        <select value={cum43Filter.analyst} onChange={e => setCum43Filter({ ...cum43Filter, analyst: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">分析人: 全部</option>
          {['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'].map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select value={cum43Filter.category} onChange={e => setCum43Filter({ ...cum43Filter, category: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">品线: 全部</option>
          {['车门系统','车身外扩件','挡泥板','机盖及附件','其他','饰条','牌照板支架'].map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={cum43Filter.ord8} onChange={e => setCum43Filter({ ...cum43Filter, ord8: e.target.value })} style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">8日出单: 全部</option>
          <option value="Y">Y</option><option value="N">N</option><option value="未出单">未出单</option>
        </select>
        <span style={{ fontSize: 12, color: '#888', alignSelf: 'center' }}>{filteredCum43.length} / {rawRows.length} SKU</span>
      </div>
      <div style={{ background: '#fff', borderRadius: 10, padding: 12 }}>
        {renderTable(
          ['SKU', '上架日期', '分析人', '品类', '拓展', '销量', '销售额', '对手量', '市占比', '8日出单', '市场状态'],
          filteredCum43,
          (r: any) => [
            gf(r, 'SKU', 'sku') || gf(r, 'sku', 'SKU') || '-',
            gf(r, 'listDate', '实际上架日期') || '-',
            gf(r, 'analyst', '4月分析人') || '-',
            gf(r, 'category', '品类') || '-',
            gf(r, 'expandType', '产品拓展') || '-',
            gf(r, 'salesCurr', 'curSalesQty') || gf(r, 'curSalesQty', '4.30-5.6销量') || 0,
            gf(r, 'revenueCurr', 'curRevenue') || gf(r, 'curRevenue', '4.30-5.6销售额') || 0,
            gf(r, 'rivalCurr', 'curRivalQty') || gf(r, 'curRivalQty', '5.6对手销量') || 0,
            (gf(r, 'shareCurr', 'curMarketShare') || gf(r, 'curMarketShare', '5.6市占比') || 0) + '%',
            gf(r, 'ord8Curr', 'cur8dStatus') || gf(r, 'cur8dStatus', '5.6 8日出单情况') || '-',
            gf(r, 'mktStatus', 'curMarketStatus') || gf(r, 'curMarketStatus', '5.6市场状态') || '-',
          ],
        )}
      </div>
    </>
  );

  // ===== Tab 7: 汇报输出 =====
  const renderReport = () => (
    <>
      {renderKpiGrid(overviewKpi)}
      <div className="section" style={{ background: '#fff5f5', borderRadius: 10, padding: 20, marginBottom: 16, borderLeft: '4px solid #c0392b' }}>
        <h3 style={{ fontSize: 15, color: '#c0392b', marginBottom: 12 }}>⚠️ 风险预警</h3>
        {findings.filter(f => f.includes('竞争') || f.includes('超7日') || f.includes('低占比')).length > 0
          ? findings.filter(f => f.includes('竞争') || f.includes('超7日') || f.includes('低占比')).map((f, i) => <p key={i} style={{ fontSize: 13, color: '#555', margin: '4px 0' }}>• {f}</p>)
          : <p style={{ fontSize: 13, color: '#888' }}>本周无重大风险</p>}
      </div>
      <div className="section" style={{ background: '#f5f9ff', borderRadius: 10, padding: 20, marginBottom: 16, borderLeft: '4px solid #2980b9' }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 12 }}>🔍 本周期主要发现</h3>
        {findings.map((f, i) => <p key={i} style={{ fontSize: 13, color: '#555', margin: '4px 0' }}>• {f}</p>)}
      </div>
      <div className="section" style={{ background: '#fdf5ff', borderRadius: 10, padding: 20, marginBottom: 16, borderLeft: '4px solid #8e44ad' }}>
        <h3 style={{ fontSize: 15, color: '#8e44ad', marginBottom: 12 }}>🎯 下周重点动作</h3>
        {actions.map((a, i) => <p key={i} style={{ fontSize: 13, color: '#555', margin: '4px 0' }}>• {a}</p>)}
      </div>
      <div className="section" style={{ background: '#f9fafb', borderRadius: 10, padding: 20, borderLeft: '4px solid #0f3460' }}>
        <h3 style={{ fontSize: 15, color: COLORS.blue, marginBottom: 12 }}>📋 可复制周报文案</h3>
        <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#444', fontFamily: 'inherit' }}>
{`【新品周报 5.14-5.20】
在跟SKU ${kpi.totalSku}个，本周销量${kpi.totalSalesQty}（环比${hbStr(kpi.totalSalesQty, kpi.prevTotalSalesQty)}），
销售额${fmtUsd(kpi.totalRevenue)}（环比${hbStr(kpi.totalRevenue, kpi.prevTotalRevenue)}）。
有对手SKU ${kpi.hasCompetitorSku}个，出单率${fmtPct(salesSit.soldRate ? parseFloat(salesSit.soldRate) : 0)}。
分析及时率${fmtPct(timeliness.timelyRate ? parseFloat(timeliness.timelyRate) : 0)}，超7日未分析${timeliness.noAnalysis7dCount}个。
低占比新品${(kpi as any).lowShareSku ?? lowShareData.length}个。

主要发现：
${findings.map((f, i) => `${i + 1}. ${f}`).join('\n')}

下周重点动作：
${actions.map((a, i) => `${i + 1}. ${a}`).join('\n')}`}
        </pre>
      </div>
    </>
  );

  // ===== 主组件 =====
  const tabs: { id: TabId; label: string; icon: string }[] = [
    { id: 'overview', label: '总盘概览', icon: '📈' },
    { id: 'marketDist', label: '市场分布', icon: '🌎' },
    { id: 'performance', label: '品效分析', icon: '🔍' },
    { id: 'lowShare', label: '低占比分析', icon: '👁' },
    { id: 'ads', label: '广告追踪', icon: '💰' },
    { id: 'cum43', label: '四三累计', icon: '📊' },
    { id: 'report', label: '汇报输出', icon: '📝' },
  ];

  const renderTab = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'marketDist': return renderMarketDist();
      case 'performance': return renderPerformance();
      case 'lowShare': return renderLowShare();
      case 'ads': return renderAds();
      case 'cum43': return renderCum43();
      case 'report': return renderReport();
      default: return renderOverview();
    }
  };

  return (
    <ModulePageLayout
      title="新品状态"
      subtitle={`${dataPeriod} | 三部新品品效分析`}
      dataPeriod={dataPeriod}
      periodTypeLabel={periodTypeLabel}
      sourceStatusLabel={sourceStatusLabel}
    >
      {/* Tab 导航 */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 20, flexWrap: 'wrap', borderBottom: '2px solid #e8f0fe', paddingBottom: 8 }}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: '8px 16px', border: 'none', borderRadius: '6px 6px 0 0',
              background: activeTab === t.id ? COLORS.blue : 'transparent',
              color: activeTab === t.id ? '#fff' : '#555',
              fontSize: 13, fontWeight: activeTab === t.id ? 600 : 400,
              cursor: 'pointer', transition: 'all 0.2s',
            }}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* 内容区 */}
      {renderTab()}
    </ModulePageLayout>
  );
}
