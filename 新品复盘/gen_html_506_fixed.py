#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 4.30-5.6 可视化 HTML 报告
修复：JS 语法错误、showSec 未定义、Chart.js 配置正确格式化
"""

import json, os

SRC = r"C:/Users/Administrator/Desktop/新品复盘/新品周报数据_4.30-5.6.xlsx"
JSON = r"C:/Users/Administrator/Desktop/新品复盘/sheets_506.json"
DST = r"C:/Users/Administrator/Desktop/新品复盘/新品周报_4.30-5.6_可视化.html"

# ── 读取 JSON ──────────────────────────────────────────────────────────────────
with open(JSON, encoding='utf-8') as f:
    sheets = json.load(f)

def safe(v, default=0):
    if v is None or v == '':
        return default
    return v

def num(v, default=0):
    if v is None or v == '':
        return default
    s = str(v).replace('%','').replace(',','').strip()
    try:
        return float(s)
    except:
        return default

def low_cls(row):
    """低占比新品行高亮"""
    plp = safe(row[18])   # 开启PLP
    plg = num(safe(row[19],0))  # PLG费率
    bd  = safe(row[17])   # 8日出单
    if plp == 'Y' and plg > 0:
        return 'highlight-orange'
    if plp == 'N' and bd == '未出单':
        return 'highlight-pink'
    if plp == 'N' and plg > 0:
        return 'highlight-green'
    return ''

def plg_cls(row):
    """PLG维度行高亮"""
    plp = safe(row[13])
    plg = num(safe(row[14],0))
    bd  = safe(row[7])
    if plp == 'Y' and plg > 0:
        return 'highlight-orange'
    if plp == 'N' and bd == '未出单':
        return 'highlight-pink'
    if plp == 'N' and plg > 0:
        return 'highlight-green'
    return ''

def make_table(headers, rows, cls_fn=None):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    trs = ''
    for row in rows:
        cls = cls_fn(row) if cls_fn else ''
        tds = ''.join(f'<td>{safe(c)}</td>' for c in row)
        trs += f'<tr class="{cls}">{tds}</tr>\n'
    return f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'

# ── 解析各 Sheet ──────────────────────────────────────────────────────────────
# sec0: 总体概况 (sheet 0)
rows0 = sheets[sorted(sheets.keys())[0]]
# 找"总SKU""总销量""总销售额"行
def find_row(rows, key):
    for r in rows:
        if r and key in [str(x) for x in r]:
            return r
    return None

# 直接用已知数据（从 Excel 读取）
# sec0: 总体概况 → sheet "总体概况"
ZONG = sheets.get('总体概况', rows0)

# sec1: 品线维度
PX = sheets.get('品线维度', [])

# sec2: 分析人维度
FX = sheets.get('分析人维度', [])

# sec3: 拓展类型
TZ = sheets.get('拓展类型', [])

# sec4: 分析及时率
JL = sheets.get('分析及时率', [])

# sec5: 低占比新品
DY = sheets.get('低占比新品', [])

# sec6: 新品PLP
PLP = sheets.get('新品PLP', [])

# sec7: 新品出单情况
CD = sheets.get('新品出单情况', [])

# sec8: 新品未出单原因
YY = sheets.get('新品未出单原因', [])

# sec9: 新品PLG维度
PLG = sheets.get('新品PLG维度', [])

print('Sheet list:', list(sheets.keys()))

# ── 辅助：提取品线维度数据 ───────────────────────────────────────────────────
def get_px_data():
    """从品线维度sheet提取数据（跳过合计行）"""
    labs, sq, sq_p, sa, sa_p = [], [], [], [], []
    for r in PX[1:]:
        if not r or not r[0]: continue
        lab = str(r[0])
        if lab == '合计': continue
        labs.append(lab)
        sq.append(num(safe(r[2],0)))
        sq_p.append(num(safe(r[3],0)))
        sa.append(num(safe(r[5],0)))
        sa_p.append(num(safe(r[6],0)))
    return labs, sq, sq_p, sa, sa_p

def get_fx_data():
    labs, sq, sq_p, sa, sa_p = [], [], [], [], []
    for r in FX[1:]:
        if not r or not r[0]: continue
        lab = str(r[0])
        if lab == '合计': continue
        labs.append(lab)
        sq.append(num(safe(r[2],0)))
        sq_p.append(num(safe(r[3],0)))
        sa.append(num(safe(r[5],0)))
        sa_p.append(num(safe(r[6],0)))
    return labs, sq, sq_p, sa, sa_p

def get_tz_data():
    labs, rate, rate_p, sq, sq_p = [], [], [], [], []
    for r in TZ[1:]:
        if not r or not r[0]: continue
        lab = str(r[0])
        if lab == '合计': continue
        labs.append(lab)
        rate.append(num(safe(r[2],0)))
        rate_p.append(num(safe(r[3],0)))
        sq.append(num(safe(r[4],0)))
        sq_p.append(num(safe(r[5],0)))
    return labs, rate, rate_p, sq, sq_p

def get_jl_data():
    labs, ok, d8, d7, rate = [], [], [], [], []
    for r in JL[1:]:
        if not r or not r[0]: continue
        lab = str(r[0])
        if lab == '合计': continue
        labs.append(lab)
        ok.append(num(safe(r[1],0)))
        d8.append(num(safe(r[2],0)))
        d7.append(num(safe(r[3],0)))
        rate.append(num(safe(r[4],0)))
    return labs, ok, d8, d7, rate

def get_plp_analyst_roas():
    """PLP sheet 分析人维度 ROAS"""
    labs, roas, roas_p = [], [], []
    # PLP sheet 结构: 前5行总计，然后分析人区块
    # 分析人区块起始行约 row 7-14
    for i, r in enumerate(PLP):
        if not r or not r[0]: continue
        lab = str(r[0])
        # 分析人名字
        if lab in ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星']:
            labs.append(lab)
            # ROAS 在 PLG 费率列? 实际上 PLP sheet 里有 ROAS 列
            # 根据 gen_xlsx_v4 的 PLP 结构:
            # 分析人维度: 列 = 分析人, 活动, 链接, 曝光, 点击, 售出, 花费, 销售额, ROAS, CVR, CTR, CPC, CPA, ACOS
            roas.append(num(safe(r[8],0)))   # ROAS
            roas_p.append(num(safe(r[20],0))) # 上周ROAS (偏移)
    return labs, roas, roas_p

# ── 提取数据 ──────────────────────────────────────────────────────────────────
PX_LAB, PX_SQ, PX_SQ_P, PX_SA, PX_SA_P = get_px_data()
FX_LAB, FX_SQ, FX_SQ_P, FX_SA, FX_SA_P = get_fx_data()
TZ_LAB, TZ_RATE, TZ_RATE_P, TZ_SQ, TZ_SQ_P = get_tz_data()
JL_LAB, JL_OK, JL_8, JL_7, JL_RATE = get_jl_data()

print('PX_LAB:', PX_LAB)
print('FX_LAB:', FX_LAB)
print('TZ_LAB:', TZ_LAB)
print('JL_LAB:', JL_LAB)

# 写 HTML
html = '''<!DOCTYPE html>
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
.chart-box { margin:20px 0; padding:16px; background:#faf5ff; border-radius:8px; }
.chart-box h3 { color:#4A148C; font-size:14px; margin-bottom:12px; }
canvas { max-width:100%; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:13px; }
th { background:#7B1FA2; color:#fff; padding:8px 10px; text-align:left; position:sticky; top:0; }
td { padding:7px 10px; border-bottom:1px solid #eee; }
tr:nth-child(even) { background:#f9f5ff; }
tr:hover { background:#ede7f6; }
.highlight-orange { background:#FFE0B2 !important; }
.highlight-pink  { background:#FCE4EC !important; }
.highlight-green  { background:#E8F5E9 !important; }
.nav-toggle { display:none; position:fixed; top:10px; left:10px; z-index:200; background:#7B1FA2; color:#fff; border:none; padding:8px 12px; border-radius:6px; font-size:18px; cursor:pointer; }
@media(max-width:768px) {{
  .sidebar {{ transform:translateX(-100%); transition:0.3s; }}
  .sidebar.open {{ transform:translateX(0); }}
  .main {{ margin-left:0; }}
  .nav-toggle {{ display:block; }}
}}
</style>
</head>
<body>
<button class="nav-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>
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

<!-- ==================== sec0: 总体概况 ==================== -->
<div class="section active" id="sec0">
  <h2>📈 总体概况（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>累计SKU数</h3><div class="val" id="kSku"></div><div class="mom" id="kSkuP"></div></div>
    <div class="kpi-card alt"><h3>总销量</h3><div class="val" id="kSq"></div><div class="mom" id="kSqP"></div></div>
    <div class="kpi-card"><h3>总销售额(USD)</h3><div class="val" id="kSa"></div><div class="mom" id="kSaP"></div></div>
  </div>
  <div class="chart-box"><h3>核心指标：本周 vs 上周</h3><canvas id="cOverview"></canvas></div>
</div>

<!-- ==================== sec1: 品线维度 ==================== -->
<div class="section" id="sec1">
  <h2>📊 品线维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各品线销量对比</h3><canvas id="cPxSales"></canvas></div>
  <div class="chart-box"><h3>各品线销售额对比（USD）</h3><canvas id="cPxAmt"></canvas></div>
  <h3>品线明细</h3>
''' + make_table(
    ['品线','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比','本周有对手','上周有对手'],
    [r[0:11] for r in PX[1:] if r and r[0] and r[0]!='合计']
) + '''
</div>

<!-- ==================== sec2: 分析人维度 ==================== -->
<div class="section" id="sec2">
  <h2>👤 分析人维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各分析人销量对比</h3><canvas id="cFxSales"></canvas></div>
  <div class="chart-box"><h3>各分析人销售额对比（USD）</h3><canvas id="cFxAmt"></canvas></div>
  <h3>分析人明细</h3>
''' + make_table(
    ['分析人','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比'],
    [r[0:9] for r in FX[1:] if r and r[0] and r[0]!='合计']
) + '''
</div>

<!-- ==================== sec3: 拓展类型 ==================== -->
<div class="section" id="sec3">
  <h2>🔄 拓展类型维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各类型出单率（%）</h3><canvas id="cTzRate"></canvas></div>
  <div class="chart-box"><h3>各类型销量对比</h3><canvas id="cTzSales"></canvas></div>
  <h3>拓展类型明细</h3>
''' + make_table(
    ['拓展类型','本周SKU','本周出单','出单率','上周出单率','出单率环比','本周销量','上周销量','本周销售额','上周销售额','销售额环比'],
    [r[0:11] for r in TZ[1:] if r and r[0] and r[0]!='合计']
) + '''
</div>

<!-- ==================== sec4: 分析及时率 ==================== -->
<div class="section" id="sec4">
  <h2>⏱ 分析及时率（截止5.6）</h2>
  <div class="chart-box"><h3>各分析人及时分析情况（SKU数）</h3><canvas id="cJlStack"></canvas></div>
  <div class="chart-box"><h3>各分析人及时率（%）</h3><canvas id="cJlRate"></canvas></div>
  <h3>分析及时率明细</h3>
''' + make_table(
    ['分析人','截止5.6SKU','及时分析','8日内无分析','超7日未分析','及时率','上周及时率','变化'],
    [r[0:8] for r in JL[1:] if r and r[0] and r[0]!='合计']
) + '''
</div>

<!-- ==================== sec5: 低占比新品 ==================== -->
<div class="section" id="sec5">
  <h2>⚠ 低占比新品明细（共'''+str(len([r for r in DY[1:] if r and r[0]]))+'''条）</h2>
''' + make_table(
    ['编号','SKU','上架日期','分析人','品类','拓展类型','销量','销量环比','销售额','销售额环比','对手销量','对手销量环比','市占比','市占比环比','8日出单','7日频次','7日新品频次','市场状态1','操作判断','市场状态2','开启PLP','PLG费率'],
    [r[0:21] for r in DY[1:] if r and r[0]],
    low_cls
) + '''
</div>

<!-- ==================== sec6: 新品PLP ==================== -->
<div class="section" id="sec6">
  <h2>📢 新品PLP数据（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>广告活动数</h3><div class="val">42</div><div class="mom">上周：47</div></div>
    <div class="kpi-card alt"><h3>广告链接数</h3><div class="val">53</div><div class="mom">上周：63</div></div>
    <div class="kpi-card"><h3>曝光量</h3><div class="val">119,686</div></div>
    <div class="kpi-card alt"><h3>ROAS</h3><div class="val">6.44x</div><div class="mom">上周：14.16x</div></div>
  </div>
  <div class="chart-box"><h3>PLP总数据：本周 vs 上周</h3><canvas id="cPlpTotal"></canvas></div>
  <h3>PLP总数据明细</h3>
''' + make_table(
    ['维度','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'],
    [r[0:14] for r in PLP[0:5] if r and r[0]]
) + '''
</div>

<!-- ==================== sec7: 新品出单情况 ==================== -->
<div class="section" id="sec7">
  <h2>📋 新品出单情况（有对手口径）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>有对手总SKU</h3><div class="val">43</div><div class="mom">上周：32（+11）</div></div>
    <div class="kpi-card alt"><h3>有销量SKU</h3><div class="val">27</div><div class="mom">上周：21（+6）</div></div></div>
    <div class="kpi-card"><h3>出单率</h3><div class="val">62.8%</div></div>
  </div>
  <div class="chart-box"><h3>有对手SKU出单分布</h3><canvas id="cChPie"></canvas></div>
  <h3>出单情况明细</h3>
''' + make_table(
    ['指标','本周','上周','变化'],
    [r[0:4] for r in CD[1:13] if r and r[0]]
) + '''
</div>

<!-- ==================== sec8: 未出单原因 ==================== -->
<div class="section" id="sec8">
  <h2>🔍 新品未出单原因分析</h2>
  <div class="chart-box"><h3>未出单原因分布</h3><canvas id="cRsPie"></canvas></div>
  <h3>未出单原因明细</h3>
''' + make_table(
    ['市场状态','SKU数量','占比','上周数量','上周占比','变化'],
    [r[0:6] for r in YY[1:3] if r and r[0]]
) + '''
</div>

<!-- ==================== sec9: PLG维度 ==================== -->
<div class="section" id="sec9">
  <h2>🎯 新品PLG维度明细（共'''+str(len([r for r in PLG[1:] if r and r[0]]))+'''条）</h2>
  <p style="color:#666;font-size:13px;margin-bottom:12px;">
    ● <span style="background:#FFE0B2;padding:2px 8px;border-radius:3px">橙色</span> PLP=Y 且 PLG费率&gt;0% &nbsp;&nbsp;
    ● <span style="background:#FCE4EC;padding:2px 8px;border-radius:3px">粉红</span> PLP=N 且 8日出单=未出单 &nbsp;&nbsp;
    ● <span style="background:#E8F5E9;padding:2px 8px;border-radius:3px">绿色</span> PLP=N 且 PLG费率&gt;0%
  </p>
''' + make_table(
    ['编号','SKU','上架日期','首次出单','分析人','品类','拓展类型','8日出单','销量','销售额','对手销量','市占比','市场状态','操作判断','开启PLP','PLG费率'],
    [r[0:16] for r in PLG[1:] if r and r[0]],
    plg_cls
) + '''
</div>

</div><!-- /main -->

<script>
/* ========== 导航 ========== */
function showSec(id, el) {
  document.querySelectorAll('.section').forEach(function(s) { s.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(function(a) { a.classList.remove('active'); });
  if (el) el.classList.add('active');
}

/* ========== JS 数据 ========== */
const PX_LAB = ''' + json.dumps(PX_LAB) + ''';
const PX_SQ  = ''' + json.dumps(PX_SQ) + ''';
const PX_SQ_P = ''' + json.dumps(PX_SQ_P) + ''';
const PX_SA  = ''' + json.dumps(PX_SA) + ''';
const PX_SA_P = ''' + json.dumps(PX_SA_P) + ''';

const FX_LAB = ''' + json.dumps(FX_LAB) + ''';
const FX_SQ  = ''' + json.dumps(FX_SQ) + ''';
const FX_SQ_P = ''' + json.dumps(FX_SQ_P) + ''';
const FX_SA  = ''' + json.dumps(FX_SA) + ''';
const FX_SA_P = ''' + json.dumps(FX_SA_P) + ''';

const TZ_LAB = ''' + json.dumps(TZ_LAB) + ''';
const TZ_RATE = ''' + json.dumps(TZ_RATE) + ''';
const TZ_RATE_P = ''' + json.dumps(TZ_RATE_P) + ''';
const TZ_SQ  = ''' + json.dumps(TZ_SQ) + ''';
const TZ_SQ_P = ''' + json.dumps(TZ_SQ_P) + ''';

const JL_LAB = ''' + json.dumps(JL_LAB) + ''';
const JL_OK  = ''' + json.dumps(JL_OK) + ''';
const JL_8   = ''' + json.dumps(JL_8) + ''';
const JL_7   = ''' + json.dumps(JL_7) + ''';
const JL_RATE = ''' + json.dumps(JL_RATE) + ''';

const P = ['#7B1FA2','#BA68C8','#AB47BC','#CE93D8','#E1BEE7','#4A148C','#FFD54F','#FF8A65','#4FC3F7'];

/* ========== KPI ========== */
document.getElementById('kSku').textContent = 101;
document.getElementById('kSkuP').textContent = '上周：90';
document.getElementById('kSq').textContent = 195;
document.getElementById('kSqP').textContent = '上周：151（环比+29.1%）';
document.getElementById('kSa').textContent = '$' + (20494.85).toLocaleString('en',{minimumFractionDigits:2});
document.getElementById('kSaP').textContent = '上周：$' + (17688.39).toLocaleString('en',{minimumFractionDigits:2}) + '（环比+15.9%）';

/* ========== Chart.js 全局设置 ========== */
Chart.defaults.font.family = "'Segoe UI','Microsoft YaHei',sans-serif";
Chart.defaults.color = '#333';

/* ========== sec0: 总览 ========== */
new Chart(document.getElementById('cOverview'), {
  type: 'bar',
  data: {
    labels: ['累计SKU','总销量','销售额(/100)'],
    datasets: [
      { label:'4.30-5.6', data:[101,195,20494.85/100], backgroundColor:P[0] },
      { label:'4.23-4.29', data:[90,151,17688.39/100], backgroundColor:P[1] }
    ]
  },
  options: { responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ========== sec1: 品线 ========== */
new Chart(document.getElementById('cPxSales'), {
  type:'bar',
  data:{ labels:PX_LAB, datasets:[{label:'本周销量',data:PX_SQ,backgroundColor:P[0]},{label:'上周销量',data:PX_SQ_P,backgroundColor:P[1]}] },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
new Chart(document.getElementById('cPxAmt'), {
  type:'bar',
  data:{ labels:PX_LAB, datasets:[{label:'本周销售额',data:PX_SA,backgroundColor:P[2]},{label:'上周销售额',data:PX_SA_P,backgroundColor:P[3]}] },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ========== sec2: 分析人 ========== */
new Chart(document.getElementById('cFxSales'), {
  type:'bar',
  data:{ labels:FX_LAB, datasets:[{label:'本周销量',data:FX_SQ,backgroundColor:P[0]},{label:'上周销量',data:FX_SQ_P,backgroundColor:P[1]}] },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
new Chart(document.getElementById('cFxAmt'), {
  type:'bar',
  data:{ labels:FX_LAB, datasets:[{label:'本周销售额',data:FX_SA,backgroundColor:P[2]},{label:'上周销售额',data:FX_SA_P,backgroundColor:P[3]}] },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ========== sec3: 拓展类型 ========== */
new Chart(document.getElementById('cTzRate'), {
  type:'bar',
  data:{ labels:TZ_LAB, datasets:[{label:'本周出单率(%)',data:TZ_RATE,backgroundColor:P[0]},{label:'上周出单率(%)',data:TZ_RATE_P,backgroundColor:P[1]}] },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true,max:100}} }
});
new Chart(document.getElementById('cTzSales'), {
  type:'bar',
  data:{ labels:TZ_LAB, datasets:[{label:'本周销量',data:TZ_SQ,backgroundColor:P[2]},{label:'上周销量',data:TZ_SQ_P,backgroundColor:P[3]}] },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ========== sec4: 及时率 ========== */
new Chart(document.getElementById('cJlStack'), {
  type:'bar',
  data:{
    labels:JL_LAB,
    datasets:[
      {label:'及时分析',data:JL_OK,backgroundColor:P[0],stack:'a'},
      {label:'8日内无分析',data:JL_8,backgroundColor:'#FFD54F',stack:'a'},
      {label:'超7日未分析',data:JL_7,backgroundColor:'#E53935',stack:'a'}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{stacked:true,beginAtZero:true}} }
});
new Chart(document.getElementById('cJlRate'), {
  type:'bar',
  data:{ labels:JL_LAB, datasets:[{label:'及时率(%)',data:JL_RATE,backgroundColor:P.slice(0,JL_LAB.length)}] },
  options:{ responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,max:100}} }
});

/* ========== sec6: PLP ========== */
new Chart(document.getElementById('cPlpTotal'), {
  type:'bar',
  data:{
    labels:['广告活动','链接','曝光量(/1000)','点击量','售出数','ROAS','CVR%','ACOS%'],
    datasets:[
      {label:'4.30-5.6', data:[42,53,119686/1000,429,27,6.44,6.29,15.54], backgroundColor:P[0]},
      {label:'4.23-4.29', data:[47,63,139169/1000,425,40,14.16,9.41,7.06], backgroundColor:P[1]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ========== sec7: 出单饼图 ========== */
new Chart(document.getElementById('cChPie'), {
  type:'doughnut',
  data:{
    labels:['有销量SKU(27)','未出单SKU(13)','8日内(6)'],
    datasets:[{ data:[27,13,6], backgroundColor:[P[0],'#E53935','#FFD54F'] }]
  },
  options:{ responsive:true, plugins:{legend:{position:'right'}} }
});

/* ========== sec8: 未出单原因饼图 ========== */
new Chart(document.getElementById('cRsPie'), {
  type:'pie',
  data:{
    labels:['竞争无优势(39)','正常(4)'],
    datasets:[{ data:[39,4], backgroundColor:[P[0],P[2]] }]
  },
  options:{ responsive:true, plugins:{legend:{position:'right'}} }
});
</script>
</body>
</html>'''

with open(DST, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done:', DST)
print('File size:', len(html), 'bytes')
