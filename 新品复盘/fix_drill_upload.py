"""
修复 新品板块_drill_upload.html 三个问题：
1. 部门占比 + PW市占 KPI 移到 Tab1（总盘概览）
2. PLP链接PLG 改为 SKU级广告构成明细表
3. 修 drilldown 消失：setupDrillTrigger 注入到正确位置
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT  = 'c:/Users/Hardy/ai-projects/新品复盘/新品板块_drill_upload.html'
OUTPUT = INPUT  # overwrite

with open(INPUT, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ===== FIX 1: Add dept% + PW KPI cards to Tab1 HTML =====
# Find Tab1 KPI section: <div class="kpi-grid" id="t1-kpi"></div>
t1_kpi_pos = html.find('<div class="kpi-grid" id="t1-kpi"></div>')
assert t1_kpi_pos > 0, "Cannot find t1-kpi"

t1_new_kpi = '''<div class="kpi-grid" id="t1-kpi"></div>
    <!-- 部门占比 + PW市占 -->
    <div class="section"><h3>&#127976; 部门占比 &amp; PW爬虫市占</h3>
      <div class="kpi-grid" id="t1-dept-kpi"></div>
    </div>'''

html = html.replace('<div class="kpi-grid" id="t1-kpi"></div>', t1_new_kpi, 1)
changes += 1
print("Fix1: Added dept+PW KPI section to Tab1 HTML")

# ===== FIX 2: Remove dept+PW from Tab4 HTML =====
html = html.replace('''    <div class="section"><h3>&#128200; 部门占比 &amp; 市占对比</h3>
      <div class="kpi-grid" id="t4-dept-kpi"></div>
    </div>
    <div class="section"><h3>&#127976; PW爬虫市占 vs 新品市占</h3>
      <div class="kpi-grid" id="t4-pw-kpi"></div>
    </div>
''', '', 1)
changes += 1
print("Fix2: Removed dept+PW from Tab4 HTML")

# ===== FIX 3: Replace PLP-PLG link in Tab4 with ad composition detail table =====
old_plp_plg = '''    <div class="section"><h3>&#128279; PLP链接开启PLG（ID维度）</h3>
      <div class="kpi-grid" id="t4-plp-plg-link"></div>
    </div>'''
new_plp_plg = '''    <div class="section"><h3>&#128279; 广告构成明细（SKU级）</h3>
      <div id="t4-plp-plg-link"></div>
    </div>'''
html = html.replace(old_plp_plg, new_plp_plg, 1)
changes += 1

# ===== FIX 4: Update renderTab1 to include dept+PW KPI rendering =====
# Find beginning of renderTab1
t1_fn = html.find('function renderTab1() {')
assert t1_fn > 0

# Find where t1-kpi is set (insert after)
t1_kpi_render = html.find("document.getElementById('t1-kpi').innerHTML", t1_fn)
t1_kpi_end = html.find(";\n\n  document.getElementById('t1-ord8')", t1_kpi_render)
if t1_kpi_end < 0:
    t1_kpi_end = html.find(";\n\n  //", t1_kpi_render + 200)
if t1_kpi_end < 0:
    t1_kpi_end = html.find("document.getElementById('t1-ord8')", t1_kpi_render) - 3

assert t1_kpi_end > 0, "Cannot find end of t1-kpi render"

dept_render = '''
  // 部门占比 + PW市占 KPI（从广告板块移到总盘概览）
  var dp = DATA.adDeptPct || {};
  var pw = DATA.adPwVsNew || {};
  document.getElementById('t1-dept-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">新品销量占部门比</div><div class="val">' + (dp.salesPct || '--') + '%</div><div class="hb">新品' + (dp.newSales || '--') + ' / 部门' + (dp.deptSales || '--') + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品销售额占部门比</div><div class="val">' + (dp.revPct || '--') + '%</div><div class="hb">新品$' + fmtMoney(dp.newRevenue||0) + ' / 部门$' + fmtMoney(dp.deptRevenue||0) + '</div></div>' +
    '<div class="kpi-card purple"><div class="label">PW爬虫市占</div><div class="val">' + (pw.pwShare || '--') + '%</div><div class="hb">' + (pw.pwTotalLinks || '--') + '个有效链接</div></div>' +
    '<div class="kpi-card success"><div class="label">新品加权市占</div><div class="val">' + (pw.newShare || '--') + '%</div><div class="hb">' + (pw.newSkuCount || '--') + '个有对手SKU</div></div>' +
    '<div class="kpi-card info"><div class="label">市占差值</div><div class="val">' + (Math.abs((pw.pwShare||0)-(pw.newShare||0)).toFixed(1)) + '%</div><div class="hb">PW vs 新品（维度不同，平行参考）</div></div>';'''

html = html[:t1_kpi_end] + dept_render + html[t1_kpi_end:]
changes += 1
print("Fix4: Added dept+PW rendering to renderTab1")

# ===== FIX 5: Update renderTab4 — remove dept+PW rendering, fix PLP-PLG section =====
# Remove dept+PW rendering from renderTab4
html = html.replace('''  // 部门占比 KPI
  document.getElementById('t4-dept-kpi').innerHTML =
    '<div class="kpi-card primary"><div class="label">新品销量占部门比</div><div class="val">' + (DATA.adDeptPct ? DATA.adDeptPct.salesPct : '--') + '%</div><div class="hb">新品' + (DATA.adDeptPct ? DATA.adDeptPct.newSales : '--') + ' / 部门' + (DATA.adDeptPct ? DATA.adDeptPct.deptSales : '--') + '</div></div>' +
    '<div class="kpi-card info"><div class="label">新品销售额占部门比</div><div class="val">' + (DATA.adDeptPct ? DATA.adDeptPct.revPct : '--') + '%</div><div class="hb">新品$' + fmtMoney((DATA.adDeptPct||{}).newRevenue||0) + ' / 部门$' + fmtMoney((DATA.adDeptPct||{}).deptRevenue||0) + '</div></div>';

  // PW vs 新品
  var p = DATA.adPwVsNew || {};
  document.getElementById('t4-pw-kpi').innerHTML =
    '<div class="kpi-card purple"><div class="label">PW爬虫市占</div><div class="val">' + (p.pwShare||'--') + '%</div><div class="hb">' + (p.pwTotalLinks||'--') + '个有效链接</div></div>' +
    '<div class="kpi-card success"><div class="label">新品加权市占</div><div class="val">' + (p.newShare||'--') + '%</div><div class="hb">' + (p.newSkuCount||'--') + '个有对手SKU</div></div>' +
    '<div class="kpi-card info"><div class="label">差值</div><div class="val">' + (Math.abs((p.pwShare||0)-(p.newShare||0)).toFixed(1)) + '%</div><div class="hb">PW vs 新品（维度不同，平行参考）</div></div>';

  // 广告构成''', '''  // 广告构成''', 1)
changes += 1

# Replace PLP-PLG link rendering with ad composition detail table
old_plp_render = '''  // PLP链接开启PLG
  var l = DATA.adPlpPlgLink || {};
  document.getElementById('t4-plp-plg-link').innerHTML =
    '<div class="kpi-card info"><div class="label">SKU总数</div><div class="val">' + (l.totalSku||0) + '</div></div>' +
    '<div class="kpi-card success"><div class="label">开启PLG</div><div class="val">' + (l.plgY||0) + '</div></div>' +
    '<div class="kpi-card warning"><div class="label">未开启PLG</div><div class="val">' + (l.plgN||0) + '</div></div>' +
    '<div class="kpi-card primary"><div class="label">PLG开启率</div><div class="val">' + (l.totalSku ? (l.plgY/l.totalSku*100).toFixed(1) + '%' : '-') + '</div></div>';'''

new_plp_render = '''  // 广告构成明细（SKU级：PLP+PLG标签 + 链接数）
  var cumData = DATA.cum43Data || [];
  // Build SKU-level ad detail
  var plpBoth = [], plpOnly = [], plgOnly = [], noAd = [];
  cumData.forEach(function(r){
    var hasPlp = (r.plpEnabled === 'Y' || r.plpEnabled === '是');
    var feePct = parseFloat(String(r.plgFee||'0').replace('%','')) || 0;
    var hasPlg = feePct > 0;
    var item = {sku: r.SKU, analyst: r.analyst, category: r.category, plp: hasPlp, plg: hasPlg, plgFee: feePct};
    if (hasPlp && hasPlg) plpBoth.push(item);
    else if (hasPlp) plpOnly.push(item);
    else if (hasPlg) plgOnly.push(item);
    else noAd.push(item);
  });

  function renderAdGroup(items, title, color) {
    if (!items.length) return '<h4 style="color:'+color+'">' + title + '：0个SKU</h4>';
    var h = '<h4 style="color:'+color+';margin:16px 0 8px">' + title + '：' + items.length + '个SKU</h4>';
    h += '<div class="table-scroll-wrap" style="max-height:300px"><table class="data-table"><thead><tr><th>SKU</th><th>分析人</th><th>品类</th><th>PLG费率</th></tr></thead><tbody>';
    items.forEach(function(d){ h += '<tr><td>' + d.sku + '</td><td>' + d.analyst + '</td><td>' + d.category + '</td><td>' + d.plgFee.toFixed(1) + '%</td></tr>'; });
    h += '</tbody></table></div>';
    return h;
  }
  var detailH = '<div class="kpi-grid" style="margin-bottom:12px">';
  detailH += '<div class="kpi-card" style="border-left:4px solid #c0392b"><div class="label">PLP+PLG同开</div><div class="val">' + plpBoth.length + '</div></div>';
  detailH += '<div class="kpi-card" style="border-left:4px solid #2980b9"><div class="label">单PLP</div><div class="val">' + plpOnly.length + '</div></div>';
  detailH += '<div class="kpi-card" style="border-left:4px solid #e67e22"><div class="label">仅PLG</div><div class="val">' + plgOnly.length + '</div></div>';
  detailH += '<div class="kpi-card" style="border-left:4px solid #95a5a6"><div class="label">无广告</div><div class="val">' + noAd.length + '</div></div></div>';
  detailH += renderAdGroup(plpBoth, 'PLP+PLG同开', '#c0392b');
  detailH += renderAdGroup(plpOnly, '仅开启PLP', '#2980b9');
  detailH += renderAdGroup(plgOnly, '仅开启PLG', '#e67e22');
  detailH += renderAdGroup(noAd, '无广告投放', '#95a5a6');
  document.getElementById('t4-plp-plg-link').innerHTML = detailH;'''

html = html.replace(old_plp_render, new_plp_render, 1)
changes += 1
print("Fix5: Replaced PLP-PLG link with ad composition detail table")

# ===== FIX 6: Fix drill wiring injection — target the RIGHT setTimeout =====
# The old wiring went into the wrong setTimeout. Let me redo it.
# First, find and remove the wrongly-placed wiring
# The correct place is right before "setTimeout(function() {\n    try { initChartOrd8()"
old_bad_wiring = '''  // Wire drilldown triggers
  setTimeout(function() {
    setupDrillTrigger('t1-cat-table', '');
    setupDrillTrigger('t1-an-table', '');
    if (document.getElementById('t1-time-table')) setupDrillTrigger('t1-time-table', 'time:');
  }, 200);

'''
if old_bad_wiring in html:
    html = html.replace(old_bad_wiring, '', 1)
    print("Fix6a: Removed incorrectly placed drill wiring")

# Now find the specific setTimeout in renderAll that calls initChartOrd8
# Pattern: "setTimeout(function() {\n    try { initChartOrd8()"
correct_target = html.find('setTimeout(function() {\n    try { initChartOrd8()')
if correct_target < 0:
    correct_target = html.find('setTimeout(function() {\n      try { initChartOrd8()')
assert correct_target > 0, "Cannot find initChartOrd8 setTimeout"

# Insert drill wiring BEFORE this setTimeout
drill_wiring = '''  // Wire drilldown triggers on rendered tables
  setTimeout(function() {
    try {
      buildDrillDataMap();
      setupDrillTrigger('t1-cat-table', '');
      setupDrillTrigger('t1-an-table', '');
      if (document.getElementById('t1-time-table')) setupDrillTrigger('t1-time-table', 'time:');
    } catch(e) { console.error('Drill wiring error:', e); }
  }, 300);

  '''
html = html[:correct_target] + drill_wiring + html[correct_target:]
changes += 1
print(f"Fix6b: Drill wiring injected before initChartOrd8 setTimeout at pos {correct_target}")

# ===== FIX 7: Update Tab4 section title =====
html = html.replace('<h3>&#128202; 四三累计</h3>', '<h3>&#128202; 四三累计</h3>')  # no-op, placeholder

# ===== Write =====
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

# ===== Validate =====
print(f"\nTotal changes: {changes}")
ob, cb = html.count('{'), html.count('}')
op, cp = html.count('('), html.count(')')
print(f"Braces: {ob}/{cb} {'OK' if ob==cb else 'MISMATCH!'}")
print(f"Parens: {op}/{cp} {'OK' if op==cp else 'MISMATCH!'}")

key_checks = [
    't1-dept-kpi', 'setupDrillTrigger', 'buildDrillDataMap',
    't4-comp-kpi', 't4-plg-tier-kpi', 't4-plp-plg-link', 't4-comp-an', 't4-comp-cat',
    'PLP+PLG同开', 'renderAdGroup',
    'computeAdExtras', 'drill-panel'
]
for c in key_checks:
    assert c in html, f"MISSING: {c}"
print(f"All {len(key_checks)} checks passed!")
print(f"Size: {len(html)//1024}KB")
print("\nDone! Refresh browser to test.")
