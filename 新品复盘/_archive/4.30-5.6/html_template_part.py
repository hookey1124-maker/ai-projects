
# ===== HTML 生成 =====
print("生成HTML...")

CSS = r'''
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', '微软雅黑', sans-serif; background: #f0f2f5; color: #1a1a2e; display: flex; min-height: 100vh; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }

.sidebar { width: 230px; min-width: 230px; background: #fff; height: 100vh; position: sticky; top: 0; overflow-y: auto; box-shadow: 2px 0 8px rgba(0,0,0,0.06); z-index: 10; }
.sidebar h2 { font-size: 16px; color: #0f3460; padding: 20px 16px 12px; border-bottom: 2px solid #e8f0fe; }
.sidebar ul { list-style: none; padding: 8px 0; }
.sidebar li a { display: block; padding: 12px 16px; color: #555; text-decoration: none; font-size: 13px; border-left: 3px solid transparent; transition: all 0.2s; }
.sidebar li a:hover, .sidebar li a.active { background: #f0f6ff; color: #0f3460; border-left-color: #0f3460; font-weight: 600; }

.main { flex: 1; padding: 24px; overflow: auto; }
.header { background: linear-gradient(135deg, #0f3460, #16213e); color: #fff; padding: 20px 24px; border-radius: 10px; margin-bottom: 20px; }
.header h1 { font-size: 20px; }
.header p { font-size: 12px; opacity: 0.8; margin-top: 4px; }

.tab-content { display: none; }
.tab-content.active { display: block; }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px; }
.kpi-card { background: #fff; border-radius: 10px; padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.kpi-card .label { font-size: 11px; color: #888; margin-bottom: 6px; }
.kpi-card .val { font-size: 24px; font-weight: 700; }
.kpi-card .hb { font-size: 11px; margin-top: 4px; }
.kpi-card.primary .val { color: #0f3460; }
.kpi-card.success .val { color: #08845a; }
.kpi-card.warning .val { color: #e07b24; }
.kpi-card.danger .val { color: #c0392b; }
.kpi-card.info .val { color: #2980b9; }
.kpi-card.purple .val { color: #8e44ad; }

.section { background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section h3 { font-size: 15px; color: #0f3460; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e8f0fe; }
.sub-module { margin-bottom: 16px; }
.sub-module h4 { font-size: 13px; color: #0f3460; background: #f5f7ff; padding: 8px 12px; border-left: 3px solid #0f3460; margin-bottom: 10px; }

.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.chart-box { background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.chart-box h4 { font-size: 13px; color: #0f3460; margin-bottom: 12px; }
.chart-box canvas { max-height: 280px; }

.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th { background: #0f3460; color: #fff; padding: 8px 10px; font-weight: 600; white-space: nowrap; text-align: center; }
.data-table td { padding: 6px 10px; border-bottom: 1px solid #eee; text-align: center; }
.data-table tr:hover td { background: #f5f7ff; }
.data-table .num { text-align: right; }
.data-table .total-row td { font-weight: 700; background: #e8f0fe; }

.hb-up { color: #08845a; font-weight: 600; }
.hb-down { color: #c0392b; font-weight: 600; }
.hb-flat { color: #888; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: #fff; font-weight: 600; }
.badge-green { background: #08845a; }
.badge-orange { background: #e07b24; }
.badge-red { background: #c0392b; }
.badge-blue { background: #2980b9; }
.badge-purple { background: #8e44ad; }
.badge-gray { background: #6c757d; }

.filter-bar { background: #f5f7ff; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.filter-bar select { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; background: #fff; }
.filter-bar select:focus { border-color: #0f3460; outline: none; }
.filter-bar .reset-btn { color: #c0392b; border: 1px solid #c0392b; background: #fff; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; }
.filter-bar .reset-btn:hover { background: #c0392b; color: #fff; }
.filter-bar .count { font-size: 12px; color: #888; margin-left: auto; }

.report-block { background: #f9fafb; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; border-left: 4px solid #0f3460; position: relative; }
.report-block h4 { font-size: 13px; color: #0f3460; margin-bottom: 8px; }
.report-block pre { white-space: pre-wrap; font-size: 12px; color: #444; font-family: '微软雅黑', sans-serif; margin: 0; }
.report-block .copy-btn { position: absolute; top: 12px; right: 16px; background: #0f3460; color: #fff; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 11px; }
.report-block .copy-btn:hover { background: #16213e; }

.risk-high { background: #fff5f5; border-left-color: #c0392b; }
.risk-high h4 { color: #c0392b; }
.risk-medium { background: #fffdf5; border-left-color: #e07b24; }
.risk-medium h4 { color: #e07b24; }
.risk-low { background: #f5fff5; border-left-color: #08845a; }
.risk-low h4 { color: #08845a; }

.findings-card { background: #f5f9ff; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; border-left: 4px solid #2980b9; }
.findings-card .title { font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 4px; }
.findings-card .desc { font-size: 12px; color: #555; }

.action-card { background: #fdf5ff; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; border-left: 4px solid #8e44ad; }
.action-card .title { font-size: 13px; font-weight: 600; color: #8e44ad; margin-bottom: 4px; }
.action-card .desc { font-size: 12px; color: #555; }

.pinxiao-table .px-high { color: #08845a; font-weight: 700; }
.pinxiao-table .px-mid { color: #000; }
.pinxiao-table .px-low { color: #c0392b; font-weight: 600; }
.trend-up { color: #08845a; }
.trend-down { color: #c0392b; }
.trend-flat { color: #888; }

@media(max-width:900px) {
  .sidebar { display: none; }
  .chart-grid { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2,1fr); }
}
</style>
'''

HTML_BODY = r'''
<div class="sidebar">
  <h2>新品周报 5.14-5.20</h2>
  <ul>
    <li><a href="javascript:void(0)" class="active" onclick="switchTab('tab1',this)">总盘概览</a></li>
    <li><a href="javascript:void(0)" onclick="switchTab('tab2',this)">低占比分析</a></li>
    <li><a href="javascript:void(0)" onclick="switchTab('tab3',this)">广告追踪</a></li>
    <li><a href="javascript:void(0)" onclick="switchTab('tab4',this)">四三累计</a></li>
    <li><a href="javascript:void(0)" onclick="switchTab('tab5',this)">品效分析</a></li>
    <li><a href="javascript:void(0)" onclick="switchTab('tab6',this)">汇报输出</a></li>
  </ul>
</div>
<div class="main">
  <div class="header">
    <h1>新品周报看板 5.14 - 5.20</h1>
    <p>数据截至 2026-05-20 | 三部新品 | 含品效分析 + PLP/PLG广告追踪</p>
  </div>

  <div class="tab-content active" id="tab1">
    <div class="kpi-grid" id="t1-kpi"></div>
    <div class="chart-grid">
      <div class="chart-box"><h4>出单分布</h4><canvas id="chart-ord8"></canvas></div>
      <div class="chart-box"><h4>品线销量对比</h4><canvas id="chart-cat-sales"></canvas></div>
      <div class="chart-box"><h4>分析人销量对比</h4><canvas id="chart-an-sales"></canvas></div>
      <div class="chart-box"><h4>分析人及时率对比</h4><canvas id="chart-an-timely"></canvas></div>
      <div class="chart-box"><h4>品线销售额对比</h4><canvas id="chart-cat-rev"></canvas></div>
      <div class="chart-box"><h4>分析人销售额对比</h4><canvas id="chart-an-rev"></canvas></div>
    </div>
    <div class="section"><h3>新品出单情况</h3><div id="t1-ord8"></div></div>
    <div class="section"><h3>多维度分析</h3>
      <div class="sub-module"><h4>品线维度</h4><div id="t1-cat-table"></div></div>
      <div class="sub-module"><h4>分析人维度</h4><div id="t1-an-table"></div></div>
    </div>
    <div class="section"><h3>拓展类型 & 及时率</h3>
      <div class="sub-module"><h4>拓展类型</h4><div id="t1-exp-table"></div></div>
      <div class="sub-module"><h4>分析及时率</h4><div id="t1-time-table"></div></div>
    </div>
  </div>

  <div class="tab-content" id="tab2">
    <div class="kpi-grid" id="t2-kpi"></div>
    <div class="section"><h3>A. 有对手未出单新品</h3>
      <div class="sub-module"><h4>按分析人</h4><div id="t2-has-an"></div></div>
      <div class="sub-module"><h4>按品线</h4><div id="t2-has-cat"></div></div>
    </div>
    <div class="section"><h3>B. 无对手未出单新品</h3>
      <div class="sub-module"><h4>按分析人</h4><div id="t2-no-an"></div></div>
      <div class="sub-module"><h4>按品线</h4><div id="t2-no-cat"></div></div>
    </div>
    <div class="section"><h3>低占比新品明细</h3><div id="t2-lowshare-table"></div></div>
  </div>

  <div class="tab-content" id="tab3">
    <div class="kpi-grid" id="t3-plp-kpi"></div>
    <div class="section"><h3>PLP 核心指标</h3><div class="kpi-grid" id="t3-plp-core"></div></div>
    <div class="section"><h3>PLP 维度分析</h3>
      <div class="sub-module"><h4>按分析人</h4><div id="t3-plp-an"></div></div>
      <div class="sub-module"><h4>按品线</h4><div id="t3-plp-cat"></div></div>
      <div class="sub-module"><h4>按拓展类型</h4><div id="t3-plp-exp"></div></div>
    </div>
    <div class="section"><h3>PLG 费率统计</h3><div id="t3-plg"></div></div>
    <div class="section"><h3>PLP 广告明细</h3><div id="t3-plp-detail"></div></div>
  </div>

  <div class="tab-content" id="tab4">
    <div class="kpi-grid" id="t4-kpi"></div>
    <div class="section">
      <div class="filter-bar" id="t4-filters"></div>
      <div id="t4-table"></div>
    </div>
  </div>

  <div class="tab-content" id="tab5">
    <div class="section"><h3>品效Cohort分析（按上架月份）</h3><div id="t5-cohort"></div></div>
    <div class="chart-grid">
      <div class="chart-box"><h4>月度销售额趋势</h4><canvas id="chart-px-rev"></canvas></div>
      <div class="chart-box"><h4>品效趋势（$/SKU）</h4><canvas id="chart-px-trend"></canvas></div>
    </div>
    <div class="section"><h3>品效 x 品线</h3><div id="t5-cat"></div></div>
    <div class="section"><h3>品效 x 拓展类型</h3><div id="t5-exp"></div></div>
  </div>

  <div class="tab-content" id="tab6">
    <div class="kpi-grid" id="t6-kpi"></div>
    <div class="section"><h3>风险预警</h3><div id="t6-risk"></div></div>
    <div class="section"><h3>本周期主要发现</h3><div id="t6-findings"></div></div>
    <div class="section"><h3>下周重点动作</h3><div id="t6-actions"></div></div>
    <div class="section"><h3>可复制周报文案</h3><div id="t6-report"></div></div>
  </div>
</div>
'''

JS_CODE = r'''
function fmtNum(n) { return n == null || n === '' ? '-' : Number(n).toLocaleString('zh-CN'); }
function fmtMoney(n) { return n == null || n === '' ? '-' : '$' + Number(n).toFixed(2); }
function pct(v) { return v == null || v === '' ? '-' : v; }
function acoasPct(v) {
  if (v == null || v === '' || v === 0) return '0.00%';
  if (typeof v === 'string') { var n = parseFloat(v); return isNaN(n) ? v : n.toFixed(2) + '%'; }
  return (v * 100).toFixed(2) + '%';
}
function hbSign(v) {
  if (typeof v !== 'string') return v;
  if (v === '-' || v === '0%' || v === '0.0%' || v === '+0%') return '<span class="hb-flat">-</span>';
  if (v.startsWith('+')) return '<span class="hb-up">' + v + '</span>';
  if (v.startsWith('-')) return '<span class="hb-down">' + v + '</span>';
  return '<span class="hb-flat">' + v + '</span>';
}
function badge(s, cls) { return '<span class="badge ' + cls + '">' + s + '</span>'; }
function badgeStatus(v) {
  if (v === '竞争无优势') return badge('竞争弱', 'badge-orange');
  if (v === '无市场') return badge('无市场', 'badge-red');
  if (v === '正常') return badge('正常', 'badge-blue');
  return v;
}
function badge8d(v) {
  if (v === 'Y') return badge('Y', 'badge-green');
  if (v === 'N') return badge('N', 'badge-orange');
  return badge(v, 'badge-red');
}
function badgeAdClass(v) {
  if (!v) return '';
  if (v.indexOf('单链接') === 0) return '<span style="color:#c0392b;font-weight:600">' + v + '</span>';
  if (v === '单PLG且未出单') return '<span style="color:#c0392b;font-weight:600">' + v + '</span>';
  if (v === 'PLP+PLG同开') return '<span style="color:#8e44ad;font-weight:600">' + v + '</span>';
  if (v === '单PLG') return '<span style="color:#e07b24;">' + v + '</span>';
  if (v === '单PLP') return '<span style="color:#2980b9;">' + v + '</span>';
  return v;
}

function switchTab(tabId, el) {
  document.querySelectorAll('.tab-content').forEach(function(t) { t.classList.remove('active'); });
  document.getElementById(tabId).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(function(a) { a.classList.remove('active'); });
  if (el) el.classList.add('active');
  if (tabId === 'tab1' && !window._charts1Init) { initCharts1(); }
  if (tabId === 'tab5' && !window._charts5Init) { initCharts5(); }
}

(function() {
  var t = cum43Stats;
  var pk = prevWeekKpi;
  var saleRate = t.hasRivalCount ? (t.yCount + t.nCount) / t.hasRivalCount * 100 : 0;

  document.getElementById('t1-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">累计SKU数</div><div class="val">' + t.total + '</div><div class="hb">' + hbSign(pk.skuChange) + ' 上周' + pk.prevTotalSku + '</div></div>' +
    '<div class="kpi-card success"><div class="label">总销量</div><div class="val">' + fmtNum(pk.prevTotalSalesQty) + '</div><div class="hb">' + hbSign(pk.salesQtyChange) + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">总销售额</div><div class="val">' + fmtMoney(pk.prevTotalRevenue) + '</div><div class="hb">' + hbSign(pk.revenueChange) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品销售占比</div><div class="val">' + pk.deptRatio + '</div><div class="hb">部门总销售额 ' + fmtMoney(pk.deptTotalRevenue) + '</div></div>' +
    '<div class="kpi-card success"><div class="label">出单率</div><div class="val">' + saleRate.toFixed(1) + '%</div><div class="hb">Y:' + t.yCount + ' N:' + t.nCount + ' 未:' + t.unCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">分析及时率</div><div class="val">' + timelinessData.total.timelyRate + '</div><div class="hb">' + hbSign(timelinessData.total.change) + '</div></div>';

  var ordHtml = '<table class="data-table"><thead><tr><th>指标</th><th>本周(5.20)</th><th>上周(5.13)</th><th>变化</th></tr></thead><tbody>' +
    '<tr><td>有对手新品总SKU</td><td>' + t.hasRivalCount + '</td><td>-</td><td>-</td></tr>' +
    '<tr><td>8日内出单(Y)</td><td>' + t.yCount + '</td><td>-</td><td>-</td></tr>' +
    '<tr><td>8日外出单(N)</td><td>' + t.nCount + '</td><td>-</td><td>-</td></tr>' +
    '<tr><td>真正未出单</td><td>' + t.unCount + '</td><td>-</td><td>-</td></tr>' +
    '<tr class="total-row"><td>已出单合计(Y+N)</td><td>' + (t.yCount+t.nCount) + '</td><td>-</td><td>-</td></tr>' +
    '<tr class="total-row"><td>出单率</td><td>' + saleRate.toFixed(1) + '%</td><td>-</td><td>-</td></tr>' +
    '</tbody></table>';
  document.getElementById('t1-ord8').innerHTML = ordHtml;

  var catHtml = '<table class="data-table"><thead><tr><th>品线</th><th>SKU数</th><th>本周新上架</th><th>本周销量</th><th>上周销量</th><th>销量环比</th><th>本周销售额</th><th>上周销售额</th><th>销售额环比</th></tr></thead><tbody>';
  categoryRevenueData.forEach(function(d) {
    catHtml += '<tr><td>' + d.category + '</td><td>' + d.curSku + '</td><td>' + d.curNewSku + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + fmtNum(d.prevSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + fmtMoney(d.prevRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td></tr>';
  });
  catHtml += '</tbody></table>';
  document.getElementById('t1-cat-table').innerHTML = catHtml;

  var anHtml = '<table class="data-table"><thead><tr><th>分析人</th><th>SKU数</th><th>本周新上架</th><th>本周销量</th><th>上周销量</th><th>销量环比</th><th>本周销售额</th><th>上周销售额</th><th>销售额环比</th></tr></thead><tbody>';
  analystRevenueData.forEach(function(d) {
    anHtml += '<tr><td>' + d.analyst + '</td><td>' + d.curSku + '</td><td>' + d.curNewSku + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + fmtNum(d.prevSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + fmtMoney(d.prevRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td></tr>';
  });
  anHtml += '</tbody></table>';
  document.getElementById('t1-an-table').innerHTML = anHtml;

  var expHtml = '<table class="data-table"><thead><tr><th>拓展类型</th><th>本周SKU</th><th>上周SKU</th><th>出单SKU</th><th>出单率</th><th>上周出单率</th><th>本周销量</th><th>上周销量</th><th>销量环比</th><th>本周销售额</th><th>上周销售额</th><th>销售额环比</th></tr></thead><tbody>';
  expandTypeData.forEach(function(d) {
    expHtml += '<tr><td>' + d.expandType + '</td><td>' + d.curSku + '</td><td>' + d.prevSku + '</td><td>' + d.curSalesSku + '</td><td>' + d.curSalesRate + '</td><td>' + d.prevSalesRate + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + fmtNum(d.prevSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + fmtMoney(d.prevRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td></tr>';
  });
  expHtml += '</tbody></table>';
  document.getElementById('t1-exp-table').innerHTML = expHtml;

  var timeHtml = '<table class="data-table"><thead><tr><th>分析人</th><th>本周SKU</th><th>及时分析</th><th>8日未分析</th><th>7日未分析</th><th>及时率</th><th>上周及时率</th><th>变化</th></tr></thead><tbody>';
  timelinessData.analysts.forEach(function(d) {
    timeHtml += '<tr><td>' + d.analyst + '</td><td>' + d.curSku + '</td><td>' + d.timelyCount + '</td><td>' + d.noAnalysis8dCount + '</td><td>' + d.noAnalysis7dCount + '</td><td>' + d.timelyRate + '</td><td>' + d.prevTimelyRate + '</td><td>' + hbSign(d.change) + '</td></tr>';
  });
  var td = timelinessData.total;
  timeHtml += '<tr class="total-row"><td>' + td.analyst + '</td><td>' + td.curSku + '</td><td>' + td.timelyCount + '</td><td>' + td.noAnalysis8dCount + '</td><td>' + td.noAnalysis7dCount + '</td><td>' + td.timelyRate + '</td><td>' + td.prevTimelyRate + '</td><td>' + hbSign(td.change) + '</td></tr>';
  timeHtml += '</tbody></table>';
  document.getElementById('t1-time-table').innerHTML = timeHtml;
})();

window._charts1Init = false;
function initCharts1() {
  if (window._charts1Init) return;
  window._charts1Init = true;
  var t = cum43Stats;

  new Chart(document.getElementById('chart-ord8'), {
    type: 'doughnut',
    data: {
      labels: ['已出单(Y+N)', '有对手未出单', '无市场/未出单'],
      datasets: [{ data: [t.yCount + t.nCount, t.unCount, t.total - t.hasRivalCount], backgroundColor: ['#08845a', '#e07b24', '#c0392b'] }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });

  var catLabels = categoryRevenueData.map(function(d) { return d.category; });
  new Chart(document.getElementById('chart-cat-sales'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销量', data: categoryRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460' },
      { label: '上周销量', data: categoryRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });
  new Chart(document.getElementById('chart-cat-rev'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销售额', data: categoryRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad' },
      { label: '上周销售额', data: categoryRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });

  var anLabels = analystRevenueData.map(function(d) { return d.analyst; });
  new Chart(document.getElementById('chart-an-sales'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销量', data: analystRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460' },
      { label: '上周销量', data: analystRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });
  new Chart(document.getElementById('chart-an-rev'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销售额', data: analystRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad' },
      { label: '上周销售额', data: analystRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });
  new Chart(document.getElementById('chart-an-timely'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '及时率(%)', data: timelinessData.analysts.map(function(d){return parseFloat(d.timelyRate)||0;}), backgroundColor: '#2980b9' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, max: 100 } } }
  });
}
setTimeout(initCharts1, 100);

(function() {
  var hcu = hasCompetitorUnsold;
  var unc = unsoldNoCompetitor;
  var t = cum43Stats;

  document.getElementById('t2-kpi').innerHTML =
    '<div class="kpi-card warning"><div class="label">有对手未出单</div><div class="val">' + hcu.total + '</div><div class="hb">上周 ' + hcu.prevTotal + ' | ' + (hcu.change >= 0 ? '+' : '') + hcu.change + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">无对手未出单</div><div class="val">' + unc.total + '</div><div class="hb">上周 ' + unc.prevTotal + ' | ' + (unc.change >= 0 ? '+' : '') + unc.change + '</div></div>' +
    '<div class="kpi-card info"><div class="label">有对手SKU总数</div><div class="val">' + t.hasRivalCount + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">未出单占比</div><div class="val">' + (t.unCount/t.total*100).toFixed(1) + '%</div><div class="hb">' + t.unCount + ' / ' + t.total + '</div></div>';

  var hasMkts = ['竞争无优势', '无市场', '站内无价格优势', '站外出单', '正常', '#N/A', '未知'];
  var hasAnHtml = '<table class="data-table"><thead><tr><th>分析人</th>';
  hasMkts.forEach(function(m) { hasAnHtml += '<th>' + m + '</th>'; });
  hasAnHtml += '<th>未出单总数</th></tr></thead><tbody>';
  hcu.byAnalyst.forEach(function(d) {
    hasAnHtml += '<tr><td>' + d.analyst + '</td>';
    hasMkts.forEach(function(m) { hasAnHtml += '<td>' + (d[m] || 0) + '</td>'; });
    hasAnHtml += '<td><b>' + d.total + '</b></td></tr>';
  });
  hasAnHtml += '</tbody></table>';
  document.getElementById('t2-has-an').innerHTML = hasAnHtml;

  var hasCatHtml = '<table class="data-table"><thead><tr><th>品线</th>';
  hasMkts.forEach(function(m) { hasCatHtml += '<th>' + m + '</th>'; });
  hasCatHtml += '<th>未出单总数</th></tr></thead><tbody>';
  hcu.byCategory.forEach(function(d) {
    hasCatHtml += '<tr><td>' + d.category + '</td>';
    hasMkts.forEach(function(m) { hasCatHtml += '<td>' + (d[m] || 0) + '</td>'; });
    hasCatHtml += '<td><b>' + d.total + '</b></td></tr>';
  });
  hasCatHtml += '</tbody></table>';
  document.getElementById('t2-has-cat').innerHTML = hasCatHtml;

  var noMkts = ['无市场', '未知', '竞争无优势', '#N/A', '其他'];
  var noAnHtml = '<table class="data-table"><thead><tr><th>分析人</th>';
  noMkts.forEach(function(m) { noAnHtml += '<th>' + m + '</th>'; });
  noAnHtml += '<th>未出单总数</th></tr></thead><tbody>';
  unc.byAnalyst.forEach(function(d) {
    noAnHtml += '<tr><td>' + d.analyst + '</td>';
    noMkts.forEach(function(m) { noAnHtml += '<td>' + (d[m] || 0) + '</td>'; });
    noAnHtml += '<td><b>' + d.total + '</b></td></tr>';
  });
  noAnHtml += '</tbody></table>';
  document.getElementById('t2-no-an').innerHTML = noAnHtml;

  var noCatHtml = '<table class="data-table"><thead><tr><th>品线</th>';
  noMkts.forEach(function(m) { noCatHtml += '<th>' + m + '</th>'; });
  noCatHtml += '<th>未出单总数</th></tr></thead><tbody>';
  unc.byCategory.forEach(function(d) {
    noCatHtml += '<tr><td>' + d.category + '</td>';
    noMkts.forEach(function(m) { noCatHtml += '<td>' + (d[m] || 0) + '</td>'; });
    noCatHtml += '<td><b>' + d.total + '</b></td></tr>';
  });
  noCatHtml += '</tbody></table>';
  document.getElementById('t2-no-cat').innerHTML = noCatHtml;

  var lsHtml = '<table class="data-table"><thead><tr><th>SKU</th><th>上架日期</th><th>分析人</th><th>品类</th><th>本周销量</th><th>销量环比</th><th>本周销售额</th><th>对手量</th><th>市占比</th><th>上期市场状态</th><th>本期运作判断</th><th>本期市场状态</th><th>广告分类</th></tr></thead><tbody>';
  lowShareData.forEach(function(d) {
    lsHtml += '<tr><td>' + d.SKU + '</td><td>' + d.launchDate + '</td><td>' + d.analyst + '</td><td>' + d.category + '</td>';
    lsHtml += '<td>' + d.curSalesQty + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td>';
    lsHtml += '<td>' + d.curRivalQty + '</td><td>' + d.curMarketShare + '%</td>';
    lsHtml += '<td>' + badgeStatus(d.prevMarketStatus) + '</td><td>' + (d.curOperation || '-') + '</td><td>' + badgeStatus(d.curMarketStatus) + '</td>';
    lsHtml += '<td>' + badgeAdClass(d.adClass) + '</td></tr>';
  });
  lsHtml += '</tbody></table>';
  document.getElementById('t2-lowshare-table').innerHTML = lsHtml;
})();

(function() {
  var pt = plpTotal;
  var pp = plpPrevTotal;

  document.getElementById('t3-plp-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">广告活动数</div><div class="val">' + pt.campaignCount + '</div><div class="hb">上周 ' + pp.campaignCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">投放链接数</div><div class="val">' + pt.linkCount + '</div><div class="hb">上周 ' + pp.linkCount + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">曝光量</div><div class="val">' + fmtNum(pt.impression) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">点击量</div><div class="val">' + fmtNum(pt.click) + '</div></div>' +
    '<div class="kpi-card success"><div class="label">售出数</div><div class="val">' + pt.sold + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">广告销售额</div><div class="val">' + fmtMoney(pt.revenue) + '</div></div>';

  document.getElementById('t3-plp-core').innerHTML =
    '<div class="kpi-card primary"><div class="label">ROAS</div><div class="val">' + pt.roas + '</div><div class="hb">上周 ' + pp.roas + '</div></div>' +
    '<div class="kpi-card info"><div class="label">CVR</div><div class="val">' + pt.cvr + '</div><div class="hb">上周 ' + pp.cvr + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">CTR</div><div class="val">' + pt.ctr + '</div><div class="hb">上周 ' + pp.ctr + '</div></div>' +
    '<div class="kpi-card info"><div class="label">CPC</div><div class="val">' + pt.cpc + '</div><div class="hb">上周 ' + pp.cpc + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">CPA</div><div class="val">' + pt.cpa + '</div><div class="hb">上周 ' + pp.cpa + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">ACOS</div><div class="val">' + pt.acos + '</div><div class="hb">上周 ' + pp.acos + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">ACOAS</div><div class="val">' + pt.acoas + '</div><div class="hb">上周 ' + pp.acoas + '</div></div>';

  function renderPlpDim(data, labelKey) {
    var h = '<table class="data-table"><thead><tr><th>' + labelKey + '</th><th>活动数</th><th>链接数</th><th>曝光量</th><th>点击量</th><th>售出数</th><th>花费</th><th>广告销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>CPC</th><th>CPA</th><th>ACOS</th><th>ACOAS</th></tr></thead><tbody>';
    data.forEach(function(d) {
      h += '<tr><td>' + d.name + '</td><td>' + d.campaignCount + '</td><td>' + d.linkCount + '</td>';
      h += '<td>' + fmtNum(d.impression) + '</td><td>' + fmtNum(d.click) + '</td><td>' + d.sold + '</td>';
      h += '<td>' + fmtMoney(d.cost) + '</td><td>' + fmtMoney(d.revenue) + '</td>';
      h += '<td>' + d.roas + '</td><td>' + d.cvr + '</td><td>' + d.ctr + '</td>';
      h += '<td>' + d.cpc + '</td><td>' + d.cpa + '</td><td>' + d.acos + '</td><td>' + d.acoas + '</td></tr>';
    });
    h += '</tbody></table>';
    return h;
  }
  document.getElementById('t3-plp-an').innerHTML = renderPlpDim(plpAnalysts, '分析人');
  document.getElementById('t3-plp-cat').innerHTML = renderPlpDim(plpCategories, '品线');
  document.getElementById('t3-plp-exp').innerHTML = renderPlpDim(plpExpandTypes, '拓展类型');

  var pg = plgStats;
  var plgHtml = '<div class="kpi-grid" style="margin-bottom:12px">';
  plgHtml += '<div class="kpi-card primary"><div class="label">新品总数</div><div class="val">' + pg.totalNewProducts + '</div></div>';
  plgHtml += '<div class="kpi-card purple"><div class="label">PLP+PLG同开</div><div class="val">' + pg.plpAndPlgBothCount + '</div></div>';
  plgHtml += '<div class="kpi-card danger"><div class="label">单链接PLP+PLG同开</div><div class="val">' + pg.singleLinkPlpPlgCount + '</div></div>';
  plgHtml += '<div class="kpi-card info"><div class="label">单PLG</div><div class="val">' + pg.plgOnlyCount + '</div></div>';
  plgHtml += '<div class="kpi-card primary"><div class="label">单PLP</div><div class="val">' + pg.plpOnlyCount + '</div></div>';
  plgHtml += '<div class="kpi-card warning"><div class="label">无广告</div><div class="val">' + pg.noAdCount + '</div></div>';
  plgHtml += '</div>';
  plgHtml += '<table class="data-table"><thead><tr><th>分析人</th><th>总数</th><th>PLP+PLG同开</th><th>单链接PLP+PLG同开</th><th>单PLG</th><th>单PLP</th><th>无广告</th><th>PLP未开未出单</th></tr></thead><tbody>';
  pg.byAnalyst.forEach(function(d) {
    plgHtml += '<tr><td>' + d.analyst + '</td><td>' + d.total + '</td>';
    plgHtml += '<td>' + d.plpAndPlgBoth + '</td>';
    plgHtml += '<td style="color:#c0392b;font-weight:600">' + d.singleLinkPlpPlg + '</td>';
    plgHtml += '<td>' + d.plgOnly + '</td><td>' + d.plpOnly + '</td><td>' + d.noAd + '</td>';
    plgHtml += '<td style="color:#c0392b;font-weight:600">' + d.plpDisabledNoSale + '</td></tr>';
  });
  plgHtml += '</tbody></table>';
  document.getElementById('t3-plg').innerHTML = plgHtml;

  var detHtml = '<table class="data-table"><thead><tr><th>SKU</th><th>广告活动</th><th>分析人</th><th>品类</th><th>曝光</th><th>点击</th><th>售出</th><th>花费</th><th>广告销售额</th><th>总销售额</th><th>ROAS</th><th>ACOS</th><th>ACOAS</th><th>广告分类</th></tr></thead><tbody>';
  plpDetailData.forEach(function(d) {
    detHtml += '<tr><td>' + d.SKU + '</td><td>' + d.campaign + '</td><td>' + d.analyst + '</td><td>' + d.category + '</td>';
    detHtml += '<td>' + fmtNum(d.impressions) + '</td><td>' + fmtNum(d.clicks) + '</td><td>' + d.salesQty + '</td>';
    detHtml += '<td>' + fmtMoney(d.spend) + '</td><td>' + fmtMoney(d.adRevenue) + '</td><td>' + fmtMoney(d.totalRevenue) + '</td>';
    detHtml += '<td>' + (d.roas ? d.roas.toFixed(2) : '-') + '</td>';
    detHtml += '<td>' + (d.acos ? (d.acos*100).toFixed(2)+'%' : '0%') + '</td>';
    detHtml += '<td>' + acoasPct(d.acoas) + '</td>';
    detHtml += '<td>' + badgeAdClass(d.adClass) + '</td></tr>';
  });
  detHtml += '</tbody></table>';
  document.getElementById('t3-plp-detail').innerHTML = detHtml;
})();

(function() {
  var t = cum43Stats;
  document.getElementById('t4-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">累计总SKU</div><div class="val">' + t.total + '</div></div>' +
    '<div class="kpi-card success"><div class="label">已出单(Y+N)</div><div class="val">' + (t.yCount + t.nCount) + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">有对手未出单</div><div class="val">' + t.unCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">市场正常</div><div class="val">' + t.normalCount + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">竞争无优势</div><div class="val">' + t.competitiveCount + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">无市场</div><div class="val">' + t.noMarketCount + '</div></div>';

  var uniqAnalysts = [];
  var seenAn = {};
  cum43Data.forEach(function(d) { if (!seenAn[d.analyst]) { seenAn[d.analyst]=1; uniqAnalysts.push(d.analyst); } });
  uniqAnalysts.sort();
  var uniqCats = [];
  var seenCat = {};
  cum43Data.forEach(function(d) { if (!seenCat[d.category]) { seenCat[d.category]=1; uniqCats.push(d.category); } });
  uniqCats.sort();

  var filHtml = '<select id="f-mkt" onchange="applyFilters()"><option value="">市场状态:全部</option><option>正常</option><option>竞争无优势</option><option>无市场</option></select>';
  filHtml += '<select id="f-an" onchange="applyFilters()"><option value="">分析人:全部</option>';
  uniqAnalysts.forEach(function(a) { filHtml += '<option>' + a + '</option>'; });
  filHtml += '</select>';
  filHtml += '<select id="f-cat" onchange="applyFilters()"><option value="">品类:全部</option>';
  uniqCats.forEach(function(c) { filHtml += '<option>' + c + '</option>'; });
  filHtml += '</select>';
  filHtml += '<select id="f-exp" onchange="applyFilters()"><option value="">产品拓展:全部</option><option>原开品</option><option>拓展品</option><option>组合件</option></select>';
  filHtml += '<select id="f-8d" onchange="applyFilters()"><option value="">8日出单:全部</option><option>Y</option><option>N</option><option>未出单</option></select>';
  filHtml += '<select id="f-share" onchange="applyFilters()"><option value="">市占比:全部</option><option value="high">75%及以上</option><option value="mid">50%-75%</option><option value="low">50%以下</option></select>';
  filHtml += '<select id="f-ad" onchange="applyFilters()"><option value="">广告条件:全部</option><option>PLP+PLG同开</option><option>单链接PLP+PLG同开</option><option>单PLG</option><option>单PLP</option><option>单PLG且未出单</option><option>无广告</option></select>';
  filHtml += '<button class="reset-btn" onclick="resetFilters()">重置筛选</button>';
  filHtml += '<span class="count" id="t4-count"></span>';
  document.getElementById('t4-filters').innerHTML = filHtml;

  window.renderT4Table = function(data) {
    var h = '<table class="data-table"><thead><tr><th>SKU</th><th>上架日期</th><th>首次出单</th><th>分析人</th><th>品类</th><th>拓展类型</th><th>本周销量</th><th>本周销售额</th><th>对手量</th><th>市占比</th><th>市场状态</th><th>8日出单</th><th>广告分类</th></tr></thead><tbody>';
    data.forEach(function(d) {
      h += '<tr><td>' + d.SKU + '</td><td>' + d.listDate + '</td><td>' + d.firstOrderDate + '</td>';
      h += '<td>' + d.analyst + '</td><td>' + d.category + '</td><td>' + d.expandType + '</td>';
      h += '<td>' + d.curSalesQty + '</td><td>' + fmtMoney(d.curRevenue) + '</td>';
      h += '<td>' + d.curRivalQty + '</td><td>' + d.curMarketShare + '%</td>';
      h += '<td>' + badgeStatus(d.curMarketStatus) + '</td><td>' + badge8d(d.cur8dStatus) + '</td>';
      h += '<td>' + badgeAdClass(d.adClass) + '</td></tr>';
    });
    h += '</tbody></table>';
    document.getElementById('t4-table').innerHTML = h;
    document.getElementById('t4-count').textContent = '筛选结果:' + data.length + ' / ' + cum43Data.length + ' 条';
  };

  window.applyFilters = function() {
    var data = cum43Data.slice();
    var mkt = document.getElementById('f-mkt').value;
    var an = document.getElementById('f-an').value;
    var cat = document.getElementById('f-cat').value;
    var exp = document.getElementById('f-exp').value;
    var d8 = document.getElementById('f-8d').value;
    var share = document.getElementById('f-share').value;
    var ad = document.getElementById('f-ad').value;
    if (mkt) data = data.filter(function(d) { return d.curMarketStatus === mkt; });
    if (an) data = data.filter(function(d) { return d.analyst === an; });
    if (cat) data = data.filter(function(d) { return d.category === cat; });
    if (exp) data = data.filter(function(d) { return d.expandType === exp; });
    if (d8) data = data.filter(function(d) { return d.cur8dStatus === d8; });
    if (share === 'high') data = data.filter(function(d) { return d.curMarketShare >= 75; });
    else if (share === 'mid') data = data.filter(function(d) { return d.curMarketShare >= 50 && d.curMarketShare < 75; });
    else if (share === 'low') data = data.filter(function(d) { return d.curMarketShare < 50; });
    if (ad) data = data.filter(function(d) { return d.adClass === ad; });
    renderT4Table(data);
  };

  window.resetFilters = function() {
    document.querySelectorAll('#t4-filters select').forEach(function(s) { s.value = ''; });
    renderT4Table(cum43Data);
  };

  renderT4Table(cum43Data);
})();

(function() {
  var cohortHtml = '<table class="data-table pinxiao-table"><thead><tr><th>上架月份</th><th>SKU个数</th>';
  for (var m = 1; m <= 5; m++) cohortHtml += '<th>' + m + '月销售额</th>';
  for (var m = 1; m <= 5; m++) cohortHtml += '<th>' + m + '月品效($/SKU)</th>';
  cohortHtml += '<th>趋势</th></tr></thead><tbody>';

  pinxiaoData.forEach(function(d) {
    cohortHtml += '<tr><td><b>' + d.launchMonth + '月上架</b></td><td>' + d.skuCount + '</td>';
    d.monthlyRevenue.forEach(function(rev) { cohortHtml += '<td>' + fmtMoney(rev) + '</td>'; });
    d.monthlyPinxiao.forEach(function(px) {
      var cls = px >= 500 ? 'px-high' : (px >= 100 ? 'px-mid' : 'px-low');
      cohortHtml += '<td class="' + cls + '">' + (px > 0 ? '$' + px.toFixed(0) : '-') + '</td>';
    });
    var pxVals = d.monthlyPinxiao.filter(function(v) { return v > 0; });
    var trend = '-';
    if (pxVals.length >= 3) {
      if (pxVals[pxVals.length-1] > pxVals[pxVals.length-2] && pxVals[pxVals.length-2] > pxVals[pxVals.length-3]) trend = '<span class="trend-up">攀升</span>';
      else if (pxVals[pxVals.length-1] < pxVals[pxVals.length-2] && pxVals[pxVals.length-2] < pxVals[pxVals.length-3]) trend = '<span class="trend-down">衰减</span>';
      else trend = '<span class="trend-flat">平稳</span>';
    } else if (pxVals.length >= 2) {
      trend = pxVals[pxVals.length-1] > pxVals[pxVals.length-2] ? '<span class="trend-up">攀升</span>' : '<span class="trend-down">衰减</span>';
    }
    cohortHtml += '<td>' + trend + '</td></tr>';
  });
  cohortHtml += '</tbody></table>';
  document.getElementById('t5-cohort').innerHTML = cohortHtml;

  var catPxHtml = '<table class="data-table pinxiao-table"><thead><tr><th>品线</th>';
  launchMonths.forEach(function(m) { catPxHtml += '<th>' + m + '月上架品效</th>'; });
  catPxHtml += '</tr></thead><tbody>';
  pinxiaoCatData.forEach(function(d) {
    catPxHtml += '<tr><td>' + d.category + '</td>';
    d.pinxiao.forEach(function(px) {
      var cls = px >= 500 ? 'px-high' : (px >= 100 ? 'px-mid' : 'px-low');
      catPxHtml += '<td class="' + cls + '">' + (px > 0 ? '$' + px : '-') + '</td>';
    });
    catPxHtml += '</tr>';
  });
  catPxHtml += '</tbody></table>';
  document.getElementById('t5-cat').innerHTML = catPxHtml;

  var expPxHtml = '<table class="data-table pinxiao-table"><thead><tr><th>拓展类型</th>';
  launchMonths.forEach(function(m) { expPxHtml += '<th>' + m + '月上架品效</th>'; });
  expPxHtml += '</tr></thead><tbody>';
  pinxiaoExpData.forEach(function(d) {
    expPxHtml += '<tr><td>' + d.expandType + '</td>';
    d.pinxiao.forEach(function(px) {
      var cls = px >= 500 ? 'px-high' : (px >= 100 ? 'px-mid' : 'px-low');
      expPxHtml += '<td class="' + cls + '">' + (px > 0 ? '$' + px : '-') + '</td>';
    });
    expPxHtml += '</tr>';
  });
  expPxHtml += '</tbody></table>';
  document.getElementById('t5-exp').innerHTML = expPxHtml;
})();

window._charts5Init = false;
function initCharts5() {
  if (window._charts5Init) return;
  window._charts5Init = true;

  var colors = ['#0f3460', '#2980b9', '#8e44ad', '#e07b24', '#08845a'];
  var revDatasets = pinxiaoData.map(function(d, i) {
    return { label: d.launchMonth + '月上架', data: d.monthlyRevenue, borderColor: colors[i], backgroundColor: 'transparent', tension: 0.3 };
  });
  new Chart(document.getElementById('chart-px-rev'), {
    type: 'line', data: { labels: ['1月','2月','3月','4月','5月'], datasets: revDatasets },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });

  var pxDatasets = pinxiaoData.map(function(d, i) {
    return { label: d.launchMonth + '月上架', data: d.monthlyPinxiao, borderColor: colors[i], backgroundColor: 'transparent', tension: 0.3 };
  });
  new Chart(document.getElementById('chart-px-trend'), {
    type: 'line', data: { labels: ['1月','2月','3月','4月','5月'], datasets: pxDatasets },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });
}

(function() {
  var t = cum43Stats;
  var pk = prevWeekKpi;
  var saleRate = t.hasRivalCount ? (t.yCount + t.nCount) / t.hasRivalCount * 100 : 0;
  var timelyRate = parseFloat(timelinessData.total.timelyRate) || 0;

  document.getElementById('t6-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">在售SKU</div><div class="val">' + t.total + '</div></div>' +
    '<div class="kpi-card success"><div class="label">总销量</div><div class="val">' + fmtNum(pk.prevTotalSalesQty) + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">总销售额</div><div class="val">' + fmtMoney(pk.prevTotalRevenue) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">出单率</div><div class="val">' + saleRate.toFixed(1) + '%</div></div>' +
    '<div class="kpi-card success"><div class="label">及时率</div><div class="val">' + timelinessData.total.timelyRate + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">低占比新品</div><div class="val">' + lowShareData.length + '</div></div>';

  var risks = [];
  if (saleRate < 70) risks.push({level:'high', title:'出单率偏低', text:'出单率仅 ' + saleRate.toFixed(1) + '%，低于70%警戒线。有对手未出单新品' + hasCompetitorUnsold.total + '款，需重点排查市场状态和定价策略。'});
  if (unsoldNoCompetitor.total > 15) risks.push({level:'high', title:'无对手未出单新品过多', text:'无对手未出单新品达' + unsoldNoCompetitor.total + '款，占比' + (unsoldNoCompetitor.total/t.total*100).toFixed(1) + '%，需加速市场调研和Listing优化。'});
  if (parseFloat(plpTotal.roas) < 8) risks.push({level:'medium', title:'PLP广告ROAS偏低', text:'PLP广告ROAS为' + plpTotal.roas + '，较上周' + plpPrevTotal.roas + '有所下降，需优化广告投放策略。'});
  if (timelyRate < 50) {
    var worstAn = timelinessData.analysts.reduce(function(a,b){ return parseFloat(a.timelyRate)<parseFloat(b.timelyRate) ? a : b; });
    risks.push({level:'high', title:'分析及时率告急', text: worstAn.analyst + '及时率仅 ' + worstAn.timelyRate + '，严重低于平均水平，需立即完成补充分析。'});
  }
  if (t.competitiveCount > t.normalCount) risks.push({level:'medium', title:'竞争无优势SKU偏多', text:'竞争无优势SKU(' + t.competitiveCount + ')超过正常SKU(' + t.normalCount + ')，需加大差异化卖点挖掘和价格竞争分析。'});
  if (risks.length === 0) risks.push({level:'low', title:'整体平稳', text:'本周各项指标整体平稳，暂无重大风险。'});

  var riskHtml = '';
  risks.forEach(function(r) {
    var cls = r.level === 'high' ? 'risk-high' : (r.level === 'medium' ? 'risk-medium' : 'risk-low');
    riskHtml += '<div class="report-block ' + cls + '"><h4>' + (r.level==='high'?'🔴':(r.level==='medium'?'🟡':'🟢')) + ' ' + r.title + '</h4><pre>' + r.text + '</pre></div>';
  });
  document.getElementById('t6-risk').innerHTML = riskHtml;

  var findings = [
    {title: '新品销售占比 ' + pk.deptRatio, desc: '本周新品销售额占部门总销售额的' + pk.deptRatio + '，部门总销售额' + fmtMoney(pk.deptTotalRevenue) + '，新品贡献销售额' + fmtMoney(pk.prevTotalRevenue) + '。'},
    {title: '出单率 ' + saleRate.toFixed(1) + '%', desc: '有对手新品出单率' + saleRate.toFixed(1) + '%(Y:' + t.yCount + '个 N:' + t.nCount + '个 未出单:' + t.unCount + '个)，整体出单情况良好。'},
    {title: '品效Cohort趋势', desc: pinxiaoData.length + '个上架月份的新品品效跟踪中，需重点关注低品效上架月份的产品优化。'},
    {title: 'PLP广告ACOAS ' + plpTotal.acoas, desc: '本周PLP广告ACOAS为' + plpTotal.acoas + '，花费' + fmtMoney(plpTotal.cost) + '，ROAS ' + plpTotal.roas + '。单链接PLP+PLG同开' + plgStats.singleLinkPlpPlgCount + '个SKU需重点关注。'},
    {title: '低占比新品' + lowShareData.length + '款', desc: '市占比<75%的低占比新品共' + lowShareData.length + '款，占总SKU的' + (lowShareData.length/t.total*100).toFixed(1) + '%，需逐一排查原因。'},
  ];
  var findingsHtml = '';
  findings.forEach(function(f) {
    findingsHtml += '<div class="findings-card"><div class="title">' + f.title + '</div><div class="desc">' + f.desc + '</div></div>';
  });
  document.getElementById('t6-findings').innerHTML = findingsHtml;

  var actions = [
    {title: '低占比新品逐一排查', desc: '对' + lowShareData.length + '款低占比新品逐一分析市场状态，重点关注"竞争无优势"和"无市场"SKU，制定差异化优化方案。'},
    {title: '品效提升专项', desc: '针对低品效上架月份的产品，重点优化标题关键词、主图质量和定价策略，提升每SKU产出。'},
    {title: '单链接PLP+PLG同开SKU优化', desc: '关注' + plgStats.singleLinkPlpPlgCount + '个单链接PLP+PLG同开SKU的广告表现，评估是否需要扩展广告活动数量。'},
    {title: '分析及时率提升', desc: '督促分析及时率偏低的分析师，确保新品8日内完成首次分析，7日内完成低占比追踪分析。'},
    {title: '竞争价格监控', desc: '对有对手但低市占比例的SKU进行竞争价格对比，必要时调整定价或运费策略以提升竞争力。'},
  ];
  var actionsHtml = '';
  actions.forEach(function(a) {
    actionsHtml += '<div class="action-card"><div class="title">' + a.title + '</div><div class="desc">' + a.desc + '</div></div>';
  });
  document.getElementById('t6-actions').innerHTML = actionsHtml;

  var reportSections = [
    {title: '核心指标', text: '【核心指标】\n累计SKU: ' + t.total + ' | 本周销量: ' + fmtNum(pk.prevTotalSalesQty) + ' | 本周销售额: ' + fmtMoney(pk.prevTotalRevenue) + '\n新品销售占比: ' + pk.deptRatio + '(部门总销售额' + fmtMoney(pk.deptTotalRevenue) + ')\n出单率: ' + saleRate.toFixed(1) + '%(Y:' + t.yCount + ' N:' + t.nCount + ' 未:' + t.unCount + ')\n及时率: ' + timelinessData.total.timelyRate},
    {title: '风险预警', text: '【风险预警】\n' + risks.map(function(r){ return '[' + r.level.toUpperCase() + '] ' + r.title + ': ' + r.text; }).join('\n')},
    {title: '主要发现', text: '【本周主要发现】\n' + findings.map(function(f){ return '- ' + f.title + ': ' + f.desc; }).join('\n')},
    {title: '品类维度', text: '【品类维度】\n' + categoryRevenueData.map(function(d){ return d.category + ': ' + d.curSku + 'SKU, 销量' + d.curSalesQty + ', 销售额' + fmtMoney(d.curRevenue) + ', 环比' + d.salesQtyChange; }).join('\n')},
    {title: '下周动作', text: '【下周重点动作】\n' + actions.map(function(a, i){ return (i+1) + '. ' + a.title + ': ' + a.desc; }).join('\n')},
  ];
  var reportHtml = '';
  reportSections.forEach(function(sec) {
    reportHtml += '<div class="report-block"><h4>' + sec.title + '</h4><pre>' + sec.text + '</pre><button class="copy-btn" onclick="copyReport(this)">复制</button></div>';
  });
  document.getElementById('t6-report').innerHTML = reportHtml;
})();

function copyReport(btn) {
  var pre = btn.parentElement.querySelector('pre');
  navigator.clipboard.writeText(pre.textContent).then(function() {
    btn.textContent = '已复制';
    setTimeout(function() { btn.textContent = '复制'; }, 1500);
  });
}
'''

full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报看板 5.14-5.20 v2</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
{CSS}
</head>
<body>
{HTML_BODY}
<script>
{js_vars_block}

{JS_CODE}
</script>
</body>
</html>'''

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"HTML已保存到: {OUTPUT_FILE}")
print(f"文件大小: {len(full_html)} 字符")
print("完成！")
