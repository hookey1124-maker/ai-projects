"""
同步修复 drill_v2.html（正式看板）：
1. 部门占比 + PW市占 KPI 从 Tab4 移到 Tab1
2. Tab4 PLP链接PLG 改为 SKU级广告构成明细表
3. Tab6 汇报输出新增部门占比+广告构成+PLG费率+下周方向
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT  = 'c:/Users/Hardy/ai-projects/新品复盘/新品板块_4.30-5.27_4weeks_drill_v2.html'
OUTPUT = INPUT.replace('_v2.html', '_v3.html')

with open(INPUT, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ===== FIX 1: Tab1 HTML — Add dept+PW KPI after t1-kpi =====
old_t1 = '<div class="kpi-grid" id="t1-kpi"></div>\n    <div class="chart-grid">'
new_t1 = '<div class="kpi-grid" id="t1-kpi"></div>\n    <div class="section"><h3>&#127976; 部门占比 &amp; PW爬虫市占</h3>\n      <div class="kpi-grid" id="t1-dept-kpi"></div>\n    </div>\n    <div class="chart-grid">'
html = html.replace(old_t1, new_t1, 1)
changes += 1
print("Fix1: Added dept+PW KPI section to Tab1 HTML")

# ===== FIX 2: Tab1 JS — Add dept+PW KPI rendering =====
# Find the end of t1-kpi.innerHTML line
t1_kpi_sentinel = "<div class=\"kpi-card info\"><div class=\"label\">分析及时率</div><div class=\"val\">' + timelinessData.total.timelyRate + '</div><div class=\"hb\">' + hbSign(timelinessData.total.change) + '</div></div>';"
assert t1_kpi_sentinel in html, "Cannot find t1-kpi end"

t1_dept_render = "\n  // 部门占比 + PW市占 KPI（从广告板块移到总盘概览）\n  var deptKpiHtml = '';\n  deptKpiHtml += '<div class=\"kpi-card primary\"><div class=\"label\">新品销量占部门比</div><div class=\"val\">' + adDeptPct.salesPct + '%</div><div class=\"hb\">新品' + fmtNum(adDeptPct.newSales) + ' / 部门' + fmtNum(adDeptPct.deptSales) + '</div></div>';\n  deptKpiHtml += '<div class=\"kpi-card info\"><div class=\"label\">新品销售额占部门比</div><div class=\"val\">' + adDeptPct.revPct + '%</div><div class=\"hb\">新品$' + fmtMoney(adDeptPct.newRevenue) + ' / 部门$' + fmtMoney(adDeptPct.deptRevenue) + '</div></div>';\n  deptKpiHtml += '<div class=\"kpi-card purple\"><div class=\"label\">PW爬虫市占</div><div class=\"val\">' + adPwVsNew.pwShare + '%</div><div class=\"hb\">' + adPwVsNew.pwTotalLinks + '个有效链接</div></div>';\n  deptKpiHtml += '<div class=\"kpi-card success\"><div class=\"label\">新品加权市占</div><div class=\"val\">' + adPwVsNew.newShare + '%</div><div class=\"hb\">' + adPwVsNew.newSkuCount + '个有对手SKU | 我方' + fmtNum(adPwVsNew.newTotalSales) + ' / 对手' + fmtNum(adPwVsNew.newRivalSales) + '</div></div>';\n  deptKpiHtml += '<div class=\"kpi-card info\"><div class=\"label\">市占差值</div><div class=\"val\">' + (Math.abs(adPwVsNew.pwShare - adPwVsNew.newShare)).toFixed(1) + '%</div><div class=\"hb\">PW vs 新品（维度不同，平行参考）</div></div>';\n  document.getElementById('t1-dept-kpi').innerHTML = deptKpiHtml;\n"
html = html.replace(t1_kpi_sentinel, t1_kpi_sentinel + t1_dept_render, 1)
changes += 1
print("Fix2: Added dept+PW rendering to Tab1 JS")

# ===== FIX 3: Tab4 HTML — Remove dept+PW, update PLP-PLG =====
old_t4 = '    <div class="section"><h3>&#128200; 部门占比 &amp; 市占对比</h3>\n      <div class="kpi-grid" id="t4-dept-kpi"></div>\n    </div>\n    <div class="section"><h3>&#127976; PW爬虫市占 vs 新品市占</h3>\n      <div class="kpi-grid" id="t4-pw-kpi"></div>\n    </div>\n    '
html = html.replace(old_t4, '', 1)
changes += 1
print("Fix3: Removed dept+PW from Tab4 HTML")

old_plp_html = '    <div class="section"><h3>&#128279; PLP链接开启PLG（ID维度）</h3>\n      <div class="kpi-grid" id="t4-plp-plg-link"></div>\n    </div>'
new_plp_html = '    <div class="section"><h3>&#128279; 广告构成明细（SKU级）</h3>\n      <div id="t4-plp-plg-link"></div>\n    </div>'
html = html.replace(old_plp_html, new_plp_html, 1)
changes += 1
print("Fix3b: Updated PLP-PLG section title")

# ===== FIX 4: Tab4 JS — Remove dept+PW rendering, remove unused vars, replace PLP-PLG =====
# Remove dept+PW JS
old_dp_js = "  var d = adDeptPct;\n  var p = adPwVsNew;\n  var c = adCompDist;\n  var t = adPlgTierDist;\n  var l = adPlpPlgLink;"
new_dp_js = "  var c = adCompDist;\n  var t = adPlgTierDist;"
html = html.replace(old_dp_js, new_dp_js, 1)
changes += 1

# Remove the dept+PW KPI rendering code
t4_dept_start = "  // 部门占比 KPI\n  document.getElementById('t4-dept-kpi').innerHTML ="
t4_dept_end = "    '<div class=\"kpi-card info\"><div class=\"label\">差值</div><div class=\"val\">3.4%</div><div class=\"hb\">PW vs 新品（维度不同，平行参考）</div></div>';\n\n  // 广告构成 KPI"
pos_start = html.find(t4_dept_start)
pos_end = html.find(t4_dept_end)
assert pos_start >= 0, "Cannot find Tab4 dept JS start"
assert pos_end >= 0, "Cannot find Tab4 dept JS end"
html = html[:pos_start] + "  // 广告构成 KPI" + html[pos_end + len(t4_dept_end):]
changes += 1
print("Fix4: Removed dept+PW JS from Tab4")

# Replace PLP-PLG rendering
old_plp_js = "  // PLP链接开启PLG (ID维度)\n  document.getElementById('t4-plp-plg-link').innerHTML =\n    '<div class=\"kpi-card info\"><div class=\"label\">SKU总数</div><div class=\"val\">' + l.totalSku + '</div></div>' +\n    '<div class=\"kpi-card success\"><div class=\"label\">开启PLG</div><div class=\"val\">' + l.plgY + '</div></div>' +\n    '<div class=\"kpi-card warning\"><div class=\"label\">未开启PLG</div><div class=\"val\">' + l.plgN + '</div></div>' +\n    '<div class=\"kpi-card primary\"><div class=\"label\">PLG开启率</div><div class=\"val\">' + (l.totalSku ? (l.plgY/l.totalSku*100).toFixed(1) + '%' : '-') + '</div></div>';"
assert old_plp_js in html, "Cannot find old PLP-PLG JS"

new_plp_js = "  // 广告构成明细（SKU级：PLP+PLG标签 + SKU列表）\n  var cumData = cum43Data || [];\n  var plpBoth = [], plpOnly = [], plgOnly = [], noAd = [];\n  cumData.forEach(function(r){\n    var hasPlp = (r.plpEnabled === 'Y' || r.plpEnabled === '是');\n    var feePct = parseFloat(String(r.plgFee||'0').replace('%','')) || 0;\n    var hasPlg = feePct > 0;\n    var item = {sku: r.SKU, analyst: r.analyst, category: r.category, plgFee: feePct};\n    if (hasPlp && hasPlg) plpBoth.push(item);\n    else if (hasPlp) plpOnly.push(item);\n    else if (hasPlg) plgOnly.push(item);\n    else noAd.push(item);\n  });\n\n  function renderAdGroup(items, title, color) {\n    if (!items.length) return '<h4 style=\"color:'+color+';margin:16px 0 8px\">' + title + '：0个SKU</h4>';\n    var h = '<h4 style=\"color:'+color+';margin:16px 0 8px\">' + title + '：' + items.length + '个SKU</h4>';\n    h += '<div class=\"table-scroll-wrap\" style=\"max-height:300px\"><table class=\"data-table\"><thead><tr><th>SKU</th><th>分析人</th><th>品类</th><th>PLG费率</th></tr></thead><tbody>';\n    items.forEach(function(d){ h += '<tr><td>' + d.sku + '</td><td>' + d.analyst + '</td><td>' + d.category + '</td><td>' + d.plgFee.toFixed(1) + '%</td></tr>'; });\n    h += '</tbody></table></div>';\n    return h;\n  }\n  var detailH = '<div class=\"kpi-grid\" style=\"margin-bottom:12px\">';\n  detailH += '<div class=\"kpi-card\" style=\"border-left:4px solid #c0392b\"><div class=\"label\">PLP+PLG同开</div><div class=\"val\">' + plpBoth.length + '</div></div>';\n  detailH += '<div class=\"kpi-card\" style=\"border-left:4px solid #2980b9\"><div class=\"label\">单PLP</div><div class=\"val\">' + plpOnly.length + '</div></div>';\n  detailH += '<div class=\"kpi-card\" style=\"border-left:4px solid #e67e22\"><div class=\"label\">仅PLG</div><div class=\"val\">' + plgOnly.length + '</div></div>';\n  detailH += '<div class=\"kpi-card\" style=\"border-left:4px solid #95a5a6\"><div class=\"label\">无广告</div><div class=\"val\">' + noAd.length + '</div></div></div>';\n  detailH += renderAdGroup(plpBoth, 'PLP+PLG同开', '#c0392b');\n  detailH += renderAdGroup(plpOnly, '仅开启PLP', '#2980b9');\n  detailH += renderAdGroup(plgOnly, '仅开启PLG', '#e67e22');\n  detailH += renderAdGroup(noAd, '无广告投放', '#95a5a6');\n  document.getElementById('t4-plp-plg-link').innerHTML = detailH;"
html = html.replace(old_plp_js, new_plp_js, 1)
changes += 1
print("Fix4b: Replaced PLP-PLG with SKU detail tables")

# ===== FIX 5: Tab6 汇报输出更新 =====
# Fix 5a: Add dept+PW to report section 1 (总盘概览)
sentinel_a = "【分析人维度】\\n' + analystRevenueData.map(function(d){\n        return d.analyst + ': ' + d.curSku + 'SKU, 销量' + fmtNum(d.curSalesQty) + '(环比' + d.salesQtyChange + '), 销售额' + fmtMoney(d.curRevenue) + '(环比' + d.revenueChange + '), 市占比' + d.curMarketShare + '%(环比' + d.marketShareChange + ')';\n      }).join('\\n')"
assert sentinel_a in html, "Cannot find 分析人维度 end in report"

dept_section = " + '\\n\\n' +\n      '【部门占比】\\n' +\n      '新品销量占部门比: ' + adDeptPct.salesPct + '% (新品' + fmtNum(adDeptPct.newSales) + ' / 部门' + fmtNum(adDeptPct.deptSales) + ')\\n' +\n      '新品销售额占部门比: ' + adDeptPct.revPct + '% (新品$' + fmtMoney(adDeptPct.newRevenue) + ' / 部门$' + fmtMoney(adDeptPct.deptRevenue) + ')\\n\\n' +\n      '【PW爬虫市占 vs 新品市占】\\n' +\n      'PW爬虫加权市占: ' + adPwVsNew.pwShare + '% (' + adPwVsNew.pwTotalLinks + '个有效链接)\\n' +\n      '新品加权市占: ' + adPwVsNew.newShare + '% (' + adPwVsNew.newSkuCount + '个有对手SKU, 我方' + fmtNum(adPwVsNew.newTotalSales) + ' / 对手' + fmtNum(adPwVsNew.newRivalSales) + ')\\n' +\n      '差值: ' + (Math.abs(adPwVsNew.pwShare - adPwVsNew.newShare)).toFixed(1) + '% (PW vs 新品，维度不同平行参考)'"

html = html.replace(sentinel_a, sentinel_a + dept_section, 1)
changes += 1
print("Fix5a: Added dept+PW to report section 1")

# Fix 5b: Add ad composition + PLG tiers to report section 3 (广告追踪)
sentinel_b = "按分析人PLG: ' + plgStats.byAnalyst.map(function(d){return d.analyst + '(花费' + fmtMoney(d.plgSpend) + ', ACOS ' + d.acos + ', ACOAS ' + d.acoas + ')';}).join('; ')"
assert sentinel_b in html, "Cannot find PLG byAnalyst in report section 3"

ad_section = " + '\\n\\n' +\n      '【广告构成分布】\\n' +\n      'PLP+PLG同开: ' + adCompDist['PLP+PLG'] + '款 | 单PLP: ' + adCompDist['单PLP'] + '款 | 仅PLG: ' + adCompDist['仅PLG'] + '款 | 无广告: ' + adCompDist['无广告'] + '款\\n' +\n      '【PLG费率分档】\\n' +\n      '无广告: ' + adPlgTierDist['无广告'] + '款 | 低费率(≤2%): ' + adPlgTierDist['低费率'] + '款 | 中费率(2-4%): ' + adPlgTierDist['中费率'] + '款 | 高费率(>4%): ' + adPlgTierDist['高费率'] + '款\\n' +\n      '（广告构成明细SKU清单见看板广告结构板块）'"

html = html.replace(sentinel_b, sentinel_b + ad_section, 1)
changes += 1
print("Fix5b: Added ad composition + PLG tiers to report section 3")

# Fix 5c: Update findings — add dept+PW finding
old_finding = "{title: 'PLG广告数据', desc: '自然周PLG花费' + fmtMoney(plgStats.totalSpend) + '，广告销售额' + fmtMoney(plgStats.totalAdRev) + '，ACOS ' + plgStats.acos + '，ACOAS ' + plgStats.acoas + '。'},"
new_finding = "{title: 'PLG广告数据', desc: '自然周PLG花费' + fmtMoney(plgStats.totalSpend) + '，广告销售额' + fmtMoney(plgStats.totalAdRev) + '，ACOS ' + plgStats.acos + '，ACOAS ' + plgStats.acoas + '。PLP+PLG同开' + adCompDist['PLP+PLG'] + '款，单PLP' + adCompDist['单PLP'] + '款，仅PLG' + adCompDist['仅PLG'] + '款，无广告' + adCompDist['无广告'] + '款。'},\n    {title: '部门占比与PW市占', desc: '新品占部门销量' + adDeptPct.salesPct + '%、销售额' + adDeptPct.revPct + '%。PW爬虫加权市占' + adPwVsNew.pwShare + '% vs 新品加权' + adPwVsNew.newShare + '%，差值' + (Math.abs(adPwVsNew.pwShare - adPwVsNew.newShare)).toFixed(1) + '%。'},"
html = html.replace(old_finding, new_finding, 1)
changes += 1
print("Fix5c: Updated findings with dept+PW data")

# Fix 5d: Update next week actions
old_actions = "  var actions = [\n    {title: '低占比新品逐一排查', desc: '对' + lowShareData.length + '款低占比新品逐一分析市场状态，重点关注\"竞争无优势\"和\"无市场\"SKU，制定差异化优化方案。'},\n    {title: '市占比提升专项', desc: '本周新品总市占比' + pk.totalMarketShare + '，重点对市占比偏低的品线和分析人SKU进行优化，提升整体市场占有率。'},\n    {title: '单链接PLP+PLG同开SKU优化', desc: '关注' + plgStats.singleLinkPlpPlgCount + '个单链接PLP+PLG同开SKU的广告表现，评估是否需要扩展广告活动数量。'},\n    {title: '分析及时率提升', desc: '督促分析及时率偏低的分析师，确保新品8日内完成首次分析，7日内完成低占比追踪分析。'},\n    {title: 'PLG广告ROI优化', desc: 'PLG广告ACOS为' + plgStats.acos + '，ACOAS为' + plgStats.acoas + '，持续监控PLG投放效果，优化花费结构。'},\n  ];"
assert old_actions in html, "Cannot find old actions"

new_actions = "  var actions = [\n    {title: '低占比新品逐一排查', desc: '对' + lowShareData.length + '款低占比新品逐一分析市场状态，重点关注\"竞争无优势\"和\"无市场\"SKU，制定差异化优化方案。'},\n    {title: '市占比提升专项', desc: '本周新品总市占比' + pk.totalMarketShare + '，重点对市占比偏低的品线和分析人SKU进行优化。新品占部门仅' + adDeptPct.salesPct + '%，增长空间巨大。'},\n    {title: '广告结构优化：主推PLP+PLG同开', desc: '当前PLP+PLG同开' + adCompDist['PLP+PLG'] + '款、单PLP' + adCompDist['单PLP'] + '款、仅PLG' + adCompDist['仅PLG'] + '款、无广告' + adCompDist['无广告'] + '款。高费率(>4%)' + adPlgTierDist['高费率'] + '款需重点评估ROI。下周围绕PLP+PLG同开SKU加大投放，评估单PLP是否适合补充PLG。'},\n    {title: '分析及时率提升', desc: '督促分析及时率偏低的分析师，确保新品8日内完成首次分析，7日内完成低占比追踪分析。'},\n    {title: 'PW爬虫市占对齐', desc: 'PW爬虫市占' + adPwVsNew.pwShare + '% vs 新品加权市占' + adPwVsNew.newShare + '%，差值' + (Math.abs(adPwVsNew.pwShare - adPwVsNew.newShare)).toFixed(1) + '%，持续监控缩小差距。'},\n  ];"
html = html.replace(old_actions, new_actions, 1)
changes += 1
print("Fix5d: Updated next week actions")

# ===== Write output =====
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

# ===== Validate =====
print(f"\nTotal changes: {changes}")
ob, cb = html.count('{'), html.count('}')
op, cp = html.count('('), html.count(')')
print(f"Braces: {ob}/{cb} {'OK' if ob==cb else 'MISMATCH!'}")
print(f"Parens: {op}/{cp} {'OK' if op==cp else 'MISMATCH!'}")

key_checks = [
    't1-dept-kpi', 'renderAdGroup', 'PLP+PLG同开',
    'adDeptPct.salesPct', 'adCompDist[',
    'drill-panel', '新品销量占部门比', '部门占比与PW市占',
]
missing = [c for c in key_checks if c not in html]
if missing:
    for m in missing:
        print(f"MISSING: {m}")
else:
    print(f"All {len(key_checks)} checks passed!")

print(f"Size: {len(html)//1024}KB")
print(f"\nOutput: {OUTPUT}")
print("Done!")
