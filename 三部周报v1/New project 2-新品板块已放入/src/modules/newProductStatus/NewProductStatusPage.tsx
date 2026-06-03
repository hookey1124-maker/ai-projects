import { useState, useMemo } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, ComposedChart,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import KpiCard from '../../components/common/KpiCard';
import ModulePageLayout from '../../components/common/ModulePageLayout';
import { useModulePeriodInfo } from '../useModulePeriodInfo';
import {
  getData, getOverviewKpi, getCategoryMetrics, getAnalystMetrics, get4wTrends,
  rawRows as _staticRawRows, WEEK_LABELS, ALL_PERIODS, getWeekLabels, getRawRows,
  getAdCompData, getLinkDetail, getShareTier, getHasOrder, getDeptKpi,
} from './newProductStatusAdapter';

// ===== 常量 =====
const BLUE = '#0f3460'; const GREEN = '#08845a'; const ORANGE = '#e07b24';
const RED = '#c0392b'; const PURPLE = '#8e44ad'; const INFO = '#2980b9';
const CHART = ['#0f3460','#08845a','#e07b24','#c0392b','#8e44ad','#2980b9','#16a085','#d35400','#2c3e50'];
const ANALYSTS = ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'];
const CATEGORIES = ['车门系统','车身外扩件','挡泥板','机盖及附件','牌照板支架','其他','饰条'];

type TabId = 'overview' | 'marketDist' | 'lowShare' | 'ads' | 'cum43' | 'report';

// ===== 工具 =====
const fmtPct = (v: number) => `${v.toFixed(1)}%`;
const fmtUsd = (v: number) => `$${v.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
const fmtNum = (v: number) => v.toLocaleString('en-US');
const fmtNum0 = (v: any) => typeof v === 'number' ? v.toLocaleString('en-US') : String(v || 0);
const hbStr = (curr: number, prev: number) => {
  if (!prev) return '-';
  const r = ((curr - prev) / Math.abs(prev)) * 100;
  return `${r > 0 ? '+' : ''}${r.toFixed(1)}%`;
};

export default function NewProductStatusPage() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [drillOpen, setDrillOpen] = useState(false);
  const defaultPeriodIdx = ALL_PERIODS.length > 0 ? ALL_PERIODS[ALL_PERIODS.length-1].index : 0;
  const [selectedPeriodIndex, setSelectedPeriodIndex] = useState(defaultPeriodIdx);
  const allData = useMemo(() => getData(selectedPeriodIndex), [selectedPeriodIndex]);
  const [drillData, setDrillData] = useState<{
    title: string; labels: string[]; datasets: any[]; dualY?: boolean; y2Label?: string;
  } | null>(null);
  const { periodTypeLabel, sourceStatusLabel } = useModulePeriodInfo('newProductStatus');

  // ===== 状态 =====
  const [lsFilter, setLsFilter] = useState({ ord8: '', analyst: '', category: '' });
  const [cum43Filter, setCum43Filter] = useState({ analyst: '', category: '', ord8: '', mktStatus: '', expandType: '', share: '', adClass: '' });

  // ===== 派生 =====
  const weekLabels = useMemo(() => getWeekLabels(selectedPeriodIndex), [selectedPeriodIndex]);
  const rawRows = useMemo(() => getRawRows(selectedPeriodIndex), [selectedPeriodIndex]);
  const kpi = useMemo(() => getOverviewKpi(selectedPeriodIndex), [selectedPeriodIndex]);
  const deptKpi = useMemo(() => getDeptKpi(selectedPeriodIndex), [selectedPeriodIndex]);
  const catMetrics = useMemo(() => getCategoryMetrics(selectedPeriodIndex), [selectedPeriodIndex]);
  const anMetrics = useMemo(() => getAnalystMetrics(selectedPeriodIndex), [selectedPeriodIndex]);
  const w4 = useMemo(() => get4wTrends(selectedPeriodIndex), [selectedPeriodIndex]);

  const timeliness = allData.timelinessData;
  const timeliness4w = allData.timeliness4w;
  const mktDist = allData.mktDistOverall;
  const priceOv = allData.priceOverview;
  const shareTier = allData.shareTierOverview;
  const hasUnsold = allData.hasCompetitorUnsold;
  const noUnsold = allData.unsoldNoCompetitor;
  const lowShareData = allData.lowShareData;
  const plgAn4w = allData.plgAn4w;

  // 广告构成数据（从 cum43Data 实时计算）
  const adComp = useMemo(() => getAdCompData(selectedPeriodIndex), [selectedPeriodIndex]);
  const linkDetail = useMemo(() => getLinkDetail(selectedPeriodIndex), [selectedPeriodIndex]);

  // 链接明细筛选
  const [linkFilter, setLinkFilter] = useState({ hasOrder: '', shareTier: '' });
  const filteredLinks = useMemo(() =>
    linkDetail.plpPlgLinks.filter((d: any) => {
      if (linkFilter.hasOrder && d.hasOrder !== linkFilter.hasOrder) return false;
      if (linkFilter.shareTier && d.shareTier !== linkFilter.shareTier) return false;
      return true;
    }), [linkDetail, linkFilter]);

  // 出单分布（4段：有/无对手 × 已/未出单）
  const ord8Dist = useMemo(() => {
    const stats = allData.cum43Stats;
    return [
      { name: '有对手已出单', value: (stats.yCount || 0) + (stats.nCount || 0), color: GREEN },
      { name: '有对手未出单', value: stats.unCount || 0, color: ORANGE },
      { name: '无对手已出单', value: stats.noRivalSold || 0, color: INFO },
      { name: '无对手未出单', value: stats.noRivalUnsold || 0, color: RED },
    ];
  }, [allData.cum43Stats]);

  // 4周趋势数据
  const trend4wData = useMemo(() =>
    weekLabels.map((l, i) => ({
      week: l,
      销量: w4.totalSales[i] || 0,
      销售额: w4.totalRev[i] || 0,
      市占比: w4.totalShare[i] || 0,
    })), [w4]);

  // 品线4周趋势（用于图表）
  const catShare4wChart = useMemo(() =>
    weekLabels.map((l, i) => {
      const pt: any = { week: l };
      CATEGORIES.forEach(cat => {
        const entry = w4.catShare.find((x: any) => x.category === cat);
        pt[cat] = entry ? (entry.share4w?.[i] ?? 0) : 0;
      });
      return pt;
    }), [w4]);

  // 分析人4周趋势
  const anShare4wChart = useMemo(() =>
    weekLabels.map((l, i) => {
      const pt: any = { week: l };
      ANALYSTS.forEach(an => {
        const entry = w4.anShare.find((x: any) => x.analyst === an);
        pt[an] = entry ? (entry.share4w?.[i] ?? 0) * 100 : 0;
      });
      return pt;
    }), [w4]);

  // 市场状态分布
  const mktCurr = useMemo(() =>
    (mktDist.distribution || []).map((d: any) => ({ name: d.status, value: d.curCount || 0 })),
    [mktDist]);
  const mktBar = useMemo(() =>
    (mktDist.distribution || []).map((d: any) => ({ name: d.status, 本周: d.curCount || 0, 上周: d.prevCount || 0 })),
    [mktDist]);

  // 货值分布
  const priceDist = useMemo(() =>
    (priceOv.distribution || []).map((d: any) => ({ name: d.range, SKU数: d.count || 0 })),
    [priceOv]);
  const priceByAn = useMemo(() => {
    const ranges = (priceOv.distribution || []).map((d: any) => d.range);
    const byAnalystList = priceOv.byAnalyst || [];
    return ranges.map((range: string) => {
      const row: any = { name: range };
      ANALYSTS.forEach(an => {
        const entry = byAnalystList.find((a: any) => a.analyst === an);
        row[an] = entry ? (entry[range] || 0) : 0;
      });
      return row;
    });
  }, [priceOv]);

  // 市占比分布（品线×高中低）
  const shareTierChart = useMemo(() =>
    (shareTier.byCategory || []).map((c: any) => ({
      name: c.category,
      '高(≥75%)': c.high || 0,
      '中(50-75%)': c.mid || 0,
      '低(<50%)': c.low || 0,
    })), [shareTier]);

  // 市占比分布明细：品线+分析人 4周市占比
  const catShareDetail = useMemo(() =>
    (w4.catShare || []).map((c: any) => ({
      name: c.category,
      shares: c.share4w || [0, 0, 0, 0],
      change: (c.share4w?.[3] || 0) - (c.share4w?.[2] || 0),
    })), [w4]);
  const anShareDetail = useMemo(() =>
    (w4.anShare || []).map((a: any) => ({
      name: a.analyst,
      shares: a.share4w || [0, 0, 0, 0],
      change: (a.share4w?.[3] || 0) - (a.share4w?.[2] || 0),
    })), [w4]);

  // 低占比筛选
  const filteredLowShare = useMemo(() =>
    lowShareData.filter((r: any) => {
      const row8d = String(r.cur8dStatus ?? '');
      if (lsFilter.ord8 !== '' && row8d !== lsFilter.ord8) return false;
      if (lsFilter.analyst !== '' && r.analyst !== lsFilter.analyst) return false;
      if (lsFilter.category !== '' && r.category !== lsFilter.category) return false;
      return true;
    }), [lowShareData, lsFilter]);

  // 四三累计筛选
  const filteredCum43 = useMemo(() =>
    rawRows.filter((r: any) => {
      if (cum43Filter.analyst && r.analyst !== cum43Filter.analyst) return false;
      if (cum43Filter.category && r.category !== cum43Filter.category) return false;
      if (cum43Filter.ord8 && r.cur8dStatus !== cum43Filter.ord8) return false;
      if (cum43Filter.mktStatus && r.curMarketStatus !== cum43Filter.mktStatus) return false;
      if (cum43Filter.expandType && r.expandType !== cum43Filter.expandType) return false;
      if (cum43Filter.share === 'high' && (r.curMarketShare || 0) < 75) return false;
      if (cum43Filter.share === 'mid' && ((r.curMarketShare || 0) < 50 || (r.curMarketShare || 0) >= 75)) return false;
      if (cum43Filter.share === 'low' && (r.curMarketShare || 0) >= 50) return false;
      if (cum43Filter.adClass && r.adClass !== cum43Filter.adClass) return false;
      return true;
    }), [rawRows, cum43Filter]);

  // 4周 drill 数据map
  const drillMap = useMemo(() => {
    const m = new Map<string, any>();
    catMetrics.forEach((c: any) => m.set(c.category, {
      label: c.category, sales4w: c.sales4w, revenue4w: c.revenue4w, share4w: c.share4w,
    }));
    anMetrics.forEach((a: any) => m.set(a.analyst, {
      label: a.analyst, sales4w: a.sales4w, revenue4w: a.revenue4w, share4w: a.share4w,
    }));
    // 及时率
    (timeliness4w.analysts || []).forEach((d: any) => m.set('time:' + d.analyst, {
      label: d.analyst + ' 及时率', rates4w: d.rates4w, isTimeliness: true,
    }));
    if (timeliness4w.totalRates) m.set('time:总及时率', {
      label: '总及时率', rates4w: timeliness4w.totalRates, isTimeliness: true,
    });
    // PLP
    (allData.plpAn4w || []).forEach((d: any) => m.set('plp:an:' + d.analyst, {
      label: d.analyst + ' PLP', spend4w: d.spend4w, adSales4w: d.adSales4w,
      acos4w: d.acos4w, acoas4w: d.acoas4w, isPLP: true,
    }));
    (allData.plpCat4w || []).forEach((d: any) => m.set('plp:cat:' + d.category, {
      label: d.category + ' PLP', spend4w: d.spend4w, adSales4w: d.adSales4w,
      acos4w: d.acos4w, acoas4w: d.acoas4w, isPLP: true,
    }));
    (allData.plpExp4w || []).forEach((d: any) => m.set('plp:exp:' + d.expandType, {
      label: d.expandType + ' PLP', spend4w: d.spend4w, adSales4w: d.adSales4w,
      acos4w: d.acos4w, acoas4w: d.acoas4w, isPLP: true,
    }));
    // PLG 分析人4周
    (allData.plgAn4w || []).forEach((d: any) => m.set('plg:an:' + d.analyst, {
      label: d.analyst + ' PLG', spend4w: d.spend4w, adSales4w: d.adSales4w,
      acos4w: d.acos4w, acoas4w: d.acoas4w, isPLP: true,
    }));
    // 四三累计 SKU 4周
    const cum4w = allData.cum43_4w || {};
    Object.keys(cum4w).forEach(sku => m.set('sku:' + sku, {
      label: sku, ...cum4w[sku], isSKU: true,
    }));
    return m;
  }, [catMetrics, anMetrics, timeliness4w]);

  // ===== 渲染工具 =====
  const renderKpiGrid = (items: any[]) => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
      {items.map((item, i) => <KpiCard key={i} {...item} />)}
    </div>
  );

  const renderTable = (columns: string[], rows: any[], getRow: (r: any) => any[], total?: any) => (
    <div className="table-scroll-wrap" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
      <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr style={{ background: BLUE, color: '#fff' }}>
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

  const chartBox = (title: string, children: any, height = 280) => (
    <div style={{ background: '#fff', borderRadius: 10, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
      <h4 style={{ fontSize: 13, color: BLUE, marginBottom: 12 }}>{title}</h4>
      <ResponsiveContainer width="100%" height={height}>{children}</ResponsiveContainer>
    </div>
  );

  // 下钻触发
  const handleDrill = (key: string, label: string) => {
    const entry = drillMap.get(key);
    if (!entry) return;
    const labels = WEEK_LABELS;

    if (entry.isTimeliness) {
      setDrillData({
        title: label + ' 4周趋势', labels,
        datasets: [{ name: '及时率(%)', data: entry.rates4w || [], stroke: PURPLE }],
      });
    } else if (entry.isPLP) {
      const acosData = (entry.acos4w || []).map((v: any) => typeof v === 'number' ? v : parseFloat(v) || 0);
      const acoasData = (entry.acoas4w || []).map((v: any) => typeof v === 'number' ? v : parseFloat(v) || 0);
      setDrillData({
        title: label + ' 4周趋势', labels, dualY: true, y2Label: 'ACOS/ACOAS(%)',
        datasets: [
          { name: '花费($)', data: entry.spend4w || [], stroke: RED, yAxis: 'left' },
          { name: '广告销售额($)', data: entry.adSales4w || [], stroke: GREEN, yAxis: 'left' },
          { name: 'ACOS(%)', data: acosData, stroke: ORANGE, yAxis: 'right' },
          { name: 'ACOAS(%)', data: acoasData, stroke: PURPLE, yAxis: 'right' },
        ],
      });
    } else if (entry.isSKU) {
      setDrillData({
        title: label + ' 4周趋势', labels,
        datasets: [
          { name: '销量', data: entry.sales4w || [0,0,0,0], stroke: BLUE },
          { name: '销售额($)', data: entry.rev4w || [0,0,0,0], stroke: GREEN },
        ],
      });
    } else {
      setDrillData({
        title: label + ' 4周趋势', labels, dualY: true, y2Label: '销量 / 市占比(%)',
        datasets: [
          { name: '销售额($)', data: entry.revenue4w || [0,0,0,0], stroke: GREEN, yAxis: 'left' },
          { name: '销量', data: entry.sales4w || [0,0,0,0], stroke: BLUE, yAxis: 'right' },
          { name: '市占比(%)', data: (entry.share4w || [0,0,0,0]), stroke: ORANGE, yAxis: 'right' },
        ],
      });
    }
    setDrillOpen(true);
  };

  const drillLink = (key: string, text: string) => (
    <span onClick={() => handleDrill(key, text)} style={{ color: BLUE, cursor: 'pointer', fontWeight: 500 }}
      onMouseEnter={e => (e.target as HTMLElement).style.textDecoration = 'underline'}
      onMouseLeave={e => (e.target as HTMLElement).style.textDecoration = 'none'}>
      {text}
    </span>
  );

  // ===== Tab 1: 总盘概览 =====
  const renderOverview = () => (
    <>
      {renderKpiGrid([
        { label: '累计在售SKU', value: fmtNum(kpi.totalSku), helper: `新上架 +${kpi.curNewSku}` },
        { label: '本周销量', value: fmtNum(kpi.totalSalesQty), helper: `环比 ${hbStr(kpi.totalSalesQty, kpi.prevTotalSalesQty)}` },
        { label: '本周销售额', value: fmtUsd(kpi.totalRevenue), helper: `上周${fmtUsd(kpi.prevTotalRevenue)} | 环比 ${hbStr(kpi.totalRevenue, kpi.prevTotalRevenue)}` },
        { label: '新品总市占比', value: `${kpi.totalMarketShare.toFixed(1)}%`, helper: `上周${kpi.totalMarketSharePrev.toFixed(1)}% | ${kpi.totalMarketShare - kpi.totalMarketSharePrev >= 0 ? '+' : ''}${(kpi.totalMarketShare - kpi.totalMarketSharePrev).toFixed(1)}%` },
        { label: '有对手SKU', value: fmtNum(kpi.hasCompetitorSku), helper: `无对手 ${kpi.noCompetitorSku}` },
        { label: '出单率', value: fmtPct(kpi.soldRate), helper: `已出单 ${kpi.soldCount}/${kpi.hasCompetitorSku}` },
        { label: '分析及时率', value: String(kpi.timeliness?.timelyRate || '-'), helper: `超7日 ${kpi.timeliness?.noAnalysis7dCount || 0}` },
        { label: '低占比新品', value: fmtNum(kpi.lowShareCount), helper: '市占比<75%' },
      ])}

      {/* 部门对比 + PW爬虫市占 KPI */}
      {renderKpiGrid([
        { label: '新品销量占部门比', value: `${deptKpi.salesPct}%`, helper: `新品${fmtNum(deptKpi.newSales)} / 部门${fmtNum(deptKpi.deptSales)}` },
        { label: '新品销售额占部门比', value: `${deptKpi.revPct}%`, helper: `新品$${fmtNum(deptKpi.newRevenue)} / 部门$${fmtNum(deptKpi.deptRevenue)}` },
        { label: 'PW爬虫市占', value: `${deptKpi.pwShare}%`, helper: `${deptKpi.pwTotalLinks}个有对手SKU` },
        { label: '新品加权市占', value: `${deptKpi.newShareW}%`, helper: `${deptKpi.newSkuCount}个有对手SKU` },
        { label: '市占差值', value: `${deptKpi.diffShare}%`, helper: 'PW vs 新品（平行参考）' },
      ])}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        {chartBox('📈 出单分布（4段）',
          <PieChart>
            <Pie data={ord8Dist} cx="50%" cy="50%" innerRadius={55} outerRadius={100} dataKey="value"
              label={({ name, value }) => `${name}: ${value}`}>
              {ord8Dist.map((d, i) => <Cell key={i} fill={d.color} />)}
            </Pie>
            <Tooltip />
          </PieChart>
        )}
        {chartBox('📈 4周销量趋势',
          <LineChart data={trend4wData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Line type="monotone" dataKey="销量" stroke={BLUE} strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        )}
        {chartBox('📈 4周销售额趋势',
          <LineChart data={trend4wData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip formatter={(v: any) => typeof v === 'number' ? fmtUsd(v) : String(v)} />
            <Line type="monotone" dataKey="销售额" stroke={GREEN} strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        )}
        {chartBox('📈 4周市占比趋势',
          <LineChart data={trend4wData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
            <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)}%` : String(v)} />
            <Line type="monotone" dataKey="市占比" stroke={ORANGE} strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        )}
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>📈 新品出单情况</h3>
        {renderTable(
          ['分类', '数量', '说明'],
          [
            { label: '有对手已出单(Y+N)', value: kpi.yCount + kpi.nCount, desc: '有竞品但有出单，正常竞争' },
            { label: '有对手未出单', value: kpi.noSaleCount, desc: '有竞品且未出单，需重点关注' },
            { label: '无对手已出单', value: allData.cum43Stats.noRivalSold || 0, desc: '无竞品已出单，市场独占' },
            { label: '无对手未出单', value: allData.cum43Stats.noRivalUnsold || 0, desc: '无竞品也未出单，需关注选品' },
          ],
          (r: any) => [r.label, r.value, r.desc],
          { label: '合计', value: kpi.totalSku, desc: `有对手${kpi.hasCompetitorSku}个 + 无对手${kpi.noCompetitorSku}个` },
        )}
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>🔍 多维度分析（含市占比）</h3>
        <h4 style={{ fontSize: 13, color: BLUE, background: '#f5f7ff', padding: '8px 12px', borderLeft: `3px solid ${BLUE}`, marginBottom: 10 }}>品线维度</h4>
        {renderTable(
          ['品线', 'SKU', '新上架', '销量', '销量环比', '销售额', '销售额环比', '市占比', '市占环比'],
          catMetrics,
          (r: any) => [
            drillLink(r.category, r.category), r.curSku, r.curNewSku || 0,
            r.curSalesQty, hbStr(r.curSalesQty, r.prevSalesQty),
            fmtUsd(r.curRevenue), hbStr(r.curRevenue, r.prevRevenue),
            r.share4w?.[3] != null ? fmtPct(r.share4w[3]) : '-',
            r.curMarketShare != null && r.prevMarketShare != null
              ? hbStr(r.curMarketShare, r.prevMarketShare) : '-',
          ],
        )}
        <h4 style={{ fontSize: 13, color: BLUE, background: '#f5f7ff', padding: '8px 12px', borderLeft: `3px solid ${BLUE}`, margin: '16px 0 10px' }}>分析人维度</h4>
        {renderTable(
          ['分析人', 'SKU', '新上架', '销量', '销量环比', '销售额', '销售额环比', '市占比', '市占环比'],
          anMetrics,
          (r: any) => [
            drillLink(r.analyst, r.analyst), r.curSku, r.curNewSku || 0,
            r.curSalesQty, hbStr(r.curSalesQty, r.prevSalesQty),
            fmtUsd(r.curRevenue), hbStr(r.curRevenue, r.prevRevenue),
            r.share4w?.[3] != null ? fmtPct(r.share4w[3]) : '-',
            r.curMarketShare != null && r.prevMarketShare != null
              ? hbStr(r.curMarketShare, r.prevMarketShare) : '-',
          ],
        )}
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>📊 拓展类型 & 及时率</h3>
        <h4 style={{ fontSize: 13, color: BLUE, background: '#f5f7ff', padding: '8px 12px', borderLeft: `3px solid ${BLUE}`, marginBottom: 10 }}>拓展类型</h4>
        {renderTable(
          ['类型', '本周SKU', '上周SKU', '出单SKU', '上期出单SKU', '出单率', '上期出单率', '销量', '上期销量', '环比', '销售额', '上期销售额'],
          allData.expandTypeData,
          (r: any) => [
            r.expandType, r.curSku, r.prevSku || '-',
            r.curSalesSku || '-', r.prevSalesSku || '-',
            r.curSalesRate || '-', r.prevSalesRate || '-',
            r.curSalesQty || '-', r.prevSalesQty || '-',
            hbStr(r.curSalesQty, r.prevSalesQty),
            fmtUsd(r.curRevenue || 0), fmtUsd(r.prevRevenue || 0),
          ],
        )}
        <h4 style={{ fontSize: 13, color: BLUE, background: '#f5f7ff', padding: '8px 12px', borderLeft: `3px solid ${BLUE}`, margin: '16px 0 10px' }}>分析及时率</h4>
        {renderTable(
          ['分析人', '本周SKU', '及时分析', '8日未分析', '7日未分析', '及时率', '上周及时率', '变化'],
          timeliness.analysts || [],
          (r: any) => [
            drillLink('time:' + r.analyst, r.analyst), r.curSku || '-',
            r.timelyCount || '-', r.noAnalysis8dCount || '-', r.noAnalysis7dCount || '-',
            r.timelyRate || '-', r.prevTimelyRate || '-', r.change || '-',
          ],
          timeliness.total ? { analyst: '合计', curSku: timeliness.total.curSku, timelyCount: timeliness.total.timelyCount, noAnalysis8dCount: timeliness.total.noAnalysis8dCount, noAnalysis7dCount: timeliness.total.noAnalysis7dCount, timelyRate: timeliness.total.timelyRate, prevTimelyRate: timeliness.total.prevTimelyRate || '-', change: timeliness.total.change || '-' } : undefined,
        )}
      </div>
    </>
  );

  // ===== Tab 2: 市场分布 =====
  const renderMarketDist = () => (
    <>
      {renderKpiGrid([
        { label: '正常市场', value: fmtNum(mktCurr.find((d: any) => d.name === '正常')?.value || 0) },
        { label: '竞争无优势', value: fmtNum(mktCurr.find((d: any) => d.name === '竞争无优势')?.value || 0) },
        { label: '无市场', value: fmtNum(mktCurr.find((d: any) => d.name === '无市场')?.value || 0) },
        { label: '站外出单', value: fmtNum(mktCurr.find((d: any) => d.name === '站外出单')?.value || 0) },
      ])}

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>🌎 市场状态分布</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {chartBox('本周市场状态占比',
            <PieChart>
              <Pie data={mktCurr.filter((d: any) => d.value > 0)} cx="50%" cy="50%" innerRadius={60} outerRadius={110} dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}>
                {mktCurr.filter((d: any) => d.value > 0).map((_: any, i: number) => <Cell key={i} fill={CHART[i % CHART.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>, 300
          )}
          {chartBox('本周vs上周各状态SKU数',
            <BarChart data={mktBar}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="本周" fill={BLUE} radius={[4,4,0,0]} />
              <Bar dataKey="上周" fill="#ccc" radius={[4,4,0,0]} />
            </BarChart>, 300
          )}
        </div>
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>📋 市场状态明细</h3>
        {renderTable(
          ['状态', '本周SKU数', '上周SKU数'],
          mktBar, (r: any) => [r.name, r.本周, r.上周],
        )}
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>💰 货值分布（销售额/销量）</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          {chartBox('价格区间SKU数分布',
            <BarChart data={priceDist}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="SKU数" fill={GREEN} radius={[4,4,0,0]} />
            </BarChart>
          )}
          {chartBox('按分析人-各价格区间SKU数',
            <BarChart data={priceByAn}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              {ANALYSTS.map((an, i) => <Bar key={an} dataKey={an} fill={CHART[i % CHART.length]} radius={[4,4,0,0]} />)}
            </BarChart>
          )}
        </div>
        <h4 style={{ fontSize: 13, color: BLUE, marginBottom: 8 }}>货值明细</h4>
        {renderTable(
          ['价格区间', 'SKU数', '占比'],
          (priceOv.distribution || []).map((d: any) => ({ range: d.range, count: d.count, pct: d.pct })),
          (r: any) => [r.range, r.count, r.pct != null ? `${r.pct}%` : '-'],
          { range: '汇总', count: `${priceOv.totalWithSales || 0} 个有销售额`, pct: `均价 $${(priceOv.avgPrice || 0).toFixed(2)} / 中位 $${(priceOv.medianPrice || 0).toFixed(2)}` },
        )}
        <h4 style={{ fontSize: 13, color: BLUE, margin: '16px 0 8px' }}>按分析人-各价格区间</h4>
        {renderTable(
          ['区间', ...ANALYSTS],
          priceByAn, (r: any) => [r.name, ...ANALYSTS.map(an => r[an] || 0)],
        )}
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>🎯 市占比分布</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          {chartBox('总市占比4周趋势',
            <LineChart data={trend4wData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)}%` : String(v)} />
              <Line type="monotone" dataKey="市占比" stroke={ORANGE} strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          )}
          {chartBox('品线市占比4周趋势',
            <LineChart data={catShare4wChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)}%` : String(v)} />
              <Legend />
              {CATEGORIES.map((cat, i) => <Line key={cat} type="monotone" dataKey={cat} stroke={CHART[i % CHART.length]} strokeWidth={1.5} dot={{ r: 3 }} />)}
            </LineChart>
          )}
          {chartBox('分析人市占比4周趋势',
            <LineChart data={anShare4wChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)}%` : String(v)} />
              <Legend />
              {ANALYSTS.map((an, i) => <Line key={an} type="monotone" dataKey={an} stroke={CHART[i % CHART.length]} strokeWidth={1.5} dot={{ r: 3 }} />)}
            </LineChart>
          )}
          {chartBox('各品线高中低市占比分布',
            <BarChart data={shareTierChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="高(≥75%)" fill={GREEN} stackId="a" />
              <Bar dataKey="中(50-75%)" fill={ORANGE} stackId="a" />
              <Bar dataKey="低(<50%)" fill={RED} stackId="a" />
            </BarChart>
          )}
        </div>
        <h4 style={{ fontSize: 13, color: BLUE, marginBottom: 8 }}>📋 品线×4周市占比</h4>
        {renderTable(
          ['品线', ...WEEK_LABELS, '环比变化'],
          catShareDetail,
          (r: any) => [
            r.name,
            ...r.shares.map((v: number) => v != null ? `${v.toFixed(1)}%` : '-'),
            hbStr(r.shares[3], r.shares[2]),
          ],
        )}
        <h4 style={{ fontSize: 13, color: BLUE, margin: '16px 0 8px' }}>📋 分析人×4周市占比</h4>
        {renderTable(
          ['分析人', ...WEEK_LABELS, '环比变化'],
          anShareDetail,
          (r: any) => [
            r.name,
            ...r.shares.map((v: number) => v != null ? `${v.toFixed(1)}%` : '-'),
            hbStr(r.shares[3], r.shares[2]),
          ],
        )}
      </div>
    </>
  );

  // ===== Tab 3: 低占比分析 =====
  const renderLowShare = () => {
    const hasMkts = ['竞争无优势', '站内无价格优势'];
    const noMkts = ['无市场', '站外出单'];

    return (
      <>
        {renderKpiGrid([
          { label: '低占比总数', value: fmtNum(lowShareData.length), helper: '市占比<75%' },
          { label: '有对手未出单', value: fmtNum(hasUnsold.total || 0), helper: `环比 ${(hasUnsold.change || 0) > 0 ? '+' : ''}${hasUnsold.change || 0}` },
          { label: '无对手未出单', value: fmtNum(noUnsold.total || 0), helper: `环比 ${(noUnsold.change || 0) > 0 ? '+' : ''}${noUnsold.change || 0}` },
        ])}

        <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20, borderLeft: `4px solid ${RED}` }}>
          <h3 style={{ fontSize: 15, color: RED, marginBottom: 16 }}>🔴 A. 有对手未出单新品 ({hasUnsold.total || 0})</h3>
          <h4 style={{ fontSize: 13, color: BLUE, marginBottom: 8 }}>按分析人</h4>
          {renderTable(
            ['分析人', ...hasMkts, '合计'],
            hasUnsold.byAnalyst || [],
            (r: any) => [r.analyst, ...hasMkts.map((k: string) => r[k] || 0), r.total],
          )}
          <h4 style={{ fontSize: 13, color: BLUE, margin: '16px 0 8px' }}>按品线</h4>
          {renderTable(
            ['品线', ...hasMkts, '合计'],
            hasUnsold.byCategory || [],
            (r: any) => [r.category, ...hasMkts.map((k: string) => r[k] || 0), r.total],
          )}
        </div>

        <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20, borderLeft: `4px solid ${GREEN}` }}>
          <h3 style={{ fontSize: 15, color: GREEN, marginBottom: 16 }}>🟢 B. 无对手未出单新品 ({noUnsold.total || 0})</h3>
          <h4 style={{ fontSize: 13, color: BLUE, marginBottom: 8 }}>按分析人</h4>
          {renderTable(
            ['分析人', ...noMkts, '合计'],
            noUnsold.byAnalyst || [],
            (r: any) => [r.analyst, ...noMkts.map((k: string) => r[k] || 0), r.total],
          )}
          <h4 style={{ fontSize: 13, color: BLUE, margin: '16px 0 8px' }}>按品线</h4>
          {renderTable(
            ['品线', ...noMkts, '合计'],
            noUnsold.byCategory || [],
            (r: any) => [r.category, ...noMkts.map((k: string) => r[k] || 0), r.total],
          )}
        </div>

        <div style={{ background: '#fff', borderRadius: 10, padding: 20 }}>
          <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>👁 低占比新品明细 ({filteredLowShare.length})</h3>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, background: '#f5f7ff', padding: 12, borderRadius: 8 }}>
            <select value={lsFilter.ord8} onChange={e => setLsFilter({ ...lsFilter, ord8: e.target.value })}
              style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
              <option value="">8日出单: 全部</option>
              <option value="Y">Y - 8日内出单</option>
              <option value="N">N - 8日外出单</option>
              <option value="未出单">未出单</option>
            </select>
            <select value={lsFilter.analyst} onChange={e => setLsFilter({ ...lsFilter, analyst: e.target.value })}
              style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
              <option value="">分析人: 全部</option>
              {ANALYSTS.map(a => <option key={a} value={a}>{a}</option>)}
            </select>
            <select value={lsFilter.category} onChange={e => setLsFilter({ ...lsFilter, category: e.target.value })}
              style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
              <option value="">品线: 全部</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <span style={{ fontSize: 12, color: '#888', alignSelf: 'center' }}>显示 {filteredLowShare.length} / {lowShareData.length}</span>
          </div>
          {renderTable(
            ['SKU', '分析人', '品类', '上架', '销量', '销售额', '市占比', '对手量', '8日出单', '市场状态', 'PLP', 'PLG费率', '广告分类'],
            filteredLowShare,
            (r: any) => [
              r.SKU || r.sku || '-',
              r.analyst || '-',
              r.category || '-',
              r.launchDate || r.listDate || '-',
              fmtNum0(r.curSalesQty),
              fmtUsd(r.curRevenue || 0),
              typeof r.curMarketShare === 'number' ? fmtPct(r.curMarketShare) : String(r.curMarketShare || '-'),
              fmtNum0(r.curRivalQty || r.curCompetitorQty || 0),
              r.cur8dStatus || '-',
              r.curMarketStatus || '-',
              r.plpEnabled || 'N',
              r.plgFee || '0%',
              r.adClass || '-',
            ],
          )}
        </div>
      </>
    );
  };

  // ===== Tab 4: 广告追踪 =====
  const renderAds = () => (
    <>
      {/* 广告构成分布 */}
      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>📊 广告构成分布</h3>
        {renderKpiGrid(
          (['PLP+PLG', '单PLP', '仅PLG', '无广告'] as const).map(k => {
            const item = adComp.compKpis.find(x => x.label === k) || { label: k, count: 0 };
            const color = { 'PLP+PLG': RED, '单PLP': BLUE, '仅PLG': ORANGE, '无广告': '#95a5a6' }[k];
            return { label: k, value: fmtNum(item.count), helper: '', _color: color };
          })
        )}
        <h4 style={{ fontSize: 13, color: BLUE, background: '#f5f7ff', padding: '8px 12px', borderLeft: `3px solid ${BLUE}`, marginBottom: 10 }}>按分析人</h4>
        {renderTable(
          ['分析人', '总数', 'PLP+PLG', '单PLP', '仅PLG', '无广告'],
          adComp.byAnalyst,
          (r: any) => [r.analyst, r.total, <b style={{color:RED}}>{r['PLP+PLG']}</b>, r['单PLP'], r['仅PLG'], r['无广告']],
        )}
        <h4 style={{ fontSize: 13, color: BLUE, background: '#f5f7ff', padding: '8px 12px', borderLeft: `3px solid ${BLUE}`, margin: '16px 0 10px' }}>按品线</h4>
        {renderTable(
          ['品线', '总数', 'PLP+PLG', '单PLP', '仅PLG', '无广告'],
          adComp.byCategory,
          (r: any) => [r.category, r.total, <b style={{color:RED}}>{r['PLP+PLG']}</b>, r['单PLP'], r['仅PLG'], r['无广告']],
        )}
      </div>

      {/* PLG费率分档 */}
      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>🏷️ PLG费率分档</h3>
        {renderKpiGrid(
          (['无广告', '低费率', '中费率', '高费率'] as const).map(k => {
            const item = adComp.tierKpis.find(x => x.label === k) || { label: k, count: 0 };
            const color = { '高费率': RED, '中费率': ORANGE, '低费率': GREEN, '无广告': '#95a5a6' }[k];
            return { label: k + (k === '低费率' ? '(≤2%)' : k === '中费率' ? '(2-4%)' : k === '高费率' ? '(>4%)' : ''), value: fmtNum(item.count), helper: '', _color: color };
          })
        )}
      </div>

      {/* 链接明细（PLP+PLG同开，链接维度） */}
      <div style={{ background: '#fff', borderRadius: 10, padding: 20, marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 16 }}>🔗 广告构成明细（链接维度：PLP+PLG同开）</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 16 }}>
          <KpiCard
            label={linkFilter.hasOrder || linkFilter.shareTier ? 'PLP+PLG同开（筛选后）' : 'PLP+PLG同开（链接数）'}
            value={fmtNum(filteredLinks.length)}
            style={{ borderLeft: '4px solid #c0392b' }}
          />
        </div>
        {/* 筛选栏 */}
        <div style={{
          position: 'sticky', top: 0, zIndex: 100, background: '#f5f7ff',
          padding: '14px 18px', marginBottom: 14, display: 'flex', flexWrap: 'nowrap',
          gap: 10, alignItems: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 0,
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}>
            <label style={{ color: '#555', whiteSpace: 'nowrap' }}>是否出单</label>
            <select value={linkFilter.hasOrder} onChange={e => setLinkFilter({ ...linkFilter, hasOrder: e.target.value })}
              style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12, background: '#fff' }}>
              <option value="">全部</option>
              <option value="是">是</option>
              <option value="否">否</option>
            </select>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}>
            <label style={{ color: '#555', whiteSpace: 'nowrap' }}>市占比</label>
            <select value={linkFilter.shareTier} onChange={e => setLinkFilter({ ...linkFilter, shareTier: e.target.value })}
              style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12, background: '#fff' }}>
              <option value="">全部</option>
              <option value="高">高(≥75%)</option>
              <option value="中">中(50%-75%)</option>
              <option value="低">低(&lt;50%)</option>
              <option value="无市场">无市场(对手0销量)</option>
            </select>
          </span>
          <button onClick={() => setLinkFilter({ hasOrder: '', shareTier: '' })}
            style={{ color: '#c0392b', border: '1px solid #c0392b', background: '#fff', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 12 }}>
            重置
          </button>
          <span style={{ fontSize: 12, color: '#888', marginLeft: 'auto' }}>
            筛选: {filteredLinks.length} / {linkDetail.plpPlgCount} 条
          </span>
        </div>
        {/* 链接明细表 */}
        {linkDetail.plpPlgCount > 0 ? (
          <div style={{ maxHeight: 360, overflow: 'auto' }}>
            {renderTable(
              ['SKU', 'ID', '广告活动', '分析人', '品类', '是否出单', '市占比', '对手销量', '销量', '销售额', 'PLG费率'],
              filteredLinks,
              (d: any) => [
                d.sku,
                <span style={{fontSize:11}}>{d.linkId || '-'}</span>,
                d.campaign,
                d.analyst,
                d.category,
                d.hasOrder,
                <>{d.marketShare > 0 ? `${d.marketShare.toFixed(1)}%` : '-'} <span style={{fontSize:10,color:'#888'}}>[{d.shareTier}]</span></>,
                d.rivalQty > 0 ? d.rivalQty : '-',
                d.salesQty > 0 ? d.salesQty : '-',
                d.revenue > 0 ? `$${d.revenue.toFixed(2)}` : '-',
                `${d.plgFee.toFixed(1)}%`,
              ],
            )}
          </div>
        ) : (
          <p style={{ color: '#888', fontSize: 13 }}>暂无PLP+PLG同开链接（需从PLP明细Sheet筛选plgEnabled=Y的记录）</p>
        )}
      </div>
    </>
  );

  // ===== Tab 5: 四三累计 =====
  const cum43TotalSales = useMemo(() => filteredCum43.reduce((s, r) => s + (r.curSalesQty || 0), 0), [filteredCum43]);
  const cum43TotalRev = useMemo(() => filteredCum43.reduce((s, r) => s + (r.curRevenue || 0), 0), [filteredCum43]);
  const cum43TotalRival = useMemo(() => filteredCum43.reduce((s, r) => s + (r.curRivalQty || 0), 0), [filteredCum43]);

  const renderCum43 = () => (
    <>
      {renderKpiGrid([
        { label: '累计SKU', value: fmtNum(rawRows.length) },
        { label: '已出单', value: fmtNum(rawRows.filter((r: any) => r.cur8dStatus === 'Y' || r.cur8dStatus === 'N').length) },
        { label: '未出单', value: fmtNum(rawRows.filter((r: any) => r.cur8dStatus !== 'Y' && r.cur8dStatus !== 'N').length) },
        { label: '筛选结果', value: `${filteredCum43.length} / ${rawRows.length}` },
      ])}

      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, background: '#f5f7ff', padding: 12, borderRadius: 8, position: 'sticky', top: 0, zIndex: 10, alignItems: 'center' }}>
        <select value={cum43Filter.mktStatus} onChange={e => setCum43Filter({ ...cum43Filter, mktStatus: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">市场状态: 全部</option>
          <option value="正常">正常</option><option value="竞争无优势">竞争无优势</option>
          <option value="无市场">无市场</option><option value="站外出单">站外出单</option>
        </select>
        <select value={cum43Filter.analyst} onChange={e => setCum43Filter({ ...cum43Filter, analyst: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">分析人: 全部</option>
          {ANALYSTS.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select value={cum43Filter.category} onChange={e => setCum43Filter({ ...cum43Filter, category: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">品线: 全部</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={cum43Filter.expandType} onChange={e => setCum43Filter({ ...cum43Filter, expandType: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">拓展类型: 全部</option>
          <option value="原开品">原开品</option><option value="拓展品">拓展品</option><option value="组合件">组合件</option>
        </select>
        <select value={cum43Filter.ord8} onChange={e => setCum43Filter({ ...cum43Filter, ord8: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">8日出单: 全部</option>
          <option value="Y">Y</option><option value="N">N</option><option value="未出单">未出单</option>
        </select>
        <select value={cum43Filter.share} onChange={e => setCum43Filter({ ...cum43Filter, share: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">市占比: 全部</option>
          <option value="high">75%及以上</option><option value="mid">50%-75%</option><option value="low">50%以下</option>
        </select>
        <select value={cum43Filter.adClass} onChange={e => setCum43Filter({ ...cum43Filter, adClass: e.target.value })}
          style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 12 }}>
          <option value="">广告条件: 全部</option>
          <option value="PLP+PLG同开">PLP+PLG同开</option>
          <option value="单链接PLP+PLG同开">单链接PLP+PLG同开</option>
          <option value="单PLG">单PLG</option><option value="单PLP">单PLP</option>
          <option value="单PLG且未出单">单PLG且未出单</option><option value="无广告">无广告</option>
        </select>
        <button onClick={() => setCum43Filter({ analyst: '', category: '', ord8: '', mktStatus: '', expandType: '', share: '', adClass: '' })}
          style={{ padding: '6px 14px', border: '1px solid #c0392b', borderRadius: 6, background: '#fff', color: '#c0392b', cursor: 'pointer', fontSize: 12 }}>
          重置筛选
        </button>
        <span style={{ fontSize: 12, color: '#888', marginLeft: 'auto' }}>筛选结果: {filteredCum43.length} / {rawRows.length} 条</span>
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: 12 }}>
        {renderTable(
          ['SKU', '上架日期', '首次出单', '分析人', '品类', '拓展类型', '本周销量', '本周销售额', '对手量', '市占比', 'PLG费率', '市场状态', '8日出单', '广告分类'],
          filteredCum43,
          (r: any) => [
            r.SKU || r.sku || '-',
            r.listDate || '-',
            r.firstOrderDate || '-',
            r.analyst || '-',
            r.category || '-',
            r.expandType || '-',
            fmtNum0(r.curSalesQty),
            fmtUsd(r.curRevenue || 0),
            fmtNum0(r.curRivalQty || 0),
            r.curMarketShare != null ? `${r.curMarketShare}%` : '-',
            r.plgFee || '0%',
            r.curMarketStatus || '-',
            r.cur8dStatus || '-',
            r.adClass || '-',
          ],
          { SKU: `合计（${filteredCum43.length}条）`, listDate: '', firstOrderDate: '', analyst: '', category: '', expandType: '', curSalesQty: cum43TotalSales, curRevenue: cum43TotalRev, curRivalQty: cum43TotalRival, curMarketShare: null, plgFee: '', curMarketStatus: '', cur8dStatus: '', adClass: '' },
        )}
      </div>
    </>
  );

  // ===== Tab 6: 汇报输出 =====
  const renderReport = () => {
    const findings = [
      kpi.soldRate < 90 ? `出单率 ${fmtPct(kpi.soldRate)}，有对手未出单 ${kpi.noSaleCount} 个SKU需关注` : null,
      parseFloat(String(kpi.timeliness?.timelyRate || '0')) < 70 ? `分析及时率 ${kpi.timeliness?.timelyRate}，超7日未分析 ${kpi.timeliness?.noAnalysis7dCount || 0} 个` : null,
      kpi.lowShareCount > 30 ? `低占比新品 ${kpi.lowShareCount} 个，竞争压力显著` : null,
    ].filter(Boolean) as string[];

    const actions = [
      (kpi.timeliness?.noAnalysis7dCount || 0) > 15 ? '集中处理超7日未分析的低占比产品' : null,
      kpi.noSaleCount > 0 ? '对有对手但未出单的SKU做竞品对标分析' : null,
      '持续关注新品爬坡与广告ROAS表现',
    ].filter(Boolean) as string[];

    const hasRisk = findings.filter(f => f.includes('低占比') || f.includes('超7日') || (kpi.soldRate < 90 && f.includes('出单率'))).length > 0;

    return (
      <>
        {renderKpiGrid([
          { label: '累计在售SKU', value: fmtNum(kpi.totalSku), helper: `新上架 +${kpi.curNewSku}` },
          { label: '本周销量', value: fmtNum(kpi.totalSalesQty), helper: `环比 ${hbStr(kpi.totalSalesQty, kpi.prevTotalSalesQty)}` },
          { label: '本周销售额', value: fmtUsd(kpi.totalRevenue), helper: `环比 ${hbStr(kpi.totalRevenue, kpi.prevTotalRevenue)}` },
          { label: '出单率', value: fmtPct(kpi.soldRate), helper: `已出单 ${kpi.soldCount}/${kpi.hasCompetitorSku}` },
          { label: '分析及时率', value: String(kpi.timeliness?.timelyRate || '-'), helper: `超7日 ${kpi.timeliness?.noAnalysis7dCount || 0}` },
          { label: '低占比新品', value: fmtNum(kpi.lowShareCount), helper: '市占比<75%' },
        ])}

        {hasRisk && (
          <div style={{ background: '#fff5f5', borderRadius: 10, padding: 20, marginBottom: 16, borderLeft: `4px solid ${RED}` }}>
            <h3 style={{ fontSize: 15, color: RED, marginBottom: 12 }}>⚠️ 风险预警</h3>
            {findings.filter(f => f.includes('低占比') || f.includes('超7日') || f.includes('出单率')).map((f, i) =>
              <p key={i} style={{ fontSize: 13, color: '#555', margin: '4px 0' }}>• {f}</p>
            )}
          </div>
        )}

        <div style={{ background: '#f5f9ff', borderRadius: 10, padding: 20, marginBottom: 16, borderLeft: `4px solid ${INFO}` }}>
          <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 12 }}>🔍 本周期主要发现</h3>
          {findings.length > 0
            ? findings.map((f, i) => <p key={i} style={{ fontSize: 13, color: '#555', margin: '4px 0' }}>• {f}</p>)
            : <p style={{ fontSize: 13, color: '#888' }}>本周各维度指标均在正常范围内</p>
          }
        </div>

        <div style={{ background: '#fdf5ff', borderRadius: 10, padding: 20, marginBottom: 16, borderLeft: `4px solid ${PURPLE}` }}>
          <h3 style={{ fontSize: 15, color: PURPLE, marginBottom: 12 }}>🎯 下周重点动作</h3>
          {actions.map((a, i) => <p key={i} style={{ fontSize: 13, color: '#555', margin: '4px 0' }}>• {a}</p>)}
        </div>

        <div style={{ background: '#f9fafb', borderRadius: 10, padding: 20, borderLeft: `4px solid ${BLUE}` }}>
          <h3 style={{ fontSize: 15, color: BLUE, marginBottom: 12 }}>📋 可复制周报文案</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#444', fontFamily: 'inherit' }}>
{`【新品周报 5.21-5.27】
在跟SKU ${kpi.totalSku}个，本周销量${kpi.totalSalesQty}（环比${hbStr(kpi.totalSalesQty, kpi.prevTotalSalesQty)}），
销售额${fmtUsd(kpi.totalRevenue)}（环比${hbStr(kpi.totalRevenue, kpi.prevTotalRevenue)}）。
有对手SKU ${kpi.hasCompetitorSku}个，出单率${fmtPct(kpi.soldRate)}。
分析及时率${kpi.timeliness?.timelyRate || '-'}，超7日未分析${kpi.timeliness?.noAnalysis7dCount || 0}个。
低占比新品${kpi.lowShareCount}个。

主要发现：
${findings.map((f, i) => `${i + 1}. ${f}`).join('\n')}

下周重点动作：
${actions.map((a, i) => `${i + 1}. ${a}`).join('\n')}`}
          </pre>
        </div>
      </>
    );
  };

  // ===== Tab 配置 =====
  const tabs: { id: TabId; label: string; icon: string }[] = [
    { id: 'overview', label: '总盘概览', icon: '📈' },
    { id: 'marketDist', label: '市场分布', icon: '🌎' },
    { id: 'lowShare', label: '低占比分析', icon: '👁' },
    { id: 'ads', label: '广告追踪', icon: '💰' },
    { id: 'cum43', label: '四三累计', icon: '📊' },
    { id: 'report', label: '汇报输出', icon: '📝' },
  ];

  const renderTab = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'marketDist': return renderMarketDist();
      case 'lowShare': return renderLowShare();
      case 'ads': return renderAds();
      case 'cum43': return renderCum43();
      case 'report': return renderReport();
    }
  };

  return (
    <ModulePageLayout
      title="新品状态"
      subtitle="5/21 - 5/27 | 三部新品品效分析"
      dataPeriod="5/21 - 5/27"
      periodTypeLabel={periodTypeLabel}
      sourceStatusLabel={sourceStatusLabel}
    >
      <div style={{ display: 'flex', gap: 4, marginBottom: 20, flexWrap: 'wrap', borderBottom: '2px solid #e8f0fe', paddingBottom: 8 }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            style={{
              padding: '8px 16px', border: 'none', borderRadius: '6px 6px 0 0',
              background: activeTab === t.id ? BLUE : 'transparent',
              color: activeTab === t.id ? '#fff' : '#555',
              fontSize: 13, fontWeight: activeTab === t.id ? 600 : 400,
              cursor: 'pointer', transition: 'all 0.2s',
            }}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* 周期选择器 */}
      {ALL_PERIODS.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, background: '#f5f7ff', padding: '8px 14px', borderRadius: 8 }}>
          <span style={{ fontSize: 13, color: '#555', whiteSpace: 'nowrap' }}>截止周:</span>
          <select
            value={selectedPeriodIndex}
            onChange={e => setSelectedPeriodIndex(Number(e.target.value))}
            style={{ padding: '6px 12px', border: '1px solid #ddd', borderRadius: 6, fontSize: 13, background: '#fff' }}
          >
            {ALL_PERIODS.map((p: any) => (
              <option key={p.index} value={p.index}>{p.label}</option>
            ))}
          </select>
          <span style={{ fontSize: 12, color: '#888' }}>
            (显示 {weekLabels[0] || '--'} ~ {weekLabels[weekLabels.length-1] || '--'} 共4周)
          </span>
        </div>
      )}

      {renderTab()}

      {/* 下钻弹窗 */}
      {drillOpen && drillData && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          onClick={() => setDrillOpen(false)}>
          <div style={{ background: '#fff', borderRadius: 10, padding: 24, maxWidth: drillData.dualY ? 800 : 700, width: '90%' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <h3 style={{ fontSize: 16, color: BLUE }}>{drillData.title}</h3>
              <button onClick={() => setDrillOpen(false)}
                style={{ border: 'none', background: 'none', fontSize: 20, cursor: 'pointer', color: '#888' }}>✕</button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              {drillData.dualY ? (
                <ComposedChart data={drillData.labels.map((l: string, i: number) => {
                  const pt: any = { week: l };
                  drillData.datasets.forEach((ds: any) => { pt[ds.name] = ds.data[i] || 0; });
                  return pt;
                })}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis yAxisId="left" tick={{ fontSize: 10 }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10 }}
                    label={{ value: drillData.y2Label, angle: -90, position: 'insideRight', fontSize: 10 }} />
                  <Tooltip />
                  <Legend />
                  {drillData.datasets.map((ds: any, i: number) => (
                    <Line key={i} yAxisId={ds.yAxis || 'left'} type="monotone" dataKey={ds.name}
                      stroke={ds.stroke} strokeWidth={2} dot={{ r: 3 }} />
                  ))}
                </ComposedChart>
              ) : (
                <LineChart data={drillData.labels.map((l: string, i: number) => {
                  const pt: any = { week: l };
                  drillData.datasets.forEach((ds: any) => { pt[ds.name] = ds.data[i] || 0; });
                  return pt;
                })}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {drillData.datasets.map((ds: any, i: number) => (
                    <Line key={i} type="monotone" dataKey={ds.name} stroke={ds.stroke} strokeWidth={2} dot={{ r: 4 }} />
                  ))}
                </LineChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </ModulePageLayout>
  );
}
