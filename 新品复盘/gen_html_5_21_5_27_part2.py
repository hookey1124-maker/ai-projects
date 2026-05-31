
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
  if (v === '站外出单') return badge('站外出单', 'badge-purple');
  if (v === '站内无价格优势') return badge('无价优', 'badge-orange');
  if (v === '未知') return badge('未知', 'badge-gray');
  if (v === '其他') return badge('其他', 'badge-gray');
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
}

// ========== Tab1: 总盘概览 ==========
(function() {
  var t = cum43Stats;
  var pk = prevWeekKpi;
  var saleRate = t.hasRivalCount ? (t.yCount + t.nCount) / t.hasRivalCount * 100 : 0;
  var totalShare = t.totalMarketShare;
  var totalSharePrev = t.totalMarketSharePrev;
  var shareChange = totalSharePrev ? ((totalShare - totalSharePrev) / totalSharePrev * 100).toFixed(1) : 0;
  var shareChangeStr = shareChange >= 0 ? '+' + shareChange + '%' : shareChange + '%';

  document.getElementById('t1-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">累计SKU数</div><div class="val">' + t.total + '</div><div class="hb">' + hbSign(pk.skuChange) + ' 上周' + pk.prevTotalSku + '</div></div>' +
    '<div class="kpi-card success"><div class="label">本品总销量</div><div class="val">' + fmtNum(pk.prevTotalSalesQty) + '</div><div class="hb">' + hbSign(pk.salesQtyChange) + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">总销售额</div><div class="val">' + fmtMoney(pk.prevTotalRevenue) + '</div><div class="hb">' + hbSign(pk.revenueChange) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品总市占比</div><div class="val">' + totalShare + '%</div><div class="hb">' + hbSign(shareChangeStr) + ' 上周' + totalSharePrev + '%</div></div>' +
    '<div class="kpi-card success"><div class="label">出单率(有对手)</div><div class="val">' + saleRate.toFixed(1) + '%</div><div class="hb">Y:' + t.yCount + ' N:' + t.nCount + ' 未:' + t.unCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">分析及时率</div><div class="val">' + timelinessData.total.timelyRate + '</div><div class="hb">' + hbSign(timelinessData.total.change) + '</div></div>';

  // 出单情况表（4段：有对手已出单/有对手未出单/无对手已出单/无对手未出单）
  var ordHtml = '<table class="data-table"><thead><tr><th>分类</th><th>数量</th><th>说明</th></tr></thead><tbody>' +
    '<tr style="background:#e8f5e9"><td>有对手已出单(Y+N)</td><td>' + (t.yCount + t.nCount) + '</td><td>有竞品但有出单，占有对手SKU的' + saleRate.toFixed(1) + '%</td></tr>' +
    '<tr style="background:#fff3e0"><td>有对手未出单</td><td>' + t.unCount + '</td><td>有竞品且未出单，需重点关注</td></tr>' +
    '<tr style="background:#e3f2fd"><td>无对手已出单</td><td>' + t.noRivalSold + '</td><td>无竞品已出单，市场独占</td></tr>' +
    '<tr style="background:#ffebee"><td>无对手未出单</td><td>' + t.noRivalUnsold + '</td><td>无竞品也未出单，需关注选品</td></tr>' +
    '<tr class="total-row"><td>合计</td><td>' + t.total + '</td><td>有对手' + t.hasRivalCount + '个 + 无对手' + t.noRivalCount + '个</td></tr>' +
    '</tbody></table>';
  document.getElementById('t1-ord8').innerHTML = ordHtml;

  // 品线维度表（含市占比）
  var catHtml = '<table class="data-table"><thead><tr><th>品线</th><th>SKU</th><th>新上架</th><th>销量</th><th>销量环比</th><th>销售额</th><th>销售额环比</th><th>市占比</th><th>市占环比</th></tr></thead><tbody>';
  categoryRevenueData.forEach(function(d) {
    catHtml += '<tr><td>' + d.category + '</td><td>' + d.curSku + '</td><td>' + d.curNewSku + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td><td>' + d.curMarketShare + '%</td><td>' + hbSign(d.marketShareChange) + '</td></tr>';
  });
  catHtml += '</tbody></table>';
  document.getElementById('t1-cat-table').innerHTML = catHtml;

  // 分析人维度表（含市占比）
  var anHtml = '<table class="data-table"><thead><tr><th>分析人</th><th>SKU</th><th>新上架</th><th>销量</th><th>销量环比</th><th>销售额</th><th>销售额环比</th><th>市占比</th><th>市占环比</th></tr></thead><tbody>';
  analystRevenueData.forEach(function(d) {
    anHtml += '<tr><td>' + d.analyst + '</td><td>' + d.curSku + '</td><td>' + d.curNewSku + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td><td>' + d.curMarketShare + '%</td><td>' + hbSign(d.marketShareChange) + '</td></tr>';
  });
  anHtml += '</tbody></table>';
  document.getElementById('t1-an-table').innerHTML = anHtml;

  // 拓展类型
  var expHtml = '<table class="data-table"><thead><tr><th>拓展类型</th><th>本周SKU</th><th>上周SKU</th><th>出单SKU</th><th>出单率</th><th>上周出单率</th><th>本周销量</th><th>上周销量</th><th>销量环比</th><th>本周销售额</th><th>上周销售额</th><th>销售额环比</th></tr></thead><tbody>';
  expandTypeData.forEach(function(d) {
    expHtml += '<tr><td>' + d.expandType + '</td><td>' + d.curSku + '</td><td>' + d.prevSku + '</td><td>' + d.curSalesSku + '</td><td>' + d.curSalesRate + '</td><td>' + d.prevSalesRate + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + fmtNum(d.prevSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + fmtMoney(d.prevRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td></tr>';
  });
  expHtml += '</tbody></table>';
  document.getElementById('t1-exp-table').innerHTML = expHtml;

  // 及时率
  var timeHtml = '<table class="data-table"><thead><tr><th>分析人</th><th>本周SKU</th><th>及时分析</th><th>8日未分析</th><th>7日未分析</th><th>及时率</th><th>上周及时率</th><th>变化</th></tr></thead><tbody>';
  timelinessData.analysts.forEach(function(d) {
    timeHtml += '<tr><td>' + d.analyst + '</td><td>' + d.curSku + '</td><td>' + d.timelyCount + '</td><td>' + d.noAnalysis8dCount + '</td><td>' + d.noAnalysis7dCount + '</td><td>' + d.timelyRate + '</td><td>' + d.prevTimelyRate + '</td><td>' + hbSign(d.change) + '</td></tr>';
  });
  var td = timelinessData.total;
  timeHtml += '<tr class="total-row"><td>' + td.analyst + '</td><td>' + td.curSku + '</td><td>' + td.timelyCount + '</td><td>' + td.noAnalysis8dCount + '</td><td>' + td.noAnalysis7dCount + '</td><td>' + td.timelyRate + '</td><td>' + td.prevTimelyRate + '</td><td>' + hbSign(td.change) + '</td></tr>';
  timeHtml += '</tbody></table>';
  document.getElementById('t1-time-table').innerHTML = timeHtml;
})();

// ========== Tab1 图表（懒初始化）==========
window._charts1Init = false;
function initCharts1() {
  if (window._charts1Init) return;
  window._charts1Init = true;
  var t = cum43Stats;

  // 1. 出单分布甜甜圈（4段）
  new Chart(document.getElementById('chart-ord8'), {
    type: 'doughnut',
    data: {
      labels: ['有对手已出单', '有对手未出单', '无对手已出单', '无对手未出单'],
      datasets: [{ data: [t.yCount + t.nCount, t.unCount, t.noRivalSold, t.noRivalUnsold], backgroundColor: ['#08845a', '#e07b24', '#2980b9', '#c0392b'] }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' }, tooltip: { callbacks: { label: function(ctx) { return ctx.label + ': ' + ctx.parsed + '个 (' + (ctx.parsed/t.total*100).toFixed(1) + '%)'; } } } } }
  });

  // 2. 新品总市占比（环比柱状图）
  var totalShareCurr = t.totalMarketShare;
  var totalSharePrev = t.totalMarketSharePrev;
  new Chart(document.getElementById('chart-total-share'), {
    type: 'bar',
    data: { labels: ['本周(5.27)', '上周(5.20)'], datasets: [
      { label: '新品总市占比(%)', data: [totalShareCurr, totalSharePrev], backgroundColor: ['#0f3460', '#ccc'] }
    ]},
    options: { responsive: true, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx) { return ctx.parsed + '%'; } } } }, scales: { y: { beginAtZero: true, max: 100 } } }
  });

  // 3. 品线市占比对比
  var catLabels = categoryRevenueData.map(function(d) { return d.category; });
  new Chart(document.getElementById('chart-cat-share'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周市占比(%)', data: categoryRevenueData.map(function(d){return d.curMarketShare;}), backgroundColor: '#0f3460' },
      { label: '上周市占比(%)', data: categoryRevenueData.map(function(d){return d.prevMarketShare;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, max: 100 } } }
  });

  // 4. 分析人市占比对比
  var anLabels = analystRevenueData.map(function(d) { return d.analyst; });
  new Chart(document.getElementById('chart-an-share'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周市占比(%)', data: analystRevenueData.map(function(d){return d.curMarketShare;}), backgroundColor: '#8e44ad' },
      { label: '上周市占比(%)', data: analystRevenueData.map(function(d){return d.prevMarketShare;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, max: 100 } } }
  });

  // 5. 品线销量对比
  new Chart(document.getElementById('chart-cat-sales'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销量', data: categoryRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460' },
      { label: '上周销量', data: categoryRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });

  // 6. 分析人销量对比
  new Chart(document.getElementById('chart-an-sales'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销量', data: analystRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460' },
      { label: '上周销量', data: analystRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });

  // 7. 品线销售额对比
  new Chart(document.getElementById('chart-cat-rev'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销售额($)', data: categoryRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad' },
      { label: '上周销售额($)', data: categoryRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });

  // 8. 分析人销售额对比
  new Chart(document.getElementById('chart-an-rev'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销售额($)', data: analystRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad' },
      { label: '上周销售额($)', data: analystRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });
}
setTimeout(initCharts1, 100);

// ========== Tab2: 低占比分析 ==========
(function() {
  var hcu = hasCompetitorUnsold;
  var unc = unsoldNoCompetitor;
  var t = cum43Stats;

  document.getElementById('t2-kpi').innerHTML =
    '<div class="kpi-card warning"><div class="label">有对手未出单</div><div class="val">' + hcu.total + '</div><div class="hb">上周 ' + hcu.prevTotal + ' | ' + (hcu.change >= 0 ? '+' : '') + hcu.change + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">无对手未出单</div><div class="val">' + unc.total + '</div><div class="hb">上周 ' + unc.prevTotal + ' | ' + (unc.change >= 0 ? '+' : '') + unc.change + '</div></div>' +
    '<div class="kpi-card info"><div class="label">有对手SKU总数</div><div class="val">' + t.hasRivalCount + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">有对手未出单占比</div><div class="val">' + (t.unCount/t.total*100).toFixed(1) + '%</div><div class="hb">' + t.unCount + ' / ' + t.total + '</div></div>';

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

  // 低占比筛选栏
  var ls8dOpts = ['', 'Y', 'N', '未出单'];
  var ls8dNames = ['全部', 'Y', 'N', '未出单'];
  var lsOpVals = {};
  lowShareData.forEach(function(d) { var v = d.curOperation || '-'; lsOpVals[v] = 1; });
  var lsOpKeys = Object.keys(lsOpVals).sort();
  var lsAdVals = {};
  lowShareData.forEach(function(d) { lsAdVals[d.adClass] = 1; });
  var lsAdKeys = Object.keys(lsAdVals).sort();

  window.toggleLsOpDropdown = function() {
    var dd = document.getElementById('ls-op-drop');
    dd.style.display = dd.style.display === 'none' ? 'block' : 'none';
  };
  document.addEventListener('click', function(e) {
    var dd = document.getElementById('ls-op-drop');
    var lbl = document.getElementById('ls-op-label');
    if (dd && lbl && !lbl.contains(e.target) && !dd.contains(e.target)) {
      dd.style.display = 'none';
    }
  });

  var lsFilHtml = '<span class="fg"><label>8日出单</label><select id="ls-f-8d" onchange="renderLowShareTable()">';
  for (var i = 0; i < ls8dOpts.length; i++) lsFilHtml += '<option value="' + ls8dOpts[i] + '">' + ls8dNames[i] + '</option>';
  lsFilHtml += '</select></span>';
  lsFilHtml += '<span class="fg" style="position:relative">';
  lsFilHtml += '<label id="ls-op-label" style="cursor:pointer" onclick="toggleLsOpDropdown()">本期运作判断 &#9662;</label>';
  lsFilHtml += '<div id="ls-op-drop" style="display:none;position:absolute;top:100%;left:0;z-index:200;background:#fff;border:1px solid #ddd;border-radius:6px;padding:6px 0;max-height:220px;overflow-y:auto;min-width:150px;box-shadow:0 4px 12px rgba(0,0,0,0.12);">';
  lsFilHtml += '<label style="display:block;padding:4px 12px;font-size:12px;cursor:pointer;white-space:nowrap;"><input type="checkbox" id="ls-op-all" onchange="var c=this.checked;var boxes=document.querySelectorAll(&quot;.ls-op-cb&quot;);boxes.forEach(function(b){b.checked=c;});renderLowShareTable();" checked> <b>全选</b></label>';
  lsFilHtml += '<hr style="margin:4px 0;border-color:#eee">';
  lsOpKeys.forEach(function(v) {
    lsFilHtml += '<label style="display:block;padding:4px 12px;font-size:12px;cursor:pointer;white-space:nowrap;"><input type="checkbox" class="ls-op-cb" value="' + v + '" onchange="renderLowShareTable()" checked> ' + v + '</label>';
  });
  lsFilHtml += '</div></span>';
  lsFilHtml += '<span class="fg"><label>广告分类</label><select id="ls-f-ad" onchange="renderLowShareTable()"><option value="">全部</option>';
  lsAdKeys.forEach(function(v) { lsFilHtml += '<option value="' + v + '">' + v + '</option>'; });
  lsFilHtml += '</select></span>';
  lsFilHtml += '<button class="reset-btn" onclick="resetLowShareFilters()">重置筛选</button>';
  lsFilHtml += '<span class="count" id="t2-ls-count"></span>';
  document.getElementById('t2-lowshare-filters').innerHTML = lsFilHtml;

  window.resetLowShareFilters = function() {
    document.getElementById("ls-f-8d").value = "";
    document.querySelectorAll(".ls-op-cb").forEach(function(b) { b.checked = true; });
    document.getElementById("ls-op-all").checked = true;
    document.getElementById("ls-f-ad").value = "";
    window.renderLowShareTable();
  };

  window.renderLowShareTable = function() {
    var f8d = document.getElementById('ls-f-8d').value;
    var fOpChecked = document.querySelectorAll('.ls-op-cb:checked');
    var fOpAll = fOpChecked.length === document.querySelectorAll('.ls-op-cb').length;
    var fAd = document.getElementById('ls-f-ad').value;
    var filtered = lowShareData.filter(function(d) {
      if (f8d && d.cur8dStatus !== f8d) return false;
      if (!fOpAll && !Array.from(fOpChecked).some(function(cb) { return cb.value === (d.curOperation || '-'); })) return false;
      if (fAd && d.adClass !== fAd) return false;
      return true;
    });
    var lsTotalSales = 0, lsTotalRev = 0;
    var h = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>SKU</th><th>上架日期</th><th>分析人</th><th>品类</th><th>本周销量</th><th>销量环比</th><th>本周销售额</th><th>对手量</th><th>市占比</th><th>8日出单</th><th>上期市场状态</th><th>本期运作判断</th><th>本期市场状态</th><th>广告分类</th></tr></thead><tbody>';
    filtered.forEach(function(d) {
      h += '<tr><td>' + d.SKU + '</td><td>' + d.launchDate + '</td><td>' + d.analyst + '</td><td>' + d.category + '</td>';
      h += '<td>' + d.curSalesQty + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td>';
      h += '<td>' + d.curRivalQty + '</td><td>' + d.curMarketShare + '%</td>';
      h += '<td>' + badge8d(d.cur8dStatus) + '</td>';
      h += '<td>' + badgeStatus(d.prevMarketStatus) + '</td><td>' + (d.curOperation || '-') + '</td><td>' + badgeStatus(d.curMarketStatus) + '</td>';
      h += '<td>' + badgeAdClass(d.adClass) + '</td></tr>';
      lsTotalSales += d.curSalesQty;
      lsTotalRev += (d.curRevenue || 0);
    });
    h += '</tbody><tfoot><tr><td colspan="2">合计（' + filtered.length + '条）</td><td></td><td></td><td>' + lsTotalSales + '</td><td></td><td>' + fmtMoney(lsTotalRev) + '</td><td colspan="7"></td></tr></tfoot></table></div>';
    document.getElementById('t2-lowshare-table').innerHTML = h;
    document.getElementById('t2-ls-count').textContent = '筛选结果:' + filtered.length + ' / ' + lowShareData.length + ' 条';
  };
  renderLowShareTable();
})();

// ========== Tab3: 广告追踪（PLP + PLG 自然周）==========
(function() {
  var pt = plpTotal;
  var pp = plpPrevTotal;

  // PLP KPI
  document.getElementById('t3-plp-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">广告活动数</div><div class="val">' + pt.campaignCount + '</div><div class="hb">上周 ' + pp.campaignCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">投放链接数</div><div class="val">' + pt.linkCount + '</div><div class="hb">上周 ' + pp.linkCount + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">曝光量</div><div class="val">' + fmtNum(pt.impression) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">点击量</div><div class="val">' + fmtNum(pt.click) + '</div></div>' +
    '<div class="kpi-card success"><div class="label">售出数</div><div class="val">' + pt.sold + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">广告销售额</div><div class="val">' + fmtMoney(pt.revenue) + '</div></div>';

  // PLP 核心指标
  document.getElementById('t3-plp-core').innerHTML =
    '<div class="kpi-card primary"><div class="label">ROAS</div><div class="val">' + pt.roas + '</div><div class="hb">上周 ' + pp.roas + '</div></div>' +
    '<div class="kpi-card info"><div class="label">CVR</div><div class="val">' + pt.cvr + '</div><div class="hb">上周 ' + pp.cvr + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">CTR</div><div class="val">' + pt.ctr + '</div><div class="hb">上周 ' + pp.ctr + '</div></div>' +
    '<div class="kpi-card info"><div class="label">CPC</div><div class="val">' + pt.cpc + '</div><div class="hb">上周 ' + pp.cpc + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">CPA</div><div class="val">' + pt.cpa + '</div><div class="hb">上周 ' + pp.cpa + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">ACOS</div><div class="val">' + pt.acos + '</div><div class="hb">上周 ' + pp.acos + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">ACOAS（去重）</div><div class="val">' + pt.acoas + '</div><div class="hb">上周 ' + pp.acoas + '</div></div>';

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

  // PLG KPI 卡片（含花费、广告销售额、ACOS、ACOAS）
  var pg = plgStats;
  document.getElementById('t3-plg-kpi').innerHTML =
    '<div class="kpi-card purple"><div class="label">PLG广告花费</div><div class="val">' + fmtMoney(pg.totalSpend) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">PLG广告销售额</div><div class="val">' + fmtMoney(pg.totalAdRev) + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">PLG自然周总销售额</div><div class="val">' + fmtMoney(pg.totalNatRev) + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">PLG ACOS</div><div class="val">' + pg.acos + '</div><div class="hb">花费/广告销售额</div></div>' +
    '<div class="kpi-card warning"><div class="label">PLG ACOAS</div><div class="val">' + pg.acoas + '</div><div class="hb">花费/自然周总销售额</div></div>';

  // PLG 费率分布
  var plgHtml = '<div class="kpi-grid" style="margin-bottom:12px">';
  plgHtml += '<div class="kpi-card primary"><div class="label">新品总数</div><div class="val">' + pg.totalNewProducts + '</div></div>';
  plgHtml += '<div class="kpi-card purple"><div class="label">PLP+PLG同开</div><div class="val">' + pg.plpAndPlgBothCount + '</div></div>';
  plgHtml += '<div class="kpi-card danger"><div class="label">单链接PLP+PLG同开</div><div class="val">' + pg.singleLinkPlpPlgCount + '</div></div>';
  plgHtml += '<div class="kpi-card info"><div class="label">单PLG</div><div class="val">' + pg.plgOnlyCount + '</div></div>';
  plgHtml += '<div class="kpi-card primary"><div class="label">单PLP</div><div class="val">' + pg.plpOnlyCount + '</div></div>';
  plgHtml += '<div class="kpi-card warning"><div class="label">无广告</div><div class="val">' + pg.noAdCount + '</div></div>';
  plgHtml += '<div class="kpi-card danger"><div class="label">单PLG且未出单</div><div class="val">' + (pg.plpDisabledNoSaleCount || 0) + '</div></div>';
  plgHtml += '</div>';
  plgHtml += '<table class="data-table"><thead><tr><th>分析人</th><th>总数</th><th>PLP+PLG</th><th>单链接PLP+PLG</th><th>单PLG</th><th>单PLP</th><th>无广告</th><th>PLP未开未出单</th></tr></thead><tbody>';
  pg.byAnalyst.forEach(function(d) {
    plgHtml += '<tr><td>' + d.analyst + '</td><td>' + d.total + '</td>';
    plgHtml += '<td>' + d.plpAndPlgBoth + '</td>';
    plgHtml += '<td style="color:#c0392b;font-weight:600">' + d.singleLinkPlpPlg + '</td>';
    plgHtml += '<td>' + d.plgOnly + '</td><td>' + d.plpOnly + '</td><td>' + d.noAd + '</td>';
    plgHtml += '<td style="color:#c0392b;font-weight:600">' + d.plpDisabledNoSale + '</td></tr>';
  });
  plgHtml += '</tbody></table>';
  document.getElementById('t3-plg').innerHTML = plgHtml;

  // PLG 按分析人（含花费/ACOS/ACOAS）
  var plgAnHtml = '<table class="data-table"><thead><tr><th>分析人</th><th>SKU数</th><th>PLG花费</th><th>PLG广告销售额</th><th>自然周销售额</th><th>PLG ACOS</th><th>PLG ACOAS</th></tr></thead><tbody>';
  pg.byAnalyst.forEach(function(d) {
    plgAnHtml += '<tr><td>' + d.analyst + '</td><td>' + d.total + '</td><td>' + fmtMoney(d.plgSpend) + '</td><td>' + fmtMoney(d.plgAdRev) + '</td><td>' + fmtMoney(d.plgNatRev) + '</td><td>' + d.acos + '</td><td>' + d.acoas + '</td></tr>';
  });
  plgAnHtml += '<tr class="total-row"><td>合计</td><td>' + pg.totalNewProducts + '</td><td>' + fmtMoney(pg.totalSpend) + '</td><td>' + fmtMoney(pg.totalAdRev) + '</td><td>' + fmtMoney(pg.totalNatRev) + '</td><td>' + pg.acos + '</td><td>' + pg.acoas + '</td></tr>';
  plgAnHtml += '</tbody></table>';
  document.getElementById('t3-plg-an').innerHTML = plgAnHtml;

  // PLP 广告明细
  var detHtml = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>SKU</th><th>广告活动</th><th>分析人</th><th>品类</th><th>曝光</th><th>点击</th><th>售出</th><th>花费</th><th>广告销售额</th><th>总销售额</th><th>ROAS</th><th>ACOS</th><th>ACOAS</th><th>广告分类</th></tr></thead><tbody>';
  var detTotalImpr=0, detTotalClick=0, detTotalSold=0, detTotalCost=0, detTotalAdRev=0, detTotalRev=0;
  plpDetailData.forEach(function(d) {
    detHtml += '<tr><td>' + d.SKU + '</td><td>' + d.campaign + '</td><td>' + d.analyst + '</td><td>' + d.category + '</td>';
    detHtml += '<td>' + fmtNum(d.impressions) + '</td><td>' + fmtNum(d.clicks) + '</td><td>' + d.salesQty + '</td>';
    detHtml += '<td>' + fmtMoney(d.spend) + '</td><td>' + fmtMoney(d.adRevenue) + '</td><td>' + fmtMoney(d.totalRevenue) + '</td>';
    detHtml += '<td>' + (d.roas ? d.roas.toFixed(2) : '-') + '</td>';
    detHtml += '<td>' + (d.acos ? (d.acos*100).toFixed(2)+'%' : '0%') + '</td>';
    detHtml += '<td>' + acoasPct(d.acoas) + '</td>';
    detHtml += '<td>' + badgeAdClass(d.adClass) + '</td></tr>';
    detTotalImpr += (d.impressions || 0); detTotalClick += (d.clicks || 0); detTotalSold += (d.salesQty || 0);
    detTotalCost += (d.spend || 0); detTotalAdRev += (d.adRevenue || 0); detTotalRev += (d.totalRevenue || 0);
  });
  detHtml += '</tbody><tfoot><tr><td colspan="2">合计（' + plpDetailData.length + '条）</td><td></td><td></td><td>' + fmtNum(detTotalImpr) + '</td><td>' + fmtNum(detTotalClick) + '</td><td>' + detTotalSold + '</td><td>' + fmtMoney(detTotalCost) + '</td><td>' + fmtMoney(detTotalAdRev) + '</td><td>' + fmtMoney(detTotalRev) + '</td><td></td><td></td><td></td><td></td></tr></tfoot></table></div>';
  document.getElementById('t3-plp-detail').innerHTML = detHtml;
})();

// ========== Tab4: 四三累计 ==========
(function() {
  var t = cum43Stats;
  document.getElementById('t4-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">累计总SKU</div><div class="val">' + t.total + '</div></div>' +
    '<div class="kpi-card success"><div class="label">已出单(Y+N)</div><div class="val">' + (t.yCount + t.nCount) + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">有对手未出单</div><div class="val">' + t.unCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">市场正常</div><div class="val">' + t.normalCount + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">竞争无优势</div><div class="val">' + t.competitiveCount + '</div></div>' +
    '<div class="kpi-card danger"><div class="label">无市场</div><div class="val">' + t.noMarketCount + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">站外出单</div><div class="val">' + (t.stationOutCount || 0) + '</div></div>';

  var uniqAnalysts = [];
  var seenAn = {};
  cum43Data.forEach(function(d) { if (!seenAn[d.analyst]) { seenAn[d.analyst]=1; uniqAnalysts.push(d.analyst); } });
  uniqAnalysts.sort();
  var uniqCats = [];
  var seenCat = {};
  cum43Data.forEach(function(d) { if (!seenCat[d.category]) { seenCat[d.category]=1; uniqCats.push(d.category); } });
  uniqCats.sort();

  var filHtml = '<span class="fg"><label>市场状态</label><select id="f-mkt" onchange="applyFilters()"><option value="">全部</option><option>正常</option><option>竞争无优势</option><option>无市场</option></select></span>';
  filHtml += '<span class="fg"><label>分析人</label><select id="f-an" onchange="applyFilters()"><option value="">全部</option>';
  uniqAnalysts.forEach(function(a) { filHtml += '<option>' + a + '</option>'; });
  filHtml += '</select></span>';
  filHtml += '<span class="fg"><label>品类</label><select id="f-cat" onchange="applyFilters()"><option value="">全部</option>';
  uniqCats.forEach(function(c) { filHtml += '<option>' + c + '</option>'; });
  filHtml += '</select></span>';
  filHtml += '<span class="fg"><label>拓展类型</label><select id="f-exp" onchange="applyFilters()"><option value="">全部</option><option>原开品</option><option>拓展品</option><option>组合件</option></select></span>';
  filHtml += '<span class="fg"><label>8日出单</label><select id="f-8d" onchange="applyFilters()"><option value="">全部</option><option>Y</option><option>N</option><option>未出单</option></select></span>';
  filHtml += '<span class="fg"><label>市占比</label><select id="f-share" onchange="applyFilters()"><option value="">全部</option><option value="high">75%及以上</option><option value="mid">50%-75%</option><option value="low">50%以下</option></select></span>';
  filHtml += '<span class="fg"><label>广告条件</label><select id="f-ad" onchange="applyFilters()"><option value="">全部</option><option>PLP+PLG同开</option><option>单链接PLP+PLG同开</option><option>单PLG</option><option>单PLP</option><option>单PLG且未出单</option><option>无广告</option></select></span>';
  filHtml += '<button class="reset-btn" onclick="resetFilters()">重置筛选</button>';
  filHtml += '<span class="count" id="t4-count"></span>';
  document.getElementById('t4-filters').innerHTML = filHtml;

  window.renderT4Table = function(data) {
    var t4TotalSales=0, t4TotalRev=0, t4TotalRival=0;
    var h = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>SKU</th><th>上架日期</th><th>首次出单</th><th>分析人</th><th>品类</th><th>拓展类型</th><th>本周销量</th><th>本周销售额</th><th>对手量</th><th>市占比</th><th>PLG费率</th><th>市场状态</th><th>8日出单</th><th>广告分类</th></tr></thead><tbody>';
    data.forEach(function(d) {
      h += '<tr><td>' + d.SKU + '</td><td>' + d.listDate + '</td><td>' + d.firstOrderDate + '</td>';
      h += '<td>' + d.analyst + '</td><td>' + d.category + '</td><td>' + d.expandType + '</td>';
      h += '<td>' + d.curSalesQty + '</td><td>' + fmtMoney(d.curRevenue) + '</td>';
      h += '<td>' + d.curRivalQty + '</td><td>' + d.curMarketShare + '%</td>';
      h += '<td>' + (d.plgFee || '0%') + '</td>';
      h += '<td>' + badgeStatus(d.curMarketStatus) + '</td><td>' + badge8d(d.cur8dStatus) + '</td>';
      h += '<td>' + badgeAdClass(d.adClass) + '</td></tr>';
      t4TotalSales += d.curSalesQty; t4TotalRev += (d.curRevenue || 0); t4TotalRival += d.curRivalQty;
    });
    h += '</tbody><tfoot><tr><td colspan="2">合计（' + data.length + '条）</td><td></td><td></td><td></td><td></td><td>' + t4TotalSales + '</td><td>' + fmtMoney(t4TotalRev) + '</td><td>' + t4TotalRival + '</td><td colspan="5"></td></tr></tfoot></table></div>';
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

// ========== Tab5: 汇报输出 ==========
(function() {
  var t = cum43Stats;
  var pk = prevWeekKpi;
  var saleRate = t.hasRivalCount ? (t.yCount + t.nCount) / t.hasRivalCount * 100 : 0;
  var timelyRate = parseFloat(timelinessData.total.timelyRate) || 0;

  document.getElementById('t5-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">在售SKU</div><div class="val">' + t.total + '</div></div>' +
    '<div class="kpi-card success"><div class="label">总销量</div><div class="val">' + fmtNum(pk.prevTotalSalesQty) + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">总销售额</div><div class="val">' + fmtMoney(pk.prevTotalRevenue) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品总市占比</div><div class="val">' + pk.totalMarketShare + '</div></div>' +
    '<div class="kpi-card success"><div class="label">出单率(有对手)</div><div class="val">' + saleRate.toFixed(1) + '%</div></div>' +
    '<div class="kpi-card info"><div class="label">及时率</div><div class="val">' + timelinessData.total.timelyRate + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">低占比新品</div><div class="val">' + lowShareData.length + '</div></div>';

  // 风险预警
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
  document.getElementById('t5-risk').innerHTML = riskHtml;

  // 主要发现
  var findings = [
    {title: '新品总市占比 ' + pk.totalMarketShare, desc: '本周新品总市占比为' + pk.totalMarketShare + '（新品销量占总销量的比例），上周为' + pk.totalMarketSharePrev + '，环比' + hbSign(pk.marketShareChange) + '。新品贡献销售额' + fmtMoney(pk.prevTotalRevenue) + '。'},
    {title: '出单率 ' + saleRate.toFixed(1) + '%', desc: '有对手新品出单率' + saleRate.toFixed(1) + '%(Y:' + t.yCount + '个 N:' + t.nCount + '个 未出单:' + t.unCount + '个)，无对手已出单' + t.noRivalSold + '个，无对手未出单' + t.noRivalUnsold + '个。'},
    {title: 'PLP广告ACOAS ' + plpTotal.acoas, desc: '自然周5.18-5.24 PLP广告ACOAS为' + plpTotal.acoas + '，花费' + fmtMoney(plpTotal.cost) + '，ROAS ' + plpTotal.roas + '。单链接PLP+PLG同开' + plgStats.singleLinkPlpPlgCount + '个SKU需重点关注。'},
    {title: 'PLG广告数据', desc: '自然周PLG花费' + fmtMoney(plgStats.totalSpend) + '，广告销售额' + fmtMoney(plgStats.totalAdRev) + '，ACOS ' + plgStats.acos + '，ACOAS ' + plgStats.acoas + '。'},
    {title: '低占比新品' + lowShareData.length + '款', desc: '市占比<75%的低占比新品共' + lowShareData.length + '款，占总SKU的' + (lowShareData.length/t.total*100).toFixed(1) + '%，需逐一排查原因。'},
  ];
  var findingsHtml = '';
  findings.forEach(function(f) {
    findingsHtml += '<div class="findings-card"><div class="title">' + f.title + '</div><div class="desc">' + f.desc + '</div></div>';
  });
  document.getElementById('t5-findings').innerHTML = findingsHtml;

  // 下周动作
  var actions = [
    {title: '低占比新品逐一排查', desc: '对' + lowShareData.length + '款低占比新品逐一分析市场状态，重点关注"竞争无优势"和"无市场"SKU，制定差异化优化方案。'},
    {title: '市占比提升专项', desc: '本周新品总市占比' + pk.totalMarketShare + '，重点对市占比偏低的品线和分析人SKU进行优化，提升整体市场占有率。'},
    {title: '单链接PLP+PLG同开SKU优化', desc: '关注' + plgStats.singleLinkPlpPlgCount + '个单链接PLP+PLG同开SKU的广告表现，评估是否需要扩展广告活动数量。'},
    {title: '分析及时率提升', desc: '督促分析及时率偏低的分析师，确保新品8日内完成首次分析，7日内完成低占比追踪分析。'},
    {title: 'PLG广告ROI优化', desc: 'PLG广告ACOS为' + plgStats.acos + '，ACOAS为' + plgStats.acoas + '，持续监控PLG投放效果，优化花费结构。'},
  ];
  var actionsHtml = '';
  actions.forEach(function(a) {
    actionsHtml += '<div class="action-card"><div class="title">' + a.title + '</div><div class="desc">' + a.desc + '</div></div>';
  });
  document.getElementById('t5-actions').innerHTML = actionsHtml;

  // 可复制周报文案
  var reportSections = [
    {title: '一、总盘概览', text: '【核心KPI】\n' +
      '累计SKU: ' + t.total + ' | 本品总销量: ' + fmtNum(pk.prevTotalSalesQty) + ' | 总销售额: ' + fmtMoney(pk.prevTotalRevenue) + '\n' +
      '新品总市占比: ' + pk.totalMarketShare + '（上周' + pk.totalMarketSharePrev + '，环比' + pk.marketShareChange + '）\n' +
      '出单率(有对手): ' + saleRate.toFixed(1) + '%（Y:' + t.yCount + '/ N:' + t.nCount + '/ 未:' + t.unCount + '）\n' +
      '无对手已出单: ' + t.noRivalSold + '个 / 无对手未出单: ' + t.noRivalUnsold + '个\n' +
      '分析及时率: ' + timelinessData.total.timelyRate + '\n\n' +
      '【品线维度】\n' + categoryRevenueData.map(function(d){
        return d.category + ': ' + d.curSku + 'SKU, 销量' + fmtNum(d.curSalesQty) + '(环比' + d.salesQtyChange + '), 销售额' + fmtMoney(d.curRevenue) + '(环比' + d.revenueChange + '), 市占比' + d.curMarketShare + '%(环比' + d.marketShareChange + ')';
      }).join('\n') + '\n\n' +
      '【分析人维度】\n' + analystRevenueData.map(function(d){
        return d.analyst + ': ' + d.curSku + 'SKU, 销量' + fmtNum(d.curSalesQty) + '(环比' + d.salesQtyChange + '), 销售额' + fmtMoney(d.curRevenue) + '(环比' + d.revenueChange + '), 市占比' + d.curMarketShare + '%(环比' + d.marketShareChange + ')';
      }).join('\n')
    },
    {title: '二、低占比分析', text: '【有对手未出单新品：' + hasCompetitorUnsold.total + '款】\n' +
      '原因分布: ' + hasCompetitorUnsold.reasons.filter(function(r){return r.count>0;}).map(function(r){return r.name + '(' + r.count + '款)';}).join('、') + '\n' +
      '【无对手未出单新品：' + unsoldNoCompetitor.total + '款】\n' +
      '原因分布: ' + unsoldNoCompetitor.reasons.filter(function(r){return r.count>0;}).map(function(r){return r.name + '(' + r.count + '款)';}).join('、') + '\n' +
      '【低占比新品（市占比<75%）：' + lowShareData.length + '款】占总SKU ' + (lowShareData.length/t.total*100).toFixed(1) + '%'
    },
    {title: '三、广告追踪（自然周5.18-5.24）', text: '【PLP广告】\n' +
      '花费: ' + fmtMoney(plpTotal.cost) + ' | 广告销售额: ' + fmtMoney(plpTotal.revenue) + ' | ROAS: ' + plpTotal.roas + '\n' +
      'ACOS: ' + plpTotal.acos + ' | ACOAS: ' + plpTotal.acoas + '\n' +
      '活动' + plpTotal.campaignCount + '个, 链接' + plpTotal.linkCount + '个, 售出' + plpTotal.sold + '单\n\n' +
      '【PLG广告】\n' +
      '花费: ' + fmtMoney(plgStats.totalSpend) + ' | 广告销售额: ' + fmtMoney(plgStats.totalAdRev) + '\n' +
      'ACOS: ' + plgStats.acos + ' | ACOAS: ' + plgStats.acoas + '\n' +
      'PLP+PLG同开' + plgStats.plpAndPlgBothCount + '款, 单PLG' + plgStats.plgOnlyCount + '款, 单PLP' + plgStats.plpOnlyCount + '款\n' +
      '按分析人PLG: ' + plgStats.byAnalyst.map(function(d){return d.analyst + '(花费' + fmtMoney(d.plgSpend) + ', ACOS ' + d.acos + ', ACOAS ' + d.acoas + ')';}).join('; ')
    },
    {title: '四、风险预警与下周动作', text: '【风险预警】\n' +
      risks.map(function(r){ return '[' + r.level.toUpperCase() + '] ' + r.title + ': ' + r.text; }).join('\n') + '\n\n' +
      '【主要发现】\n' + findings.map(function(f){ return '- ' + f.title + ': ' + f.desc; }).join('\n') + '\n\n' +
      '【下周重点动作】\n' + actions.map(function(a, i){ return (i+1) + '. ' + a.title + ': ' + a.desc; }).join('\n')
    },
  ];
  var reportHtml = '';
  reportSections.forEach(function(sec) {
    reportHtml += '<div class="report-block"><h4>' + sec.title + '</h4><pre>' + sec.text + '</pre><button class="copy-btn" onclick="copyReport(this)">复制</button></div>';
  });
  document.getElementById('t5-report').innerHTML = reportHtml;
})();

function copyReport(btn) {
  var pre = btn.parentElement.querySelector('pre');
  navigator.clipboard.writeText(pre.textContent).then(function() {
    btn.textContent = '已复制';
    setTimeout(function() { btn.textContent = '复制'; }, 1500);
  });
}
'''

# ===== 组装完整 HTML =====
print("组装完整HTML...")
full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报看板 5.21-5.27</title>
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
