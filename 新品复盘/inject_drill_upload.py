"""
向 新品板块.html 注入 drilldown + 新广告结构 Tab4
输出: 新品板块_4.30-5.27_4weeks_drill_v2.html (upload-compatible drill version)
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT  = 'c:/Users/Hardy/ai-projects/新品复盘/新品板块.html'
OUTPUT = 'c:/Users/Hardy/ai-projects/新品复盘/新品板块_drill_upload.html'

with open(INPUT, 'r', encoding='utf-8') as f:
    html = f.read()
base = len(html)

# ===== 1. Drilldown CSS =====
drill_css = '''
/* ===== Drilldown Panel ===== */
#drill-panel { display: none; position: relative; z-index: 100; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin: 10px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.15); max-width: 100%; }
#drill-panel.open { display: block; animation: drillIn 0.25s ease-out; }
#drill-panel.closing { display: none; }
@keyframes drillIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.drill-trigger { cursor: pointer; color: #0f3460 !important; font-weight: 500 !important; transition: background 0.15s; }
.drill-trigger:hover { background: #e8f0fe !important; }
.drill-trigger.active { background: #d0e0ff !important; color: #0f3460 !important; }
'''

html = html.replace('</style>', drill_css + '\n</style>', 1)

# ===== 2. Drilldown HTML (panel) =====
# Insert before </div> of dashboard-container (last </div> before <script>)
drill_html = '''
<div id="drill-panel">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
    <strong id="drill-title" style="font-size:13px;color:#0f3460"></strong>
    <span id="drill-close" style="cursor:pointer;font-size:20px;color:#999;line-height:1" title="关闭">&times;</span>
  </div>
  <canvas id="drill-canvas" style="max-height:260px"></canvas>
</div>
'''
# Find the last </div> before </body>
body_end = html.find('</body>')
html = html[:body_end] + drill_html + '\n' + html[body_end:]

# ===== 3. Replace Tab4 HTML =====
old_t4_start = html.find('<div class="tab-content" id="tab4">')
old_t4_end = html.find('<!-- ===== Tab5:', old_t4_start)
assert old_t4_start > 0 and old_t4_end > 0, "Cannot find Tab4 HTML"

new_tab4_html = '''  <div class="tab-content" id="tab4">
    <div class="section"><h3>&#128200; 部门占比 &amp; 市占对比</h3>
      <div class="kpi-grid" id="t4-dept-kpi"></div>
    </div>
    <div class="section"><h3>&#127976; PW爬虫市占 vs 新品市占</h3>
      <div class="kpi-grid" id="t4-pw-kpi"></div>
    </div>
    <div class="section"><h3>&#128176; 广告构成分布</h3>
      <div class="kpi-grid" id="t4-comp-kpi"></div>
      <div class="sub-module"><h4>按分析人</h4><div id="t4-comp-an"></div></div>
      <div class="sub-module"><h4>按品线</h4><div id="t4-comp-cat"></div></div>
    </div>
    <div class="section"><h3>&#127991; PLG费率分档（四档）</h3>
      <div class="kpi-grid" id="t4-plg-tier-kpi"></div>
      <div class="sub-module"><h4>按分析人</h4><div id="t4-plg-tier-an"></div></div>
    </div>
    <div class="section"><h3>&#128279; PLP链接开启PLG（ID维度）</h3>
      <div class="kpi-grid" id="t4-plp-plg-link"></div>
    </div>
  </div>'''

html = html[:old_t4_start] + new_tab4_html + '\n\n' + html[old_t4_end:]

# ===== 4. Replace Tab4 nav label =====
html = html.replace('&#128176; 广告追踪</a>', '&#128176; 广告结构</a>')

# ===== 5. Add drilldown JS functions =====
# Insert after compute_engine is defined (before renderAll)
drill_js = '''
// ===== Drilldown Functions =====
var _drillDataMap = null;
function buildDrillDataMap() {
  if (_drillDataMap) return;
  var map = new Map();
  var WLABELS = (DATA.weekLabels4w || ['4.30-5.6','5.7-5.13','5.14-5.20','5.21-5.27']);

  // Tab1: 品线维度
  (DATA.categoryRevenueData || []).forEach(function(d) {
    map.set(d.category, {
      label: d.category, tab: 't1-cat',
      sales4w: d.sales4w || [0,0,0,0],
      revenue4w: d.revenue4w || [0,0,0,0],
      share4w: d.share4w || [0,0,0,0],
      newSku4w: [0,0,0,0]
    });
  });
  // Tab1: 分析人维度
  (DATA.analystRevenueData || []).forEach(function(d) {
    map.set(d.analyst, {
      label: d.analyst, tab: 't1-an',
      sales4w: d.sales4w || [0,0,0,0],
      revenue4w: d.revenue4w || [0,0,0,0],
      share4w: d.share4w || [0,0,0,0],
      newSku4w: [0,0,0,0]
    });
  });

  // 新上架SKU per week
  var weekStarts = [new Date(2026,3,30), new Date(2026,4,7), new Date(2026,4,14), new Date(2026,4,21), new Date(2026,4,28)];
  function weekIdx(ds) {
    if (!ds) return -1;
    var d = new Date(ds);
    if (isNaN(d.getTime())) return -1;
    for (var i=0;i<4;i++) { if (d>=weekStarts[i] && d<weekStarts[i+1]) return i; }
    return -1;
  }
  (DATA.cum43Data || []).forEach(function(d) {
    var wi = weekIdx(d.listDate);
    if (wi < 0) return;
    var entry = map.get(d.category);
    if (entry) entry.newSku4w[wi]++;
    entry = map.get(d.analyst);
    if (entry) entry.newSku4w[wi]++;
  });

  // Tab1: 及时率
  if (DATA.timeliness4w) {
    (DATA.timeliness4w.analysts || []).forEach(function(d) {
      map.set('time:' + d.analyst, {
        label: d.analyst + ' 及时率', tab: 't1-time',
        rates4w: d.rates4w, isTimeliness: true
      });
    });
    if (DATA.timeliness4w.totalRates) {
      map.set('time:总及时率', {
        label: '总及时率', tab: 't1-time',
        rates4w: DATA.timeliness4w.totalRates, isTimeliness: true
      });
    }
  }

  _drillDataMap = map;
}

function showDrillChart(key, data, title) {
  if (window._drillChartInstance) { window._drillChartInstance.destroy(); window._drillChartInstance = null; }
  var panel = document.getElementById('drill-panel');
  if (!panel) return;

  var activeTd = document.querySelector('.drill-trigger.active');
  if (activeTd) {
    var tableWrap = activeTd.closest('.table-scroll-wrap') || activeTd.closest('table');
    if (tableWrap && tableWrap.parentElement) {
      if (panel.parentNode !== tableWrap.parentElement) {
        tableWrap.parentElement.appendChild(panel);
      }
    }
  }

  document.getElementById('drill-title').textContent = title + ' — 4周趋势';
  var WLABELS = DATA.weekLabels4w || ['4.30-5.6','5.7-5.13','5.14-5.20','5.21-5.27'];
  var datasets = [];

  if (data.isTimeliness) {
    datasets.push({label:'及时率(%)',data:data.rates4w,borderColor:'#0f3460',backgroundColor:'rgba(15,52,96,0.1)',tension:0.3,borderWidth:3,pointRadius:5,fill:true,yAxisID:'y'});
  } else {
    var hasSales = data.sales4w && data.sales4w.some(function(v){return v>0;});
    var hasRev = data.revenue4w && data.revenue4w.some(function(v){return v>0;});
    if (!hasSales && !hasRev) {
      document.getElementById('drill-title').textContent = title + ' — 无4周数据';
      panel.classList.add('open'); panel.classList.remove('closing'); return;
    }
    if (hasSales) datasets.push({label:'销量',data:data.sales4w,borderColor:'#0f3460',backgroundColor:'rgba(15,52,96,0.08)',tension:0.3,borderWidth:2.5,pointRadius:4,yAxisID:'y'});
    if (hasRev) datasets.push({label:'销售额($)',data:data.revenue4w,borderColor:'#8e44ad',backgroundColor:'rgba(142,68,173,0.08)',tension:0.3,borderWidth:2.5,pointRadius:4,yAxisID:'y1'});
    if (data.share4w && data.share4w.some(function(v){return v>0;})) {
      datasets.push({label:'市占比(%)',data:data.share4w,borderColor:'#08845a',backgroundColor:'transparent',tension:0.3,borderWidth:2,borderDash:[5,3],pointRadius:3,yAxisID:'y1'});
    }
    var hasNewSku = data.newSku4w && data.newSku4w.some(function(v){return v>0;});
    if (hasNewSku) datasets.push({label:'新上架SKU',data:data.newSku4w,type:'bar',backgroundColor:'rgba(224,123,36,0.35)',borderColor:'#e07b24',borderWidth:1,borderRadius:3,yAxisID:'y'});
  }

  panel.classList.add('open'); panel.classList.remove('closing');
  window._drillChartInstance = new Chart(document.getElementById('drill-canvas'), {
    type: 'line',
    data: { labels: WLABELS, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: data.isTimeliness ? '及时率(%)' : '销量' }, position: 'left' },
        y1: { beginAtZero: true, title: { display: true, text: '金额/占比' }, position: 'right', grid: { drawOnChartArea: false } }
      }
    }
  });
}

function hideDrillChart() {
  if (window._drillChartInstance) { window._drillChartInstance.destroy(); window._drillChartInstance = null; }
  var panel = document.getElementById('drill-panel');
  if (!panel) return;
  panel.classList.add('closing'); panel.classList.remove('open');
  document.querySelectorAll('.drill-trigger.active').forEach(function(td){td.classList.remove('active');});
  window._activeDrillKey = null;
}

function handleDrillClick(td) {
  var key = td.getAttribute('data-drill');
  if (!key) return;
  if (window._activeDrillKey === key) { hideDrillChart(); return; }
  document.querySelectorAll('.drill-trigger.active').forEach(function(t){t.classList.remove('active');});
  td.classList.add('active');
  window._activeDrillKey = key;
  buildDrillDataMap();
  var data = _drillDataMap.get(key);
  if (!data) { hideDrillChart(); return; }
  showDrillChart(key, data, data.label + (key.indexOf('sku:')===0 ? ' SKU趋势' : ' 4周趋势'));
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
    if (!firstTd.getAttribute('data-drill')) firstTd.setAttribute('data-drill', dk);
    firstTd.classList.add('drill-trigger');
    firstTd.style.cursor = 'pointer';
    firstTd.style.color = '#0f3460';
    firstTd.style.fontWeight = '500';
    firstTd.onclick = function(e) { handleDrillClick(this); };
  });
}

// Close button
setTimeout(function() {
  var closeBtn = document.getElementById('drill-close');
  if (closeBtn) closeBtn.onclick = hideDrillChart;
}, 100);

// Override switchTab to close drill
var _origSwitchTab = switchTab;
switchTab = function(tabId, el) {
  hideDrillChart();
  _origSwitchTab(tabId, el);
};
'''

# Insert drill JS before function renderAll
insert_pos = html.find('function renderAll(data) {')
assert insert_pos > 0, "Cannot find renderAll"

# Add computeAdExtras function after drill JS
ad_extras_js = '''
// ===== 广告扩展数据计算 =====
function computeAdExtras(wb, DATA) {
  try {
    // 读取四三销售数据 Sheet Row 2 — 部门总计
    var salesSheet = wb.Sheets['四三销售数据'];
    if (salesSheet) {
      var salesArr = XLSX.utils.sheet_to_json(salesSheet, {header:1});
      if (salesArr.length > 1 && String(salesArr[1][0]||'').trim() === '统计') {
        var deptSales = Number(salesArr[1][2]) || 0;
        var deptRevenue = Number(salesArr[1][3]) || 0;
        var newSales = DATA.totalSales4w ? DATA.totalSales4w[DATA.totalSales4w.length-1] : 0;
        var newRevenue = DATA.totalRev4w ? DATA.totalRev4w[DATA.totalRev4w.length-1] : 0;
        DATA.adDeptPct = {
          salesPct: deptSales ? Math.round(newSales/deptSales*1000)/10 : 0,
          revPct: deptRevenue ? Math.round(newRevenue/deptRevenue*1000)/10 : 0,
          newSales: newSales, newRevenue: Math.round(newRevenue*100)/100,
          deptSales: deptSales, deptRevenue: Math.round(deptRevenue*100)/100
        };
      }
    }

    // 读取 PW表
    var pwSheet = wb.Sheets['PW表'];
    if (pwSheet) {
      var pwArr = XLSX.utils.sheet_to_json(pwSheet, {header:1});
      var ourShareSum = 0, shareCount = 0, totalWeight = 0, weightedSum = 0;

      for (var i = 3; i < pwArr.length; i++) {
        var row = pwArr[i];
        if (!row || !row[0]) continue;
        var rivalShare = row[2];
        var totalSales = Number(row[3]) || 0;
        var ourShare = null;

        if (rivalShare !== null && rivalShare !== undefined && String(rivalShare).trim() !== '市场无出单' && String(rivalShare).trim() !== '') {
          var rs = Number(rivalShare);
          if (!isNaN(rs)) { ourShare = Math.round((1-rs)*1000)/10; }
        } else if (String(rivalShare).trim() === '市场无出单') {
          ourShare = 100;
        } else if (totalSales > Number(row[1]||0)) {
          ourShare = Math.round((totalSales-Number(row[1]||0))/totalSales*1000)/10;
        }

        if (ourShare !== null && !isNaN(ourShare)) {
          ourShareSum += ourShare; shareCount++;
          if (totalSales > 0) { weightedSum += ourShare * totalSales; totalWeight += totalSales; }
        }
      }

      var cumData = DATA.cum43Data || [];
      var skuWR = cumData.filter(function(r){return (r.curRivalQty||0) > 0;});
      var newSalesW = skuWR.reduce(function(s,r){return s+(r.curSalesQty||0);},0);
      var rivalSalesW = skuWR.reduce(function(s,r){return s+(r.curRivalQty||0);},0);
      var newShareW = (newSalesW+rivalSalesW) ? Math.round(newSalesW/(newSalesW+rivalSalesW)*1000)/10 : 0;

      DATA.adPwVsNew = {
        pwShare: totalWeight ? Math.round(weightedSum/totalWeight*10)/10 : (shareCount ? Math.round(ourShareSum/shareCount*10)/10 : 0),
        newShare: newShareW,
        pwTotalLinks: shareCount, pwAvgShare: shareCount ? Math.round(ourShareSum/shareCount*10)/10 : 0,
        newSkuCount: skuWR.length, newTotalSales: newSalesW, newRivalSales: rivalSalesW
      };
    }

    // 广告构成 & PLG费率分档
    var skuData = DATA.cum43Data || [];
    var comp = {'PLP+PLG':0,'单PLP':0,'仅PLG':0,'无广告':0};
    var tiers = {'无广告':0,'低费率':0,'中费率':0,'高费率':0};
    var anComp = {}; var anTiers = {};
    var catComp = {};

    var ANALYSTS = ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'];
    var CATEGORIES = ['车门系统','车身外扩件','挡泥板','机盖及附件','其他','饰条','牌照板支架'];

    skuData.forEach(function(r){
      var an = r.analyst || '未知';
      var cat = r.category || '未分类';
      var hasPlp = (r.plpEnabled === 'Y' || r.plpEnabled === '是');
      var feePct = parseFloat(String(r.plgFee||'0').replace('%','')) || 0;
      var hasPlg = feePct > 0;

      var label = hasPlp && hasPlg ? 'PLP+PLG' : (hasPlp ? '单PLP' : (hasPlg ? '仅PLG' : '无广告'));
      comp[label] = (comp[label]||0) + 1;
      if (!anComp[an]) anComp[an] = {'PLP+PLG':0,'单PLP':0,'仅PLG':0,'无广告':0,total:0,tierNone:0,tierLow:0,tierMid:0,tierHigh:0};
      anComp[an][label]++; anComp[an].total++;
      if (!catComp[cat]) catComp[cat] = {'PLP+PLG':0,'单PLP':0,'仅PLG':0,'无广告':0,total:0};
      catComp[cat][label]++; catComp[cat].total++;

      var tier = feePct === 0 ? '无广告' : (feePct <= 2 ? '低费率' : (feePct <= 4 ? '中费率' : '高费率'));
      tiers[tier] = (tiers[tier]||0) + 1;
      if (anComp[an]) { anComp[an]['tier' + (tier === '无广告' ? 'None' : tier === '低费率' ? 'Low' : tier === '中费率' ? 'Mid' : 'High')]++; }
    });

    DATA.adCompDist = comp;
    DATA.adPlgTierDist = tiers;
    DATA.adCompLabels = ['PLP+PLG','单PLP','仅PLG','无广告'];
    DATA.adPlgTierLabels = ['无广告','低费率','中费率','高费率'];

    DATA.adAnDetail = ANALYSTS.filter(function(a){return anComp[a];}).map(function(a){
      var d = anComp[a];
      return {analyst:a, total:d.total||0, plpPlg:d['PLP+PLG']||0, plpOnly:d['单PLP']||0, plgOnly:d['仅PLG']||0, noAd:d['无广告']||0, tierNone:d.tierNone||0, tierLow:d.tierLow||0, tierMid:d.tierMid||0, tierHigh:d.tierHigh||0};
    });
    DATA.adCatDetail = CATEGORIES.filter(function(c){return catComp[c];}).map(function(c){
      var d = catComp[c];
      return {category:c, total:d.total||0, plpPlg:d['PLP+PLG']||0, plpOnly:d['单PLP']||0, plgOnly:d['仅PLG']||0, noAd:d['无广告']||0};
    });

    // PLP链接PLG — from PLP明细 sheet
    var plpSheet = wb.Sheets['PLP明细'];
    if (plpSheet) {
      var plpArr = XLSX.utils.sheet_to_json(plpSheet, {header:1});
      var plpPlgMap = {};
      for (var j = 1; j < plpArr.length; j++) {
        var pr = plpArr[j];
        var psku = String(pr[2]||'').trim();
        var plgFlag = String(pr[4]||'').trim();
        if (!psku) continue;
        if (!plpPlgMap[psku]) plpPlgMap[psku] = {total:0, y:0};
        plpPlgMap[psku].total++;
        if (plgFlag === 'Y') plpPlgMap[psku].y++;
      }
      var totalSku = 0, plgY = 0;
      for (var k in plpPlgMap) { totalSku++; if (plpPlgMap[k].y > 0) plgY++; }
      DATA.adPlpPlgLink = {totalSku: totalSku, plgY: plgY, plgN: totalSku - plgY};
    } else {
      DATA.adPlpPlgLink = {totalSku:0, plgY:0, plgN:0};
    }
  } catch(e) {
    console.error('computeAdExtras error:', e);
  }
  return DATA;
}
'''

html = html[:insert_pos] + drill_js + ad_extras_js + '\n' + html[insert_pos:]

# ===== 6. Add drill wiring to renderAll =====
# After renderFns loop, add drill trigger setup
old_loop_end = html.find('setTimeout(function() {')
assert old_loop_end > 0, "Cannot find setTimeout in renderAll"

drill_wiring = '''
  // Wire drilldown triggers
  setTimeout(function() {
    setupDrillTrigger('t1-cat-table', '');
    setupDrillTrigger('t1-an-table', '');
    if (document.getElementById('t1-time-table')) setupDrillTrigger('t1-time-table', 'time:');
  }, 200);

'''

html = html[:old_loop_end] + drill_wiring + html[old_loop_end:]

# ===== 7. Replace renderTab4 with new ad structure =====
old_t4_fn_start = html.find('function renderTab4(){')
old_t4_fn_end = html.find('// ===== Tab5:', old_t4_fn_start)
assert old_t4_fn_start > 0 and old_t4_fn_end > 0, "Cannot find renderTab4"

new_render_tab4 = '''function renderTab4(){
  // 部门占比 KPI
  document.getElementById('t4-dept-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">新品销量占部门比</div><div class="val">' + (DATA.adDeptPct ? DATA.adDeptPct.salesPct : '--') + '%</div><div class="hb">新品' + (DATA.adDeptPct ? DATA.adDeptPct.newSales : '--') + ' / 部门' + (DATA.adDeptPct ? DATA.adDeptPct.deptSales : '--') + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品销售额占部门比</div><div class="val">' + (DATA.adDeptPct ? DATA.adDeptPct.revPct : '--') + '%</div><div class="hb">新品$' + fmtMoney((DATA.adDeptPct||{}).newRevenue||0) + ' / 部门$' + fmtMoney((DATA.adDeptPct||{}).deptRevenue||0) + '</div></div>';

  // PW vs 新品
  var p = DATA.adPwVsNew || {};
  document.getElementById('t4-pw-kpi').innerHTML =
    '<div class="kpi-card purple"><div class="label">PW爬虫市占</div><div class="val">' + (p.pwShare||'--') + '%</div><div class="hb">' + (p.pwTotalLinks||'--') + '个有效链接</div></div>' +
    '<div class="kpi-card success"><div class="label">新品加权市占</div><div class="val">' + (p.newShare||'--') + '%</div><div class="hb">' + (p.newSkuCount||'--') + '个有对手SKU</div></div>' +
    '<div class="kpi-card info"><div class="label">差值</div><div class="val">' + (Math.abs((p.pwShare||0)-(p.newShare||0)).toFixed(1)) + '%</div><div class="hb">PW vs 新品（维度不同，平行参考）</div></div>';

  // 广告构成
  var c = DATA.adCompDist || {};
  var compLabels = DATA.adCompLabels || ['PLP+PLG','单PLP','仅PLG','无广告'];
  var compColors = {'PLP+PLG':'#c0392b','单PLP':'#2980b9','仅PLG':'#e67e22','无广告':'#95a5a6'};
  var ch = '';
  compLabels.forEach(function(k){ ch += '<div class="kpi-card" style="border-left:4px solid ' + (compColors[k]||'#999') + '"><div class="label">' + k + '</div><div class="val">' + (c[k]||0) + '</div></div>'; });
  document.getElementById('t4-comp-kpi').innerHTML = ch;

  // 广告构成按分析人
  var anDetail = DATA.adAnDetail || [];
  var ah = '<table class="data-table"><thead><tr><th>分析人</th><th>总数</th><th>PLP+PLG</th><th>单PLP</th><th>仅PLG</th><th>无广告</th></tr></thead><tbody>';
  var anT = {};
  anDetail.forEach(function(d){
    ah += '<tr><td>' + d.analyst + '</td><td>' + d.total + '</td><td style="color:#c0392b;font-weight:600">' + d.plpPlg + '</td><td>' + d.plpOnly + '</td><td>' + d.plgOnly + '</td><td>' + d.noAd + '</td></tr>';
    for (var k in d) { if (k!=='analyst') anT[k] = (anT[k]||0) + d[k]; }
  });
  ah += '<tfoot><tr class="total-row"><td><b>合计</b></td><td><b>' + (anT.total||0) + '</b></td><td><b>' + (anT.plpPlg||0) + '</b></td><td><b>' + (anT.plpOnly||0) + '</b></td><td><b>' + (anT.plgOnly||0) + '</b></td><td><b>' + (anT.noAd||0) + '</b></td></tr></tfoot></tbody></table>';
  document.getElementById('t4-comp-an').innerHTML = ah;

  // 广告构成按品线
  var catDetail = DATA.adCatDetail || [];
  var ch2 = '<table class="data-table"><thead><tr><th>品线</th><th>总数</th><th>PLP+PLG</th><th>单PLP</th><th>仅PLG</th><th>无广告</th></tr></thead><tbody>';
  var ct = {};
  catDetail.forEach(function(d){
    ch2 += '<tr><td>' + d.category + '</td><td>' + d.total + '</td><td style="color:#c0392b;font-weight:600">' + d.plpPlg + '</td><td>' + d.plpOnly + '</td><td>' + d.plgOnly + '</td><td>' + d.noAd + '</td></tr>';
    for (var k in d) { if (k!=='category') ct[k] = (ct[k]||0) + d[k]; }
  });
  ch2 += '<tfoot><tr class="total-row"><td><b>合计</b></td><td><b>' + (ct.total||0) + '</b></td><td><b>' + (ct.plpPlg||0) + '</b></td><td><b>' + (ct.plpOnly||0) + '</b></td><td><b>' + (ct.plgOnly||0) + '</b></td><td><b>' + (ct.noAd||0) + '</b></td></tr></tfoot></tbody></table>';
  document.getElementById('t4-comp-cat').innerHTML = ch2;

  // PLG费率分档
  var t = DATA.adPlgTierDist || {};
  var tierLabels = DATA.adPlgTierLabels || ['无广告','低费率','中费率','高费率'];
  var tierColors = {'高费率':'#c0392b','中费率':'#e67e22','低费率':'#27ae60','无广告':'#95a5a6'};
  var th = '';
  tierLabels.forEach(function(k){ th += '<div class="kpi-card" style="border-left:4px solid ' + (tierColors[k]||'#999') + '"><div class="label">' + k + '</div><div class="val">' + (t[k]||0) + '</div></div>'; });
  document.getElementById('t4-plg-tier-kpi').innerHTML = th;

  // PLG费率按分析人
  var ta = '<table class="data-table"><thead><tr><th>分析人</th><th>总数</th><th>无广告</th><th>低(&le;2%)</th><th>中(2-4%)</th><th>高(>4%)</th></tr></thead><tbody>';
  var tt = {};
  anDetail.forEach(function(d){
    ta += '<tr><td>' + d.analyst + '</td><td>' + d.total + '</td><td>' + d.tierNone + '</td><td>' + d.tierLow + '</td><td>' + d.tierMid + '</td><td style="color:#c0392b;font-weight:600">' + d.tierHigh + '</td></tr>';
    for (var k in d) { if (k!=='analyst') tt[k] = (tt[k]||0) + d[k]; }
  });
  ta += '<tfoot><tr class="total-row"><td><b>合计</b></td><td><b>' + (tt.total||0) + '</b></td><td><b>' + (tt.tierNone||0) + '</b></td><td><b>' + (tt.tierLow||0) + '</b></td><td><b>' + (tt.tierMid||0) + '</b></td><td><b>' + (tt.tierHigh||0) + '</b></td></tr></tfoot></tbody></table>';
  document.getElementById('t4-plg-tier-an').innerHTML = ta;

  // PLP链接开启PLG
  var l = DATA.adPlpPlgLink || {};
  document.getElementById('t4-plp-plg-link').innerHTML =
    '<div class="kpi-card info"><div class="label">SKU总数</div><div class="val">' + (l.totalSku||0) + '</div></div>' +
    '<div class="kpi-card success"><div class="label">开启PLG</div><div class="val">' + (l.plgY||0) + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">未开启PLG</div><div class="val">' + (l.plgN||0) + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">PLG开启率</div><div class="val">' + (l.totalSku ? (l.plgY/l.totalSku*100).toFixed(1) + '%' : '-') + '</div></div>';
}'''

html = html[:old_t4_fn_start] + new_render_tab4 + '\n\n' + html[old_t4_fn_end:]

# ===== 7b. Modify upload handler to call computeAdExtras =====
html = html.replace(
    'var data=computeEngine(wb);',
    'var data=computeEngine(wb);\n\t            data=computeAdExtras(wb, data);'
)

# ===== 8. Write output =====
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

# ===== 9. Validate =====
print(f"Input:  {INPUT} ({base//1024}KB)")
print(f"Output: {OUTPUT} ({len(html)//1024}KB, {len(html)-base:+d} bytes)")

checks = ['drill-panel', 'drill-canvas', 'buildDrillDataMap', 'setupDrillTrigger',
          'handleDrillClick', 'showDrillChart', 'hideDrillChart',
          't4-dept-kpi', 't4-pw-kpi', 't4-comp-kpi', 't4-plg-tier-kpi', 't4-plp-plg-link',
          't4-comp-an', 't4-comp-cat', 't4-plg-tier-an',
          'adDeptPct', 'adPwVsNew', 'adCompDist', 'adPlgTierDist']
for c in checks:
    assert c in html, f"MISSING: {c}"

# Brace check
ob, cb = html.count('{'), html.count('}')
op, cp = html.count('('), html.count(')')
print(f"Braces: {ob}/{cb} {'OK' if ob==cb else 'MISMATCH'}")
print(f"Parens: {op}/{cp} {'OK' if op==cp else 'MISMATCH'}")
print(f"All {len(checks)} checks passed!")
print("\nDone! Open the file in browser and drag-drop Excel to test.")
