# -*- coding: utf-8 -*-
"""
生成新品周报 HTML (5 Tab 完整版)
读取 corrected_data.json → 嵌入全部 21 个数据块 → 输出自包含 HTML
"""

import json
import os

JSON_PATH = r"C:/Users/Administrator/Desktop/三部周报v1/New project 2-新品板块已放入/src/modules/newProductStatus/corrected_data.json"
OUTPUT_PATH = r"C:/Users/Administrator/Desktop/三部周报v1/新品周报-单模块/新品板块_4.30-5.6_v3.html"

DATA_KEYS = [
    "cum43Data", "cum43Stats", "lowShareData", "expandTypeData", "timelinessData",
    "hasCompetitorUnsold", "plpTotal", "plpPrevTotal", "plpCategories", "plpExpandTypes",
    "plpAnalysts", "unsoldNoCompetitor", "prevWeekKpi", "plgStats",
    "prevWeekCategories", "prevWeekAnalysts", "plgRecords",
    "categoryRevenueData", "analystRevenueData", "plpSummaryData", "plpDetailData",
]

# ========== 加载数据 ==========
with open(JSON_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

# 验证所有 key 存在
for k in DATA_KEYS:
    if k not in raw:
        raise ValueError(f"Missing key: {k}")

# 序列化嵌入
js_vars = "\n".join(f"const {k} = {json.dumps(raw[k], ensure_ascii=False, indent=0)};" for k in DATA_KEYS)

# ========== 构建 HTML ==========
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报板块 · 4.30-5.6</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "Microsoft YaHei","PingFang SC",Arial,sans-serif; background: #f0f2f5; color: #1a1a2e; }}
.header {{ background: linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%); color: white; padding: 28px 40px; }}
.header h1 {{ font-size: 26px; font-weight: 700; letter-spacing: 2px; }}
.header .subtitle {{ font-size: 13px; opacity: 0.75; margin-top: 6px; }}
.container {{ display: flex; min-height: calc(100vh - 80px); }}
.sidebar {{ width: 230px; background: #fff; border-right: 1px solid #e8e8e8; padding: 20px 0; position: sticky; top: 0; height: 100vh; overflow-y: auto; flex-shrink: 0; }}
.sidebar ul {{ list-style: none; }}
.sidebar li a {{ display: block; padding: 10px 20px; font-size: 13px; color: #555; text-decoration: none; border-left: 3px solid transparent; transition: all 0.2s; }}
.sidebar li a:hover,.sidebar li a.active {{ background: #f0f6ff; color: #0f3460; border-left-color: #0f3460; font-weight: 600; }}
.main-content {{ flex: 1; padding: 24px; overflow: auto; }}
.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(155px,1fr)); gap: 14px; margin-bottom: 24px; }}
.kpi-card {{ background: white; border-radius: 10px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
.kpi-card .val {{ font-size: 26px; font-weight: 700; color: #0f3460; }}
.kpi-card .label {{ font-size: 12px; color: #888; margin-top: 6px; }}
.kpi-card .hb {{ font-size: 11px; margin-top: 4px; font-weight: 600; }}
.kpi-card.green .val {{ color: #08845a; }}
.kpi-card.orange .val {{ color: #e07b24; }}
.kpi-card.red .val {{ color: #c0392b; }}
.kpi-card.purple .val {{ color: #8e44ad; }}
.section {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.section h3 {{ font-size: 16px; font-weight: 700; color: #0f3460; padding-bottom: 12px; border-bottom: 2px solid #e8f0fe; margin-bottom: 16px; }}
.sub-module {{ margin-bottom: 20px; }}
.sub-module h4 {{ font-size: 13px; font-weight: 600; color: #444; margin-bottom: 10px; padding: 6px 12px; background: #f5f7ff; border-radius: 4px; border-left: 3px solid #0f3460; }}
.chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(400px,1fr)); gap: 20px; margin-bottom: 20px; }}
.chart-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.chart-card h4 {{ font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 14px; }}
.chart-card canvas {{ max-height: 260px; }}
.table-wrap {{ overflow-x: auto; }}
.data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.data-table th {{ background: #0f3460; color: white; padding: 8px; text-align: center; white-space: nowrap; font-weight: 600; }}
.data-table th.p1 {{ background: #6c757d; }}
.data-table th.p2 {{ background: #667eea; }}
.data-table th.p3 {{ background: #2980b9; }}
.data-table th.p4 {{ background: #c0392b; }}
.data-table th.hb {{ background: #e07b24; }}
.data-table th.green {{ background: #08845a; }}
.data-table td {{ padding: 6px 8px; text-align: center; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }}
.data-table tr:hover td {{ background: #f5f7ff; }}
.data-table tfoot td {{ font-weight: 700; background: #f5f7ff; }}
.hb-up {{ color: #c0392b; font-weight: 700; }}
.hb-down {{ color: #08845a; font-weight: 700; }}
.hb-flat {{ color: #888; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: white; font-weight: 600; }}
.badge-y {{ background: #08845a; }}
.badge-n {{ background: #e07b24; }}
.badge-un {{ background: #c0392b; }}
.badge-normal {{ background: #2980b9; }}
select {{ padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; font-size: 13px; background: white; cursor: pointer; }}
select:focus {{ outline: none; border-color: #0f3460; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #f1f1f1; }}
::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 3px; }}
@media(max-width:900px) {{ .sidebar {{ display: none; }} .chart-grid {{ grid-template-columns: 1fr; }} .kpi-grid {{ grid-template-columns: repeat(2,1fr); }} }}
.tab-bar {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.tab-btn {{ padding: 6px 16px; border-radius: 6px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.2s; }}
.tab-btn:hover {{ border-color: #0f3460; }}
.tab-btn.active {{ background: #0f3460; color: white; border-color: #0f3460; }}
.filter-bar {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; padding: 12px; background: #f5f7ff; border-radius: 8px; }}
.filter-item {{ display: flex; align-items: center; gap: 6px; }}
.filter-item label {{ font-size: 12px; color: #666; font-weight: 600; }}
.filter-item select {{ padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; background: white; font-size: 12px; cursor: pointer; min-width: 120px; }}
.filter-item select:focus {{ outline: none; border-color: #0f3460; }}
.reset-btn {{ padding: 6px 14px; border-radius: 6px; border: 1px solid #c0392b; background: white; color: #c0392b; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }}
.reset-btn:hover {{ background: #c0392b; color: white; }}
.filter-result {{ font-size: 12px; color: #666; margin-top: 8px; text-align: right; }}
.plp-grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap: 16px; margin-bottom: 20px; }}
.plp-card {{ background: white; border-radius: 10px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #8e44ad; }}
.plp-card h4 {{ font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 12px; }}
.plp-metric {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #f0f0f0; font-size: 12px; }}
.plp-metric:last-child {{ border-bottom: none; }}
.plp-metric .lbl {{ color: #666; }}
.plp-metric .val {{ font-weight: 600; color: #1a1a2e; }}
.highlight-red {{ background: #fdecea; border-radius: 6px; padding: 10px; margin-top: 10px; }}
.highlight-orange {{ background: #fff3e6; border-radius: 6px; padding: 10px; margin-top: 10px; }}
.highlight-green {{ background: #e8f5e9; border-radius: 6px; padding: 10px; margin-top: 10px; }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
.copy-btn {{ padding: 6px 16px; border-radius: 6px; border: 1px solid #0f3460; background: white; color: #0f3460; font-size: 12px; font-weight: 600; cursor: pointer; margin-top: 10px; }}
.copy-btn:hover {{ background: #0f3460; color: white; }}
.report-block {{ background: #f9fafb; border-radius: 8px; padding: 16px; margin-bottom: 12px; border-left: 4px solid #0f3460; font-size: 13px; line-height: 1.8; white-space: pre-wrap; }}
.risk-item {{ display: flex; align-items: flex-start; gap: 8px; padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; font-size: 13px; }}
.risk-high {{ background: #fdecea; border-left: 4px solid #c0392b; }}
.risk-medium {{ background: #fff3e6; border-left: 4px solid #e07b24; }}
.risk-low {{ background: #e8f5e9; border-left: 4px solid #08845a; }}
.finding-item {{ padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; background: #f5f7ff; font-size: 13px; border-left: 4px solid #2980b9; }}
.action-item {{ padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; background: #f0f6ff; font-size: 13px; border-left: 4px solid #667eea; }}
</style>
</head>
<body>

<div class="header">
  <h1>新品周报板块 · 4.30-5.6</h1>
  <div class="subtitle">数据周期：2026年4月30日 - 5月6日 | 自动生成报告</div>
</div>

<div class="container">
  <div class="sidebar">
    <ul>
      <li><a href="#" class="active" onclick="switchTab('tab1',this)">总盘概览</a></li>
      <li><a href="#" onclick="switchTab('tab2',this)">低占比分析</a></li>
      <li><a href="#" onclick="switchTab('tab3',this)">广告追踪</a></li>
      <li><a href="#" onclick="switchTab('tab4',this)">四三累计</a></li>
      <li><a href="#" onclick="switchTab('tab5',this)">汇报输出</a></li>
    </ul>
  </div>

  <div class="main-content">

<!-- ============================================================ -->
<!-- TAB 1: 总盘概览 -->
<!-- ============================================================ -->
<div id="tab1" class="tab-content active">

  <!-- KPI 卡片 -->
  <div class="kpi-grid" id="kpi-overview"></div>

  <!-- 6 图表 -->
  <div class="chart-grid">
    <div class="chart-card"><h4>出单分布饼图</h4><canvas id="chart-pie1"></canvas></div>
    <div class="chart-card"><h4>品线销量对比</h4><canvas id="chart-bar1"></canvas></div>
    <div class="chart-card"><h4>分析人销量对比</h4><canvas id="chart-bar2"></canvas></div>
    <div class="chart-card"><h4>分析人及时率对比</h4><canvas id="chart-bar3"></canvas></div>
    <div class="chart-card"><h4>品线销售额对比</h4><canvas id="chart-bar4"></canvas></div>
    <div class="chart-card"><h4>分析人销售额对比</h4><canvas id="chart-bar5"></canvas></div>
  </div>

  <!-- 新品出单情况(有对手口径) -->
  <div class="section">
    <h3>新品出单情况（有对手口径）</h3>
    <div id="sold-overview-kpi" class="kpi-grid" style="margin-bottom:16px"></div>
    <div class="sub-module">
      <h4>按分析人维度</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-sold-analyst"></table></div>
    </div>
    <div class="sub-module">
      <h4>按品线维度</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-sold-category"></table></div>
    </div>
  </div>

  <!-- 多维度分析 -->
  <div class="section">
    <h3>多维度分析</h3>
    <div class="sub-module">
      <h4>品线维度</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-multi-category"></table></div>
    </div>
    <div class="sub-module">
      <h4>分析人维度</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-multi-analyst"></table></div>
    </div>
  </div>

  <!-- 拓展类型 + 及时率 -->
  <div class="section">
    <h3>拓展类型维度 &amp; 分析及时率</h3>
    <div class="sub-module">
      <h4>拓展类型统计</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-expand"></table></div>
    </div>
    <div class="sub-module">
      <h4>分析及时率（按分析人）</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-timely"></table></div>
    </div>
  </div>
</div>

<!-- ============================================================ -->
<!-- TAB 2: 低占比分析 -->
<!-- ============================================================ -->
<div id="tab2" class="tab-content">
  <div class="kpi-grid" id="kpi-lowshare"></div>

  <div class="section">
    <h3>A - 有对手未出单新品</h3>
    <div class="table-wrap"><table class="data-table" id="tbl-has-competitor"></table></div>
  </div>

  <div class="section">
    <h3>B - 无对手未出单新品</h3>
    <div class="table-wrap"><table class="data-table" id="tbl-no-competitor"></table></div>
  </div>

  <div class="section">
    <h3>新品未出单原因分析</h3>
    <div class="sub-module">
      <h4>按分析人维度</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-reason-analyst"></table></div>
    </div>
    <div class="sub-module">
      <h4>按品线维度</h4>
      <div class="table-wrap"><table class="data-table" id="tbl-reason-category"></table></div>
    </div>
  </div>
</div>

<!-- ============================================================ -->
<!-- TAB 3: 广告追踪 -->
<!-- ============================================================ -->
<div id="tab3" class="tab-content">
  <div class="kpi-grid" id="kpi-plp"></div>

  <div class="plp-grid" id="plp-core-metrics"></div>

  <div class="section">
    <h3>分析人维度 PLP</h3>
    <div class="table-wrap"><table class="data-table" id="tbl-plp-analyst"></table></div>
  </div>
  <div class="section">
    <h3>品线维度 PLP</h3>
    <div class="table-wrap"><table class="data-table" id="tbl-plp-category"></table></div>
  </div>

  <div class="section">
    <h3>PLG 费率统计</h3>
    <div class="kpi-grid" id="kpi-plg"></div>
    <div class="table-wrap"><table class="data-table" id="tbl-plg-analyst"></table></div>
  </div>

  <div class="section">
    <h3>PLP 广告明细（53条）</h3>
    <div class="table-wrap"><table class="data-table" id="tbl-plp-detail"></table></div>
  </div>
</div>

<!-- ============================================================ -->
<!-- TAB 4: 四三累计 -->
<!-- ============================================================ -->
<div id="tab4" class="tab-content">
  <div class="kpi-grid" id="kpi-cum43"></div>

  <div class="filter-bar" id="filter-bar">
    <div class="filter-item"><label>市场状态</label>
      <select id="f-market"><option value="">全部</option><option>正常</option><option>竞争无优势</option><option>无市场</option></select></div>
    <div class="filter-item"><label>分析人</label>
      <select id="f-analyst"><option value="">全部</option></select></div>
    <div class="filter-item"><label>品类</label>
      <select id="f-category"><option value="">全部</option></select></div>
    <div class="filter-item"><label>产品拓展</label>
      <select id="f-expand"><option value="">全部</option><option>原开品</option><option>拓展品</option><option>组合件</option></select></div>
    <div class="filter-item"><label>8日出单</label>
      <select id="f-8d"><option value="">全部</option><option>Y</option><option>N</option></select></div>
    <div class="filter-item"><label>市占比</label>
      <select id="f-share"><option value="">全部</option><option value="high">&gt;=75%</option><option value="mid">50%~75%</option><option value="low">&lt;50%</option></select></div>
    <div class="filter-item"><label>市场竞争</label>
      <select id="f-compete"><option value="">全部</option><option value="yes">有竞争</option><option value="no">无竞争</option></select></div>
    <div class="filter-item"><label>广告条件</label>
      <select id="f-ad"><option value="">全部</option><option value="plp_plg">PLP+PLG</option><option value="plg_only">单PLG</option><option value="plp_only">单PLP</option><option value="no_ad">无广告</option><option value="plp_off_nosale">PLP未开且未出单</option></select></div>
    <button class="reset-btn" onclick="resetFilters()">取消筛选</button>
  </div>
  <div class="filter-result" id="filter-result"></div>

  <div class="section">
    <h3>新品明细表格</h3>
    <div class="table-wrap"><table class="data-table" id="tbl-cum43"></table></div>
  </div>
</div>

<!-- ============================================================ -->
<!-- TAB 5: 汇报输出 -->
<!-- ============================================================ -->
<div id="tab5" class="tab-content">
  <div class="kpi-grid" id="kpi-report"></div>

  <div class="section">
    <h3>风险预警</h3>
    <div id="risk-list"></div>
  </div>

  <div class="section">
    <h3>本周期主要发现</h3>
    <div id="finding-list"></div>
  </div>

  <div class="section">
    <h3>下周重点动作</h3>
    <div id="action-list"></div>
  </div>

  <div class="section">
    <h3>可复制周报文案</h3>
    <div id="report-blocks"></div>
  </div>
</div>

  </div><!-- /main-content -->
</div><!-- /container -->

<script>
{js_vars}

// ========== Tab 切换 ==========
function switchTab(tabId, el) {{
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
  if(el) el.classList.add('active');
  // 初始化 tab1 图表（延迟渲染）
  if(tabId === 'tab1' && !window._charts1Init) initCharts1();
}}

// ========== 工具函数 ==========
function hbClass(v) {{
  if(typeof v !== 'string') return '';
  if(v.startsWith('+')) return 'hb-up';
  if(v.startsWith('-')) return 'hb-down';
  return 'hb-flat';
}}
function hbSign(v) {{
  if(typeof v !== 'string') return v;
  if(v === '-' || v === '0%' || v === '0.0%' || v === '+0%') return '<span class="hb-flat">-</span>';
  if(v.startsWith('+')) return '<span class="hb-up">' + v + '</span>';
  if(v.startsWith('-')) return '<span class="hb-down">' + v + '</span>';
  return '<span class="hb-flat">' + v + '</span>';
}}
function badge8d(v) {{
  if(v === 'Y') return '<span class="badge badge-y">Y</span>';
  if(v === 'N') return '<span class="badge badge-n">N</span>';
  return '<span class="badge badge-un">' + (v||'-') + '</span>';
}}
function badgeStatus(v) {{
  if(v === '正常') return '<span class="badge badge-normal">' + v + '</span>';
  if(v === '竞争无优势') return '<span class="badge badge-n">' + v + '</span>';
  if(v === '无市场') return '<span class="badge badge-un">' + v + '</span>';
  return v;
}}
function badgePLP(v) {{
  if(v === 'Y') return '<span class="badge badge-y">Y</span>';
  return '<span class="badge badge-n">' + (v||'N') + '</span>';
}}
function fmtNum(n) {{ return n == null ? '-' : Number(n).toLocaleString('zh-CN'); }}
function fmtMoney(n) {{ return n == null ? '-' : '$' + Number(n).toFixed(2); }}
function pct(v) {{ return v == null || v === '' ? '-' : v; }}

// ========== Tab1: 总盘概览 ==========
(function() {{
  // KPI
  const stats = cum43Stats;
  const totalQty = cum43Data.reduce((s,r) => s + (r['4.30-5.6销量']||0), 0);
  const totalRev = cum43Data.reduce((s,r) => s + (r['4.30-5.6销售额']||0), 0);
  const soldRate = ((stats.yCount / stats.total) * 100).toFixed(1) + '%';
  const timelyRate = timelinessData.total.timelyRate;
  const kpi = document.getElementById('kpi-overview');
  kpi.innerHTML = `
    <div class="kpi-card"><div class="val">${{stats.total}}</div><div class="label">累计SKU</div><div class="hb hb-up">${{hbSign(prevWeekKpi.skuChange)}} 环比</div></div>
    <div class="kpi-card green"><div class="val">${{fmtNum(totalQty)}}</div><div class="label">总销量</div><div class="hb hb-up">${{hbSign(prevWeekKpi.salesQtyChange)}} 环比</div></div>
    <div class="kpi-card purple"><div class="val">${{fmtMoney(totalRev)}}</div><div class="label">总销售额</div><div class="hb hb-up">${{hbSign(prevWeekKpi.revenueChange)}} 环比</div></div>
    <div class="kpi-card"><div class="val">${{soldRate}}</div><div class="label">出单率</div></div>
    <div class="kpi-card orange"><div class="val">${{timelyRate}}</div><div class="label">分析及时率</div><div class="hb hb-up">${{hbSign(timelinessData.total.change)}} 环比</div></div>
  `;

  // ---- 出单情况(有对手口径) ----
  // 有对手SKU = curCompetitorQty > 0 在 cum43Data
  const hasComp = cum43Data.filter(r => r['5.6对手销量'] > 0);
  const hasCompSold = hasComp.filter(r => r['4.30-5.6销量'] > 0);
  const hasCompRate = hasComp.length ? ((hasCompSold.length / hasComp.length) * 100).toFixed(1) + '%' : '-';
  // 上周
  const prevHasComp = lowShareData.filter(r => r.curCompetitorQty > 0);
  const prevHasCompSold = prevHasComp.filter(r => r.curSalesQty > 0);
  const prevHasCompRate = prevHasComp.length ? ((prevHasCompSold.length / prevHasComp.length) * 100).toFixed(1) + '%' : '-';
  const soldKpiEl = document.getElementById('sold-overview-kpi');
  soldKpiEl.innerHTML = `
    <div class="kpi-card"><div class="val">${{hasComp.length}}</div><div class="label">有对手SKU总数</div></div>
    <div class="kpi-card green"><div class="val">${{hasCompSold.length}}</div><div class="label">有对手出单数</div></div>
    <div class="kpi-card"><div class="val">${{hasCompRate}}</div><div class="label">有对手出单率</div><div class="hb">${{prevHasCompRate}} 上周</div></div>
  `;

  // 有对手出单-分析人
  const acMap = {{}};
  hasComp.forEach(r => {{
    const a = r['4月分析人'];
    if(!acMap[a]) acMap[a] = {{total:0, sold:0, qty:0, rev:0}};
    acMap[a].total++;
    if(r['4.30-5.6销量']>0) acMap[a].sold++;
    acMap[a].qty += r['4.30-5.6销量']||0;
    acMap[a].rev += r['4.30-5.6销售额']||0;
  }});
  // 上周
  const prevAcMap = {{}};
  prevHasComp.forEach(r => {{
    const a = r.analyst;
    if(!prevAcMap[a]) prevAcMap[a] = {{total:0, sold:0}};
    prevAcMap[a].total++;
    if(r.curSalesQty>0) prevAcMap[a].sold++;
  }});
  let h1 = '<thead><tr><th>分析人</th><th>有对手SKU</th><th>出单数</th><th>出单率</th><th>上周出单率</th><th>环比</th><th>销量</th><th>销售额</th></tr></thead><tbody>';
  Object.keys(acMap).sort().forEach(a => {{
    const c = acMap[a];
    const rate = (c.sold/c.total*100).toFixed(1)+'%';
    const prev = prevAcMap[a];
    const prevRate = prev ? (prev.sold/prev.total*100).toFixed(1)+'%' : '-';
    const change = prev && prev.total>0 ? ((c.sold/c.total - prev.sold/prev.total)*100).toFixed(1) : '-';
    const changeStr = change === '-' ? '-' : (change >= 0 ? '+'+change+'%' : change+'%');
    h1 += `<tr><td>${{a}}</td><td>${{c.total}}</td><td>${{c.sold}}</td><td>${{rate}}</td><td>${{prevRate}}</td><td>${{hbSign(changeStr)}}</td><td>${{fmtNum(c.qty)}}</td><td>${{fmtMoney(c.rev)}}</td></tr>`;
  }});
  h1 += '</tbody>';
  document.getElementById('tbl-sold-analyst').innerHTML = h1;

  // 有对手出单-品线
  const catMap = {{}};
  hasComp.forEach(r => {{
    const c = r['品类'];
    if(!catMap[c]) catMap[c] = {{total:0, sold:0, qty:0, rev:0}};
    catMap[c].total++;
    if(r['4.30-5.6销量']>0) catMap[c].sold++;
    catMap[c].qty += r['4.30-5.6销量']||0;
    catMap[c].rev += r['4.30-5.6销售额']||0;
  }});
  const prevCatMap = {{}};
  prevHasComp.forEach(r => {{
    const c = r.category;
    if(!prevCatMap[c]) prevCatMap[c] = {{total:0, sold:0}};
    prevCatMap[c].total++;
    if(r.curSalesQty>0) prevCatMap[c].sold++;
  }});
  let h2 = '<thead><tr><th>品线</th><th>有对手SKU</th><th>出单数</th><th>出单率</th><th>上周出单率</th><th>环比</th><th>销量</th><th>销售额</th></tr></thead><tbody>';
  Object.keys(catMap).sort().forEach(c => {{
    const d = catMap[c];
    const rate = (d.sold/d.total*100).toFixed(1)+'%';
    const prev = prevCatMap[c];
    const prevRate = prev ? (prev.sold/prev.total*100).toFixed(1)+'%' : '-';
    const change = prev && prev.total>0 ? ((d.sold/d.total - prev.sold/prev.total)*100).toFixed(1) : '-';
    const changeStr = change === '-' ? '-' : (change >= 0 ? '+'+change+'%' : change+'%');
    h2 += `<tr><td>${{c}}</td><td>${{d.total}}</td><td>${{d.sold}}</td><td>${{rate}}</td><td>${{prevRate}}</td><td>${{hbSign(changeStr)}}</td><td>${{fmtNum(d.qty)}}</td><td>${{fmtMoney(d.rev)}}</td></tr>`;
  }});
  h2 += '</tbody>';
  document.getElementById('tbl-sold-category').innerHTML = h2;

  // ---- 多维度分析：品线维度 ----
  let h3 = '<thead><tr><th>品线</th><th>SKU</th><th>出单SKU</th><th>出单率</th><th>销量</th><th>上周销量</th><th>环比</th><th>销售额</th><th>上周销售额</th><th>环比</th></tr></thead><tbody>';
  categoryRevenueData.forEach(r => {{
    h3 += `<tr><td>${{r.category}}</td><td>${{Math.round(r.curSku)}}</td><td>${{Math.round(r.curSalesQty > 0 ? (r.curSku - cum43Data.filter(d=>d['品类']===r.category && d['4.30-5.6销量']===0).length) : 0)}}</td>
    <td>${{r.curSku>0?(r.curSalesQty>0?Math.round((cum43Data.filter(d=>d['品类']===r.category && d['4.30-5.6销量']>0)).length/r.curSku*100):0).toFixed(1)+'%':'-'}}</td>
    <td>${{fmtNum(r.curSalesQty)}}</td><td>${{fmtNum(r.prevSalesQty)}}</td><td>${{hbSign(r.salesQtyChange)}}</td>
    <td>${{fmtMoney(r.curRevenue)}}</td><td>${{fmtMoney(r.prevRevenue)}}</td><td>${{hbSign(r.revenueChange)}}</td></tr>`;
  }});
  h3 += '</tbody>';
  document.getElementById('tbl-multi-category').innerHTML = h3;

  // 分析人维度
  let h4 = '<thead><tr><th>分析人</th><th>SKU</th><th>出单SKU</th><th>销量</th><th>上周销量</th><th>环比</th><th>销售额</th><th>上周销售额</th><th>环比</th></tr></thead><tbody>';
  analystRevenueData.forEach(r => {{
    const soldSku = cum43Data.filter(d=>d['4月分析人']===r.analyst && d['4.30-5.6销量']>0).length;
    h4 += `<tr><td>${{r.analyst}}</td><td>${{Math.round(r.curSku)}}</td><td>${{soldSku}}</td>
    <td>${{fmtNum(r.curSalesQty)}}</td><td>${{fmtNum(r.prevSalesQty)}}</td><td>${{hbSign(r.salesQtyChange)}}</td>
    <td>${{fmtMoney(r.curRevenue)}}</td><td>${{fmtMoney(r.prevRevenue)}}</td><td>${{hbSign(r.revenueChange)}}</td></tr>`;
  }});
  h4 += '</tbody>';
  document.getElementById('tbl-multi-analyst').innerHTML = h4;

  // 拓展类型
  let h5 = '<thead><tr><th>拓展类型</th><th>本周SKU</th><th>上周SKU</th><th>出单SKU</th><th>出单率</th><th>上周出单率</th><th>环比</th><th>销量</th><th>上周销量</th><th>销量环比</th><th>销售额</th><th>上周销售额</th><th>销售额环比</th></tr></thead><tbody>';
  expandTypeData.forEach(r => {{
    h5 += `<tr><td>${{r.expandType}}</td><td>${{r.curSku}}</td><td>${{r.prevSku}}</td><td>${{r.curSalesCount}}</td><td>${{pct(r.curSalesRate)}}</td><td>${{pct(r.prevSalesRate)}}</td><td>${{hbSign(r.salesRateChange)}}</td>
    <td>${{fmtNum(r.curSalesQty)}}</td><td>${{fmtNum(r.prevSalesQty)}}</td><td>${{hbSign(r.salesQtyChange)}}</td>
    <td>${{fmtMoney(r.curRevenue)}}</td><td>${{fmtMoney(r.prevRevenue)}}</td><td>${{hbSign(r.revenueChange)}}</td></tr>`;
  }});
  h5 += '</tbody>';
  document.getElementById('tbl-expand').innerHTML = h5;

  // 及时率
  let h6 = '<thead><tr><th>分析人</th><th>SKU</th><th>及时数</th><th>及时率</th><th>上周SKU</th><th>上周及时数</th><th>上周及时率</th><th>环比</th><th>8日未分析</th><th>7日未分析</th></tr></thead><tbody>';
  timelinessData.analysts.forEach(r => {{
    h6 += `<tr><td>${{r.analyst}}</td><td>${{r.curSku}}</td><td>${{r.timelyCount}}</td><td>${{pct(r.timelyRate)}}</td>
    <td>${{r.prevSku}}</td><td>${{r.prevTimelyCount}}</td><td>${{pct(r.prevTimelyRate)}}</td><td>${{hbSign(r.change)}}</td>
    <td>${{r.noAnalysis8dCount}}</td><td>${{r.noAnalysis7dCount}}</td></tr>`;
  }});
  const tt = timelinessData.total;
  h6 += `<tfoot><tr><td>合计</td><td>${{tt.curSku}}</td><td>${{tt.timelyCount}}</td><td>${{pct(tt.timelyRate)}}</td>
    <td>${{tt.prevSku}}</td><td>${{tt.prevTimelyCount}}</td><td>${{pct(tt.prevTimelyRate)}}</td><td>${{hbSign(tt.change)}}</td>
    <td>${{tt.noAnalysis8dCount}}</td><td>${{tt.noAnalysis7dCount}}</td></tr></tfoot>`;
  h6 += '</table>';
  document.getElementById('tbl-timely').innerHTML = h6;
}})();

// ========== Tab1: 图表 ==========
window._charts1Init = false;
function initCharts1() {{
  window._charts1Init = true;
  const colors = ['#0f3460','#2980b9','#08845a','#e07b24','#8e44ad','#c0392b','#667eea','#6c757d'];

  // 出单分布饼图
  new Chart(document.getElementById('chart-pie1'), {{
    type: 'doughnut',
    data: {{
      labels: ['已出单','未出单(有对手)','未出单(无市场)'],
      datasets: [{{ data: [cum43Stats.yCount, cum43Stats.nCount, cum43Stats.unCount],
        backgroundColor: ['#08845a','#e07b24','#c0392b'] }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});

  // 品线销量
  const catLabels = categoryRevenueData.map(r=>r.category);
  new Chart(document.getElementById('chart-bar1'), {{
    type: 'bar',
    data: {{
      labels: catLabels,
      datasets: [
        {{ label:'本周', data: categoryRevenueData.map(r=>r.curSalesQty), backgroundColor:'#0f3460' }},
        {{ label:'上周', data: categoryRevenueData.map(r=>r.prevSalesQty), backgroundColor:'#ccc' }}
      ]
    }},
    options: {{ responsive: true, plugins:{{legend:{{position:'bottom'}}}}, scales:{{y:{{beginAtZero:true}}}} }}
  }});

  // 分析人销量
  new Chart(document.getElementById('chart-bar2'), {{
    type: 'bar',
    data: {{
      labels: analystRevenueData.map(r=>r.analyst),
      datasets: [
        {{ label:'本周', data: analystRevenueData.map(r=>r.curSalesQty), backgroundColor:'#0f3460' }},
        {{ label:'上周', data: analystRevenueData.map(r=>r.prevSalesQty), backgroundColor:'#ccc' }}
      ]
    }},
    options: {{ responsive: true, plugins:{{legend:{{position:'bottom'}}}}, scales:{{y:{{beginAtZero:true}}}} }}
  }});

  // 分析人及时率
  const tData = timelinessData.analysts;
  new Chart(document.getElementById('chart-bar3'), {{
    type: 'bar',
    data: {{
      labels: tData.map(r=>r.analyst),
      datasets: [
        {{ label:'本周及时率', data: tData.map(r=>parseFloat(r.timelyRate)), backgroundColor:'#2980b9' }},
        {{ label:'上周及时率', data: tData.map(r=>parseFloat(r.prevTimelyRate)), backgroundColor:'#ddd' }}
      ]
    }},
    options: {{ responsive: true, plugins:{{legend:{{position:'bottom'}}}}, scales:{{y:{{beginAtZero:true,max:100}}}} }}
  }});

  // 品线销售额
  new Chart(document.getElementById('chart-bar4'), {{
    type: 'bar',
    data: {{
      labels: catLabels,
      datasets: [
        {{ label:'本周', data: categoryRevenueData.map(r=>r.curRevenue), backgroundColor:'#8e44ad' }},
        {{ label:'上周', data: categoryRevenueData.map(r=>r.prevRevenue), backgroundColor:'#e0c0e8' }}
      ]
    }},
    options: {{ responsive: true, plugins:{{legend:{{position:'bottom'}}}}, scales:{{y:{{beginAtZero:true}}}} }}
  }});

  // 分析人销售额
  new Chart(document.getElementById('chart-bar5'), {{
    type: 'bar',
    data: {{
      labels: analystRevenueData.map(r=>r.analyst),
      datasets: [
        {{ label:'本周', data: analystRevenueData.map(r=>r.curRevenue), backgroundColor:'#8e44ad' }},
        {{ label:'上周', data: analystRevenueData.map(r=>r.prevRevenue), backgroundColor:'#e0c0e8' }}
      ]
    }},
    options: {{ responsive: true, plugins:{{legend:{{position:'bottom'}}}}, scales:{{y:{{beginAtZero:true}}}} }}
  }});
}}
// 首次加载 tab1 立即初始化图表
setTimeout(initCharts1, 100);

// ========== Tab2: 低占比分析 ==========
(function() {{
  const unsoldTotal = hasCompetitorUnsold.total + unsoldNoCompetitor.total;
  const lowRate = cum43Stats.total ? ((unsoldTotal/cum43Stats.total)*100).toFixed(1)+'%' : '-';
  document.getElementById('kpi-lowshare').innerHTML = `
    <div class="kpi-card orange"><div class="val">${{hasCompetitorUnsold.total}}</div><div class="label">有对手未出单</div><div class="hb">${{hasCompetitorUnsold.prevTotal}} 上周 | ${{hbSign(hasCompetitorUnsold.change>=0?'+'+hasCompetitorUnsold.change:hasCompetitorUnsold.change)}}</div></div>
    <div class="kpi-card red"><div class="val">${{unsoldNoCompetitor.total}}</div><div class="label">无对手未出单</div><div class="hb">${{unsoldNoCompetitor.prevTotal}} 上周 | ${{hbSign(unsoldNoCompetitor.change>=0?'+'+unsoldNoCompetitor.change:unsoldNoCompetitor.change)}}</div></div>
    <div class="kpi-card"><div class="val">${{cum43Stats.total}}</div><div class="label">有对手SKU总数</div></div>
    <div class="kpi-card purple"><div class="val">${{lowRate}}</div><div class="label">未出单占比</div></div>
  `;

  // A - 有对手未出单
  let ha = '<thead><tr><th>分析人</th><th>竞争无优势</th><th>无市场</th><th>无价格优势</th><th>海外仓</th><th>正常</th><th>N/A</th><th>未知</th><th>小计</th></tr></thead><tbody>';
  hasCompetitorUnsold.byAnalyst.forEach(r => {{
    ha += `<tr><td>${{r.analyst}}</td><td>${{r.competitiveWeak}}</td><td>${{r.noMarket}}</td><td>${{r.noPriceAdv}}</td><td>${{r.overseas}}</td><td>${{r.normal}}</td><td>${{r.na}}</td><td>${{r.unknown}}</td><td>${{r.total}}</td></tr>`;
  }});
  ha += '</tbody>';
  document.getElementById('tbl-has-competitor').innerHTML = ha;

  // B - 无对手未出单
  let hb = '<thead><tr><th>分析人</th><th>无市场</th><th>未知</th><th>竞争无优势</th><th>N/A</th><th>其他</th><th>小计</th></tr></thead><tbody>';
  unsoldNoCompetitor.byAnalyst.forEach(r => {{
    hb += `<tr><td>${{r.analyst}}</td><td>${{r.noMarket}}</td><td>${{r.unknown}}</td><td>${{r.competitiveWeak}}</td><td>${{r.na}}</td><td>${{r.other}}</td><td>${{r.total}}</td></tr>`;
  }});
  hb += '</tbody>';
  document.getElementById('tbl-no-competitor').innerHTML = hb;

  // 原因分析-分析人
  const allAnalysts = [...new Set([...hasCompetitorUnsold.byAnalyst.map(r=>r.analyst), ...unsoldNoCompetitor.byAnalyst.map(r=>r.analyst)])].sort();
  let hc = '<thead><tr><th>分析人</th><th class="p1">有对手-竞争无优势</th><th class="p1">有对手-无市场</th><th class="p1">有对手-小计</th><th class="p2">无对手-无市场</th><th class="p2">无对手-竞争无优势</th><th class="p2">无对手-小计</th><th class="p4">未出单总计</th></tr></thead><tbody>';
  allAnalysts.forEach(a => {{
    const hcRec = hasCompetitorUnsold.byAnalyst.find(r=>r.analyst===a) || {{}};
    const ncRec = unsoldNoCompetitor.byAnalyst.find(r=>r.analyst===a) || {{}};
    const hcSub = (hcRec.competitiveWeak||0) + (hcRec.noMarket||0);
    const ncSub = (ncRec.noMarket||0) + (ncRec.competitiveWeak||0);
    hc += `<tr><td>${{a}}</td>
      <td>${{hcRec.competitiveWeak||0}}</td><td>${{hcRec.noMarket||0}}</td><td>${{hcSub}}</td>
      <td>${{ncRec.noMarket||0}}</td><td>${{ncRec.competitiveWeak||0}}</td><td>${{ncSub}}</td>
      <td>${{(hcRec.total||0)+(ncRec.total||0)}}</td></tr>`;
  }});
  hc += '</tbody>';
  document.getElementById('tbl-reason-analyst').innerHTML = hc;

  // 原因分析-品线
  const allCats = [...new Set([...hasCompetitorUnsold.byCategory.map(r=>r.category), ...unsoldNoCompetitor.byCategory.map(r=>r.category)])].sort();
  let hd = '<thead><tr><th>品线</th><th class="p1">有对手-竞争无优势</th><th class="p1">有对手-无市场</th><th class="p1">有对手-小计</th><th class="p2">无对手-无市场</th><th class="p2">无对手-竞争无优势</th><th class="p2">无对手-小计</th><th class="p4">未出单总计</th></tr></thead><tbody>';
  allCats.forEach(c => {{
    const hcRec = hasCompetitorUnsold.byCategory.find(r=>r.category===c) || {{}};
    const ncRec = unsoldNoCompetitor.byCategory.find(r=>r.category===c) || {{}};
    const hcSub = (hcRec.competitiveWeak||0) + (hcRec.noMarket||0);
    const ncSub = (ncRec.noMarket||0) + (ncRec.competitiveWeak||0);
    hd += `<tr><td>${{c}}</td>
      <td>${{hcRec.competitiveWeak||0}}</td><td>${{hcRec.noMarket||0}}</td><td>${{hcSub}}</td>
      <td>${{ncRec.noMarket||0}}</td><td>${{ncRec.competitiveWeak||0}}</td><td>${{ncSub}}</td>
      <td>${{(hcRec.total||0)+(ncRec.total||0)}}</td></tr>`;
  }});
  hd += '</tbody>';
  document.getElementById('tbl-reason-category').innerHTML = hd;
}})();

// ========== Tab3: 广告追踪 ==========
(function() {{
  const t = plpTotal, p = plpPrevTotal;
  document.getElementById('kpi-plp').innerHTML = `
    <div class="kpi-card"><div class="val">${{t.campaignCount}}</div><div class="label">广告活动数</div><div class="hb">${{p.campaignCount}} 上周</div></div>
    <div class="kpi-card green"><div class="val">${{t.linkCount}}</div><div class="label">投放链接数</div><div class="hb">${{p.linkCount}} 上周</div></div>
    <div class="kpi-card purple"><div class="val">${{fmtNum(t.impression)}}</div><div class="label">曝光量</div></div>
    <div class="kpi-card"><div class="val">${{fmtNum(t.click)}}</div><div class="label">点击量</div></div>
    <div class="kpi-card orange"><div class="val">${{fmtNum(t.sold)}}</div><div class="label">售出数</div><div class="hb">${{p.sold}} 上周</div></div>
    <div class="kpi-card"><div class="val">${{fmtMoney(t.revenue)}}</div><div class="label">广告销售额</div></div>
  `;

  // 核心指标
  document.getElementById('plp-core-metrics').innerHTML = `
    <div class="plp-card"><h4>ROAS</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{t.roas}}</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{p.roas}}</span></div></div></div>
    <div class="plp-card"><h4>CVR</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{t.cvr}}</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{p.cvr}}</span></div></div></div>
    <div class="plp-card"><h4>CTR</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{t.ctr}}</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{p.ctr}}</span></div></div></div>
    <div class="plp-card"><h4>CPC</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{t.cpc}}</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{p.cpc}}</span></div></div></div>
    <div class="plp-card"><h4>CPA</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{t.cpa}}</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{p.cpa}}</span></div></div></div>
    <div class="plp-card"><h4>ACOS</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{t.acos}}</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{p.acos}}</span></div></div></div>
    <div class="plp-card"><h4>ACOAS</h4><div class="plp-highlight"><div class="plp-metric"><span class="lbl">本周</span><span class="val">${{(t.acoas*100).toFixed(2)}}%</span></div><div class="plp-metric"><span class="lbl">上周</span><span class="val">${{(p.acoas*100).toFixed(2)}}%</span></div></div></div>
  `;

  // 分析人维度 PLP
  let ha = '<thead><tr><th>分析人</th><th>曝光</th><th>点击</th><th>售出</th><th>花费</th><th>广告销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>CPC</th><th>CPA</th><th>ACOS</th><th>ACOAS</th></tr></thead><tbody>';
  plpAnalysts.forEach(r => {{
    ha += `<tr><td>${{r.name}}</td><td>${{fmtNum(r.impression)}}</td><td>${{r.click}}</td><td>${{r.sold}}</td><td>${{fmtMoney(r.cost)}}</td><td>${{fmtMoney(r.revenue)}}</td>
    <td>${{r.roas}}</td><td>${{pct(r.cvr)}}</td><td>${{pct(r.ctr)}}</td><td>${{r.cpc}}</td><td>${{r.cpa}}</td><td>${{pct(r.acos)}}</td><td>${{(r.acoas*100).toFixed(2)}}%</td></tr>`;
  }});
  ha += '</tbody>';
  document.getElementById('tbl-plp-analyst').innerHTML = ha;

  // 品线维度 PLP
  let hb = '<thead><tr><th>品线</th><th>活动数</th><th>链接数</th><th>曝光</th><th>点击</th><th>售出</th><th>花费</th><th>广告销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>CPC</th><th>CPA</th><th>ACOS</th><th>ACOAS</th></tr></thead><tbody>';
  plpCategories.forEach(r => {{
    hb += `<tr><td>${{r.category}}</td><td>${{r.campaignCount}}</td><td>${{r.linkCount}}</td><td>${{fmtNum(r.impression)}}</td><td>${{r.click}}</td><td>${{r.sold}}</td><td>${{fmtMoney(r.cost)}}</td><td>${{fmtMoney(r.revenue)}}</td>
    <td>${{r.roas}}</td><td>${{pct(r.cvr)}}</td><td>${{pct(r.ctr)}}</td><td>${{r.cpc}}</td><td>${{r.cpa}}</td><td>${{pct(r.acos)}}</td><td>${{(r.acoas*100).toFixed(2)}}%</td></tr>`;
  }});
  hb += '</tbody>';
  document.getElementById('tbl-plp-category').innerHTML = hb;

  // PLG 费率统计
  const s = plgStats;
  document.getElementById('kpi-plg').innerHTML = `
    <div class="kpi-card"><div class="val">${{s.totalNewProducts}}</div><div class="label">新品总数</div></div>
    <div class="kpi-card green"><div class="val">${{s.plpAndPlgBothCount}}</div><div class="label">PLP+PLG双开</div></div>
    <div class="kpi-card purple"><div class="val">${{s.plgOnlyCount}}</div><div class="label">单PLG</div></div>
    <div class="kpi-card"><div class="val">${{s.plpOnlyCount}}</div><div class="label">单PLP</div></div>
    <div class="kpi-card orange"><div class="val">${{s.noAdCount}}</div><div class="label">无广告</div></div>
    <div class="kpi-card"><div class="val">${{s.plpDisabledNoSaleCount}}</div><div class="label">PLP未开且未出单</div></div>
    <div class="kpi-card"><div class="val">${{s.plpEnabledCount}}</div><div class="label">PLP已开</div></div>
    <div class="kpi-card"><div class="val">${{s.plpDisabledCount}}</div><div class="label">PLP未开</div></div>
  `;
  let hpg = '<thead><tr><th>分析人</th><th>总数</th><th>PLP+PLG</th><th>单PLG</th><th>单PLP</th><th>无广告</th><th>PLP未开未出单</th></tr></thead><tbody>';
  s.byAnalyst.forEach(r => {{
    hpg += `<tr><td>${{r.analyst}}</td><td>${{r.total}}</td><td>${{r.plpAndPlgBoth}}</td><td>${{r.plgOnly}}</td><td>${{r.plpOnly}}</td><td>${{r.noAd}}</td><td>${{r.plpDisabledNoSale}}</td></tr>`;
  }});
  hpg += '</tbody>';
  document.getElementById('tbl-plg-analyst').innerHTML = hpg;

  // PLP 广告明细
  let hpd = '<thead><tr><th>#</th><th>SKU</th><th>广告活动</th><th>分析人</th><th>品类</th><th>拓展类型</th><th>曝光</th><th>点击</th><th>售出</th><th>花费</th><th>广告销售额</th><th>总销售额</th><th>ROAS</th><th>ACOS</th><th>ACOAS</th></tr></thead><tbody>';
  plpDetailData.forEach((r,i) => {{
    const acosVal = r.acos != null ? (r.acos*100).toFixed(2)+'%' : '-';
    const acoasVal = r.acoas != null ? (r.acoas*100).toFixed(2)+'%' : '-';
    hpd += `<tr><td>${{i+1}}</td><td>${{r.sku}}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">${{r.campaign}}</td><td>${{r.analyst}}</td><td>${{r.category}}</td><td>${{r.productExpansion}}</td>
    <td>${{fmtNum(r.impressions)}}</td><td>${{fmtNum(r.clicks)}}</td><td>${{r.salesQty}}</td><td>${{fmtMoney(r.spend)}}</td><td>${{fmtMoney(r.adRevenue||r.revenue)}}</td><td>${{fmtMoney(r.totalRevenue)}}</td>
    <td>${{r.roas!=null?r.roas.toFixed(2):'-'}}</td><td>${{acosVal}}</td><td>${{acoasVal}}</td></tr>`;
  }});
  hpd += '</tbody>';
  document.getElementById('tbl-plp-detail').innerHTML = hpd;
}})();

// ========== Tab4: 四三累计 ==========
(function() {{
  const s = cum43Stats;
  document.getElementById('kpi-cum43').innerHTML = `
    <div class="kpi-card"><div class="val">${{s.total}}</div><div class="label">累计总SKU</div></div>
    <div class="kpi-card green"><div class="val">${{s.yCount}}</div><div class="label">已出单</div></div>
    <div class="kpi-card orange"><div class="val">${{s.nCount}}</div><div class="label">有竞争未出单</div></div>
    <div class="kpi-card red"><div class="val">${{s.unCount}}</div><div class="label">无市场</div></div>
    <div class="kpi-card"><div class="val">${{s.normalCount}}</div><div class="label">市场正常</div></div>
    <div class="kpi-card purple"><div class="val">${{s.competitiveCount}}</div><div class="label">竞争无优势</div></div>
    <div class="kpi-card"><div class="val">${{s.noMarketCount}}</div><div class="label">无市场</div></div>
  `;

  // 填充筛选器选项
  const analysts = [...new Set(cum43Data.map(r=>r['4月分析人']))].sort();
  const categories = [...new Set(cum43Data.map(r=>r['品类']))].sort();
  const selA = document.getElementById('f-analyst');
  const selC = document.getElementById('f-category');
  analysts.forEach(a => {{ const o = document.createElement('option'); o.text = a; selA.add(o); }});
  categories.forEach(c => {{ const o = document.createElement('option'); o.text = c; selC.add(o); }});

  // PLG 匹配 map
  const plgMap = {{}};
  plgRecords.forEach(r => {{ plgMap[r.sku] = r; }});

  // 渲染表格
  function renderTable(data) {{
    let h = '<thead><tr><th>SKU</th><th>实际上架</th><th>首次出单</th><th>分析人</th><th>品类</th><th>拓展类型</th><th>销量</th><th>销售额</th><th>对手销量</th><th>市占比</th><th>市场状态</th><th>8日出单</th><th>PLP</th><th>PLG费率</th></tr></thead><tbody>';
    data.forEach(r => {{
      const plg = plgMap[r.SKU] || {{}};
      h += `<tr><td>${{r.SKU}}</td><td>${{r['实际上架日期']}}</td><td>${{r['首次出单日期']}}</td><td>${{r['4月分析人']}}</td><td>${{r['品类']}}</td><td>${{r['产品拓展']}}</td>
      <td>${{r['4.30-5.6销量']}}</td><td>${{fmtMoney(r['4.30-5.6销售额'])}}</td><td>${{r['5.6对手销量']}}</td><td>${{r['5.6市占比']}}%</td>
      <td>${{badgeStatus(r['5.6市场状态'])}}</td><td>${{badge8d(r['5.6 8日出单情况'])}}</td>
      <td>${{badgePLP(plg.plpEnabled)}}</td><td>${{plg.plgFee || '-'}}</td></tr>`;
    }});
    // 汇总行
    const totQty = data.reduce((s,r)=>s+(r['4.30-5.6销量']||0),0);
    const totRev = data.reduce((s,r)=>s+(r['4.30-5.6销售额']||0),0);
    h += `<tfoot><tr><td colspan="6"><strong>合计 ({{data.length}}条)</strong></td><td><strong>${{fmtNum(totQty)}}</strong></td><td><strong>${{fmtMoney(totRev)}}</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr></tfoot>`;
    h += '</tbody>';
    document.getElementById('tbl-cum43').innerHTML = h;
    document.getElementById('filter-result').textContent = '筛选结果：' + data.length + ' / ' + cum43Data.length + ' 条';
  }}

  // 筛选逻辑
  function applyFilters() {{
    let data = [...cum43Data];
    const market = document.getElementById('f-market').value;
    const analyst = document.getElementById('f-analyst').value;
    const category = document.getElementById('f-category').value;
    const expand = document.getElementById('f-expand').value;
    const d8 = document.getElementById('f-8d').value;
    const share = document.getElementById('f-share').value;
    const compete = document.getElementById('f-compete').value;
    const ad = document.getElementById('f-ad').value;

    if(market) data = data.filter(r => r['5.6市场状态'] === market);
    if(analyst) data = data.filter(r => r['4月分析人'] === analyst);
    if(category) data = data.filter(r => r['品类'] === category);
    if(expand) data = data.filter(r => r['产品拓展'] === expand);
    if(d8) data = data.filter(r => r['5.6 8日出单情况'] === d8);
    if(share === 'high') data = data.filter(r => r['5.6市占比'] >= 75);
    if(share === 'mid') data = data.filter(r => r['5.6市占比'] >= 50 && r['5.6市占比'] < 75);
    if(share === 'low') data = data.filter(r => r['5.6市占比'] < 50);
    if(compete === 'yes') data = data.filter(r => r['5.6对手销量'] > 0);
    if(compete === 'no') data = data.filter(r => r['5.6对手销量'] === 0);
    if(ad) {{
      data = data.filter(r => {{
        const plg = plgMap[r.SKU] || {{}};
        const plpOn = plg.plpEnabled === 'Y';
        const plgOn = plg.plgFee && plg.plgFee !== '0%';
        const hasSale = r['4.30-5.6销量'] > 0;
        if(ad === 'plp_plg') return plpOn && plgOn;
        if(ad === 'plg_only') return !plpOn && plgOn;
        if(ad === 'plp_only') return plpOn && !plgOn;
        if(ad === 'no_ad') return !plpOn && !plgOn;
        if(ad === 'plp_off_nosale') return !plpOn && !hasSale;
        return true;
      }});
    }}
    renderTable(data);
  }}

  window.resetFilters = function() {{
    document.querySelectorAll('#filter-bar select').forEach(s => s.value = '');
    applyFilters();
  }};

  document.querySelectorAll('#filter-bar select').forEach(s => s.addEventListener('change', applyFilters));

  // 初始渲染
  renderTable(cum43Data);
}})();

// ========== Tab5: 汇报输出 ==========
(function() {{
  const s = cum43Stats;
  const totalQty = cum43Data.reduce((s,r)=>s+(r['4.30-5.6销量']||0),0);
  const totalRev = cum43Data.reduce((s,r)=>s+(r['4.30-5.6销售额']||0),0);
  const soldRate = (s.yCount/s.total*100).toFixed(1)+'%';
  const timelyRate = timelinessData.total.timelyRate;
  const lowShareCount = hasCompetitorUnsold.total + unsoldNoCompetitor.total;

  document.getElementById('kpi-report').innerHTML = `
    <div class="kpi-card"><div class="val">${{s.total}}</div><div class="label">在售SKU</div></div>
    <div class="kpi-card green"><div class="val">${{fmtNum(totalQty)}}</div><div class="label">总销量</div></div>
    <div class="kpi-card purple"><div class="val">${{fmtMoney(totalRev)}}</div><div class="label">总销售额</div></div>
    <div class="kpi-card"><div class="val">${{soldRate}}</div><div class="label">出单率</div></div>
    <div class="kpi-card orange"><div class="val">${{timelyRate}}</div><div class="label">及时率</div></div>
    <div class="kpi-card red"><div class="val">${{lowShareCount}}</div><div class="label">低占比新品</div></div>
  `;

  // 风险预警
  const risks = [];
  if(parseFloat(soldRate) < 70) risks.push({{level:'high',text:'出单率仅'+soldRate+'，低于70%警戒线，需重点关注未出单SKU的转化策略。'}});
  if(unsoldNoCompetitor.total > 15) risks.push({{level:'high',text:'无对手未出单新品达'+unsoldNoCompetitor.total+'款，占比过高，需排查无市场原因。'}});
  if(parseFloat(plpTotal.roas) < 8) risks.push({{level:'medium',text:'PLP广告ROAS为'+plpTotal.roas+'，较上周'+plpPrevTotal.roas+'下降明显，需优化广告投放。'}});
  const worstAnalyst = timelinessData.analysts.reduce((a,b) => parseFloat(a.timelyRate) < parseFloat(b.timelyRate) ? a : b);
  if(parseFloat(worstAnalyst.timelyRate) < 50) risks.push({{level:'high',text:worstAnalyst.analyst+'及时率仅'+worstAnalyst.timelyRate+'，严重低于平均水平，需加强分析跟进。'}});
  if(s.competitiveCount > s.normalCount) risks.push({{level:'medium',text:'竞争无优势SKU('+s.competitiveCount+')超过正常SKU('+s.normalCount+')，市场竞争压力较大。'}});
  if(risks.length === 0) risks.push({{level:'low',text:'本期各项指标整体平稳，暂无重大风险。'}});
  document.getElementById('risk-list').innerHTML = risks.map(r => `<div class="risk-item risk-${{r.level}}">${{r.text}}</div>`).join('');

  // 主要发现
  const findings = [];
  findings.push('出单率'+soldRate+'，环比'+prevWeekKpi.salesQtyChange+'；累计SKU '+s.total+'款，出单 '+s.yCount+'款。');
  const topCat = categoryRevenueData.reduce((a,b)=>a.curSalesQty>b.curSalesQty?a:b);
  findings.push('品线表现：'+topCat.category+'销量领先('+fmtNum(topCat.curSalesQty)+'件，环比'+topCat.salesQtyChange+')，需关注高增长品类。');
  const topAnalyst = analystRevenueData.reduce((a,b)=>a.curSalesQty>b.curSalesQty?a:b);
  findings.push('分析人维度：'+topAnalyst.analyst+'销量最高('+fmtNum(topAnalyst.curSalesQty)+'件)，及时率方面胡煜星表现最优('+timelinessData.analysts.find(a=>a.analyst==='胡煜星').timelyRate+')。');
  findings.push('拓展类型：原开品出单率'+expandTypeData.find(e=>e.expandType==='原开品').curSalesRate+'，拓展品'+expandTypeData.find(e=>e.expandType==='拓展品').curSalesRate+'，原开品表现更稳定。');
  findings.push('PLP广告：投放'+plpTotal.linkCount+'个链接，ROAS '+plpTotal.roas+'，张潇ROAS最高('+plpAnalysts.find(a=>a.name==='张潇').roas+')。');
  findings.push('低占比新品共'+lowShareCount+'款（有对手'+hasCompetitorUnsold.total+'+无对手'+unsoldNoCompetitor.total+'），较上周'+prevWeekKpi.prevLowShareCount+'款'+(lowShareCount<prevWeekKpi.prevLowShareCount?'减少':'增加')+'。');
  document.getElementById('finding-list').innerHTML = findings.map(f => `<div class="finding-item">${{f}}</div>`).join('');

  // 下周动作
  const actions = [];
  actions.push('重点跟进'+s.nCount+'款有竞争未出单新品，结合竞争分析制定差异化策略（优化Listing/调整价格/加强广告）。');
  actions.push('针对'+unsoldNoCompetitor.total+'款无市场新品进行评估，确认是否需要调整品类定位或下架处理。');
  actions.push('优化PLP广告投放：重点关注ROAS低于平均的分析人，调整出价策略和关键词。');
  actions.push('提升分析及时率：重点关注'+worstAnalyst.analyst+'('+worstAnalyst.timelyRate+')和'+timelinessData.analysts.reduce((a,b)=>parseFloat(a.timelyRate)<parseFloat(b.timelyRate)?a:b).analyst+'的8日分析覆盖率。');
  actions.push('拓展品出单率仅'+expandTypeData.find(e=>e.expandType==='拓展品').curSalesRate+'，需评估拓展品选品策略和上架节奏。');
  document.getElementById('action-list').innerHTML = actions.map(a => `<div class="action-item">${{a}}</div>`).join('');

  // 周报文案
  const block1 = `【核心指标】\\n本周期累计在售新品${{s.total}}款，出单${{s.yCount}}款，出单率${{soldRate}}（环比${{prevWeekKpi.salesQtyChange}}）。总销量${{fmtNum(totalQty)}}件（环比${{prevWeekKpi.salesQtyChange}}），总销售额${{fmtMoney(totalRev)}}（环比${{prevWeekKpi.revenueChange}}）。分析及时率${{timelyRate}}（环比${{timelinessData.total.change}}）。`;
  const block2 = `【风险预警】\\n` + risks.map(r => r.text).join('\\n');
  const block3 = `【主要发现】\\n` + findings.join('\\n');
  const block4 = `【品类维度】\\n` + categoryRevenueData.map(r => r.category+'：SKU '+Math.round(r.curSku)+'，销量'+fmtNum(r.curSalesQty)+'件（'+r.salesQtyChange+'），销售额'+fmtMoney(r.curRevenue)+'（'+r.revenueChange+'）').join('\\n');
  const block5 = `【下周重点动作】\\n` + actions.join('\\n');

  const blocks = [block1,block2,block3,block4,block5];
  const titles = ['核心指标','风险预警','主要发现','品类维度','下周动作'];
  document.getElementById('report-blocks').innerHTML = blocks.map((b,i) =>
    `<div class="report-block" id="report-text-${{i}}">${{b}}<button class="copy-btn" onclick="copyText('report-text-${{i}}',this)">复制</button></div>`
  ).join('');
}})();

function copyText(id, btn) {{
  const el = document.getElementById(id);
  const text = el.innerText.replace('复制','').trim();
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = '已复制';
    setTimeout(() => btn.textContent = '复制', 1500);
  }});
}}
</script>
</body>
</html>'''

# ========== 写入文件 ==========
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML 生成成功: {OUTPUT_PATH}")
print(f"文件大小: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

# 验证所有数据块嵌入
import re
for k in DATA_KEYS:
    pattern = f"const {k} = "
    if pattern in html:
        print(f"  [OK] {k}")
    else:
        print(f"  [MISSING] {k}")
