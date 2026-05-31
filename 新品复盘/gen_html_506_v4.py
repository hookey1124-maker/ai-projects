#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 4.30-5.6 可视化 HTML 报告 - 正确版 v4
策略：JS 数据变量单独注入，图表代码接在后面，彻底避免 f-string 冲突
"""

import json

JSON = r"C:/Users/Administrator/Desktop/新品复盘/sheets_506.json"
DST  = r"C:/Users/Administrator/Desktop/新品复盘/新品周报_4.30-5.6_可视化.html"

with open(JSON, encoding='utf-8') as f:
    sheets = json.load(f)

def safe(v, default=''):
    if v is None or v == '': return default
    return v

def num(v, default=0.0):
    if v is None or v == '': return default
    s = str(v).replace('%','').replace(',','').strip()
    try: return float(s)
    except: return default

# ── 读取各 Sheet ────────────────────────────────────────────────────────────
PX = sheets.get('品线维度', [])
FX = sheets.get('分析人维度', [])
TZ = sheets.get('拓展类型', [])
JL = sheets.get('分析及时率', [])
DY = sheets.get('低占比新品', [])
PLP = sheets.get('新品PLP', [])
CD = sheets.get('新品出单情况', [])
YY = sheets.get('新品未出单原因', [])
PLG = sheets.get('新品PLG维度', [])

# ── 提取数据行（跳过表头和合计）────────────────────────────────────────────────
def data_rows(rows):
    return [r for r in rows[1:] if r and r[0] and str(r[0]).strip() not in ('合计','维度')]

PX_DATA = data_rows(PX)
FX_DATA = data_rows(FX)
TZ_DATA = data_rows(TZ)
JL_DATA = data_rows(JL)
DY_DATA = data_rows(DY)
CD_DATA = data_rows(CD)
YY_DATA = data_rows(YY)
PLG_DATA = data_rows(PLG)

# PLP 分块
PLP_TOTAL, PLP_AN, PLP_PX, PLP_TZ = [], [], [], []
block = None
for r in PLP:
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    if lab in ('【分析人维度】','分析人维度'): block = 'an'; continue
    if lab in ('【品线维度】','品线维度'):   block = 'px'; continue
    if lab in ('【拓展类型维度】','拓展类型维度'): block = 'tz'; continue
    if lab in ('合计','总计'):   block = None; continue
    if lab == '维度': continue  # 表头行
    if block == 'an' and lab in ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星']:
        PLP_AN.append(r)
    elif block == 'px' and lab not in ('合计','','【品线维度】'):
        PLP_PX.append(r)
    elif block == 'tz' and lab not in ('合计','','【拓展类型维度】'):
        PLP_TZ.append(r)
    elif block is None and lab == '总计':
        PLP_TOTAL.append(r)

print("PLP_AN:", [r[0] for r in PLP_AN])

# ── 辅助函数 ────────────────────────────────────────────────────────────────
def make_table(headers, rows, cls_fn=None):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    trs = ''
    for i, row in enumerate(rows):
        cls = cls_fn(i, row) if cls_fn else ''
        cells = ''.join(f'<td>{safe(c)}</td>' for c in row)
        trs += f'<tr class="{cls}">{cells}</tr>\n'
    return f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'

def low_cls(i, row):
    try:
        plp = str(safe(row[18])).strip()
        plg = num(safe(row[19]), 0)
        bd  = str(safe(row[17])).strip()
        if plp == 'Y' and plg > 0: return 'highlight-orange'
        if plp == 'N' and bd == '未出单': return 'highlight-pink'
        if plp == 'N' and plg > 0: return 'highlight-green'
    except: pass
    return ''

def plg_cls(i, row):
    try:
        plp = str(safe(row[13])).strip()
        plg = num(safe(row[14]), 0)
        bd  = str(safe(row[7])).strip()
        if plp == 'Y' and plg > 0: return 'highlight-orange'
        if plp == 'N' and bd == '未出单': return 'highlight-pink'
        if plp == 'N' and plg > 0: return 'highlight-green'
    except: pass
    return ''

# ── JS 数据变量 ──────────────────────────────────────────────────────────────
# 使用 json.dumps() 生成合法 JS 字面量
JL_LEN = len(JL_DATA)
PLP_ACT  = int(num(safe(PLP_TOTAL[0][0] if PLP_TOTAL else 42), 42))
PLP_LINK = int(num(safe(PLP_TOTAL[0][1] if PLP_TOTAL else 53), 53))
PLP_IMP  = int(num(safe(PLP_TOTAL[0][2] if PLP_TOTAL else 119686), 119686))
PLP_ROAS = num(safe(PLP_TOTAL[0][7] if PLP_TOTAL else 6.44), 6.44)

# 写入 HTML 文件
lines = []
W = lines.append

# ===== HTML head + CSS =====
W('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报可视化报告 - 4.30-5.6</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI','Microsoft YaHei',sans-serif; background:#f5f0fa; color:#333; }
.sidebar { position:fixed; left:0; top:0; width:200px; height:100vh; background:linear-gradient(180deg,#4A148C,#7B1FA2); color:#fff; padding:20px 0; overflow-y:auto; z-index:100; }
.sidebar h2 { text-align:center; font-size:14px; padding:0 10px 15px; border-bottom:1px solid rgba(255,255,255,0.2); margin-bottom:10px; line-height:1.6; }
.sidebar a { display:block; color:rgba(255,255,255,0.85); text-decoration:none; padding:9px 16px; font-size:13px; transition:0.2s; cursor:pointer; }
.sidebar a:hover,.sidebar a.active { background:rgba(255,255,255,0.15); color:#fff; border-left:3px solid #FFD54F; }
.main { margin-left:200px; padding:20px; }
.section { background:#fff; border-radius:12px; margin-bottom:24px; padding:24px; box-shadow:0 2px 12px rgba(74,20,140,0.08); display:none; }
.section.active { display:block; }
.section h2 { color:#4A148C; font-size:18px; margin-bottom:16px; padding-bottom:10px; border-bottom:2px solid #E1BEE7; }
.kpi-row { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px; }
.kpi-card { background:linear-gradient(135deg,#7B1FA2,#BA68C8); color:#fff; border-radius:10px; padding:18px 22px; min-width:150px; flex:1; }
.kpi-card.alt { background:linear-gradient(135deg,#4A148C,#6A1B9A); }
.kpi-card h3 { font-size:13px; opacity:0.85; margin-bottom:6px; }
.kpi-card .val { font-size:26px; font-weight:700; }
.kpi-card .mom { font-size:12px; margin-top:4px; opacity:0.8; }
.chart-box { margin:20px 0; padding:16px; background:#faf5ff; border-radius:8px; min-height:320px; }
.chart-box h3 { color:#4A148C; font-size:14px; margin-bottom:12px; }
canvas { max-width:100%; height:320px !important; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:13px; }
th { background:#7B1FA2; color:#fff; padding:8px 10px; text-align:left; }
td { padding:7px 10px; border-bottom:1px solid #eee; }
tr:nth-child(even) { background:#f9f5ff; }
tr:hover { background:#ede7f6; }
.highlight-orange { background:#FFE0B2 !important; }
.highlight-pink  { background:#FCE4EC !important; }
.highlight-green  { background:#E8F5E9 !important; }
.nav-toggle { display:none; position:fixed; top:10px; left:10px; z-index:200; background:#7B1FA2; color:#fff; border:none; padding:8px 12px; border-radius:6px; font-size:18px; cursor:pointer; }
@media(max-width:768px) {
  .sidebar { transform:translateX(-100%); transition:0.3s; }
  .sidebar.open { transform:translateX(0); }
  .main { margin-left:0; }
  .nav-toggle { display:block; }
}
</style>
</head>
<body>
<button class="nav-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">&#9776;</button>
<div class="sidebar">
  <h2>📊 新品周报<br/>4.30-5.6</h2>
  <a href="javascript:void(0)" id="nav_sec0" class="active" onclick="showSec('sec0',this)">📈 总体概况</a>
  <a href="javascript:void(0)" id="nav_sec1" onclick="showSec('sec1',this)">📊 品线维度</a>
  <a href="javascript:void(0)" id="nav_sec2" onclick="showSec('sec2',this)">👤 分析人维度</a>
  <a href="javascript:void(0)" id="nav_sec3" onclick="showSec('sec3',this)">🔄 拓展类型</a>
  <a href="javascript:void(0)" id="nav_sec4" onclick="showSec('sec4',this)">⏱ 分析及时率</a>
  <a href="javascript:void(0)" id="nav_sec5" onclick="showSec('sec5',this)">⚠ 低占比新品</a>
  <a href="javascript:void(0)" id="nav_sec6" onclick="showSec('sec6',this)">📢 新品PLP</a>
  <a href="javascript:void(0)" id="nav_sec7" onclick="showSec('sec7',this)">📋 新品出单情况</a>
  <a href="javascript:void(0)" id="nav_sec8" onclick="showSec('sec8',this)">🔍 未出单原因</a>
  <a href="javascript:void(0)" id="nav_sec9" onclick="showSec('sec9',this)">🎯 新品PLG维度</a>
</div>
<div class="main">
''')

# sec0
W('''<div class="section active" id="sec0">
  <h2>📈 总体概况（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>累计SKU数</h3><div class="val" id="kSku"></div><div class="mom" id="kSkuP"></div></div>
    <div class="kpi-card alt"><h3>总销量</h3><div class="val" id="kSq"></div><div class="mom" id="kSqP"></div></div>
    <div class="kpi-card"><h3>总销售额(USD)</h3><div class="val" id="kSa"></div><div class="mom" id="kSaP"></div></div>
  </div>
  <div class="chart-box"><h3>核心指标：本周 vs 上周</h3><canvas id="cOverview"></canvas></div>
</div>''')

# sec1
W(f'''<div class="section" id="sec1">
  <h2>📊 品线维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各品线销量对比</h3><canvas id="cPxSales"></canvas></div>
  <div class="chart-box"><h3>各品线销售额对比（USD）</h3><canvas id="cPxAmt"></canvas></div>
  <h3>品线明细</h3>
{make_table(['品线','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比','本周有对手','上周有对手'], PX_DATA)}
</div>''')

# sec2
W(f'''<div class="section" id="sec2">
  <h2>👤 分析人维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各分析人销量对比</h3><canvas id="cFxSales"></canvas></div>
  <div class="chart-box"><h3>各分析人销售额对比（USD）</h3><canvas id="cFxAmt"></canvas></div>
  <h3>分析人明细</h3>
{make_table(['分析人','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比'], FX_DATA)}
</div>''')

# sec3
W(f'''<div class="section" id="sec3">
  <h2>🔄 拓展类型维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各类型出单率（%）</h3><canvas id="cTzRate"></canvas></div>
  <div class="chart-box"><h3>各类型销量对比</h3><canvas id="cTzSales"></canvas></div>
  <h3>拓展类型明细</h3>
{make_table(['拓展类型','本周SKU','本周出单','出单率','上周出单率','出单率环比','本周销量','上周销量','本周销售额','上周销售额','销售额环比'], TZ_DATA)}
</div>''')

# sec4
W(f'''<div class="section" id="sec4">
  <h2>⏱ 分析及时率（截止5.6）</h2>
  <div class="chart-box"><h3>各分析人及时分析情况（SKU数）</h3><canvas id="cJlStack"></canvas></div>
  <div class="chart-box"><h3>各分析人及时率（%）</h3><canvas id="cJlRate"></canvas></div>
  <h3>分析及时率明细</h3>
{make_table(['分析人','截止5.6SKU','及时分析','8日内无分析','超7日未分析','及时率','上周及时率','变化'], JL_DATA)}
</div>''')

# sec5
W(f'''<div class="section" id="sec5">
  <h2>⚠ 低占比新品明细（共{len(DY_DATA)}条）</h2>
{make_table(['编号','SKU','上架日期','分析人','品类','拓展类型','销量','销量环比','销售额','销售额环比','对手销量','对手销量环比','市占比','市占比环比','8日出单','7日频次','7日新品频次','市场状态1','操作判断','市场状态2','开启PLP','PLG费率'], DY_DATA, low_cls)}
</div>''')

# sec6
W(f'''<div class="section" id="sec6">
  <h2>📢 新品PLP数据（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>广告活动数</h3><div class="val">{PLP_ACT}</div><div class="mom">上周：47</div></div>
    <div class="kpi-card alt"><h3>广告链接数</h3><div class="val">{PLP_LINK}</div><div class="mom">上周：63</div></div>
    <div class="kpi-card"><h3>曝光量</h3><div class="val">{PLP_IMP:,}</div></div>
    <div class="kpi-card alt"><h3>ROAS</h3><div class="val">{PLP_ROAS}x</div><div class="mom">上周：14.16x</div></div>
  </div>
  <div class="chart-box"><h3>PLP总数据：本周 vs 上周</h3><canvas id="cPlpTotal"></canvas></div>
  <h3>PLP分析人维度</h3>
{make_table(['分析人','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'], PLP_AN)}
  <h3>PLP品线维度</h3>
{make_table(['品线','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'], PLP_PX)}
  <h3>PLP拓展类型维度</h3>
{make_table(['拓展类型','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'], PLP_TZ)}
</div>''')

# sec7
W(f'''<div class="section" id="sec7">
  <h2>📋 新品出单情况（有对手口径）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>有对手总SKU</h3><div class="val">43</div><div class="mom">上周：32（+11）</div></div>
    <div class="kpi-card alt"><h3>有销量SKU</h3><div class="val">27</div><div class="mom">上周：21（+6）</div></div>
    <div class="kpi-card"><h3>出单率</h3><div class="val">62.8%</div></div>
  </div>
  <div class="chart-box"><h3>有对手SKU出单分布</h3><canvas id="cChPie"></canvas></div>
  <h3>出单情况明细</h3>
{make_table(['指标','本周','上周','变化'], CD_DATA[:13])}
</div>''')

# sec8
W(f'''<div class="section" id="sec8">
  <h2>🔍 新品未出单原因分析</h2>
  <div class="chart-box"><h3>未出单原因分布</h3><canvas id="cRsPie"></canvas></div>
  <h3>未出单原因明细</h3>
{make_table(['市场状态','SKU数量','占比','上周数量','上周占比','变化'], YY_DATA[:3])}
</div>''')

# sec9
W(f'''<div class="section" id="sec9">
  <h2>🎯 新品PLG维度明细（共{len(PLG_DATA)}条）</h2>
  <p style="color:#666;font-size:13px;margin-bottom:12px;">
    ● <span style="background:#FFE0B2;padding:2px 8px;border-radius:3px">橙色</span> PLP=Y 且 PLG费率&gt;0% &nbsp;&nbsp;
    ● <span style="background:#FCE4EC;padding:2px 8px;border-radius:3px">粉红</span> PLP=N 且 8日出单=未出单 &nbsp;&nbsp;
    ● <span style="background:#E8F5E9;padding:2px 8px;border-radius:3px">绿色</span> PLP=N 且 PLG费率&gt;0%
  </p>
{make_table(['编号','SKU','上架日期','首次出单','分析人','品类','拓展类型','8日出单','销量','销售额','对手销量','市占比','市场状态','操作判断','开启PLP','PLG费率'], PLG_DATA, plg_cls)}
</div>
</div><!-- /main -->
''')

# ── JS 数据变量（JSON 注入）───────────────────────────────────────────────────
# 用 json.dumps 生成合法 JS 字面量，嵌入 <script> 变量
W('''<script>
// ===== JS 数据变量 =====
const PX_LAB  = ''' + json.dumps([r[0] for r in PX_DATA]) + ''';
const PX_SQ   = ''' + json.dumps([num(safe(r[3]),0) for r in PX_DATA]) + ''';
const PX_SQP  = ''' + json.dumps([num(safe(r[4]),0) for r in PX_DATA]) + ''';
const PX_SA   = ''' + json.dumps([num(safe(r[5]),0) for r in PX_DATA]) + ''';
const PX_SAP  = ''' + json.dumps([num(safe(r[6]),0) for r in PX_DATA]) + ''';

const FX_LAB  = ''' + json.dumps([r[0] for r in FX_DATA]) + ''';
const FX_SQ   = ''' + json.dumps([num(safe(r[3]),0) for r in FX_DATA]) + ''';
const FX_SQP  = ''' + json.dumps([num(safe(r[4]),0) for r in FX_DATA]) + ''';
const FX_SA   = ''' + json.dumps([num(safe(r[5]),0) for r in FX_DATA]) + ''';
const FX_SAP  = ''' + json.dumps([num(safe(r[6]),0) for r in FX_DATA]) + ''';

const TZ_LAB  = ''' + json.dumps([r[0] for r in TZ_DATA]) + ''';
const TZ_RATE = ''' + json.dumps([num(safe(r[3]),0) for r in TZ_DATA]) + ''';
const TZ_RP   = ''' + json.dumps([num(safe(r[4]),0) for r in TZ_DATA]) + ''';
const TZ_SQ   = ''' + json.dumps([num(safe(r[6]),0) for r in TZ_DATA]) + ''';
const TZ_SQP  = ''' + json.dumps([num(safe(r[7]),0) for r in TZ_DATA]) + ''';

const JL_LAB  = ''' + json.dumps([r[0] for r in JL_DATA]) + ''';
const JL_OK   = ''' + json.dumps([int(num(safe(r[1]),0)) for r in JL_DATA]) + ''';
const JL_8    = ''' + json.dumps([int(num(safe(r[2]),0)) for r in JL_DATA]) + ''';
const JL_7    = ''' + json.dumps([int(num(safe(r[3]),0)) for r in JL_DATA]) + ''';
const JL_RATE = ''' + json.dumps([num(safe(r[4]),0) for r in JL_DATA]) + ''';

const JL_LEN  = ''' + str(JL_LEN) + ''';
const PLP_ACT = ''' + str(PLP_ACT) + ''';
const PLP_LINK = ''' + str(PLP_LINK) + ''';
const PLP_IMP  = ''' + str(PLP_IMP) + ''';
const PLP_ROAS = ''' + str(PLP_ROAS) + ''';
''')

# ── JS 代码（图表）───────────────────────────────────────────────────────────────
W('''
// ===== 导航 =====
function showSec(id, el) {
  document.querySelectorAll('.section').forEach(function(s) { s.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(function(a) { a.classList.remove('active'); });
  if (el) el.classList.add('active');
}

// ===== KPI =====
document.getElementById('kSku').textContent = 101;
document.getElementById('kSkuP').textContent = '上周：90';
document.getElementById('kSq').textContent = 195;
document.getElementById('kSqP').textContent = '上周：151（环比+29.1%）';
document.getElementById('kSa').textContent = '$' + (20494.85).toLocaleString('en',{minimumFractionDigits:2});
document.getElementById('kSaP').textContent = '上周：$' + (17688.39).toLocaleString('en',{minimumFractionDigits:2}) + '（环比+15.9%）';

// ===== Chart.js 全局 =====
var P = ['#7B1FA2','#BA68C8','#AB47BC','#CE93D8','#E1BEE7','#4A148C','#FFD54F','#FF8A65','#4FC3F7'];
Chart.defaults.font.family = "'Segoe UI','Microsoft YaHei',sans-serif";
Chart.defaults.color = '#333';

// ===== sec0: 总览 =====
new Chart(document.getElementById('cOverview'), {
  type: 'bar',
  data: {
    labels: ['累计SKU','总销量','销售额(/100)'],
    datasets: [
      {label:'4.30-5.6', data:[101,195,20494.85/100], backgroundColor:P[0]},
      {label:'4.23-4.29', data:[90,151,17688.39/100], backgroundColor:P[1]}
    ]
  },
  options: { responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

// ===== sec1: 品线销量 =====
new Chart(document.getElementById('cPxSales'), {
  type:'bar',
  data:{ labels:PX_LAB, datasets:[{label:'本周销量',data:PX_SQ,backgroundColor:P[0]},{label:'上周销量',data:PX_SQP,backgroundColor:P[1]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
// ===== sec1: 品线销售额 =====
new Chart(document.getElementById('cPxAmt'), {
  type:'bar',
  data:{ labels:PX_LAB, datasets:[{label:'本周销售额',data:PX_SA,backgroundColor:P[2]},{label:'上周销售额',data:PX_SAP,backgroundColor:P[3]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

// ===== sec2: 分析人销量 =====
new Chart(document.getElementById('cFxSales'), {
  type:'bar',
  data:{ labels:FX_LAB, datasets:[{label:'本周销量',data:FX_SQ,backgroundColor:P[0]},{label:'上周销量',data:FX_SQP,backgroundColor:P[1]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
// ===== sec2: 分析人销售额 =====
new Chart(document.getElementById('cFxAmt'), {
  type:'bar',
  data:{ labels:FX_LAB, datasets:[{label:'本周销售额',data:FX_SA,backgroundColor:P[2]},{label:'上周销售额',data:FX_SAP,backgroundColor:P[3]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

// ===== sec3: 拓展出单率 =====
new Chart(document.getElementById('cTzRate'), {
  type:'bar',
  data:{ labels:TZ_LAB, datasets:[{label:'本周出单率(%)',data:TZ_RATE,backgroundColor:P[0]},{label:'上周出单率(%)',data:TZ_RP,backgroundColor:P[1]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true,max:100}} }
});
// ===== sec3: 拓展销量 =====
new Chart(document.getElementById('cTzSales'), {
  type:'bar',
  data:{ labels:TZ_LAB, datasets:[{label:'本周销量',data:TZ_SQ,backgroundColor:P[2]},{label:'上周销量',data:TZ_SQP,backgroundColor:P[3]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

// ===== sec4: 及时率堆叠 =====
new Chart(document.getElementById('cJlStack'), {
  type:'bar',
  data:{
    labels:JL_LAB,
    datasets:[
      {label:'及时分析', data:JL_OK, backgroundColor:P[0], stack:'a'},
      {label:'8日内无分析', data:JL_8, backgroundColor:'#FFD54F', stack:'a'},
      {label:'超7日未分析', data:JL_7, backgroundColor:'#E53935', stack:'a'}
    ]
  },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
// ===== sec4: 及时率% =====
new Chart(document.getElementById('cJlRate'), {
  type:'bar',
  data:{ labels:JL_LAB, datasets:[{label:'及时率(%)',data:JL_RATE,backgroundColor:P.slice(0,JL_LEN)}] },
  options:{ responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,max:100}} }
});

// ===== sec6: PLP总数据 =====
new Chart(document.getElementById('cPlpTotal'), {
  type:'bar',
  data:{
    labels:['广告活动','链接','曝光量(/1000)','点击量','售出数','ROAS','CVR%','ACOS%'],
    datasets:[
      {label:'4.30-5.6', data:[PLP_ACT,PLP_LINK,PLP_IMP/1000,429,27,PLP_ROAS,6.29,15.54], backgroundColor:P[0]},
      {label:'4.23-4.29', data:[47,63,139.169,425,40,14.16,9.41,7.06], backgroundColor:P[1]}
    ]
  },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

// ===== sec7: 出单饼图 =====
new Chart(document.getElementById('cChPie'), {
  type:'doughnut',
  data:{ labels:['有销量SKU(27)','未出单SKU(13)','8日内(6)'], datasets:[{data:[27,13,6],backgroundColor:[P[0],'#E53935','#FFD54F']}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right'}}}
});

// ===== sec8: 未出单原因饼图 =====
new Chart(document.getElementById('cRsPie'), {
  type:'pie',
  data:{ labels:['竞争无优势(39)','正常(4)'], datasets:[{data:[39,4],backgroundColor:[P[0],P[2]]}] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right'}}}
});
</script>
</body>
</html>''')

# 写文件
content = '\n'.join(lines)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!', DST)
print('Size:', len(content), 'bytes')
