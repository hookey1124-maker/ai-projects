# -*- coding: utf-8 -*-
import json

with open('temp_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

low_share_js = json.dumps(data['low_share'], ensure_ascii=False)

# 生成完整的HTML
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品月报 · 2026年3月（带环比）</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }
.header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 28px 40px; }
.header h1 { font-size: 26px; font-weight: 700; letter-spacing: 2px; }
.header .subtitle { font-size: 13px; opacity: 0.75; margin-top: 6px; }
.container { display: flex; min-height: calc(100vh - 80px); }
.sidebar { width: 220px; background: #fff; border-right: 1px solid #e8e8e8; padding: 20px 0; position: sticky; top: 0; height: 100vh; overflow-y: auto; flex-shrink: 0; }
.sidebar ul { list-style: none; }
.sidebar li a { display: block; padding: 10px 20px; font-size: 13px; color: #555; text-decoration: none; border-left: 3px solid transparent; transition: all 0.2s; }
.sidebar li a:hover, .sidebar li a.active { background: #f0f6ff; color: #0f3460; border-left-color: #0f3460; font-weight: 600; }
.main-content { flex: 1; padding: 24px; overflow: auto; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 24px; }
.kpi-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }
.kpi-card .val { font-size: 28px; font-weight: 700; color: #0f3460; }
.kpi-card .label { font-size: 12px; color: #888; margin-top: 6px; }
.kpi-card .hb { font-size: 11px; margin-top: 4px; font-weight: 600; }
.kpi-card.green .val { color: #08845a; }
.kpi-card.orange .val { color: #e07b24; }
.kpi-card.red .val { color: #c0392b; }
.section { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section h3 { font-size: 16px; font-weight: 700; color: #0f3460; padding-bottom: 12px; border-bottom: 2px solid #e8f0fe; margin-bottom: 16px; }
.sub-module { margin-bottom: 20px; }
.sub-module h4 { font-size: 13px; font-weight: 600; color: #444; margin-bottom: 10px; padding: 6px 12px; background: #f5f7ff; border-radius: 4px; border-left: 3px solid #0f3460; }
.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; margin-bottom: 20px; }
.chart-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.chart-card h4 { font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 14px; }
.chart-card canvas { max-height: 280px; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th { background: #0f3460; color: white; padding: 8px 10px; text-align: center; white-space: nowrap; font-weight: 600; }
.data-table td { padding: 7px 10px; text-align: center; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }
.data-table tr:hover td { background: #f5f7ff; }
.data-table .highlight { color: #0f3460; font-weight: 700; }
.data-table .row-ordered { background: #f0fff4; }
.hb-up { color: #c0392b; font-weight: 700; }
.hb-down { color: #08845a; font-weight: 700; }
.hb-flat { color: #888; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
@media (max-width: 900px) { .sidebar { display: none; } .chart-grid { grid-template-columns: 1fr; } .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
</head>
<body>

<div class="header">
  <h1>🚀 新品月报 · 2026年3月（带完整环比）</h1>
  <div class="subtitle">统计周期：2026年3月 | 按月上架新品分别统计 | 含所有指标环比 | 生成时间：2026-04-09</div>
</div>

<div class="container">
<nav class="sidebar">
  <ul>
    <li><a href="#overview" onclick="showSection('overview',this)" class="active">📊 数据总览</a></li>
    <li><a href="#pinxian" onclick="showSection('pinxian',this)">🏷️ 品线维度</a></li>
    <li><a href="#analyst" onclick="showSection('analyst',this)">👤 分析人维度</a></li>
    <li><a href="#expand" onclick="showSection('expand',this)">🔖 拓展类型维度</a></li>
    <li><a href="#order" onclick="showSection('order',this)">📦 出单情况分析</a></li>
    <li><a href="#unorder" onclick="showSection('unorder',this)">❌ 未出单市场</a></li>
    <li><a href="#lowshare" onclick="showSection('lowshare',this)">📉 低占比新品</a></li>
    <li><a href="#detail" onclick="showSection('detail',this)">📋 全量明细</a></li>
  </ul>
</nav>

<div class="main-content">

<!-- KPI总览 -->
<div class="kpi-grid">
  <div class="kpi-card"><div class="val">156</div><div class="label">在跟SKU总数</div></div>
  <div class="kpi-card green"><div class="val">82</div><div class="label">3月已出单SKU</div></div>
  <div class="kpi-card red"><div class="val">74</div><div class="label">3月未出单SKU</div></div>
  <div class="kpi-card orange"><div class="val">52.6%</div><div class="label">3月出单率</div><div class="hb" id="kpi-rate-hb">环比 +5.4%</div></div>
  <div class="kpi-card"><div class="val">1,464</div><div class="label">3月总销量</div><div class="hb" id="kpi-qty-hb">环比 -245</div></div>
  <div class="kpi-card"><div class="val">¥18.2万</div><div class="label">3月总销售额</div></div>
</div>

<!-- 数据总览 -->
<div id="section-overview" class="section-wrap">
  <div class="section">
    <h3>📊 数据总览 · 图形可视化</h3>
    <div class="chart-grid">
      <div class="chart-card"><h4>📈 各批次3月销量对比</h4><canvas id="chartBatchQty"></canvas></div>
      <div class="chart-card"><h4>💰 各批次3月销售额对比</h4><canvas id="chartBatchAmt"></canvas></div>
      <div class="chart-card"><h4>🏷️ 各品类3月销量对比</h4><canvas id="chartCategoryQty"></canvas></div>
      <div class="chart-card"><h4>📊 各品类出单率对比</h4><canvas id="chartCategoryRate"></canvas></div>
      <div class="chart-card"><h4>🔖 拓展类型销量对比</h4><canvas id="chartExpand"></canvas></div>
      <div class="chart-card"><h4>👤 分析人销量贡献</h4><canvas id="chartAnalyst"></canvas></div>
    </div>
  </div>
</div>

<!-- 品线维度 -->
<div id="section-pinxian" class="section-wrap" style="display:none">
  <div class="section">
    <h3>🏷️ 品线维度（含完整环比）</h3>
    <div class="sub-module">
<h4>各品类3月绩效汇总（含环比）</h4>
<table class="data-table">
<thead><tr><th>品类</th><th>3月销量</th><th>销量环比</th><th>3月出单率</th><th>出单率环比</th></tr></thead>
<tbody id="cat-tbody"></tbody>
</table>
</div>
    <div class="chart-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="chart-card"><h4>📈 各品类3月销量对比</h4><canvas id="chartCatQty"></canvas></div>
      <div class="chart-card"><h4>📊 各品类出单率对比</h4><canvas id="chartCatRate"></canvas></div>
    </div>
  </div>
</div>

<!-- 分析人维度 -->
<div id="section-analyst" class="section-wrap" style="display:none">
  <div class="section">
    <h3>👤 分析人维度（含完整环比）</h3>
    <div class="sub-module">
<h4>各分析人3月绩效统计（含环比）</h4>
<table class="data-table">
<thead><tr><th>分析人</th><th>SKU数</th><th>3月销量</th><th>销量环比</th><th>3月出单率</th><th>出单率环比</th></tr></thead>
<tbody id="analyst-tbody"></tbody>
</table>
</div>
    <div class="chart-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="chart-card"><h4>👤 各分析人3月销量对比</h4><canvas id="chartAnalystQty"></canvas></div>
      <div class="chart-card"><h4>📊 各分析人出单率对比</h4><canvas id="chartAnalystRate"></canvas></div>
    </div>
  </div>
</div>

<!-- 拓展类型维度 -->
<div id="section-expand" class="section-wrap" style="display:none">
  <div class="section">
    <h3>🔖 拓展类型维度（含完整环比）</h3>
    <div class="sub-module">
<h4>各拓展类型3月绩效统计（含环比）</h4>
<table class="data-table">
<thead><tr><th>拓展类型</th><th>SKU数</th><th>3月销量</th><th>销量环比</th><th>3月出单率</th><th>出单率环比</th></tr></thead>
<tbody id="expand-tbody"></tbody>
</table>
</div>
    <div class="chart-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="chart-card"><h4>📈 各拓展类型SKU数</h4><canvas id="chartExpandSku"></canvas></div>
      <div class="chart-card"><h4>📊 各拓展类型出单率</h4><canvas id="chartExpandRate"></canvas></div>
    </div>
  </div>
</div>

<!-- 出单情况 -->
<div id="section-order" class="section-wrap" style="display:none">
  <div class="section">
    <h3>📦 出单情况分析（含完整环比）</h3>
    <div class="sub-module">
<h4>各批次出单情况统计（含环比）</h4>
<table class="data-table">
<thead><tr><th>批次</th><th>SKU数</th><th>3月销量</th><th>销量环比</th><th>8日Y出单</th><th>8日N出单</th><th>未出单</th><th>出单率</th><th>出单率环比</th></tr></thead>
<tbody id="order-tbody"></tbody>
</table>
</div>
    <div class="chart-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="chart-card"><h4>📊 各批次出单情况</h4><canvas id="chartOrderBatch"></canvas></div>
      <div class="chart-card"><h4>📈 各批次出单率趋势</h4><canvas id="chartOrderRate"></canvas></div>
    </div>
  </div>
</div>

<!-- 未出单市场 -->
<div id="section-unorder" class="section-wrap" style="display:none">
  <div class="section">
    <h3>❌ 未出单市场状态分布</h3>
    <div class="sub-module">
<h4>3月市场状态统计</h4>
<table class="data-table">
<thead><tr><th>市场状态</th><th>数量</th><th>占比</th></tr></thead>
<tbody id="market-tbody"></tbody>
</table>
</div>
    <div class="chart-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="chart-card"><h4>🥧 市场状态分布</h4><canvas id="chartMarketPie"></canvas></div>
      <div class="chart-card"><h4>📊 正常 vs 异常对比</h4><canvas id="chartMarketCompare"></canvas></div>
    </div>
  </div>
</div>

<!-- 低占比新品 -->
<div id="section-lowshare" class="section-wrap" style="display:none">
  <div class="section">
    <h3>📉 低市占比新品清单（阈值75% · 对手有出单）</h3>
    <p style="font-size:12px;color:#e07b24;margin-bottom:10px;">⚠️ 筛选条件：自身市占比 &lt; 75% 且 对手有出单（comp &gt; 0）</p>
    <div style="margin-bottom:10px;">
      <select id="low-share-batch" onchange="renderLowShare()" style="padding:6px 12px;border-radius:6px;border:1px solid #ddd;font-size:13px;">
        <option value="all">全部批次（72个SKU）</option>
        <option value="1">1月新品（24个SKU）</option>
        <option value="2">2月新品（13个SKU）</option>
        <option value="3">3月新品（35个SKU）</option>
      </select>
    </div>
    <div class="table-wrap">
    <table class="data-table">
    <thead><tr><th>批次</th><th>SKU</th><th>商品类</th><th>分析人</th><th>拓展类型</th><th>3月销量</th><th>对手出单</th><th>市占比</th><th>8日出单</th><th>市场状态</th></tr></thead>
    <tbody id="lowmkt-tbody"></tbody>
    </table>
    </div>
  </div>
</div>

<!-- 全量明细 -->
<div id="section-detail" class="section-wrap" style="display:none">
  <div class="section">
    <h3>📋 全量SKU明细（共156个SKU）</h3>
    <p style="font-size:12px;color:#888;margin-bottom:10px;">绿色背景行为3月8日已出单SKU，橙色为未出单</p>
    <div style="margin-bottom:10px;">
      <select id="detail-batch" onchange="renderDetailTable()" style="padding:6px 12px;border-radius:6px;border:1px solid #ddd;font-size:13px;">
        <option value="all">全部批次</option>
        <option value="1">1月新品</option>
        <option value="2">2月新品</option>
        <option value="3">3月新品</option>
      </select>
    </div>
    <div class="table-wrap">
    <table class="data-table">
    <thead><tr><th>销售编号</th><th>SKU</th><th>批次</th><th>分析人</th><th>品类</th><th>拓展类型</th><th>3月销量</th><th>对手出单</th><th>市占比</th><th>8日出单</th><th>市场状态</th></tr></thead>
    <tbody id="detail-tbody"></tbody>
    </table>
    </div>
  </div>
</div>

</div>
</div>

<script>
// ========== 数据定义 ==========
const ALL_DATA = ''' + low_share_js + ''';

const CATEGORY_DATA = ''' + json.dumps(data['category'], ensure_ascii=False) + ''';
const ANALYST_DATA = ''' + json.dumps(data['analyst'], ensure_ascii=False) + ''';
const EXPAND_DATA = ''' + json.dumps(data['expand'], ensure_ascii=False) + ''';
const BATCH_DATA = ''' + json.dumps(data['batch'], ensure_ascii=False) + ''';
const MARKET_DATA = ''' + json.dumps(data['market_dist'], ensure_ascii=False) + ''';

const COLORS = ['#0f3460','#e07b24','#08845a','#c0392b','#8e44ad','#2980b9','#16a085','#d35400','#7f8c8d'];

// ========== 环比辅助函数 ==========
function fmtHb(val, suffix) {
  if (val === null || val === undefined || val === '-') return '<span class="hb-flat">-</span>';
  suffix = suffix || '';
  if (val > 0) return '<span class="hb-up">+' + val + suffix + '</span>';
  if (val < 0) return '<span class="hb-down">' + val + suffix + '</span>';
  return '<span class="hb-flat">0' + suffix + '</span>';
}

// ========== 图表函数 ==========
function mkBar(id, labels, datasets) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {type: 'bar', data: { labels, datasets }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: datasets.length > 1, position: 'top', labels: { font: { size: 10 } } } }, scales: { x: { ticks: { font: { size: 10 }, maxRotation: 30 } }, y: { ticks: { font: { size: 10 } }, beginAtZero: true } } }});
}
function mkLine(id, labels, datasets) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {type: 'line', data: { labels, datasets }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: datasets.length > 1, position: 'top', labels: { font: { size: 10 } } } }, scales: { x: { ticks: { font: { size: 10 } } }, y: { ticks: { font: { size: 10 } } } }});
}
function mkPie(id, labels, data) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {type: 'doughnut', data: { labels, datasets: [{ data, backgroundColor: COLORS, borderWidth: 1 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 12 } } } }});
}

// ========== 初始化图表 ==========
mkBar('chartBatchQty', ['1月新品', '2月新品', '3月新品'], [{ label: '销量', data: [613, 483, 368], backgroundColor: ['#adb5bd', '#667eea', '#e74c3c'] }]);
mkBar('chartBatchAmt', ['1月新品', '2月新品', '3月新品'], [{ label: '销售额(百元)', data: [523, 553, 746], backgroundColor: ['#adb5bd', '#667eea', '#e74c3c'] }]);

const catLabels = Object.keys(CATEGORY_DATA);
mkBar('chartCategoryQty', catLabels, [{ label: '3月销量', data: catLabels.map(k => CATEGORY_DATA[k].qty_3), backgroundColor: COLORS }]);
mkBar('chartCategoryRate', catLabels, [{ label: '出单率(%)', data: catLabels.map(k => CATEGORY_DATA[k].rate_3), backgroundColor: COLORS }]);
mkBar('chartExpand', Object.keys(EXPAND_DATA), [{ label: '3月销量', data: Object.values(EXPAND_DATA).map(v => v.qty_3), backgroundColor: ['#0f3460','#e07b24','#08845a'] }]);
mkBar('chartAnalyst', Object.keys(ANALYST_DATA), [{ label: '3月销量', data: Object.values(ANALYST_DATA).map(v => v.qty_3), backgroundColor: COLORS }]);

// ========== 渲染品线表格 ==========
function renderCatTable() {
  let html = '';
  for (const [cat, d] of Object.entries(CATEGORY_DATA)) {
    html += `<tr><td style="text-align:left;font-weight:600">${cat}</td><td>${d.qty_3}</td><td>${fmtHb(d.qty_hb, '')}</td><td>${d.rate_3}%</td><td>${fmtHb(d.rate_hb, '%')}</td></tr>`;
  }
  document.getElementById('cat-tbody').innerHTML = html;
}
renderCatTable();
mkBar('chartCatQty', catLabels, [{ label: '3月销量', data: catLabels.map(k => CATEGORY_DATA[k].qty_3), backgroundColor: COLORS }]);
mkBar('chartCatRate', catLabels, [{ label: '出单率(%)', data: catLabels.map(k => CATEGORY_DATA[k].rate_3), backgroundColor: COLORS }]);

// ========== 渲染分析人表格 ==========
function renderAnalystTable() {
  let html = '';
  for (const [name, d] of Object.entries(ANALYST_DATA)) {
    html += `<tr><td style="text-align:left;font-weight:600">${name}</td><td>${d.sku_3}</td><td>${d.qty_3}</td><td>${fmtHb(d.qty_hb, '')}</td><td class="highlight">${d.rate_3}%</td><td>${fmtHb(d.rate_hb, '%')}</td></tr>`;
  }
  document.getElementById('analyst-tbody').innerHTML = html;
}
renderAnalystTable();
mkBar('chartAnalystQty', Object.keys(ANALYST_DATA), [{ label: '3月销量', data: Object.values(ANALYST_DATA).map(v => v.qty_3), backgroundColor: COLORS }]);
mkBar('chartAnalystRate', Object.keys(ANALYST_DATA), [{ label: '出单率(%)', data: Object.values(ANALYST_DATA).map(v => v.rate_3), backgroundColor: COLORS }]);

// ========== 渲染拓展类型表格 ==========
function renderExpandTable() {
  let html = '';
  for (const [exp, d] of Object.entries(EXPAND_DATA)) {
    html += `<tr><td style="text-align:left;font-weight:600">${exp}</td><td>${d.sku_3}</td><td>${d.qty_3}</td><td>${fmtHb(d.qty_hb, '')}</td><td>${d.rate_3}%</td><td>${fmtHb(d.rate_hb, '%')}</td></tr>`;
  }
  document.getElementById('expand-tbody').innerHTML = html;
}
renderExpandTable();
mkBar('chartExpandSku', Object.keys(EXPAND_DATA), [{ label: 'SKU数', data: Object.values(EXPAND_DATA).map(v => v.sku_3), backgroundColor: ['#0f3460','#e07b24','#08845a'] }]);
mkBar('chartExpandRate', Object.keys(EXPAND_DATA), [{ label: '出单率(%)', data: Object.values(EXPAND_DATA).map(v => v.rate_3), backgroundColor: ['#0f3460','#e07b24','#08845a'] }]);

// ========== 渲染出单情况表格 ==========
function renderOrderTable() {
  let html = '';
  const batches = [['1月', '1月新品'], ['2月', '2月新品'], ['3月', '3月新品']];
  for (const [k, label] of batches) {
    const d = BATCH_DATA[k];
    const qty_hb_html = d.qty_hb !== '-' ? fmtHb(d.qty_hb, '') : '<span class="hb-flat">-</span>';
    const rate_hb_html = d.rate_hb !== '-' ? fmtHb(d.rate_hb, '%') : '<span class="hb-flat">-</span>';
    html += `<tr><td>${label}</td><td>${d.sku}</td><td>${d.qty}</td><td>${qty_hb_html}</td><td style="color:#08845a;font-weight:700">${d.ordered}</td><td style="color:#e07b24;font-weight:700">${d.unorder}</td><td>${d.not_order}</td><td class="highlight">${d.rate}%</td><td>${rate_hb_html}</td></tr>`;
  }
  document.getElementById('order-tbody').innerHTML = html;
}
renderOrderTable();
mkBar('chartOrderBatch', ['1月新品', '2月新品', '3月新品'], [
  { label: '8日Y出单', data: [24, 19, 39], backgroundColor: '#08845a' },
  { label: '8日N出单', data: [28, 14, 9], backgroundColor: '#e07b24' },
  { label: '未出单', data: [1, 3, 19], backgroundColor: '#c0392b' }
]);
mkLine('chartOrderRate', ['1月新品', '2月新品', '3月新品'], [{label: '出单率(%)', data: [45.3, 52.8, 58.2], borderColor: '#0f3460', backgroundColor: 'rgba(15,52,96,0.1)', fill: true, tension: 0.3}]);

// ========== 渲染市场状态表格 ==========
function renderMarketTable() {
  let html = '';
  const total = Object.values(MARKET_DATA).reduce((a,b) => a+b, 0);
  for (const [status, count] of Object.entries(MARKET_DATA)) {
    const pct = (count / total * 100).toFixed(1);
    html += `<tr><td style="text-align:left">${status}</td><td>${count}</td><td>${pct}%</td></tr>`;
  }
  document.getElementById('market-tbody').innerHTML = html;
  const normalCount = MARKET_DATA['正常'] || 0;
  mkBar('chartMarketCompare', ['正常', '异常'], [{ label: '数量', data: [normalCount, total - normalCount], backgroundColor: ['#08845a', '#c0392b'] }]);
}
renderMarketTable();
mkPie('chartMarketPie', Object.keys(MARKET_DATA), Object.values(MARKET_DATA));

// ========== 渲染低占比新品表格 ==========
function renderLowShare() {
  const batch = document.getElementById('low-share-batch').value;
  const filtered = batch === 'all' ? ALL_DATA : ALL_DATA.filter(d => d.batch === batch);
  let html = '';
  for (const d of filtered) {
    const sharePct = d.share > 0 ? d.share.toFixed(1) + '%' : '0%';
    const shareColor = d.share >= 75 ? '#08845a' : '#c0392b';
    const orderColor = d.order === 'Y' ? '#08845a' : d.order === 'N' ? '#e07b24' : '#c0392b';
    const statusColor = d.status === '正常' ? '#08845a' : '#c0392b';
    html += `<tr><td><span style="background:${d.batch==='1月'?'#adb5bd':d.batch==='2月'?'#667eea':'#e74c3c'};color:white;padding:2px 8px;border-radius:10px;font-size:10px">${d.batch}</span></td><td style="text-align:left;font-weight:600">${d.sku}</td><td>${d.cat}</td><td>${d.analyst}</td><td>${d.expand}</td><td>${d.qty}</td><td>${d.comp}</td><td style="color:${shareColor};font-weight:700">${sharePct}</td><td style="color:${orderColor};font-weight:600">${d.order}</td><td style="color:${statusColor}">${d.status}</td></tr>`;
  }
  document.getElementById('lowmkt-tbody').innerHTML = html;
}
renderLowShare();

// ========== 渲染全量明细表格 ==========
function renderDetailTable() {
  const batch = document.getElementById('detail-batch').value;
  const filtered = batch === 'all' ? ALL_DATA : ALL_DATA.filter(d => d.batch === batch);
  let html = '';
  for (const d of filtered) {
    const isOrdered = d.order === 'Y';
    const bgClass = isOrdered ? 'row-ordered' : '';
    const sharePct = d.share > 0 ? d.share.toFixed(1) + '%' : '0%';
    const orderColor = isOrdered ? '#08845a' : '#e07b24';
    const statusColor = d.status === '正常' ? '#08845a' : '#c0392b';
    html += `<tr class="${bgClass}"><td>${d.sku}</td><td style="text-align:left;font-weight:600">${d.sku}</td><td><span style="background:${d.batch==='1月'?'#adb5bd':d.batch==='2月'?'#667eea':'#e74c3c'};color:white;padding:2px 8px;border-radius:10px;font-size:10px">${d.batch}</span></td><td>${d.analyst}</td><td>${d.cat}</td><td>${d.expand}</td><td>${d.qty}</td><td>${d.comp}</td><td>${sharePct}</td><td style="color:${orderColor};font-weight:600">${d.order}</td><td style="color:${statusColor}">${d.status}</td></tr>`;
  }
  document.getElementById('detail-tbody').innerHTML = html;
}
renderDetailTable();

// ========== 导航切换 ==========
const sections = ['overview','pinxian','analyst','expand','order','unorder','lowshare','detail'];
function showSection(name, el) {
  sections.forEach(s => {
    const wrap = document.getElementById('section-' + s);
    if (wrap) wrap.style.display = s === name ? 'block' : 'none';
  });
  document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
  if (el) el.classList.add('active');
  return false;
}
document.querySelector('.sidebar a').classList.add('active');
</script>
</body>
</html>'''

with open('新品月报_2026年3月_带环比.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('HTML生成成功!')
print(f'低占比新品: {len(data["low_share"])}条')
