"""
后处理脚本：将HTML调整为最终版
1. 把市占比KPI+图表从Tab1移到Tab2
2. 重新编号所有Tab3-6的DOM ID
3. 给所有柱状图添加环比折线副轴
4. Tab2增加市场分布完整JS渲染
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

HTML_FILE = 'C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"原始文件: {len(html)} 字符")

# ============================================================
# Step 0: 移动市占比chart canvas从Tab1到Tab2
# ============================================================
# 从Tab1 HTML中提取3个canvas并移除
canvases_to_move = [
    '<div class="chart-box"><h4>&#128200; 新品总市占比</h4><canvas id="chart-total-share"></canvas></div>',
    '<div class="chart-box"><h4>&#128200; 品线市占比对比</h4><canvas id="chart-cat-share"></canvas></div>',
    '<div class="chart-box"><h4>&#128101; 分析人市占比对比</h4><canvas id="chart-an-share"></canvas></div>',
]
# 从HTML中移除这些canvas（Tab1中）
for canvas in canvases_to_move:
    html = html.replace(canvas, '')

# 在Tab2的chart-grid中添加这些canvas（放在chart-mkt-ring之前）
tab2_chart_grid = '<div class="chart-grid">\n        <div class="chart-box"><h4>&#128200; 本周市场状态占比</h4><canvas id="chart-mkt-ring" style="max-height:320px"></canvas></div>'
tab2_new_charts = '<div class="chart-grid">\n        <div class="chart-box"><h4>&#128200; 新品总市占比</h4><canvas id="chart-total-share"></canvas></div>\n        <div class="chart-box"><h4>&#128200; 品线市占比对比</h4><canvas id="chart-cat-share"></canvas></div>\n        <div class="chart-box"><h4>&#128101; 分析人市占比对比</h4><canvas id="chart-an-share"></canvas></div>\n        <div class="chart-box"><h4>&#128200; 本周市场状态占比</h4><canvas id="chart-mkt-ring" style="max-height:320px"></canvas></div>'
html = html.replace(tab2_chart_grid, tab2_new_charts)

# ============================================================
# Step 1: 从Tab1移除市占比KPI卡片
# ============================================================
# 删除这一行：'<div class="kpi-card info"><div class="label">新品总市占比</div>...'
old_kpi_line = r"'<div class=\"kpi-card info\"><div class=\"label\">新品总市占比</div><div class=\"val\">' \+ totalShare \+ '%</div><div class=\"hb\">' \+ hbSign\(shareChangeStr\) \+ ' 上周' \+ totalSharePrev \+ '%</div></div>' \+"
html = html.replace(
    "'<div class=\"kpi-card info\"><div class=\"label\">新品总市占比</div><div class=\"val\">' + totalShare + '%</div><div class=\"hb\">' + hbSign(shareChangeStr) + ' 上周' + totalSharePrev + '%</div></div>' +",
    ""
)

# ============================================================
# Step 2: 从initCharts1移除3个市占比图表
# ============================================================
# 移除 chart-total-share
html = re.sub(
    r'\s*// 2\. 新品总市占比.*?new Chart\(document\.getElementById\(\'chart-total-share\'\).*?\}\);\s*',
    '\n  ',
    html, flags=re.DOTALL
)
# 移除 chart-cat-share
html = re.sub(
    r'\s*// 3\. 品线市占比对比.*?new Chart\(document\.getElementById\(\'chart-cat-share\'\).*?\}\);\s*',
    '\n  ',
    html, flags=re.DOTALL
)
# 移除 chart-an-share
html = re.sub(
    r'\s*// 4\. 分析人市占比对比.*?new Chart\(document\.getElementById\(\'chart-an-share\'\).*?\}\);\s*',
    '\n  ',
    html, flags=re.DOTALL
)

# Fix chart numbering comments in initCharts1
html = html.replace("// 5. 品线销量对比", "// 2. 品线销量对比")
html = html.replace("// 6. 分析人销量对比", "// 3. 分析人销量对比")
html = html.replace("// 7. 品线销售额对比", "// 4. 品线销售额对比")
html = html.replace("// 8. 分析人销售额对比", "// 5. 分析人销售额对比")

# ============================================================
# Step 3: 重新编号JS中的DOM ID（旧Tab2→Tab3, Tab3→Tab4, Tab4→Tab5, Tab5→Tab6）
# ============================================================
# 注意: 只改JS内的ID引用，不改新的Tab2容器

# 低占比Tab: t2- → t3-
id_map_lowshare = {
    't2-kpi': 't3-kpi',
    't2-has-an': 't3-has-an',
    't2-has-cat': 't3-has-cat',
    't2-no-an': 't3-no-an',
    't2-no-cat': 't3-no-cat',
    't2-lowshare-filters': 't3-lowshare-filters',
    't2-lowshare-table': 't3-lowshare-table',
    't2-ls-count': 't3-ls-count',
}

# 广告Tab: t3- → t4-
id_map_ad = {
    't3-plp-kpi': 't4-plp-kpi',
    't3-plp-core': 't4-plp-core',
    't3-plp-an': 't4-plp-an',
    't3-plp-cat': 't4-plp-cat',
    't3-plp-exp': 't4-plp-exp',
    't3-plg-kpi': 't4-plg-kpi',
    "t3-plg'": "t4-plg'",
    't3-plg-an': 't4-plg-an',
    't3-plp-detail': 't4-plp-detail',
}

# 四三累计Tab: t4- → t5-
id_map_43 = {
    't4-kpi': 't5-kpi',
    't4-filters': 't5-filters',
    't4-table': 't5-table',
    't4-count': 't5-count',
}

# 汇报输出Tab: t5- → t6-
id_map_report = {
    't5-kpi': 't6-kpi',
    't5-risk': 't6-risk',
    't5-findings': 't6-findings',
    't5-actions': 't6-actions',
    't5-report': 't6-report',
}

# 函数名
func_map = {
    'renderT4Table': 'renderT5Table',
}

all_maps = [id_map_lowshare, id_map_ad, id_map_43, id_map_report, func_map]

# Find the <script> block and apply renames there
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script_match:
    js_code = script_match.group(1)
    for mapping in all_maps:
        for old_id, new_id in mapping.items():
            js_code = js_code.replace(old_id, new_id)

    # Replace the script block
    html = html[:script_match.start(1)] + js_code + html[script_match.end(1):]

# ============================================================
# Step 4: 更新switchTab以支持Tab2懒初始化
# ============================================================
html = html.replace(
    "if (tabId === 'tab1' && !window._charts1Init) { initCharts1(); }",
    "if (tabId === 'tab1' && !window._charts1Init) { initCharts1(); }\n  if (tabId === 'tab2' && !window._charts2Init) { initCharts2(); }"
)

# ============================================================
# Step 5: 在initCharts1后面添加initCharts2（市场分布+市占比图表）
# ============================================================
charts2_code = r'''
// ========== Tab2 图表（市场分布 + 市占比）==========
window._charts2Init = false;
function initCharts2() {
  if (window._charts2Init) return;
  window._charts2Init = true;
  var t = cum43Stats;

  // 1. 新品总市占比环比
  var totalShareCurr = t.totalMarketShare;
  var totalSharePrev = t.totalMarketSharePrev;
  new Chart(document.getElementById('chart-total-share'), {
    type: 'bar',
    data: {
      labels: ['本周(5.27)', '上周(5.20)'],
      datasets: [
        { label: '市占比(%)', data: [totalShareCurr, totalSharePrev], backgroundColor: ['#0f3460', '#ccc'], yAxisID: 'y' },
        { label: '环比变化', data: [null, ((totalShareCurr-totalSharePrev)/totalSharePrev*100).toFixed(1)], borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', pointRadius: 5, pointBackgroundColor: '#c0392b' }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: { callbacks: { label: function(ctx) { return ctx.dataset.label + ': ' + (ctx.parsed.y != null ? ctx.parsed.y + (ctx.dataset.yAxisID==='y1'?'%':'%') : 'N/A'); } } }
      },
      scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: '市占比(%)' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } }
    }
  });

  // 2. 品线市占比环比对比
  var catLabels = categoryRevenueData.map(function(d) { return d.category; });
  var catShareCurr = categoryRevenueData.map(function(d) { return d.curMarketShare; });
  var catSharePrev = categoryRevenueData.map(function(d) { return d.prevMarketShare; });
  var catShareChange = categoryRevenueData.map(function(d) {
    var v = parseFloat(d.marketShareChange);
    return isNaN(v) ? 0 : v;
  });

  new Chart(document.getElementById('chart-cat-share'), {
    type: 'bar',
    data: {
      labels: catLabels,
      datasets: [
        { label: '本周市占比(%)', data: catShareCurr, backgroundColor: '#0f3460', yAxisID: 'y' },
        { label: '上周市占比(%)', data: catSharePrev, backgroundColor: '#ccc', yAxisID: 'y' },
        { label: '环比变化(%)', data: catShareChange, borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', tension: 0.3, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#c0392b' }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: '市占比(%)' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } }
    }
  });

  // 3. 分析人市占比环比对比
  var anLabels = analystRevenueData.map(function(d) { return d.analyst; });
  var anShareCurr = analystRevenueData.map(function(d) { return d.curMarketShare; });
  var anSharePrev = analystRevenueData.map(function(d) { return d.prevMarketShare; });
  var anShareChange = analystRevenueData.map(function(d) {
    var v = parseFloat(d.marketShareChange);
    return isNaN(v) ? 0 : v;
  });

  new Chart(document.getElementById('chart-an-share'), {
    type: 'bar',
    data: {
      labels: anLabels,
      datasets: [
        { label: '本周市占比(%)', data: anShareCurr, backgroundColor: '#8e44ad', yAxisID: 'y' },
        { label: '上周市占比(%)', data: anSharePrev, backgroundColor: '#ddd', yAxisID: 'y' },
        { label: '环比变化(%)', data: anShareChange, borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', tension: 0.3, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#c0392b' }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: '市占比(%)' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } }
    }
  });

  // 4. 市场状态环形图
  var mktLabels = mktDistOverall.distribution.map(function(d) { return d.status; });
  var mktData = mktDistOverall.distribution.map(function(d) { return d.curCount; });
  var mktColors = { '正常': '#08845a', '竞争无优势': '#e07b24', '无市场': '#c0392b', '站外出单': '#8e44ad', '站内无价格优势': '#f39c12', '#N/A': '#95a5a6', '未知': '#7f8c8d', '其他': '#bdc3c7' };
  new Chart(document.getElementById('chart-mkt-ring'), {
    type: 'doughnut',
    data: {
      labels: mktLabels,
      datasets: [{ data: mktData, backgroundColor: mktLabels.map(function(s) { return mktColors[s] || '#95a5a6'; }) }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' }, tooltip: { callbacks: { label: function(ctx) { return ctx.label + ': ' + ctx.parsed + '个 (' + (ctx.parsed/mktDistOverall.curTotal*100).toFixed(1) + '%)'; } } } } }
  });

  // 5. 市场状态本周vs上周柱状图
  var mktCurrCounts = mktDistOverall.distribution.map(function(d) { return d.curCount; });
  var mktPrevCounts = mktDistOverall.distribution.map(function(d) { return d.prevCount; });
  new Chart(document.getElementById('chart-mkt-bar'), {
    type: 'bar',
    data: {
      labels: mktLabels,
      datasets: [
        { label: '本周SKU数', data: mktCurrCounts, backgroundColor: '#0f3460' },
        { label: '上周SKU数', data: mktPrevCounts, backgroundColor: '#ccc' }
      ]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });

  // 6. 货值分布-价格区间
  var priceRanges = priceOverview.priceRanges;
  var priceCounts = priceOverview.distribution.map(function(d) { return d.count; });
  new Chart(document.getElementById('chart-price-dist'), {
    type: 'bar',
    data: {
      labels: priceRanges,
      datasets: [{ label: 'SKU数', data: priceCounts, backgroundColor: '#2980b9' }]
    },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
  });

  // 7. 货值分布-按分析人（堆叠柱状图）
  var priceAnDatasets = priceOverview.byAnalyst.map(function(d) {
    return { label: d.analyst, data: priceRanges.map(function(r) { return d[r] || 0; }) };
  });
  var priceAnColors = ['#0f3460', '#2980b9', '#8e44ad', '#e07b24', '#08845a', '#c0392b'];
  priceAnDatasets.forEach(function(ds, i) { ds.backgroundColor = priceAnColors[i % priceAnColors.length]; });
  new Chart(document.getElementById('chart-price-an'), {
    type: 'bar',
    data: { labels: priceRanges, datasets: priceAnDatasets },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } }
  });

  // 8. 市占比分布堆叠柱状图（品线x高中低）
  var tierLabels = shareTierOverview.byCategory.map(function(d) { return d.category; });
  var tierHigh = shareTierOverview.byCategory.map(function(d) { return d.high; });
  var tierMid = shareTierOverview.byCategory.map(function(d) { return d.mid; });
  var tierLow = shareTierOverview.byCategory.map(function(d) { return d.low; });
  new Chart(document.getElementById('chart-share-tier'), {
    type: 'bar',
    data: {
      labels: tierLabels,
      datasets: [
        { label: '高市占比(>=75%)', data: tierHigh, backgroundColor: '#08845a' },
        { label: '中市占比(50-75%)', data: tierMid, backgroundColor: '#e07b24' },
        { label: '低市占比(<50%)', data: tierLow, backgroundColor: '#c0392b' }
      ]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } }
  });
}
'''

# Insert initCharts2 after initCharts1 closing brace
init_charts1_end = "setTimeout(initCharts1, 100);"
html = html.replace(init_charts1_end, init_charts1_end + charts2_code)

# ============================================================
# Step 6: 添加Tab2的KPI和表格渲染JS（在低占比IIFE之前）
# ============================================================
tab2_js = r'''
// ========== Tab2: 市场分布（KPI + 表格）==========
(function() {
  var mo = mktDistOverall;
  var t = cum43Stats;
  var normalItem = mo.distribution.find(function(d) { return d.status === '正常'; }) || {curCount:0, curPct:0, change:0};
  var competitiveItem = mo.distribution.find(function(d) { return d.status === '竞争无优势'; }) || {curCount:0, change:0};
  var noMarketItem = mo.distribution.find(function(d) { return d.status === '无市场'; }) || {curCount:0, change:0};
  var stationOutItem = mo.distribution.find(function(d) { return d.status === '站外出单'; }) || {curCount:0, change:0};
  var totalShare = t.totalMarketShare;
  var totalSharePrev = t.totalMarketSharePrev;
  var shareChange = totalSharePrev ? ((totalShare - totalSharePrev) / totalSharePrev * 100).toFixed(1) : 0;
  var shareChangeStr = shareChange >= 0 ? '+' + shareChange + '%' : shareChange + '%';

  document.getElementById('t2-kpi').innerHTML =
    '<div class="kpi-card info"><div class="label">新品总市占比</div><div class="val">' + totalShare + '%</div><div class="hb">' + hbSign(shareChangeStr) + ' 上周' + totalSharePrev + '%</div></div>' +
    '<div class="kpi-card primary"><div class="label">在售SKU总数</div><div class="val">' + mo.curTotal + '</div><div class="hb">上周 ' + mo.prevTotal + '</div></div>' +
    '<div class="kpi-card success"><div class="label">市场正常</div><div class="val">' + normalItem.curCount + '</div><div class="hb">占比 ' + normalItem.curPct + '%</div></div>' +
    '<div class="kpi-card warning"><div class="label">竞争无优势</div><div class="val">' + competitiveItem.curCount + '</div><div class="hb">' + hbSign((competitiveItem.change >= 0 ? '+' : '') + competitiveItem.change) + ' vs 上周</div></div>' +
    '<div class="kpi-card danger"><div class="label">无市场</div><div class="val">' + noMarketItem.curCount + '</div><div class="hb">' + hbSign((noMarketItem.change >= 0 ? '+' : '') + noMarketItem.change) + ' vs 上周</div></div>' +
    '<div class="kpi-card purple"><div class="label">站外出单</div><div class="val">' + (stationOutItem.curCount || 0) + '</div></div>';

  // 市场状态明细表
  var mh = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>市场状态</th><th>本周数量</th><th>本周占比</th><th>上周数量</th><th>上周占比</th><th>变化</th></tr></thead><tbody>';
  mo.distribution.forEach(function(d) {
    mh += '<tr><td>' + badgeStatus(d.status) + '</td><td>' + d.curCount + '</td><td>' + d.curPct + '%</td><td>' + d.prevCount + '</td><td>' + d.prevPct + '%</td><td>' + hbSign((d.change >= 0 ? '+' : '') + d.change) + '</td></tr>';
  });
  mh += '</tbody></table></div>';
  document.getElementById('t2-mkt-table').innerHTML = mh;

  // 货值明细表
  var po = priceOverview;
  var ph = '<p>出单均价: <b>$' + po.avgPrice.toFixed(2) + '</b> | 中位数: <b>$' + po.medianPrice.toFixed(2) + '</b> | 有出单SKU: <b>' + po.totalWithSales + '</b>个</p>';
  ph += '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>价格区间</th><th>SKU数</th><th>占比</th></tr></thead><tbody>';
  po.distribution.forEach(function(d) {
    ph += '<tr><td>' + d.range + '</td><td>' + d.count + '</td><td>' + d.pct + '%</td></tr>';
  });
  ph += '</tbody></table></div>';
  document.getElementById('t2-price-table').innerHTML = ph;

  // 市占比分布明细表
  var sto = shareTierOverview;
  var sh = '<div class="table-scroll-wrap"><table class="data-table"><thead><tr><th>品线</th><th>总SKU</th><th>高市占比(>=75%)</th><th>中市占比(50-75%)</th><th>低市占比(<50%)</th></tr></thead><tbody>';
  sto.byCategory.forEach(function(d) {
    sh += '<tr><td><b>' + d.category + '</b></td><td>' + d.total + '</td><td>' + d.high + '</td><td>' + d.mid + '</td><td>' + d.low + '</td></tr>';
  });
  sh += '</tbody></table></div>';
  document.getElementById('t2-share-tier-table').innerHTML = sh;
})();
'''

# Insert Tab2 JS before the Tab3 (原Tab2) IIFE
tab3_start = "// ========== Tab2: 低占比分析 =========="
# Actually find the first IIFE after "低占比" comment
low_share_iife = "(function() {\n  var hcu = hasCompetitorUnsold;"
html = html.replace(low_share_iife, tab2_js + "\n" + low_share_iife)

# Also fix the Tab section comments
html = html.replace("// ========== Tab2: 低占比分析 ==========", "// ========== Tab3: 低占比分析 ==========")
html = html.replace("// ========== Tab3: 广告追踪（PLP + PLG 自然周）==========", "// ========== Tab4: 广告追踪（PLP + PLG 自然周）==========")
html = html.replace("// ========== Tab4: 四三累计 ==========", "// ========== Tab5: 四三累计 ==========")
html = html.replace("// ========== Tab5: 汇报输出 ==========", "// ========== Tab6: 汇报输出 ==========")

# ============================================================
# Step 7: 更新汇报输出中的Tab编号
# ============================================================
html = html.replace("一、总盘概览", "一、总盘概览（Tab1）")
html = html.replace("二、低占比分析", "三、低占比分析（Tab3）")
html = html.replace("三、广告追踪", "四、广告追踪（Tab4）")
html = html.replace("四、风险预警与下周动作", "五、风险预警与下周动作")

# Add market distribution section to report
report_insert = r"""    {title: '二、市场分布（Tab2）', text: '【新品总市占比】' + pk.totalMarketShare + '（上周' + pk.totalMarketSharePrev + '，环比' + pk.marketShareChange + '）\n' +
      '【品线市占比】\n' + categoryRevenueData.map(function(d){ return d.category + ': ' + d.curMarketShare + '%（环比' + d.marketShareChange + '）'; }).join('\n') + '\n\n' +
      '【分析人市占比】\n' + analystRevenueData.map(function(d){ return d.analyst + ': ' + d.curMarketShare + '%（环比' + d.marketShareChange + '）'; }).join('\n') + '\n\n' +
      '【市场状态分布】正常' + (mktDistOverall.distribution.find(function(d){return d.status==='正常';})||{curCount:0}).curCount + '个 / 竞争无优势' + (mktDistOverall.distribution.find(function(d){return d.status==='竞争无优势';})||{curCount:0}).curCount + '个 / 无市场' + (mktDistOverall.distribution.find(function(d){return d.status==='无市场';})||{curCount:0}).curCount + '个\n' +
      '【货值分布】出单均价$' + priceOverview.avgPrice.toFixed(2) + '，中位数$' + priceOverview.medianPrice.toFixed(2)},
    """

html = html.replace(
    "{title: '三、低占比分析（Tab3）', text: '【有对手未出单新品：'",
    report_insert + "\n    {title: '三、低占比分析（Tab3）', text: '【有对手未出单新品：'"
)

# Add chart-total-share chart-canvas back to Tab2 HTML if needed
# Actually the HTML body should already have the canvas elements from the earlier edit

# ============================================================
# Step 8: 给Tab1的品线/分析人销量销售额柱状图也添加环比折线
# ============================================================
# Replace the cat-sales chart to add change line
old_cat_sales = """new Chart(document.getElementById('chart-cat-sales'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销量', data: categoryRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460' },
      { label: '上周销量', data: categoryRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });"""

# Get the change values for cat sales
new_cat_sales = """new Chart(document.getElementById('chart-cat-sales'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销量', data: categoryRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460', yAxisID: 'y' },
      { label: '上周销量', data: categoryRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc', yAxisID: 'y' },
      { label: '环比变化(%)', data: categoryRevenueData.map(function(d){ var v=parseFloat(d.salesQtyChange); return isNaN(v)?0:v; }), borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', tension: 0.3, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#c0392b' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, title: { display: true, text: '销量' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } } }
  });"""

html = html.replace(old_cat_sales, new_cat_sales)

# Same for cat-rev
old_cat_rev = """new Chart(document.getElementById('chart-cat-rev'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销售额', data: categoryRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad' },
      { label: '上周销售额', data: categoryRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });"""

new_cat_rev = """new Chart(document.getElementById('chart-cat-rev'), {
    type: 'bar', data: { labels: catLabels, datasets: [
      { label: '本周销售额($)', data: categoryRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad', yAxisID: 'y' },
      { label: '上周销售额($)', data: categoryRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd', yAxisID: 'y' },
      { label: '环比变化(%)', data: categoryRevenueData.map(function(d){ var v=parseFloat(d.revenueChange); return isNaN(v)?0:v; }), borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', tension: 0.3, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#c0392b' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, title: { display: true, text: '销售额($)' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } } }
  });"""

html = html.replace(old_cat_rev, new_cat_rev)

# Same for an-sales and an-rev
old_an_sales = """new Chart(document.getElementById('chart-an-sales'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销量', data: analystRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460' },
      { label: '上周销量', data: analystRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });"""

new_an_sales = """new Chart(document.getElementById('chart-an-sales'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销量', data: analystRevenueData.map(function(d){return d.curSalesQty;}), backgroundColor: '#0f3460', yAxisID: 'y' },
      { label: '上周销量', data: analystRevenueData.map(function(d){return d.prevSalesQty;}), backgroundColor: '#ccc', yAxisID: 'y' },
      { label: '环比变化(%)', data: analystRevenueData.map(function(d){ var v=parseFloat(d.salesQtyChange); return isNaN(v)?0:v; }), borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', tension: 0.3, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#c0392b' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, title: { display: true, text: '销量' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } } }
  });"""

html = html.replace(old_an_sales, new_an_sales)

old_an_rev = """new Chart(document.getElementById('chart-an-rev'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销售额', data: analystRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad' },
      { label: '上周销售额', data: analystRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
  });"""

new_an_rev = """new Chart(document.getElementById('chart-an-rev'), {
    type: 'bar', data: { labels: anLabels, datasets: [
      { label: '本周销售额($)', data: analystRevenueData.map(function(d){return d.curRevenue;}), backgroundColor: '#8e44ad', yAxisID: 'y' },
      { label: '上周销售额($)', data: analystRevenueData.map(function(d){return d.prevRevenue;}), backgroundColor: '#ddd', yAxisID: 'y' },
      { label: '环比变化(%)', data: analystRevenueData.map(function(d){ var v=parseFloat(d.revenueChange); return isNaN(v)?0:v; }), borderColor: '#c0392b', backgroundColor: 'transparent', type: 'line', yAxisID: 'y1', tension: 0.3, borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#c0392b' }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, title: { display: true, text: '销售额($)' } }, y1: { position: 'right', title: { display: true, text: '环比变化(%)' }, grid: { drawOnChartArea: false } } } }
  });"""

html = html.replace(old_an_rev, new_an_rev)

# Save
with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"处理后文件: {len(html)} 字符")
print("完成！Tab结构已调整为6个，市占比已移到Tab2，环比折线已添加")
