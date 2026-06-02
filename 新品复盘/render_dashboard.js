/**
 * 新品复盘 — 渲染引擎
 * 从 DATA 对象渲染全部 6 个 Tab + Chart.js 图表 + XLSX 导出
 */

// ===== 工具函数 =====
function fmtNum(n) { return n == null || n === '' ? '-' : Number(n).toLocaleString('zh-CN'); }
function fmtMoney(n) { return n == null || n === '' ? '-' : '$' + Number(n).toFixed(2); }
function hbSign(v) {
  if (typeof v !== 'string') return v;
  if (v === '-' || v === '0%' || v === '0.0%' || v === '+0%' || v === '+0.0%') return '<span class="hb-flat">-</span>';
  if (v.startsWith('+')) return '<span class="hb-up">' + v + '</span>';
  if (v.startsWith('-')) return '<span class="hb-down">' + v + '</span>';
  return '<span class="hb-flat">' + v + '</span>';
}
function badge(s, cls) { return '<span class="badge badge-' + cls + '">' + s + '</span>'; }
function badgeStatus(v) {
  if (v === '竞争无优势') return badge('竞争弱', 'orange');
  if (v === '无市场') return badge('无市场', 'red');
  if (v === '正常') return badge('正常', 'blue');
  if (v === '站外出单') return badge('站外出单', 'purple');
  if (v === '站内无价格优势') return badge('无价优', 'orange');
  return v;
}
function badge8d(v) {
  if (v === 'Y') return badge('Y', 'green');
  if (v === 'N') return badge('N', 'orange');
  return badge(v, 'red');
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

// ===== 全局状态 =====
var DATA = null;
var allCharts = [];

function destroyAllCharts() {
  allCharts.forEach(function(c) { try { c.destroy(); } catch(e) {} });
  allCharts = [];
}

// ===== Tab 切换 =====
function switchTab(tabId, el) {
  document.querySelectorAll('.tab-content').forEach(function(t) { t.classList.remove('active'); });
  document.getElementById(tabId).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(function(a) { a.classList.remove('active'); });
  if (el) el.classList.add('active');
  if (tabId === 'tab1' && !window._charts1Init) { initTab1Charts(); }
  if (tabId === 'tab2' && !window._charts2Init) { renderCharts2(); }
  hideDrillChart();
}

// ===== 主渲染入口 =====
function renderAll(data) {
  DATA = data;
  console.log('[renderAll] DATA keys:', Object.keys(DATA).join(', '));
  console.log('[renderAll] cum43Stats:', DATA.cum43Stats);
  console.log('[renderAll] weekLabels4w:', DATA.weekLabels4w);

  var t = DATA.cum43Stats;
  if (!t) { console.error('[renderAll] cum43Stats is undefined!'); return; }

  var period = DATA.weekLabels4w ? DATA.weekLabels4w[DATA.weekLabels4w.length-1] : '--';
  document.getElementById('period-label').textContent = period;
  document.getElementById('h1-period').textContent = period;
  document.getElementById('h1-date').textContent = '2026-' + period.replace(/\./g,'-');
  document.getElementById('h1-sku').textContent = t.total + ' SKU';

  document.getElementById('upload-overlay').classList.add('hidden');
  document.getElementById('dashboard-container').classList.add('visible');

  destroyAllCharts();

  var renderFns = [
    {name: 'renderTab1', fn: renderTab1},
    {name: 'renderTab2', fn: renderTab2},
    {name: 'renderTab3', fn: renderTab3},
    {name: 'renderTab4', fn: renderTab4},
    {name: 'renderTab5', fn: renderTab5},
    {name: 'renderTab6', fn: renderTab6}
  ];
  for (var i = 0; i < renderFns.length; i++) {
    try {
      renderFns[i].fn();
    } catch(e) {
      console.error('[renderAll] Error in ' + renderFns[i].name + ':', e.message, e.stack);
      // Show error in header
      var h1 = document.getElementById('h1-period');
      if (h1) h1.textContent = h1.textContent + ' [ERR:' + renderFns[i].name + ']';
    }
  }

  setTimeout(function() {
    try { initTab1Charts(); } catch(e) { console.error('[renderAll] Error in initTab1Charts:', e.message); }
  }, 100);
}

// ===== Tab1: 总盘概览 =====
function renderTab1() {
  var t = DATA.cum43Stats, pk = DATA.prevWeekKpi;
  var saleRate = t.hasRivalCount ? (t.yCount + t.nCount) / t.hasRivalCount * 100 : 0;
  var ts = t.totalMarketShare, tsp = t.totalMarketSharePrev;
  var sc = tsp ? ((ts - tsp) / tsp * 100).toFixed(1) : '0';
  var scStr = (sc >= 0 ? '+' : '') + sc + '%';
  // FIX: use current week from 4w arrays, not prevWeekKpi
  var curSales = DATA.totalSales4w ? DATA.totalSales4w[3] : 0;
  var curRev = DATA.totalRev4w ? DATA.totalRev4w[3] : 0;

  document.getElementById('t1-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">累计SKU数</div><div class="val">' + t.total + '</div><div class="hb">' + hbSign(pk.skuChange) + ' 上周' + pk.prevTotalSku + '</div></div>' +
    '<div class="kpi-card success"><div class="label">本品总销量</div><div class="val">' + fmtNum(curSales) + '</div><div class="hb">' + hbSign(pk.salesQtyChange) + ' 上周' + fmtNum(pk.prevTotalSalesQty) + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">总销售额</div><div class="val">' + fmtMoney(curRev) + '</div><div class="hb">' + hbSign(pk.revenueChange) + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品总市占比</div><div class="val">' + ts + '%</div><div class="hb">' + hbSign(scStr) + ' 上周' + tsp + '%</div></div>' +
    '<div class="kpi-card success"><div class="label">出单率(有对手)</div><div class="val">' + saleRate.toFixed(1) + '%</div><div class="hb">Y:' + t.yCount + ' N:' + t.nCount + ' 未:' + t.unCount + '</div></div>' +
    '<div class="kpi-card info"><div class="label">分析及时率</div><div class="val">' + DATA.timelinessData.total.timelyRate + '</div><div class="hb">' + hbSign(DATA.timelinessData.total.change) + '</div></div>';

  document.getElementById('t1-ord8').innerHTML =
    '<table class="data-table"><thead><tr><th>分类</th><th>数量</th><th>说明</th></tr></thead><tbody>' +
    '<tr style="background:#e8f5e9"><td>有对手已出单(Y+N)</td><td>' + (t.yCount + t.nCount) + '</td><td>占有对手SKU的' + saleRate.toFixed(1) + '%</td></tr>' +
    '<tr style="background:#fff3e0"><td>有对手未出单</td><td>' + t.unCount + '</td><td>有竞品且未出单，需重点关注</td></tr>' +
    '<tr style="background:#e3f2fd"><td>无对手已出单</td><td>' + t.noRivalSold + '</td><td>无竞品已出单，市场独占</td></tr>' +
    '<tr style="background:#ffebee"><td>无对手未出单</td><td>' + t.noRivalUnsold + '</td><td>无竞品也未出单，需关注选品</td></tr>' +
    '<tr class="total-row"><td>合计</td><td>' + t.total + '</td><td>有对手' + t.hasRivalCount + '+无对手' + t.noRivalCount + '</td></tr></tbody></table>';

  var catH = '<table class="data-table"><thead><tr><th>品线</th><th>SKU</th><th>新上架</th><th>销量</th><th>销量环比</th><th>销售额</th><th>销售额环比</th><th>市占比</th><th>市占环比</th></tr></thead><tbody>';
  DATA.categoryRevenueData.forEach(function(d) {
    catH += '<tr><td>' + d.category + '</td><td>' + d.curSku + '</td><td>' + d.curNewSku + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td><td>' + d.curMarketShare + '%</td><td>' + hbSign(d.marketShareChange) + '</td></tr>';
  });
  document.getElementById('t1-cat-table').innerHTML = catH + '</tbody></table>';

  var anH = '<table class="data-table"><thead><tr><th>分析人</th><th>SKU</th><th>新上架</th><th>销量</th><th>销量环比</th><th>销售额</th><th>销售额环比</th><th>市占比</th><th>市占环比</th></tr></thead><tbody>';
  DATA.analystRevenueData.forEach(function(d) {
    anH += '<tr><td>' + d.analyst + '</td><td>' + d.curSku + '</td><td>' + d.curNewSku + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td><td>' + d.curMarketShare + '%</td><td>' + hbSign(d.marketShareChange) + '</td></tr>';
  });
  document.getElementById('t1-an-table').innerHTML = anH + '</tbody></table>';

  var expH = '<table class="data-table"><thead><tr><th>拓展类型</th><th>本周SKU</th><th>上周SKU</th><th>出单SKU</th><th>出单率</th><th>上周出单率</th><th>本周销量</th><th>上周销量</th><th>销量环比</th><th>本周销售额</th><th>上周销售额</th><th>销售额环比</th></tr></thead><tbody>';
  DATA.expandTypeData.forEach(function(d) {
    expH += '<tr><td>' + d.expandType + '</td><td>' + d.curSku + '</td><td>' + d.prevSku + '</td><td>' + d.curSalesSku + '</td><td>' + d.curSalesRate + '</td><td>' + d.prevSalesRate + '</td><td>' + fmtNum(d.curSalesQty) + '</td><td>' + fmtNum(d.prevSalesQty) + '</td><td>' + hbSign(d.salesQtyChange) + '</td><td>' + fmtMoney(d.curRevenue) + '</td><td>' + fmtMoney(d.prevRevenue) + '</td><td>' + hbSign(d.revenueChange) + '</td></tr>';
  });
  document.getElementById('t1-exp-table').innerHTML = expH + '</tbody></table>';

  var timeH = '<table class="data-table"><thead><tr><th>分析人</th><th>本周SKU</th><th>及时分析</th><th>8日未分析</th><th>7日未分析</th><th>及时率</th><th>上周及时率</th><th>变化</th></tr></thead><tbody>';
  DATA.timelinessData.analysts.forEach(function(d) {
    timeH += '<tr><td>' + d.analyst + '</td><td>' + d.curSku + '</td><td>' + d.timelyCount + '</td><td>' + d.noAnalysis8dCount + '</td><td>' + d.noAnalysis7dCount + '</td><td>' + d.timelyRate + '</td><td>' + d.prevTimelyRate + '</td><td>' + hbSign(d.change) + '</td></tr>';
  });
  var td = DATA.timelinessData.total;
  timeH += '<tr class="total-row"><td>' + td.analyst + '</td><td>' + td.curSku + '</td><td>' + td.timelyCount + '</td><td>' + td.noAnalysis8dCount + '</td><td>' + td.noAnalysis7dCount + '</td><td>' + td.timelyRate + '</td><td>' + td.prevTimelyRate + '</td><td>' + hbSign(td.change) + '</td></tr></tbody></table>';
  document.getElementById('t1-time-table').innerHTML = timeH;

  // 下钻触发器
  try { setupDrillTrigger('t1-cat-table', ''); } catch(e) {}
  try { setupDrillTrigger('t1-an-table', ''); } catch(e) {}
  try { setupDrillTrigger('t1-time-table', 'time:'); } catch(e) {}
}

// ===== Tab1 图表初始化 =====
window._charts1Init = false;
function initTab1Charts() {
  if (window._charts1Init) return;
  window._charts1Init = true;
  var t = DATA.cum43Stats;

  // 1. 出单分布甜甜圈
  var ctx0 = document.getElementById('chart-ord8');
  if (ctx0) {
    allCharts.push(new Chart(ctx0, {
      type: 'doughnut',
      data: { labels: ['有对手已出单','有对手未出单','无对手已出单','无对手未出单'], datasets: [{ data: [t.yCount+t.nCount,t.unCount,t.noRivalSold,t.noRivalUnsold], backgroundColor: ['#08845a','#e07b24','#2980b9','#c0392b'] }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom' }, tooltip: { callbacks: { label: function(ctx) { return ctx.label + ': ' + ctx.parsed + '个 (' + (ctx.parsed/t.total*100).toFixed(1) + '%)'; } } } } }
    }));
  }

  // 2. 4周销量趋势
  var ctx1 = document.getElementById('chart-4w-sales');
  if (ctx1) {
    allCharts.push(new Chart(ctx1, {
      type: 'line', data: { labels: DATA.weekLabels4w, datasets: [
        { label: '总销量', data: DATA.totalSales4w || [0,0,0,0], borderColor: '#0f3460', backgroundColor: 'rgba(15,52,96,0.1)', tension: 0.3, borderWidth: 3, pointRadius: 5, fill: true }
      ]},
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: '销量' } } } }
    }));
  }

  // 3. 4周销售额趋势
  var ctx2 = document.getElementById('chart-4w-rev');
  if (ctx2) {
    allCharts.push(new Chart(ctx2, {
      type: 'line', data: { labels: DATA.weekLabels4w, datasets: [
        { label: '总销售额($)', data: DATA.totalRev4w || [0,0,0,0], borderColor: '#8e44ad', backgroundColor: 'rgba(142,68,173,0.1)', tension: 0.3, borderWidth: 3, pointRadius: 5, fill: true }
      ]},
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: '销售额($)' } } } }
    }));
  }

  // 4. 4周市占比趋势
  var ctx3 = document.getElementById('chart-4w-share');
  if (ctx3) {
    allCharts.push(new Chart(ctx3, {
      type: 'line', data: { labels: DATA.weekLabels4w, datasets: [
        { label: '总市占比(%)', data: DATA.totalShare4w || [0,0,0,0], borderColor: '#08845a', backgroundColor: 'rgba(8,132,90,0.1)', tension: 0.3, borderWidth: 3, pointRadius: 5, fill: true }
      ]},
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: '市占比(%)' } } } }
    }));
  }
}

// ===== 下钻图表系统 =====
window._drillChartInstance = null;
window._drillDataMap = null;
window._activeDrillKey = null;

function buildDrillDataMap() {
  if (window._drillDataMap) return;
  var map = new Map();
  var WLABELS = DATA.weekLabels4w;

  // Tab1 品线维度
  DATA.catSales4w.forEach(function(d) {
    var si = DATA.catShare4w.find(function(s){return s.category===d.category;}) || {};
    var ri = DATA.catRev4w.find(function(s){return s.category===d.category;}) || {};
    map.set(d.category, {label: d.category, tab: 't1-cat', sales4w: d.sales4w, rev4w: ri.rev4w || [0,0,0,0], share4w: si.share4w || [0,0,0,0], newSku4w: [0,0,0,0]});
  });
  // Tab1 分析人维度
  DATA.anSales4w.forEach(function(d) {
    var si = DATA.anShare4w.find(function(s){return s.analyst===d.analyst;}) || {};
    var ri = DATA.anRev4w.find(function(s){return s.analyst===d.analyst;}) || {};
    map.set(d.analyst, {label: d.analyst, tab: 't1-an', sales4w: d.sales4w, rev4w: ri.rev4w || [0,0,0,0], share4w: si.share4w || [0,0,0,0], newSku4w: [0,0,0,0]});
  });

  // 按周统计新上架SKU数（从 cum43Data）
  function parseWeekDates(label) {
    var parts = label.split('-');
    if (parts.length >= 2) {
      var m1 = parts[0].split('.'), m2 = parts[1].split('.');
      if (m1.length >= 2 && m2.length >= 2) {
        return [new Date(2026, parseInt(m1[0])-1, parseInt(m1[1])), new Date(2026, parseInt(m2[0])-1, parseInt(m2[1]))];
      }
    }
    return null;
  }
  var weekRanges = WLABELS.map(function(l) { return parseWeekDates(l); });
  if (DATA.cum43Data) {
    DATA.cum43Data.forEach(function(d) {
      var ld = d.listDate;
      if (!ld) return;
      var listD = ld instanceof Date ? ld : new Date(ld);
      if (isNaN(listD.getTime())) return;
      for (var wi = 0; wi < 4; wi++) {
        if (weekRanges[wi] && listD >= weekRanges[wi][0] && listD <= weekRanges[wi][1]) {
          var entry = map.get(d.category);
          if (entry) entry.newSku4w[wi]++;
          entry = map.get(d.analyst);
          if (entry) entry.newSku4w[wi]++;
          break;
        }
      }
    });
  }

  // Tab1 及时率维度
  if (DATA.timeliness4w && DATA.timeliness4w.analysts) {
    DATA.timeliness4w.analysts.forEach(function(d) {
      map.set('time:' + d.analyst, {label: d.analyst + ' 及时率', tab: 't1-time', rates4w: d.rates4w, isTimeliness: true});
    });
    map.set('time:总及时率', {label: '总及时率', tab: 't1-time', rates4w: DATA.timeliness4w.totalRates, isTimeliness: true});
  }

  // Tab4 PLP分析人
  if (DATA.plpAn4w) {
    DATA.plpAn4w.forEach(function(d) {
      map.set('plp:an:' + d.analyst, {label: d.analyst, tab: 'plp-an', spend4w: d.spend4w, adSales4w: d.adSales4w, acos4w: d.acos4w, acoas4w: d.acoas4w});
    });
  }
  // Tab4 PLP品线
  if (DATA.plpCat4w) {
    DATA.plpCat4w.forEach(function(d) {
      map.set('plp:cat:' + d.category, {label: d.category, tab: 'plp-cat', spend4w: d.spend4w, adSales4w: d.adSales4w, acos4w: d.acos4w, acoas4w: d.acoas4w});
    });
  }
  // Tab4 PLP拓展类型
  if (DATA.plpExp4w) {
    DATA.plpExp4w.forEach(function(d) {
      map.set('plp:exp:' + d.expandType, {label: d.expandType, tab: 'plp-exp', spend4w: d.spend4w, adSales4w: d.adSales4w, acos4w: d.acos4w, acoas4w: d.acoas4w});
    });
  }
  // Tab4 PLG按分析人
  if (DATA.plgAn4w) {
    DATA.plgAn4w.forEach(function(d) {
      map.set('plg:an:' + d.analyst, {label: d.analyst, tab: 'plg-an', spend4w: d.spend4w, adSales4w: d.adSales4w, acos4w: d.acos4w, acoas4w: d.acoas4w});
    });
  }

  window._drillDataMap = map;
}

function showDrillChart(key, data, title) {
  if (window._drillChartInstance) {
    window._drillChartInstance.destroy();
    window._drillChartInstance = null;
  }
  var panel = document.getElementById('drill-panel');
  if (!panel) return;

  var activeTd = document.querySelector('.drill-trigger.active');
  if (activeTd) {
    var tableWrap = activeTd.closest('.table-scroll-wrap');
    if (!tableWrap) tableWrap = activeTd.closest('table');
    if (tableWrap) {
      var targetParent = tableWrap.parentElement;
      if (targetParent && panel.parentNode !== targetParent) {
        targetParent.appendChild(panel);
      }
    }
  }

  var isPLP = (key.indexOf('plp:') === 0);
  var isPLG = (key.indexOf('plg:') === 0);
  var isAd = isPLP || isPLG;

  document.getElementById('drill-title').textContent = title + ' — 4周趋势';

  var WLABELS = DATA.weekLabels4w;
  var datasets = [];

  if (isAd) {
    var hasSpend = data.spend4w && data.spend4w.some(function(v){return v>0;});
    var hasAdSales = data.adSales4w && data.adSales4w.some(function(v){return v>0;});
    if (!hasSpend && !hasAdSales) {
      document.getElementById('drill-title').textContent = title + ' — 无4周广告数据';
      panel.classList.add('open');
      panel.classList.remove('closing');
      return;
    }
    if (hasSpend) {
      datasets.push({label:'广告花费($)',data:data.spend4w,borderColor:'#c0392b',backgroundColor:'rgba(192,57,43,0.08)',tension:0.3,borderWidth:2.5,pointRadius:4,yAxisID:'y'});
    }
    if (hasAdSales) {
      datasets.push({label:'广告销售额($)',data:data.adSales4w,borderColor:'#8e44ad',backgroundColor:'rgba(142,68,173,0.08)',tension:0.3,borderWidth:2.5,pointRadius:4,yAxisID:'y'});
    }
    if (data.acos4w && data.acos4w.some(function(v){return v>0;})) {
      datasets.push({label:'ACOS(%)',data:data.acos4w,borderColor:'#e07b24',backgroundColor:'transparent',tension:0.3,borderWidth:2,borderDash:[5,3],pointRadius:3,yAxisID:'y1'});
    }
    if (data.acoas4w && data.acoas4w.some(function(v){return v>0;})) {
      datasets.push({label:'ACOAS(%)',data:data.acoas4w,borderColor:'#0f3460',backgroundColor:'transparent',tension:0.3,borderWidth:2,borderDash:[3,3],pointRadius:3,yAxisID:'y1'});
    }
  } else if (data.isTimeliness) {
    datasets.push({label:'及时率(%)',data:data.rates4w,borderColor:'#0f3460',backgroundColor:'rgba(15,52,96,0.1)',tension:0.3,borderWidth:3,pointRadius:5,fill:true,yAxisID:'y'});
  } else {
    var hasSales = data.sales4w && data.sales4w.some(function(v){return v>0;});
    var hasRev = data.rev4w && data.rev4w.some(function(v){return v>0;});
    if (!hasSales && !hasRev) {
      document.getElementById('drill-title').textContent = title + ' — 无4周趋势数据';
      panel.classList.add('open');
      panel.classList.remove('closing');
      return;
    }
    if (hasSales) {
      datasets.push({label:'销量',data:data.sales4w,borderColor:'#0f3460',backgroundColor:'rgba(15,52,96,0.08)',tension:0.3,borderWidth:2.5,pointRadius:4,yAxisID:'y'});
    }
    if (hasRev) {
      datasets.push({label:'销售额($)',data:data.rev4w,borderColor:'#8e44ad',backgroundColor:'rgba(142,68,173,0.08)',tension:0.3,borderWidth:2.5,pointRadius:4,yAxisID:'y1'});
    }
    if (data.share4w && data.share4w.some(function(v){return v>0;})) {
      datasets.push({label:'市占比(%)',data:data.share4w,borderColor:'#08845a',backgroundColor:'transparent',tension:0.3,borderWidth:2,borderDash:[5,3],pointRadius:3,yAxisID:'y1'});
    }
    var hasNewSku = data.newSku4w && data.newSku4w.some(function(v){return v>0;});
    if (hasNewSku) {
      datasets.push({label:'新上架SKU',data:data.newSku4w,type:'bar',backgroundColor:'rgba(224,123,36,0.35)',borderColor:'#e07b24',borderWidth:1,borderRadius:3,yAxisID:'y'});
    }
  }

  panel.classList.add('open');
  panel.classList.remove('closing');

  var yLabel = data.isTimeliness ? '及时率(%)' : (isAd ? '金额($)' : '销量');
  var y1Label = data.isTimeliness ? '' : (isPLP ? '百分比(%)' : '金额/占比');
  window._drillChartInstance = new Chart(document.getElementById('drill-canvas'), {
    type: 'line',
    data: { labels: WLABELS, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: yLabel }, position: 'left' },
        y1: { beginAtZero: true, title: { display: true, text: y1Label }, position: 'right', grid: { drawOnChartArea: false } }
      }
    }
  });
}

function hideDrillChart() {
  if (window._drillChartInstance) {
    window._drillChartInstance.destroy();
    window._drillChartInstance = null;
  }
  var panel = document.getElementById('drill-panel');
  if (!panel) return;
  panel.classList.add('closing');
  panel.classList.remove('open');
  document.querySelectorAll('.drill-trigger.active').forEach(function(td){td.classList.remove('active');});
  window._activeDrillKey = null;
}

function handleDrillClick(td) {
  var key = td.getAttribute('data-drill');
  if (!key) return;

  if (window._activeDrillKey === key) {
    hideDrillChart();
    return;
  }

  document.querySelectorAll('.drill-trigger.active').forEach(function(t){t.classList.remove('active');});
  td.classList.add('active');
  window._activeDrillKey = key;

  buildDrillDataMap();

  var data = window._drillDataMap.get(key);
  if (!data) {
    hideDrillChart();
    return;
  }

  var isAd2 = (key.indexOf('plp:') === 0 || key.indexOf('plg:') === 0);
  var title = data.label + (isAd2 ? (key.indexOf('plg:')===0 ? ' PLG趋势' : ' PLP趋势') : ' 4周趋势');
  showDrillChart(key, data, title);
}

function setupDrillTrigger(containerId, keyPrefix) {
  var container = document.getElementById(containerId);
  if (!container) return;
  var rows = container.querySelectorAll('tbody tr');
  rows.forEach(function(tr) {
    var firstTd = tr.querySelector('td');
    if (!firstTd) return;
    var txt = (firstTd.textContent || '').trim();
    if (!txt || txt === '合计') return;
    var dk = (keyPrefix || '') + txt;
    if (!firstTd.getAttribute('data-drill')) {
      firstTd.setAttribute('data-drill', dk);
    }
    firstTd.classList.add('drill-trigger');
    firstTd.onclick = function(e) { handleDrillClick(this); };
  });
}

// 关闭按钮
setTimeout(function() {
  var closeBtn = document.getElementById('drill-close');
  if (closeBtn) closeBtn.onclick = hideDrillChart;
}, 100);

// ===== Tab2: 市场分布 =====
window._charts2Init = false;
function renderTab2() {
  var mo = DATA.mktDistOverall;
  var ni = mo.distribution.find(function(d){return d.status==='正常'})||{curCount:0,curPct:0,change:0};
  var ci = mo.distribution.find(function(d){return d.status==='竞争无优势'})||{curCount:0,change:0};
  var nmi = mo.distribution.find(function(d){return d.status==='无市场'})||{curCount:0,change:0};
  var si = mo.distribution.find(function(d){return d.status==='站外出单'})||{curCount:0,change:0};

  document.getElementById('t2-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">在售SKU总数</div><div class="val">' + mo.curTotal + '</div><div class="hb">上周' + mo.prevTotal + '</div></div>' +
    '<div class="kpi-card success"><div class="label">市场正常</div><div class="val">' + ni.curCount + '</div><div class="hb">占比' + ni.curPct + '%</div></div>' +
    '<div class="kpi-card warning"><div class="label">竞争无优势</div><div class="val">' + ci.curCount + '</div><div class="hb">' + hbSign((ci.change>=0?'+':'')+ci.change) + ' vs 上周</div></div>' +
    '<div class="kpi-card danger"><div class="label">无市场</div><div class="val">' + nmi.curCount + '</div><div class="hb">' + hbSign((nmi.change>=0?'+':'')+nmi.change) + ' vs 上周</div></div>' +
    '<div class="kpi-card purple"><div class="label">站外出单</div><div class="val">' + si.curCount + '</div><div class="hb">' + hbSign((si.change>=0?'+':'')+si.change) + ' vs 上周</div></div>';

  var mh = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>市场状态</th><th>本周数量</th><th>本周占比</th><th>上周数量</th><th>上周占比</th><th>变化</th></tr></thead><tbody>';
  mo.distribution.forEach(function(d) {
    mh += '<tr><td>' + badgeStatus(d.status) + '</td><td>' + d.curCount + '</td><td>' + d.curPct + '%</td><td>' + d.prevCount + '</td><td>' + d.prevPct + '%</td><td>' + hbSign((d.change>=0?'+':'')+d.change) + '</td></tr>';
  });
  document.getElementById('t2-mkt-table').innerHTML = mh + '</tbody></table></div>';

  var po = DATA.priceOverview;
  var ph = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>价格区间</th><th>SKU数</th><th>占比</th></tr></thead><tbody>';
  po.distribution.forEach(function(d) { ph += '<tr><td>' + d.range + '</td><td>' + d.count + '</td><td>' + d.pct + '%</td></tr>'; });
  ph += '<tfoot><tr class="total-row"><td><b>汇总</b></td><td><b>' + po.totalWithSales + '个有销售额</b></td><td><b>均价$' + (po.avgPrice||0).toFixed(2) + ' / 中位$' + (po.medianPrice||0).toFixed(2) + '</b></td></tr></tfoot></tbody></table></div>';
  document.getElementById('t2-price-table').innerHTML = ph;

  var sh = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>品线</th>';
  DATA.weekLabels4w.forEach(function(w){sh+='<th>'+w+'</th>';});
  sh += '<th>环比</th></tr></thead><tbody>';
  DATA.catShare4w.forEach(function(d){
    sh += '<tr><td><b>'+d.category+'</b></td>';
    d.share4w.forEach(function(v){sh+='<td>'+v+'%</td>';});
    var c=d.share4w[3]-d.share4w[2];
    sh+='<td>'+hbSign((c>=0?'+':'')+c.toFixed(1)+'%')+'</td></tr>';
  });
  sh += '</tbody></table></div><div class="table-scroll-wrap" style="margin-top:10px"><table class="data-table"><thead><tr><th>分析人</th>';
  DATA.weekLabels4w.forEach(function(w){sh+='<th>'+w+'</th>';});
  sh += '<th>环比</th></tr></thead><tbody>';
  DATA.anShare4w.forEach(function(d){
    sh += '<tr><td><b>'+d.analyst+'</b></td>';
    d.share4w.forEach(function(v){sh+='<td>'+v+'%</td>';});
    var c=d.share4w[3]-d.share4w[2];
    sh+='<td>'+hbSign((c>=0?'+':'')+c.toFixed(1)+'%')+'</td></tr>';
  });
  document.getElementById('t2-share-tier-table').innerHTML = sh + '</tbody></table></div>';
}

function renderCharts2() {
  if (window._charts2Init) return; window._charts2Init = true;
  var mc = {'正常':'#08845a','竞争无优势':'#e07b24','无市场':'#c0392b','站外出单':'#8e44ad','站内无价格优势':'#f39c12'};
  var rd = DATA.mktDistOverall.distribution.filter(function(d){return d.curCount>0;});
  allCharts.push(new Chart(document.getElementById('chart-mkt-ring'),{type:'doughnut',data:{labels:rd.map(function(d){return d.status}),datasets:[{data:rd.map(function(d){return d.curCount}),backgroundColor:rd.map(function(d){return mc[d.status]||'#999'}),borderWidth:2}]},options:{responsive:true,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:function(ctx){return ctx.label+': '+ctx.parsed+'个 ('+rd[ctx.dataIndex].curPct+'%)';}}}}}}));
  allCharts.push(new Chart(document.getElementById('chart-mkt-bar'),{type:'bar',data:{labels:DATA.mktDistOverall.distribution.map(function(d){return d.status}),datasets:[{label:'本周',data:DATA.mktDistOverall.distribution.map(function(d){return d.curCount}),backgroundColor:'#0f3460'},{label:'上周',data:DATA.mktDistOverall.distribution.map(function(d){return d.prevCount}),backgroundColor:'#ccc'}]},options:{responsive:true,plugins:{legend:{position:'bottom'}},scales:{y:{beginAtZero:true,title:{display:true,text:'SKU数'}}}}}));
  var pl = DATA.priceOverview.distribution.map(function(d){return d.range});
  allCharts.push(new Chart(document.getElementById('chart-price-dist'),{type:'bar',data:{labels:pl,datasets:[{label:'SKU数',data:DATA.priceOverview.distribution.map(function(d){return d.count}),backgroundColor:['#08845a','#2980b9','#e07b24','#8e44ad','#c0392b','#0f3460']}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,title:{display:true,text:'SKU数'}}}}}));
  var apd = DATA.priceOverview.byAnalyst.map(function(d){return{label:d.analyst,data:DATA.priceOverview.priceRanges.map(function(r){return d[r]||0}),backgroundColor:'#'+Math.floor(Math.random()*16777215).toString(16).padStart(6,'0')}});
  if(apd.length) allCharts.push(new Chart(document.getElementById('chart-price-an'),{type:'bar',data:{labels:pl,datasets:apd},options:{responsive:true,plugins:{legend:{position:'bottom'}},scales:{x:{stacked:true},y:{stacked:true,beginAtZero:true,title:{display:true,text:'SKU数'}}}}}));
  var tl = DATA.shareTierOverview.byCategory.map(function(d){return d.category});
  allCharts.push(new Chart(document.getElementById('chart-share-tier'),{type:'bar',data:{labels:tl,datasets:[{label:'高(>=75%)',data:DATA.shareTierOverview.byCategory.map(function(d){return d.high}),backgroundColor:'#08845a'},{label:'中(50-75%)',data:DATA.shareTierOverview.byCategory.map(function(d){return d.mid}),backgroundColor:'#e07b24'},{label:'低(<50%)',data:DATA.shareTierOverview.byCategory.map(function(d){return d.low}),backgroundColor:'#c0392b'}]},options:{responsive:true,plugins:{legend:{position:'bottom'}},scales:{x:{stacked:true},y:{stacked:true,beginAtZero:true,title:{display:true,text:'SKU数'}}}}}));
  allCharts.push(new Chart(document.getElementById('chart-total-share-4w'),{type:'line',data:{labels:DATA.weekLabels4w,datasets:[{label:'总市占比(%)',data:DATA.totalShare4w,borderColor:'#0f3460',backgroundColor:'rgba(15,52,96,0.1)',fill:true,tension:0.3,borderWidth:2}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{min:0,max:100,title:{display:true,text:'市占比(%)'}}}}}));
  var csd = DATA.catShare4w.map(function(d){return{label:d.category,data:d.share4w,borderColor:'#'+Math.floor(Math.random()*16777215).toString(16).padStart(6,'0'),backgroundColor:'transparent',tension:0.3}});
  allCharts.push(new Chart(document.getElementById('chart-cat-share-4w'),{type:'line',data:{labels:DATA.weekLabels4w,datasets:csd},options:{responsive:true,plugins:{legend:{position:'bottom'}},scales:{y:{min:0,max:100,title:{display:true,text:'市占比(%)'}}}}}));
  var asd = DATA.anShare4w.map(function(d){return{label:d.analyst,data:d.share4w,borderColor:'#'+Math.floor(Math.random()*16777215).toString(16).padStart(6,'0'),backgroundColor:'transparent',tension:0.3}});
  allCharts.push(new Chart(document.getElementById('chart-an-share-4w'),{type:'line',data:{labels:DATA.weekLabels4w,datasets:asd},options:{responsive:true,plugins:{legend:{position:'bottom'}},scales:{y:{min:0,max:100,title:{display:true,text:'市占比(%)'}}}}}));
}

// ===== Tab3: 低占比分析 =====
function renderTab3() {
  var hcu = DATA.hasCompetitorUnsold, unc = DATA.unsoldNoCompetitor, t = DATA.cum43Stats;
  document.getElementById('t3-kpi').innerHTML =
    '<div class="kpi-card warning"><div class="label">有对手未出单</div><div class="val">'+hcu.total+'</div><div class="hb">上周'+hcu.prevTotal+' | '+(hcu.change>=0?'+':'')+hcu.change+'</div></div>'+
    '<div class="kpi-card danger"><div class="label">无对手未出单</div><div class="val">'+unc.total+'</div><div class="hb">上周'+unc.prevTotal+' | '+(unc.change>=0?'+':'')+unc.change+'</div></div>'+
    '<div class="kpi-card info"><div class="label">有对手SKU总数</div><div class="val">'+t.hasRivalCount+'</div></div>'+
    '<div class="kpi-card primary"><div class="label">有对手未出单占比</div><div class="val">'+(t.unCount/t.total*100).toFixed(1)+'%</div><div class="hb">'+t.unCount+' / '+t.total+'</div></div>';

  var hasMkts=['竞争无优势','站内无价格优势'];
  function buildMktTable(data, mkts, labelKey){
    var h='<table class="data-table"><thead><tr><th>'+labelKey+'</th>'; mkts.forEach(function(m){h+='<th>'+m+'</th>';}); h+='<th>未出单总数</th></tr></thead><tbody>';
    var total=0;
    data.forEach(function(d){h+='<tr><td>'+d[labelKey]+'</td>'; mkts.forEach(function(m){h+='<td>'+(d[m]||0)+'</td>';}); h+='<td><b>'+d.total+'</b></td></tr>'; total+=d.total;});
    h+='<tfoot><tr class="total-row"><td><b>合计</b></td>';
    mkts.forEach(function(m){var s=0;data.forEach(function(d){s+=(d[m]||0);});h+='<td><b>'+s+'</b></td>';});
    h+='<td><b>'+total+'</b></td></tr></tfoot></tbody></table>';
    return h;
  }
  document.getElementById('t3-has-an').innerHTML = buildMktTable(hcu.byAnalyst, hasMkts, 'analyst');
  document.getElementById('t3-has-cat').innerHTML = buildMktTable(hcu.byCategory, hasMkts, 'category');

  var noMkts=['无市场','站外出单'];
  document.getElementById('t3-no-an').innerHTML = buildMktTable(unc.byAnalyst, noMkts, 'analyst');
  document.getElementById('t3-no-cat').innerHTML = buildMktTable(unc.byCategory, noMkts, 'category');

  // 低占比筛选
  var opVals={}, adVals={};
  DATA.lowShareData.forEach(function(d){opVals[d.curOperation||'-']=1;adVals[d.adClass]=1;});
  var opKeys=Object.keys(opVals).sort(), adKeys=Object.keys(adVals).sort();
  var fh='<span class="fg"><label>8日出单</label><select id="ls-f-8d" onchange="renderLowShareTable()"><option value="">全部</option><option>Y</option><option>N</option><option>未出单</option></select></span>';
  fh+='<span class="fg" style="position:relative"><label id="ls-op-label" style="cursor:pointer" onclick="var d=document.getElementById(\'ls-op-drop\');d.style.display=d.style.display===\'none\'?\'block\':\'none\';">运作判断 &#9662;</label><div id="ls-op-drop" class="dropdown-panel"><label><input type="checkbox" id="ls-op-all" onchange="var c=this.checked;document.querySelectorAll(\'.ls-op-cb\').forEach(function(b){b.checked=c;});renderLowShareTable();" checked> <b>全选</b></label><hr style="margin:4px 0;border-color:#eee">';
  opKeys.forEach(function(v){fh+='<label><input type="checkbox" class="ls-op-cb" value="'+v+'" onchange="renderLowShareTable()" checked> '+v+'</label>';});
  fh+='</div></span><span class="fg"><label>广告分类</label><select id="ls-f-ad" onchange="renderLowShareTable()"><option value="">全部</option>';
  adKeys.forEach(function(v){fh+='<option value="'+v+'">'+v+'</option>';});
  fh+='</select></span><button class="reset-btn" onclick="resetLowShareFilters()">重置</button><span class="count" id="t3-ls-count"></span>';
  document.getElementById('t3-lowshare-filters').innerHTML = fh;

  document.addEventListener('click',function(e){var d=document.getElementById('ls-op-drop'),l=document.getElementById('ls-op-label');if(d&&l&&!l.contains(e.target)&&!d.contains(e.target))d.style.display='none';});
  renderLowShareTable();
}

window.resetLowShareFilters=function(){document.getElementById('ls-f-8d').value='';document.querySelectorAll('.ls-op-cb').forEach(function(b){b.checked=true;});document.getElementById('ls-op-all').checked=true;document.getElementById('ls-f-ad').value='';renderLowShareTable();};

window.renderLowShareTable=function(){
  var f8d=document.getElementById('ls-f-8d').value;
  var fOpChecked=document.querySelectorAll('.ls-op-cb:checked');
  var fOpAll=fOpChecked.length===document.querySelectorAll('.ls-op-cb').length;
  var fAd=document.getElementById('ls-f-ad').value;
  var filtered=DATA.lowShareData.filter(function(d){
    if(f8d&&d.cur8dStatus!==f8d)return false;
    if(!fOpAll&&!Array.from(fOpChecked).some(function(cb){return cb.value===(d.curOperation||'-');}))return false;
    if(fAd&&d.adClass!==fAd)return false;
    return true;
  });
  var ts=0,tr=0,tri=0,tsh=0;
  var h='<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>SKU</th><th>上架日期</th><th>分析人</th><th>品类</th><th>本周销量</th><th>销量环比</th><th>本周销售额</th><th>对手量</th><th>市占比</th><th>8日出单</th><th>上期市场状态</th><th>运作判断</th><th>本期市场状态</th><th>广告分类</th></tr></thead><tbody>';
  filtered.forEach(function(d){
    h+='<tr><td>'+d.SKU+'</td><td>'+d.launchDate+'</td><td>'+d.analyst+'</td><td>'+d.category+'</td><td>'+d.curSalesQty+'</td><td>'+hbSign(d.salesQtyChange)+'</td><td>'+fmtMoney(d.curRevenue)+'</td><td>'+d.curRivalQty+'</td><td>'+d.curMarketShare+'%</td><td>'+badge8d(d.cur8dStatus)+'</td><td>'+badgeStatus(d.prevMarketStatus)+'</td><td>'+(d.curOperation||'-')+'</td><td>'+badgeStatus(d.curMarketStatus)+'</td><td>'+badgeAdClass(d.adClass)+'</td></tr>';
    ts+=d.curSalesQty;tr+=d.curRevenue||0;tri+=d.curRivalQty||0;tsh+=d.curMarketShare||0;
  });
  var as=filtered.length>0?(tsh/filtered.length).toFixed(1):'-';
  h+='</tbody><tfoot><tr class="total-row"><td colspan="2">合计('+filtered.length+'条)</td><td></td><td></td><td><b>'+ts+'</b></td><td></td><td><b>'+fmtMoney(tr)+'</b></td><td><b>'+tri+'</b></td><td><b>'+as+'%</b></td><td colspan="5"></td></tr></tfoot></table></div>';
  document.getElementById('t3-lowshare-table').innerHTML=h;
  document.getElementById('t3-ls-count').textContent='筛选:'+filtered.length+'/'+DATA.lowShareData.length+'条';
};

// ===== Tab4: 广告追踪 =====
function renderTab4(){
  var pt=DATA.plpTotal,pp=DATA.plpPrevTotal;
  document.getElementById('t4-plp-kpi').innerHTML=
    '<div class="kpi-card primary"><div class="label">广告活动数</div><div class="val">'+pt.campaignCount+'</div><div class="hb">上周'+pp.campaignCount+'</div></div>'+
    '<div class="kpi-card info"><div class="label">投放链接数</div><div class="val">'+pt.linkCount+'</div><div class="hb">上周'+pp.linkCount+'</div></div>'+
    '<div class="kpi-card primary"><div class="label">曝光量</div><div class="val">'+fmtNum(pt.impression)+'</div></div>'+
    '<div class="kpi-card info"><div class="label">点击量</div><div class="val">'+fmtNum(pt.click)+'</div></div>'+
    '<div class="kpi-card success"><div class="label">售出数</div><div class="val">'+pt.sold+'</div></div>'+
    '<div class="kpi-card purple"><div class="label">广告销售额</div><div class="val">'+fmtMoney(pt.revenue)+'</div></div>';
  document.getElementById('t4-plp-core').innerHTML=
    '<div class="kpi-card primary"><div class="label">ROAS</div><div class="val">'+pt.roas+'</div><div class="hb">上周'+pp.roas+'</div></div>'+
    '<div class="kpi-card info"><div class="label">CVR</div><div class="val">'+pt.cvr+'</div><div class="hb">上周'+pp.cvr+'</div></div>'+
    '<div class="kpi-card primary"><div class="label">CTR</div><div class="val">'+pt.ctr+'</div><div class="hb">上周'+pp.ctr+'</div></div>'+
    '<div class="kpi-card info"><div class="label">CPC</div><div class="val">'+pt.cpc+'</div><div class="hb">上周'+pp.cpc+'</div></div>'+
    '<div class="kpi-card warning"><div class="label">CPA</div><div class="val">'+pt.cpa+'</div><div class="hb">上周'+pp.cpa+'</div></div>'+
    '<div class="kpi-card danger"><div class="label">ACOS</div><div class="val">'+pt.acos+'</div><div class="hb">上周'+pp.acos+'</div></div>'+
    '<div class="kpi-card danger"><div class="label">ACOAS(去重)</div><div class="val">'+pt.acoas+'</div><div class="hb">上周'+pp.acoas+'</div></div>';

  function rpd(data,lk){var h='<table class="data-table"><thead><tr><th>'+lk+'</th><th>活动数</th><th>链接数</th><th>曝光量</th><th>点击量</th><th>售出数</th><th>花费</th><th>广告销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>CPC</th><th>CPA</th><th>ACOS</th><th>ACOAS</th></tr></thead><tbody>';
    data.forEach(function(d){h+='<tr><td>'+d.name+'</td><td>'+d.campaignCount+'</td><td>'+d.linkCount+'</td><td>'+fmtNum(d.impression)+'</td><td>'+fmtNum(d.click)+'</td><td>'+d.sold+'</td><td>'+fmtMoney(d.cost)+'</td><td>'+fmtMoney(d.revenue)+'</td><td>'+d.roas+'</td><td>'+d.cvr+'</td><td>'+d.ctr+'</td><td>'+d.cpc+'</td><td>'+d.cpa+'</td><td>'+d.acos+'</td><td>'+d.acoas+'</td></tr>';});
    return h+'</tbody></table>';}
  document.getElementById('t4-plp-an').innerHTML=rpd(DATA.plpAnalysts,'分析人');
  document.getElementById('t4-plp-cat').innerHTML=rpd(DATA.plpCategories,'品线');
  document.getElementById('t4-plp-exp').innerHTML=rpd(DATA.plpExpandTypes,'拓展类型');

  var pg=DATA.plgStats;
  document.getElementById('t4-plg-kpi').innerHTML=
    '<div class="kpi-card purple"><div class="label">PLG广告花费</div><div class="val">'+fmtMoney(pg.totalSpend)+'</div></div>'+
    '<div class="kpi-card info"><div class="label">PLG广告销售额</div><div class="val">'+fmtMoney(pg.totalAdRev)+'</div></div>'+
    '<div class="kpi-card primary"><div class="label">PLG自然周总销售额</div><div class="val">'+fmtMoney(pg.totalNatRev)+'</div></div>'+
    '<div class="kpi-card danger"><div class="label">PLG ACOS</div><div class="val">'+pg.acos+'</div></div>'+
    '<div class="kpi-card warning"><div class="label">PLG ACOAS</div><div class="val">'+pg.acoas+'</div></div>';

  var plgH='<div class="kpi-grid" style="margin-bottom:12px">';
  plgH+='<div class="kpi-card primary"><div class="label">新品总数</div><div class="val">'+pg.totalNewProducts+'</div></div>';
  plgH+='<div class="kpi-card purple"><div class="label">PLP+PLG同开</div><div class="val">'+pg.plpAndPlgBothCount+'</div></div>';
  plgH+='<div class="kpi-card danger"><div class="label">单链接PLP+PLG同开</div><div class="val">'+pg.singleLinkPlpPlgCount+'</div></div>';
  plgH+='<div class="kpi-card info"><div class="label">单PLG</div><div class="val">'+pg.plgOnlyCount+'</div></div>';
  plgH+='<div class="kpi-card primary"><div class="label">单PLP</div><div class="val">'+pg.plpOnlyCount+'</div></div>';
  plgH+='<div class="kpi-card warning"><div class="label">无广告</div><div class="val">'+pg.noAdCount+'</div></div>';
  plgH+='<div class="kpi-card danger"><div class="label">单PLG且未出单</div><div class="val">'+(pg.plpDisabledNoSaleCount||0)+'</div></div></div>';
  plgH+='<table class="data-table"><thead><tr><th>分析人</th><th>总数</th><th>PLP+PLG</th><th>单链接PLP+PLG</th><th>单PLG</th><th>单PLP</th><th>无广告</th><th>PLP未开未出单</th></tr></thead><tbody>';
  var plgT={total:0,plpAndPlgBoth:0,singleLinkPlpPlg:0,plgOnly:0,plpOnly:0,noAd:0,plpDisabledNoSale:0};
  pg.byAnalyst.forEach(function(d){
    plgH+='<tr><td>'+d.analyst+'</td><td>'+d.total+'</td><td>'+d.plpAndPlgBoth+'</td><td style="color:#c0392b;font-weight:600">'+d.singleLinkPlpPlg+'</td><td>'+d.plgOnly+'</td><td>'+d.plpOnly+'</td><td>'+d.noAd+'</td><td style="color:#c0392b;font-weight:600">'+d.plpDisabledNoSale+'</td></tr>';
    for(var k in plgT)plgT[k]+=(d[k]||0);
  });
  plgH+='<tfoot><tr class="total-row"><td><b>合计</b></td><td><b>'+plgT.total+'</b></td><td><b>'+plgT.plpAndPlgBoth+'</b></td><td><b>'+plgT.singleLinkPlpPlg+'</b></td><td><b>'+plgT.plgOnly+'</b></td><td><b>'+plgT.plpOnly+'</b></td><td><b>'+plgT.noAd+'</b></td><td><b>'+plgT.plpDisabledNoSale+'</b></td></tr></tfoot></tbody></table>';
  document.getElementById('t4-plg').innerHTML=plgH;

  var plgAnH='<table class="data-table"><thead><tr><th>分析人</th><th>SKU数</th><th>PLG花费</th><th>PLG广告销售额</th><th>自然周销售额</th><th>PLG ACOS</th><th>PLG ACOAS</th></tr></thead><tbody>';
  pg.byAnalyst.forEach(function(d){plgAnH+='<tr><td>'+d.analyst+'</td><td>'+d.total+'</td><td>'+fmtMoney(d.plgSpend)+'</td><td>'+fmtMoney(d.plgAdRev)+'</td><td>'+fmtMoney(d.plgNatRev)+'</td><td>'+d.acos+'</td><td>'+d.acoas+'</td></tr>';});
  plgAnH+='<tr class="total-row"><td>合计</td><td>'+pg.totalNewProducts+'</td><td>'+fmtMoney(pg.totalSpend)+'</td><td>'+fmtMoney(pg.totalAdRev)+'</td><td>'+fmtMoney(pg.totalNatRev)+'</td><td>'+pg.acos+'</td><td>'+pg.acoas+'</td></tr></tbody></table>';
  document.getElementById('t4-plg-an').innerHTML=plgAnH;

  // PLP明细
  var dH='<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>SKU</th><th>广告活动</th><th>分析人</th><th>品类</th><th>曝光</th><th>点击</th><th>售出</th><th>花费</th><th>广告销售额</th><th>总销售额</th><th>ROAS</th><th>ACOS</th><th>ACOAS</th><th>广告分类</th></tr></thead><tbody>';
  var dT={impr:0,click:0,sold:0,cost:0,adRev:0,totalRev:0};
  DATA.plpDetailData.forEach(function(d){
    dH+='<tr><td>'+d.SKU+'</td><td>'+d.campaign+'</td><td>'+d.analyst+'</td><td>'+d.category+'</td><td>'+fmtNum(d.impressions)+'</td><td>'+fmtNum(d.clicks)+'</td><td>'+d.salesQty+'</td><td>'+fmtMoney(d.spend)+'</td><td>'+fmtMoney(d.adRevenue)+'</td><td>'+fmtMoney(d.totalRevenue)+'</td><td>'+(d.roas?d.roas.toFixed(2):'-')+'</td><td>'+(d.acos?(d.acos*100).toFixed(2)+'%':'0%')+'</td><td>'+(d.acoas?(d.acoas*100).toFixed(2)+'%':'0.00%')+'</td><td>'+badgeAdClass(d.adClass)+'</td></tr>';
    dT.impr+=d.impressions||0;dT.click+=d.clicks||0;dT.sold+=d.salesQty||0;dT.cost+=d.spend||0;dT.adRev+=d.adRevenue||0;dT.totalRev+=d.totalRevenue||0;
  });
  dH+='</tbody><tfoot><tr><td colspan="2">合计('+DATA.plpDetailData.length+'条)</td><td></td><td></td><td>'+fmtNum(dT.impr)+'</td><td>'+fmtNum(dT.click)+'</td><td>'+dT.sold+'</td><td>'+fmtMoney(dT.cost)+'</td><td>'+fmtMoney(dT.adRev)+'</td><td>'+fmtMoney(dT.totalRev)+'</td><td></td><td></td><td></td><td></td></tr></tfoot></table></div>';
  document.getElementById('t4-plp-detail').innerHTML=dH;

  // 下钻触发器
  try { setupDrillTrigger('t4-plp-an', 'plp:an:'); } catch(e) {}
  try { setupDrillTrigger('t4-plp-cat', 'plp:cat:'); } catch(e) {}
  try { setupDrillTrigger('t4-plp-exp', 'plp:exp:'); } catch(e) {}
  try { setupDrillTrigger('t4-plg-an', 'plg:an:'); } catch(e) {}
}

// ===== Tab5: 四三累计 =====
function renderTab5(){
  var t=DATA.cum43Stats;
  document.getElementById('t5-kpi').innerHTML=
    '<div class="kpi-card primary"><div class="label">累计总SKU</div><div class="val">'+t.total+'</div></div>'+
    '<div class="kpi-card success"><div class="label">已出单(Y+N)</div><div class="val">'+(t.yCount+t.nCount)+'</div></div>'+
    '<div class="kpi-card warning"><div class="label">有对手未出单</div><div class="val">'+t.unCount+'</div></div>'+
    '<div class="kpi-card info"><div class="label">市场正常</div><div class="val">'+t.normalCount+'</div></div>'+
    '<div class="kpi-card warning"><div class="label">竞争无优势</div><div class="val">'+t.competitiveCount+'</div></div>'+
    '<div class="kpi-card danger"><div class="label">无市场</div><div class="val">'+t.noMarketCount+'</div></div>'+
    '<div class="kpi-card purple"><div class="label">站外出单</div><div class="val">'+(t.stationOutCount||0)+'</div></div>';

  var ua=[],sa={}; DATA.cum43Data.forEach(function(d){if(!sa[d.analyst]){sa[d.analyst]=1;ua.push(d.analyst);}}); ua.sort();
  var uc=[],sc={}; DATA.cum43Data.forEach(function(d){if(!sc[d.category]){sc[d.category]=1;uc.push(d.category);}}); uc.sort();
  var fh='<span class="fg"><label>市场状态</label><select id="f-mkt" onchange="applyFilters()"><option value="">全部</option><option>正常</option><option>竞争无优势</option><option>无市场</option><option>站外出单</option></select></span>';
  fh+='<span class="fg"><label>分析人</label><select id="f-an" onchange="applyFilters()"><option value="">全部</option>'; ua.forEach(function(a){fh+='<option>'+a+'</option>';});
  fh+='</select></span><span class="fg"><label>品类</label><select id="f-cat" onchange="applyFilters()"><option value="">全部</option>'; uc.forEach(function(c){fh+='<option>'+c+'</option>';});
  fh+='</select></span><span class="fg"><label>拓展类型</label><select id="f-exp" onchange="applyFilters()"><option value="">全部</option><option>原开品</option><option>拓展品</option><option>组合件</option></select></span>';
  fh+='<span class="fg"><label>8日出单</label><select id="f-8d" onchange="applyFilters()"><option value="">全部</option><option>Y</option><option>N</option><option>未出单</option></select></span>';
  fh+='<span class="fg"><label>市占比</label><select id="f-share" onchange="applyFilters()"><option value="">全部</option><option value="high">75%及以上</option><option value="mid">50%-75%</option><option value="low">50%以下</option></select></span>';
  fh+='<span class="fg"><label>广告条件</label><select id="f-ad" onchange="applyFilters()"><option value="">全部</option><option>PLP+PLG同开</option><option>单链接PLP+PLG同开</option><option>单PLG</option><option>单PLP</option><option>单PLG且未出单</option><option>无广告</option></select></span>';
  fh+='<button class="reset-btn" onclick="resetFilters()">重置</button><span class="count" id="t5-count"></span>';
  document.getElementById('t5-filters').innerHTML=fh;
  renderT5Table(DATA.cum43Data);
}

window.renderT5Table=function(data){
  var ts=0,tr=0,tri=0;
  var h='<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>SKU</th><th>上架日期</th><th>首次出单</th><th>分析人</th><th>品类</th><th>拓展类型</th><th>本周销量</th><th>本周销售额</th><th>对手量</th><th>市占比</th><th>PLG费率</th><th>市场状态</th><th>8日出单</th><th>广告分类</th></tr></thead><tbody>';
  data.forEach(function(d){
    h+='<tr><td>'+d.SKU+'</td><td>'+d.listDate+'</td><td>'+d.firstOrderDate+'</td><td>'+d.analyst+'</td><td>'+d.category+'</td><td>'+d.expandType+'</td><td>'+d.curSalesQty+'</td><td>'+fmtMoney(d.curRevenue)+'</td><td>'+d.curRivalQty+'</td><td>'+d.curMarketShare+'%</td><td>'+(d.plgFee||'0%')+'</td><td>'+badgeStatus(d.curMarketStatus)+'</td><td>'+badge8d(d.cur8dStatus)+'</td><td>'+badgeAdClass(d.adClass)+'</td></tr>';
    ts+=d.curSalesQty;tr+=d.curRevenue||0;tri+=d.curRivalQty;
  });
  h+='</tbody><tfoot><tr><td colspan="2">合计('+data.length+'条)</td><td></td><td></td><td></td><td></td><td>'+ts+'</td><td>'+fmtMoney(tr)+'</td><td>'+tri+'</td><td colspan="5"></td></tr></tfoot></table></div>';
  document.getElementById('t5-table').innerHTML=h;
  document.getElementById('t5-count').textContent='筛选:'+data.length+'/'+DATA.cum43Data.length+'条';
};

window.applyFilters=function(){
  var data=DATA.cum43Data.slice();
  var mkt=document.getElementById('f-mkt').value,an=document.getElementById('f-an').value;
  var cat=document.getElementById('f-cat').value,exp=document.getElementById('f-exp').value;
  var d8=document.getElementById('f-8d').value,share=document.getElementById('f-share').value;
  var ad=document.getElementById('f-ad').value;
  if(mkt)data=data.filter(function(d){return d.curMarketStatus===mkt;});
  if(an)data=data.filter(function(d){return d.analyst===an;});
  if(cat)data=data.filter(function(d){return d.category===cat;});
  if(exp)data=data.filter(function(d){return d.expandType===exp;});
  if(d8)data=data.filter(function(d){return d.cur8dStatus===d8;});
  if(share==='high')data=data.filter(function(d){return d.curMarketShare>=75;});
  else if(share==='mid')data=data.filter(function(d){return d.curMarketShare>=50&&d.curMarketShare<75;});
  else if(share==='low')data=data.filter(function(d){return d.curMarketShare<50;});
  if(ad)data=data.filter(function(d){return d.adClass===ad;});
  renderT5Table(data);
};

window.resetFilters=function(){document.querySelectorAll('#t5-filters select').forEach(function(s){s.value='';});renderT5Table(DATA.cum43Data);};

// ===== Tab6: 汇报输出 =====
function renderTab6(){
  var t=DATA.cum43Stats,pk=DATA.prevWeekKpi;
  var saleRate=t.hasRivalCount?(t.yCount+t.nCount)/t.hasRivalCount*100:0;
  var timelyRate=parseFloat(DATA.timelinessData.total.timelyRate)||0;
  var curSales=DATA.totalSales4w?DATA.totalSales4w[3]:0;
  var curRev=DATA.totalRev4w?DATA.totalRev4w[3]:0;

  document.getElementById('t6-kpi').innerHTML=
    '<div class="kpi-card primary"><div class="label">在售SKU</div><div class="val">'+t.total+'</div></div>'+
    '<div class="kpi-card success"><div class="label">总销量</div><div class="val">'+fmtNum(curSales)+'</div></div>'+
    '<div class="kpi-card purple"><div class="label">总销售额</div><div class="val">'+fmtMoney(curRev)+'</div></div>'+
    '<div class="kpi-card info"><div class="label">新品总市占比</div><div class="val">'+pk.totalMarketShare+'</div></div>'+
    '<div class="kpi-card success"><div class="label">出单率(有对手)</div><div class="val">'+saleRate.toFixed(1)+'%</div></div>'+
    '<div class="kpi-card info"><div class="label">及时率</div><div class="val">'+DATA.timelinessData.total.timelyRate+'</div></div>'+
    '<div class="kpi-card warning"><div class="label">低占比新品</div><div class="val">'+DATA.lowShareData.length+'</div></div>';

  var risks=[];
  if(saleRate<70)risks.push({level:'high',title:'出单率偏低',text:'出单率仅'+saleRate.toFixed(1)+'%，低于70%警戒线。有对手未出单'+DATA.hasCompetitorUnsold.total+'款。'});
  if(DATA.unsoldNoCompetitor.total>15)risks.push({level:'high',title:'无对手未出单过多',text:'无对手未出单新品达'+DATA.unsoldNoCompetitor.total+'款，占比'+(DATA.unsoldNoCompetitor.total/t.total*100).toFixed(1)+'%。'});
  if(parseFloat(DATA.plpTotal.roas)<8)risks.push({level:'medium',title:'PLP ROAS偏低',text:'PLP ROAS为'+DATA.plpTotal.roas+'，较上周'+DATA.plpPrevTotal.roas+'下降。'});
  if(timelyRate<50){var wa=DATA.timelinessData.analysts.reduce(function(a,b){return parseFloat(a.timelyRate)<parseFloat(b.timelyRate)?a:b;});risks.push({level:'high',title:'分析及时率告急',text:wa.analyst+'及时率仅'+wa.timelyRate+'。'});}
  if(t.competitiveCount>t.normalCount)risks.push({level:'medium',title:'竞争无优势SKU偏多',text:'竞争无优势('+t.competitiveCount+')超过正常('+t.normalCount+')。'});
  if(!risks.length)risks.push({level:'low',title:'整体平稳',text:'本周各项指标整体平稳，暂无重大风险。'});

  var rh='';risks.forEach(function(r){var c=r.level==='high'?'risk-high':(r.level==='medium'?'risk-medium':'risk-low'),e=r.level==='high'?'🔴':(r.level==='medium'?'🟡':'🟢');rh+='<div class="report-block '+c+'"><h4>'+e+' '+r.title+'</h4><pre>'+r.text+'</pre></div>';});
  document.getElementById('t6-risk').innerHTML=rh;

  var findings=[
    {title:'新品总市占比 '+pk.totalMarketShare,desc:'本周新品总市占比为'+pk.totalMarketShare+'，上周'+pk.totalMarketSharePrev+'，环比'+hbSign(pk.marketShareChange)+'。'},
    {title:'出单率 '+saleRate.toFixed(1)+'%',desc:'Y:'+t.yCount+'个 N:'+t.nCount+'个 未:'+t.unCount+'个。无对手已出单'+t.noRivalSold+'个，未出单'+t.noRivalUnsold+'个。'},
    {title:'PLP广告ACOAS '+DATA.plpTotal.acoas,desc:'花费'+fmtMoney(DATA.plpTotal.cost)+'，ROAS '+DATA.plpTotal.roas+'。单链接PLP+PLG同开'+DATA.plgStats.singleLinkPlpPlgCount+'个。'},
    {title:'PLG广告',desc:'花费'+fmtMoney(DATA.plgStats.totalSpend)+'，ACOS '+DATA.plgStats.acos+'，ACOAS '+DATA.plgStats.acoas+'。'},
    {title:'低占比新品'+DATA.lowShareData.length+'款',desc:'市占比<75%，占总SKU的'+(DATA.lowShareData.length/t.total*100).toFixed(1)+'%。'}
  ];
  var fh='';findings.forEach(function(f){fh+='<div class="findings-card"><div class="title">'+f.title+'</div><div class="desc">'+f.desc+'</div></div>';});
  document.getElementById('t6-findings').innerHTML=fh;

  var actions=[
    {title:'低占比新品排查',desc:'对'+DATA.lowShareData.length+'款低占比新品逐一分析，重点关注竞争无优势和无市场SKU。'},
    {title:'市占比提升',desc:'本周新品总市占比'+pk.totalMarketShare+'，重点优化市占比偏低的品线和分析人SKU。'},
    {title:'单链接PLP+PLG同开优化',desc:'关注'+DATA.plgStats.singleLinkPlpPlgCount+'个单链接SKU的广告表现。'},
    {title:'分析及时率提升',desc:'督促及时率偏低的分析师，确保新品8日内完成首次分析。'},
    {title:'PLG广告ROI优化',desc:'PLG ACOS为'+DATA.plgStats.acos+'，持续监控投放效果。'}
  ];
  var ah='';actions.forEach(function(a){ah+='<div class="action-card"><div class="title">'+a.title+'</div><div class="desc">'+a.desc+'</div></div>';});
  document.getElementById('t6-actions').innerHTML=ah;

  var report=[
    {title:'一、总盘概览',text:'【核心KPI】\n累计SKU: '+t.total+' | 本品总销量: '+fmtNum(curSales)+' | 总销售额: '+fmtMoney(curRev)+'\n新品总市占比: '+pk.totalMarketShare+'（上周'+pk.totalMarketSharePrev+'，环比'+pk.marketShareChange+'）\n出单率(有对手): '+saleRate.toFixed(1)+'%（Y:'+t.yCount+'/ N:'+t.nCount+'/ 未:'+t.unCount+'）\n无对手已出单: '+t.noRivalSold+'个 / 无对手未出单: '+t.noRivalUnsold+'个\n分析及时率: '+DATA.timelinessData.total.timelyRate+'\n\n【品线维度】\n'+DATA.categoryRevenueData.map(function(d){return d.category+': '+d.curSku+'SKU, 销量'+fmtNum(d.curSalesQty)+', 销售额'+fmtMoney(d.curRevenue)+', 市占比'+d.curMarketShare+'%';}).join('\n')+'\n\n【分析人维度】\n'+DATA.analystRevenueData.map(function(d){return d.analyst+': '+d.curSku+'SKU, 销量'+fmtNum(d.curSalesQty)+', 销售额'+fmtMoney(d.curRevenue)+', 市占比'+d.curMarketShare+'%';}).join('\n')},
    {title:'二、低占比分析',text:'【有对手未出单：'+DATA.hasCompetitorUnsold.total+'款】\n原因: '+DATA.hasCompetitorUnsold.reasons.filter(function(r){return r.count>0;}).map(function(r){return r.name+'('+r.count+'款)';}).join('、')+'\n【无对手未出单：'+DATA.unsoldNoCompetitor.total+'款】\n原因: '+DATA.unsoldNoCompetitor.reasons.filter(function(r){return r.count>0;}).map(function(r){return r.name+'('+r.count+'款)';}).join('、')+'\n【低占比新品(<75%)：'+DATA.lowShareData.length+'款】占总SKU '+(DATA.lowShareData.length/t.total*100).toFixed(1)+'%'},
    {title:'三、广告追踪',text:'【PLP】\n花费: '+fmtMoney(DATA.plpTotal.cost)+' | 广告销售额: '+fmtMoney(DATA.plpTotal.revenue)+' | ROAS: '+DATA.plpTotal.roas+'\nACOS: '+DATA.plpTotal.acos+' | ACOAS: '+DATA.plpTotal.acoas+'\n活动'+DATA.plpTotal.campaignCount+'个, 链接'+DATA.plpTotal.linkCount+'个\n\n【PLG】\n花费: '+fmtMoney(DATA.plgStats.totalSpend)+' | 广告销售额: '+fmtMoney(DATA.plgStats.totalAdRev)+'\nACOS: '+DATA.plgStats.acos+' | ACOAS: '+DATA.plgStats.acoas+'\n按分析人: '+DATA.plgStats.byAnalyst.map(function(d){return d.analyst+'(花费'+fmtMoney(d.plgSpend)+', ACOS '+d.acos+', ACOAS '+d.acoas+')';}).join('; ')},
    {title:'四、风险预警与下周动作',text:'【风险预警】\n'+risks.map(function(r){return '['+r.level.toUpperCase()+'] '+r.title+': '+r.text;}).join('\n')+'\n\n【主要发现】\n'+findings.map(function(f){return '- '+f.title+': '+f.desc;}).join('\n')+'\n\n【下周动作】\n'+actions.map(function(a,i){return (i+1)+'. '+a.title+': '+a.desc;}).join('\n')}
  ];
  var rph='';report.forEach(function(s){rph+='<div class="report-block"><h4>'+s.title+'</h4><pre>'+s.text+'</pre><button class="copy-btn" onclick="copyReport(this)">复制</button></div>';});
  document.getElementById('t6-report').innerHTML=rph;
}

function copyReport(btn){
  var pre=btn.parentElement.querySelector('pre');
  navigator.clipboard.writeText(pre.textContent).then(function(){btn.textContent='已复制';setTimeout(function(){btn.textContent='复制';},1500);});
}

// ===== XLSX 导出（美化版） =====
function exportXLSX(){
  if(!DATA)return alert('请先上传数据文件');
  if(typeof XLSX==='undefined'){alert('SheetJS未加载，请使用离线版');return;}

  var wb=XLSX.utils.book_new();
  var W=DATA.weekLabels4w,P=W?W[W.length-1]:'current';
  var t=DATA.cum43Stats,pk=DATA.prevWeekKpi||{};
  var periodLabel=P;

  // ---- helpers ----
  function chg(a,b){if(!b||b===0)return'-';return (a-b)/Math.abs(b)*100;}  // raw number change rate
  function rawM(n){return (n!=null&&!isNaN(Number(n)))?Number(n):0;}
  function rawI(n){return (n!=null&&!isNaN(Number(n)))?Number(n):0;}

  // Apply column widths + number formats + merges + auto-filter + freeze
  function styleSheet(ws, colDefs, opts){
    opts=opts||{};
    // Column widths
    ws['!cols']=colDefs.map(function(d){return {wch:d.wch||12};});
    // Merged cells
    if(opts.merges)ws['!merges']=opts.merges;
    // Auto-filter + freeze header row
    if(opts.headerRow!=null){
      try{
        var range=XLSX.utils.decode_range(ws['!ref']);
        if(range.e.r>=opts.headerRow){
          ws['!autofilter']={ref:XLSX.utils.encode_range({s:{r:opts.headerRow,c:0},e:{r:range.e.r,c:colDefs.length-1}})};
          ws['!freeze']={xsplit:0,ysplit:opts.headerRow+1};
        }
      }catch(e){}
    }
    // Number formatting: convert numeric cells to proper types
    var rng=XLSX.utils.decode_range(ws['!ref']);
    for(var R=rng.s.r;R<=rng.e.r;R++){
      for(var C=rng.s.c;C<=rng.e.c;C++){
        if(!colDefs[C]||!colDefs[C].fmt)continue;
        var addr=XLSX.utils.encode_cell({r:R,c:C}),cell=ws[addr];
        if(!cell||typeof cell.v!=='number')continue;
        var f=colDefs[C].fmt,v=cell.v;cell.t='n';
        if(f==='money')cell.z='#,##0.00';
        else if(f==='int')cell.z='#,##0';
        else if(f==='pct'){cell.v=v/100;cell.z='0.0%';}
        else if(f==='pct2'){cell.v=v/100;cell.z='0.00%';}
        else if(f==='dec4')cell.z='0.0000';
        else if(f==='dec2')cell.z='0.00';
      }
    }
  }

  // ---- Sheet 1: 总盘概览 ----
  var s1=[['新品周报汇总 - '+periodLabel,'','',''],['','','',''],
    ['一、总体概况','','',''],
    ['指标','本期('+periodLabel+')','上期','环比']];
  var curSales=W&&DATA.totalSales4w?DATA.totalSales4w[W.length-1]:t.curSalesQty||0;
  var curRev=W&&DATA.totalRev4w?DATA.totalRev4w[W.length-1]:0;
  var prevSales=W&&DATA.totalSales4w&&W.length>=2?DATA.totalSales4w[W.length-2]:pk.prevTotalSalesQty||0;
  var prevRev=W&&DATA.totalRev4w&&W.length>=2?DATA.totalRev4w[W.length-2]:0;
  var ts=t.totalMarketShare||0,tsp=t.totalMarketSharePrev||0;
  var deptRev=DATA.prevWeekKpi?DATA.prevWeekKpi.deptTotalRevenue:0;
  var deptRatio=DATA.prevWeekKpi?DATA.prevWeekKpi.deptRatio:'-';
  var newList=DATA.categoryRevenueData.reduce(function(s,d){return s+(d.curNewSku||0);},0);
  s1.push(['累计SKU数',t.total||0,pk.prevTotalSku||0,chg(t.total||0,pk.prevTotalSku||0)]);
  s1.push(['本周新上架SKU',newList,'-','-']);
  s1.push(['总销量',rawI(curSales),rawI(prevSales),chg(curSales,prevSales)]);
  s1.push(['总销售额(USD)',rawM(curRev),rawM(prevRev),chg(curRev,prevRev)]);
  s1.push(['新品销售占三部比',deptRatio,'-','-']);
  s1.push(['三部总销售额(USD)',rawM(deptRev),'-','-']);
  s1.push(['有对手SKU数',t.hasRivalCount||0,'-','-']);
  s1.push(['无对手SKU数',t.noRivalCount||0,'-','-']);

  // 分析及时率
  var td=DATA.timelinessData;
  s1.push(['','','',''],['二、分析及时率','','',''],['指标','本期','上期','变化']);
  s1.push(['及时分析产品数',td.total.timelyCount,td.total.prevTimelyCount||0,(td.total.timelyCount||0)-(td.total.prevTimelyCount||0)]);
  s1.push(['8日内新品无分析',td.total.noAnalysis8dCount,'-','-']);
  s1.push(['超7日低占比未分析',td.total.noAnalysis7dCount,'-','-']);
  var tCntAll=td.total.timelyCount+td.total.noAnalysis8dCount+td.total.noAnalysis7dCount;
  s1.push(['统计总数',tCntAll,'-','-']);
  s1.push(['及时分析率',td.total.timelyRate,'-','-']);

  // 新品出单情况
  s1.push(['','','',''],['三、新品出单情况（有对手口径）','','',''],['指标','本期','上期','变化']);
  var hasR=t.hasRivalCount||1;
  s1.push(['有对手总SKU',t.hasRivalCount,'-','-']);
  s1.push(['8日内出单(Y)',t.yCount||0,'-','-']);
  s1.push(['8日外出单(N)',t.nCount||0,'-','-']);
  s1.push(['真正未出单',t.unCount||0,'-','-']);
  var yAll2=(t.yCount||0)+(t.nCount||0);
  s1.push(['已出单合计(Y+N)',yAll2,'-','-']);
  s1.push(['出单率',(yAll2/hasR*100),'-','-']);
  var ws1=XLSX.utils.aoa_to_sheet(s1);
  styleSheet(ws1,[{wch:24},{wch:20},{wch:16},{wch:14}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:3}},{s:{r:10,c:0},e:{r:10,c:3}},{s:{r:17,c:0},e:{r:17,c:3}}]
  });
  XLSX.utils.book_append_sheet(wb,ws1,'总盘概览');

  // ---- Sheet 2: 品线维度 ----
  var s2=[['品线维度 - '+periodLabel,'','','','','','','','','','','']];
  s2.push(['品线','SKU数','本周新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比','市占比','上周市占比','市占环比']);
  DATA.categoryRevenueData.forEach(function(d){
    s2.push([d.category,d.curSku,d.curNewSku||0,rawI(d.curSalesQty),rawI(d.prevSalesQty),d.salesQtyChange||'-',rawM(d.curRevenue),rawM(d.prevRevenue),d.revenueChange||'-',d.curMarketShare||0,d.prevMarketShare||0,d.marketShareChange||'-']);
  });
  var catTot=DATA.categoryRevenueData.reduce(function(a,d){a.sku+=d.curSku;a.newSku+=d.curNewSku||0;a.cs+=rawI(d.curSalesQty);a.ps+=rawI(d.prevSalesQty);a.cr+=rawM(d.curRevenue);a.pr+=rawM(d.prevRevenue);return a;},{sku:0,newSku:0,cs:0,ps:0,cr:0,pr:0});
  s2.push(['合计',catTot.sku,catTot.newSku,catTot.cs,catTot.ps,chg(catTot.cs,catTot.ps),catTot.cr,catTot.pr,chg(catTot.cr,catTot.pr),'','','']);
  var ws2=XLSX.utils.aoa_to_sheet(s2);
  styleSheet(ws2,[{wch:14},{wch:8,fmt:'int'},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10},{wch:16,fmt:'money'},{wch:16,fmt:'money'},{wch:10},{wch:12,fmt:'pct'},{wch:12,fmt:'pct'},{wch:10}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:11}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws2,'品线维度');

  // ---- Sheet 3: 分析人维度 ----
  var s3=[['分析人维度 - '+periodLabel,'','','','','','','','','','','']];
  s3.push(['分析人','SKU数','本周新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比','市占比','上周市占比','市占环比']);
  DATA.analystRevenueData.forEach(function(d){
    s3.push([d.analyst,d.curSku,d.curNewSku||0,rawI(d.curSalesQty),rawI(d.prevSalesQty),d.salesQtyChange||'-',rawM(d.curRevenue),rawM(d.prevRevenue),d.revenueChange||'-',d.curMarketShare||0,d.prevMarketShare||0,d.marketShareChange||'-']);
  });
  var anTot=DATA.analystRevenueData.reduce(function(a,d){a.sku+=d.curSku;a.newSku+=d.curNewSku||0;a.cs+=rawI(d.curSalesQty);a.ps+=rawI(d.prevSalesQty);a.cr+=rawM(d.curRevenue);a.pr+=rawM(d.prevRevenue);return a;},{sku:0,newSku:0,cs:0,ps:0,cr:0,pr:0});
  s3.push(['合计',anTot.sku,anTot.newSku,anTot.cs,anTot.ps,chg(anTot.cs,anTot.ps),anTot.cr,anTot.pr,chg(anTot.cr,anTot.pr),'','','']);
  var ws3=XLSX.utils.aoa_to_sheet(s3);
  styleSheet(ws3,[{wch:12},{wch:8,fmt:'int'},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10},{wch:16,fmt:'money'},{wch:16,fmt:'money'},{wch:10},{wch:12,fmt:'pct'},{wch:12,fmt:'pct'},{wch:10}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:11}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws3,'分析人维度');

  // ---- Sheet 4: 拓展类型 ----
  var s4=[['拓展类型 - '+periodLabel,'','','','','','','','','','','']];
  s4.push(['拓展类型','本周SKU','上周SKU','出单SKU','出单率','上周出单率','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比']);
  DATA.expandTypeData.forEach(function(d){
    s4.push([d.expandType,d.curSku,d.prevSku,d.curSalesSku,d.curSalesRate,d.prevSalesRate,rawI(d.curSalesQty),rawI(d.prevSalesQty),d.salesQtyChange||'-',rawM(d.curRevenue),rawM(d.prevRevenue),d.revenueChange||'-']);
  });
  var ws4=XLSX.utils.aoa_to_sheet(s4);
  styleSheet(ws4,[{wch:12},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10},{wch:10},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:10},{wch:16,fmt:'money'},{wch:16,fmt:'money'},{wch:10}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:11}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws4,'拓展类型');

  // ---- Sheet 5: 分析及时率 ----
  var s5=[['分析及时率 - '+periodLabel,'','','','','']];
  s5.push(['分析人','及时分析产品数','8日内新品无分析','超7日低占比未分析','统计总数','及时分析率']);
  DATA.timelinessData.analysts.forEach(function(d){
    var tot2=d.timelyCount+d.noAnalysis8dCount+d.noAnalysis7dCount;
    s5.push([d.analyst,d.timelyCount,d.noAnalysis8dCount,d.noAnalysis7dCount,tot2,d.timelyRate]);
  });
  var ttd=DATA.timelinessData.total;
  var tCnt2=ttd.timelyCount+ttd.noAnalysis8dCount+ttd.noAnalysis7dCount;
  s5.push(['合计',ttd.timelyCount,ttd.noAnalysis8dCount,ttd.noAnalysis7dCount,tCnt2,ttd.timelyRate]);
  var ws5=XLSX.utils.aoa_to_sheet(s5);
  styleSheet(ws5,[{wch:12},{wch:14,fmt:'int'},{wch:14,fmt:'int'},{wch:16,fmt:'int'},{wch:10,fmt:'int'},{wch:12}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:5}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws5,'分析及时率');

  // ---- Sheet 6: 低占比新品 ----
  var s6=[['低占比新品明细 - '+periodLabel]];
  s6.push(['销售编号','SKU','上架日期','分析人','品类','拓展类型','本周销量','销量环比','本周销售额','销售额环比','上期末对手销量','本期末对手销量','对手销量环比','上期末市占比','本期末市占比','市占比环比','8日出单','本期操作判断','本期市场状态','PLP','PLG费率','广告分类']);
  DATA.lowShareData.forEach(function(d){
    s6.push([d.salesCode||'',d.SKU,d.launchDate||'',d.analyst,d.category,d.expandType,rawI(d.curSalesQty),d.salesQtyChange||'-',rawM(d.curRevenue),d.revenueChange||'-',rawI(d.prevRivalQty),rawI(d.curRivalQty),d.rivalQtyChange||'-',d.prevMarketShare||0,d.curMarketShare||0,chg(d.curMarketShare,d.prevMarketShare),d.cur8dStatus||'',d.curOperation||'',d.curMarketStatus||'',d.plpEnabled||'N',d.plgFee||'0%',d.adClass||'']);
  });
  var ws6=XLSX.utils.aoa_to_sheet(s6);
  styleSheet(ws6,[{wch:16},{wch:22},{wch:12},{wch:10},{wch:12},{wch:10},{wch:10,fmt:'int'},{wch:10},{wch:14,fmt:'money'},{wch:10},{wch:14,fmt:'int'},{wch:14,fmt:'int'},{wch:10},{wch:12,fmt:'pct'},{wch:12,fmt:'pct'},{wch:12,fmt:'pct'},{wch:10},{wch:14},{wch:12},{wch:8},{wch:10},{wch:12}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:21}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws6,'低占比新品');

  // ---- Sheet 7: PLP总览 ----
  var plpBySku={},skuRevMap={};
  DATA.cum43Data.forEach(function(d){skuRevMap[d.SKU]=d.curRevenue||0;});
  (DATA.plpDetailData||[]).forEach(function(d){
    var s=d.SKU; if(!s)return;
    if(!plpBySku[s])plpBySku[s]={impr:0,click:0,sold:0,cost:0,adRev:0,camps:new Set()};
    var b=plpBySku[s];b.impr+=d.impressions||0;b.click+=d.clicks||0;b.sold+=d.salesQty||0;b.cost+=d.spend||0;b.adRev+=d.adRevenue||0;if(d.campaign)b.camps.add(d.campaign);
  });
  var plpT={campaigns:0,links:0,impr:0,click:0,sold:0,cost:0,adRev:0,totalRev:0},allCamps=new Set();
  for(var sk in plpBySku){var b=plpBySku[sk];plpT.links++;plpT.impr+=b.impr;plpT.click+=b.click;plpT.sold+=b.sold;plpT.cost+=b.cost;plpT.adRev+=b.adRev;plpT.totalRev+=skuRevMap[sk]||0;b.camps.forEach(function(c){allCamps.add(c);});}
  plpT.campaigns=allCamps.size;
  function plpRates(t2){t2.roas=t2.cost>0?t2.adRev/t2.cost:0;t2.cvr=t2.click>0?t2.sold/t2.click:0;t2.ctr=t2.impr>0?t2.click/t2.impr:0;t2.cpc=t2.click>0?t2.cost/t2.click:0;t2.cpa=t2.sold>0?t2.cost/t2.sold:0;t2.acos=t2.adRev>0?t2.cost/t2.adRev:0;t2.acoas=t2.totalRev>0?t2.cost/t2.totalRev:0;}
  plpRates(plpT);
  // Return raw numbers for number formatting
  function fmtPlpRow(period,t2){return [period,t2.campaigns,t2.links,t2.impr,t2.click,t2.sold,Math.round(t2.cost*100)/100,Math.round(t2.adRev*100)/100,Math.round(t2.totalRev*100)/100,t2.roas||0,t2.cvr||0,t2.ctr||0,t2.cpc||0,t2.cpa||0,t2.acos||0,t2.acoas||0];}

  var s7=[['PLP总览 - '+periodLabel],[''],
    ['【总数据】'],
    ['周期','活动数','链接数','曝光量','点击量','售出数','花费','广告销售额','总销售额','ROAS','CVR','CTR','CPC','CPA','ACOS','ACOAS'],
    fmtPlpRow(periodLabel,plpT)];

  // PLP by dimension
  function writePlpDim(s7,title,data,keyFn){
    s7.push([''],['【'+title+'】']);
    s7.push(['维度','活动数','链接数','曝光量','点击量','售出数','花费','广告销售额','总销售额','ROAS','CVR','CTR','CPC','CPA','ACOS','ACOAS']);
    data.forEach(function(d){s7.push([keyFn(d),d.campaignCount||0,d.linkCount||0,d.impression||0,d.click||0,d.sold||0,d.cost||0,d.revenue||0,d.totalRevenue||0,d.roas||0,d.cvr||0,d.ctr||0,d.cpc||0,d.cpa||0,d.acos||0,d.acoas||0]);});
  }
  writePlpDim(s7,'按分析人',DATA.plpAnalysts||[],function(d){return d.name;});
  writePlpDim(s7,'按品线',DATA.plpCategories||[],function(d){return d.name;});
  writePlpDim(s7,'按拓展类型',DATA.plpExpandTypes||[],function(d){return d.name;});
  var ws7=XLSX.utils.aoa_to_sheet(s7);
  // PLP has sub-tables, no auto-filter; just column widths + number formats
  styleSheet(ws7,[{wch:16},{wch:8,fmt:'int'},{wch:8,fmt:'int'},{wch:12,fmt:'int'},{wch:10,fmt:'int'},{wch:10,fmt:'int'},{wch:12,fmt:'money'},{wch:14,fmt:'money'},{wch:14,fmt:'money'},{wch:8,fmt:'dec2'},{wch:10,fmt:'pct2'},{wch:10,fmt:'pct2'},{wch:10,fmt:'dec2'},{wch:10,fmt:'dec2'},{wch:10,fmt:'pct2'},{wch:10,fmt:'pct2'}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:15}},{s:{r:2,c:0},e:{r:2,c:15}}]
  });
  XLSX.utils.book_append_sheet(wb,ws7,'PLP总览');

  // ---- Sheet 8: PLG总览 ----
  var pg=DATA.plgStats;
  var s8=[['PLG总览 - '+periodLabel],[''],
    ['【PLG费率分布】'],
    ['分析人','总数','PLP+PLG','单链接PLP+PLG','单PLG','单PLP','无广告','PLP未开未出单']];
  (pg.byAnalyst||[]).forEach(function(d){s8.push([d.analyst,d.total,d.plpAndPlgBoth,d.singleLinkPlpPlg,d.plgOnly,d.plpOnly,d.noAd,d.plpDisabledNoSale]);});
  s8.push(['合计',pg.totalNewProducts,pg.totalPlpAndPlgBoth||0,pg.totalSingleLinkPlpPlg||0,pg.totalPlgOnly||0,pg.totalPlpOnly||0,pg.totalNoAd||0,pg.totalPlpDisabledNoSale||0]);
  s8.push([''],['【PLG花费/ACOS/ACOAS】'],
    ['分析人','SKU数','PLG花费','PLG广告销售额','自然周销售额','PLG ACOS','PLG ACOAS']);
  (pg.byAnalyst||[]).forEach(function(d){s8.push([d.analyst,d.total||0,rawM(d.plgSpend),rawM(d.plgAdRev),rawM(d.plgNatRev),d.acos||0,d.acoas||0]);});
  s8.push(['合计',pg.totalNewProducts,rawM(pg.totalSpend),rawM(pg.totalAdRev),rawM(pg.totalNatRev),pg.acos||0,pg.acoas||0]);
  var ws8=XLSX.utils.aoa_to_sheet(s8);
  styleSheet(ws8,[{wch:12},{wch:8,fmt:'int'},{wch:12,fmt:'int'},{wch:14,fmt:'int'},{wch:8,fmt:'int'},{wch:8,fmt:'int'},{wch:8,fmt:'int'},{wch:14,fmt:'int'}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:7}},{s:{r:2,c:0},e:{r:2,c:7}}]
  });
  XLSX.utils.book_append_sheet(wb,ws8,'PLG总览');

  // ---- Sheet 9: 四三累计明细 ----
  var s9=[['四三累计明细 - '+periodLabel]];
  s9.push(['SKU','销售编号','上架日期','首次出单','分析人','品类','拓展类型','本周销量','本周销售额','对手量','市占比','8日出单','7日频次','8日新品频次','市场状态','PLP','PLG费率','广告分类']);
  DATA.cum43Data.forEach(function(d){
    s9.push([d.SKU,d.saleNo||'',d.listDate||'',d.firstOrderDate||'',d.analyst,d.category,d.expandType,rawI(d.curSalesQty),rawM(d.curRevenue),rawI(d.curRivalQty),d.curMarketShare||0,d.cur8dStatus||'',d.curFreq7||'',d.curNfreq7||'',d.curMarketStatus||'',d.plpEnabled||'N',(d.plgFee||0),d.adClass||'']);
  });
  var ws9=XLSX.utils.aoa_to_sheet(s9);
  styleSheet(ws9,[{wch:22},{wch:16},{wch:12},{wch:12},{wch:10},{wch:12},{wch:10},{wch:10,fmt:'int'},{wch:14,fmt:'money'},{wch:10,fmt:'int'},{wch:10,fmt:'pct'},{wch:10},{wch:10},{wch:12},{wch:12},{wch:6},{wch:10,fmt:'pct'},{wch:14}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:17}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws9,'四三累计明细');

  // ---- Sheet 10: 市场分布 ----
  var mo=DATA.mktDistOverall;
  var s10=[['市场分布 - '+periodLabel]];
  s10.push(['市场状态','本周数量','本周占比','上周数量','上周占比','变化']);
  (mo.distribution||[]).forEach(function(d){s10.push([d.status,d.curCount,d.curPct||0,d.prevCount,d.prevPct||0,(d.change>=0?'+':'')+d.change]);});
  var ws10=XLSX.utils.aoa_to_sheet(s10);
  styleSheet(ws10,[{wch:16},{wch:12,fmt:'int'},{wch:12,fmt:'pct'},{wch:12,fmt:'int'},{wch:12,fmt:'pct'},{wch:10}],{
    merges:[{s:{r:0,c:0},e:{r:0,c:5}}],headerRow:1
  });
  XLSX.utils.book_append_sheet(wb,ws10,'市场分布');

  XLSX.writeFile(wb,'新品周报数据表_'+P+'.xlsx',{cellStyles:true});
}


// ===== 文件上传 =====
(function(){
  var dz=document.getElementById('drop-zone'),fi=document.getElementById('file-input'),se=document.getElementById('upload-status');
  function handleFile(file){
    if(!file)return;
    if(!file.name.match(/\.xlsx?$/i)){se.textContent='❌ 请选择.xlsx/.xls文件';se.className='status error';se.style.display='block';return;}
    if(typeof XLSX==='undefined'){se.textContent='❌ SheetJS 未加载，请使用 新品板块_离线版.html （离线版已内置完整依赖）';se.className='status error';se.style.display='block';return;}
    if(typeof computeEngine==='undefined'){se.textContent='❌ 计算引擎未加载，请刷新页面重试';se.className='status error';se.style.display='block';return;}
    se.textContent='⏳ 解析中...';se.className='status';se.style.display='block';
    console.log('[handleFile] 文件:', file.name, '大小:', (file.size/1024).toFixed(1) + 'KB');
    var r=new FileReader();
    r.onload=function(e){
      try{
        var wb=XLSX.read(e.target.result,{type:'array'});
        console.log('[handleFile] Sheets:', wb.SheetNames.join(', '));
        se.textContent='⏳ 检测到Sheet: '+wb.SheetNames.join(',')+'，计算中...';
        setTimeout(function(){
          try{
            console.log('[handleFile] 开始计算...');
            var data=computeEngine(wb);
            console.log('[handleFile] 计算完成, 数据keys:', Object.keys(data).join(', '));
            se.textContent='✅ 计算完成，渲染中...';
            setTimeout(function(){renderAll(data);},50);
          }catch(err){se.textContent='❌ 计算失败: '+err.message;se.className='status error';console.error('[handleFile] 计算错误:', err);}
        },100);
      }catch(err){se.textContent='❌ 解析失败: '+err.message;se.className='status error';console.error('[handleFile] 解析错误:', err);}
    };
    r.onerror=function(){se.textContent='❌ 文件读取失败';se.className='status error';se.style.display='block';};
    r.readAsArrayBuffer(file);
  }
  dz.addEventListener('dragover',function(e){e.preventDefault();dz.classList.add('drag-over');});
  dz.addEventListener('dragleave',function(){dz.classList.remove('drag-over');});
  dz.addEventListener('drop',function(e){e.preventDefault();dz.classList.remove('drag-over');handleFile(e.dataTransfer.files[0]);});
  dz.addEventListener('click',function(e){if(e.target.tagName!=='SPAN')fi.click();});
  fi.addEventListener('change',function(){handleFile(fi.files[0]);});
  document.addEventListener('dragover',function(e){e.preventDefault();});
  document.addEventListener('drop',function(e){e.preventDefault();if(!document.getElementById('upload-overlay').classList.contains('hidden'))handleFile(e.dataTransfer.files[0]);});
})();
