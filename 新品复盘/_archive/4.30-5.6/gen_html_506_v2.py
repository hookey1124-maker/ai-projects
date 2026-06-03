#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 4.30-5.6 可视化 HTML 报告 - 正确版
从 sheets_506.json 正确提取各 Sheet 数据并生成 HTML
"""

import json, os

JSON = r"c:/Users/Hardy/ai-projects/新品复盘/sheets_506.json"
DST  = r"c:/Users/Hardy/ai-projects/新品复盘/新品周报_4.30-5.6_可视化.html"

with open(JSON, encoding='utf-8') as f:
    sheets = json.load(f)

def safe(v, default=''):
    if v is None or v == '':
        return default
    return v

def num(v, default=0.0):
    if v is None or v == '':
        return default
    s = str(v).replace('%','').replace(',','').strip()
    try:
        return float(s)
    except:
        return default

# ── 读取各 Sheet ────────────────────────────────────────────────────────────
# 所有 sheet 名
print("Sheets:", list(sheets.keys()))

# 总体概况 -> 用已知值（从 Excel 确认）
SKU_THIS, SKU_PREV = 101, 90
SQ_THIS,  SQ_PREV  = 195, 151
SA_THIS,  SA_PREV  = 20494.85, 17688.39

# ── 品线维度 ─────────────────────────────────────────────────────────────────
PX = sheets.get('品线维度', [])
# 第0行是表头: ['品线','本周SKU',...]
# 数据行: r[0]=品线名, r[1]=本周SKU, r[2]=新上架, r[3]=本周销量, r[4]=上周销量, r[5]=销量环比, ...
# 跳过第0行(表头)和包含'合计'的行
PX_DATA = []
for r in PX[1:]:
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    if lab == '合计': continue
    PX_DATA.append(r)

print("PX_DATA labs:", [r[0] for r in PX_DATA])

PX_LAB  = [str(r[0]) for r in PX_DATA]
PX_SKU  = [int(num(safe(r[1]),0)) for r in PX_DATA]
PX_NEW  = [int(num(safe(r[2]),0)) for r in PX_DATA]
PX_SQ   = [num(safe(r[3]),0) for r in PX_DATA]
PX_SQ_P = [num(safe(r[4]),0) for r in PX_DATA]
PX_SA   = [num(safe(r[5]),0) for r in PX_DATA]
PX_SA_P = [num(safe(r[6]),0) for r in PX_DATA]
PX_OPP   = [int(num(safe(r[8]),0)) for r in PX_DATA]  # 本周有对手
PX_OPP_P = [int(num(safe(r[9]),0)) for r in PX_DATA]  # 上周有对手

# ── 分析人维度 ────────────────────────────────────────────────────────────────
FX = sheets.get('分析人维度', [])
FX_DATA = []
for r in FX[1:]:
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    if lab == '合计': continue
    FX_DATA.append(r)

print("FX_DATA labs:", [r[0] for r in FX_DATA])

FX_LAB  = [str(r[0]) for r in FX_DATA]
FX_SKU  = [int(num(safe(r[1]),0)) for r in FX_DATA]
FX_NEW  = [int(num(safe(r[2]),0)) for r in FX_DATA]
FX_SQ   = [num(safe(r[3]),0) for r in FX_DATA]
FX_SQ_P = [num(safe(r[4]),0) for r in FX_DATA]
FX_SA   = [num(safe(r[5]),0) for r in FX_DATA]
FX_SA_P = [num(safe(r[6]),0) for r in FX_DATA]

# ── 拓展类型 ──────────────────────────────────────────────────────────────────
TZ = sheets.get('拓展类型', [])
TZ_DATA = []
for r in TZ[1:]:
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    if lab == '合计': continue
    TZ_DATA.append(r)

print("TZ_DATA labs:", [r[0] for r in TZ_DATA])

TZ_LAB   = [str(r[0]) for r in TZ_DATA]
TZ_SKU   = [int(num(safe(r[1]),0)) for r in TZ_DATA]
TZ_ORD   = [int(num(safe(r[2]),0)) for r in TZ_DATA]
TZ_RATE  = [num(safe(r[3]),0) for r in TZ_DATA]
TZ_RP    = [num(safe(r[4]),0) for r in TZ_DATA]
TZ_SQ    = [num(safe(r[6]),0) for r in TZ_DATA]   # 本周销量 (idx6)
TZ_SQ_P  = [num(safe(r[7]),0) for r in TZ_DATA]   # 上周销量 (idx7)

# ── 分析及时率 ────────────────────────────────────────────────────────────────
JL = sheets.get('分析及时率', [])
JL_DATA = []
for r in JL[1:]:
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    if lab == '合计': continue
    JL_DATA.append(r)

print("JL_DATA labs:", [r[0] for r in JL_DATA])

JL_LAB  = [str(r[0]) for r in JL_DATA]
JL_OK    = [int(num(safe(r[1]),0)) for r in JL_DATA]  # 及时分析
JL_8     = [int(num(safe(r[2]),0)) for r in JL_DATA]  # 8日内无分析
JL_7     = [int(num(safe(r[3]),0)) for r in JL_DATA]  # 超7日未分析
JL_RATE  = [num(safe(r[4]),0) for r in JL_DATA]  # 及时率

# ── 低占比新品 ────────────────────────────────────────────────────────────────
DY = sheets.get('低占比新品', [])
DY_DATA = []
for r in DY[1:]:
    if not r or not r[0]: continue
    DY_DATA.append(r)

print("DY_DATA len:", len(DY_DATA))

# ── 新品PLP ──────────────────────────────────────────────────────────────────
PLP = sheets.get('新品PLP', [])
# PLP sheet: 前5行为总计，然后分析人区块、品线区块等
# 总数据: rows 0-4 (其中 row0 是表头)
PLP_TOTAL = []
PLP_AN    = []  # 分析人维度
PLP_PX    = []  # 品线维度
PLP_TZ    = []  # 拓展类型

in_an = False
in_px = False
in_tz = False

for i, r in enumerate(PLP):
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    
    if lab == '分析人':
        in_an = True
        in_px = False
        in_tz = False
        continue
    if lab == '品线':
        in_an = False
        in_px = True
        in_tz = False
        continue
    if lab == '拓展类型':
        in_an = False
        in_px = False
        in_tz = True
        continue
    if lab == '合计':
        in_an = False
        in_px = False
        in_tz = False
        continue
    
    if in_an and lab in ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星']:
        PLP_AN.append(r)
    elif in_px and lab != '合计':
        PLP_PX.append(r)
    elif in_tz and lab != '合计':
        PLP_TZ.append(r)
    elif i < 5:
        PLP_TOTAL.append(r)

print("PLP_AN:", [r[0] for r in PLP_AN])
print("PLP_PX:", [r[0] for r in PLP_PX])
print("PLP_TZ:", [r[0] for r in PLP_TZ])

# PLP 总数据 KPI（从 PLP_TOTAL 提取）
# PLP_TOTAL 结构: [活动数, 链接数, 曝光量, 点击量, 售出数, 花费, 销售额, ROAS, ...]
PLP_ACT      = int(num(safe(PLP_TOTAL[0][0] if PLP_TOTAL else 42), 42))
PLP_LINK     = int(num(safe(PLP_TOTAL[0][1] if PLP_TOTAL else 53), 53))
PLP_IMP      = int(num(safe(PLP_TOTAL[0][2] if PLP_TOTAL else 119686), 119686))
PLP_ROAS     = num(safe(PLP_TOTAL[0][7] if PLP_TOTAL else 6.44), 6.44)
PLP_ROAS_P   = num(safe(PLP_TOTAL[1][7] if len(PLP_TOTAL)>1 else 14.16), 14.16)

# ── 新品出单情况 ────────────────────────────────────────────────────────────────
CD = sheets.get('新品出单情况', [])
CD_DATA = []
for r in CD[1:]:
    if not r or not r[0]: continue
    CD_DATA.append(r)

print("CD_DATA len:", len(CD_DATA))

# ── 新品未出单原因 ──────────────────────────────────────────────────────────────
YY = sheets.get('新品未出单原因', [])
YY_DATA = []
for r in YY[1:]:
    if not r or not r[0]: continue
    YY_DATA.append(r)

print("YY_DATA len:", len(YY_DATA))

# ── 新品PLG维度 ────────────────────────────────────────────────────────────────
PLG = sheets.get('新品PLG维度', [])
PLG_DATA = []
for r in PLG[1:]:
    if not r or not r[0]: continue
    PLG_DATA.append(r)

print("PLG_DATA len:", len(PLG_DATA))


# ── HTML 模板生成 ────────────────────────────────────────────────────────────
import json as json2

def make_table(headers, rows, cls_fn=None):
    """生成 HTML 表格"""
    th = ''.join(f'<th>{h}</th>' for h in headers)
    trs = ''
    for row in rows:
        cls = cls_fn(row) if cls_fn else ''
        cells = ''.join(f'<td>{safe(c)}</td>' for c in row)
        trs += f'<tr class="{cls}">{cells}</tr>\n'
    return f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


# ── 行高亮函数 (用于 low_cls 和 plg_cls) ──────────────────────────────────
def low_row_highlight(row):
    """低占比新品行高亮: PLP=Y & PLG>0 → orange; PLP=N & 未出单 → pink; PLP=N & PLG>0 → green"""
    try:
        plp = str(safe(row[18])).strip()   # 开启PLP
        plg = num(safe(row[19]), 0)        # PLG费率
        bd  = str(safe(row[17])).strip()   # 8日出单 (操作判断列附近)
        if plp == 'Y' and plg > 0:
            return 'highlight-orange'
        if plp == 'N' and bd == '未出单':
            return 'highlight-pink'
        if plp == 'N' and plg > 0:
            return 'highlight-green'
    except:
        pass
    return ''

def plg_row_highlight(row):
    """PLG维度行高亮"""
    try:
        plp = str(safe(row[13])).strip()  # 开启PLP
        plg = num(safe(row[14]), 0)       # PLG费率
        bd  = str(safe(row[7])).strip()   # 8日出单
        if plp == 'Y' and plg > 0:
            return 'highlight-orange'
        if plp == 'N' and bd == '未出单':
            return 'highlight-pink'
        if plp == 'N' and plg > 0:
            return 'highlight-green'
    except:
        pass
    return ''


# ── 构建 HTML ─────────────────────────────────────────────────────────────────
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
@media(max-width:768px) {
  .sidebar { transform:translateX(-100%); transition:0.3s; }
  .sidebar.open { transform:translateX(0); }
  .main { margin-left:0; }
  .nav-toggle { display:block; }
}
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

<!-- ===== sec0: 总体概况 ===== -->
<div class="section active" id="sec0">
  <h2>📈 总体概况（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>累计SKU数</h3><div class="val" id="kSku"></div><div class="mom" id="kSkuP"></div></div>
    <div class="kpi-card alt"><h3>总销量</h3><div class="val" id="kSq"></div><div class="mom" id="kSqP"></div></div>
    <div class="kpi-card"><h3>总销售额(USD)</h3><div class="val" id="kSa"></div><div class="mom" id="kSaP"></div></div>
  </div>
  <div class="chart-box"><h3>核心指标：本周 vs 上周</h3><canvas id="cOverview"></canvas></div>
</div>

<!-- ===== sec1: 品线维度 ===== -->
<div class="section" id="sec1">
  <h2>📊 品线维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各品线销量对比</h3><canvas id="cPxSales"></canvas></div>
  <div class="chart-box"><h3>各品线销售额对比（USD）</h3><canvas id="cPxAmt"></canvas></div>
  <h3>品线明细</h3>
''' + make_table(
    ['品线','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比','本周有对手','上周有对手'],
    PX_DATA
) + '''
</div>

<!-- ===== sec2: 分析人维度 ===== -->
<div class="section" id="sec2">
  <h2>👤 分析人维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各分析人销量对比</h3><canvas id="cFxSales"></canvas></div>
  <div class="chart-box"><h3>各分析人销售额对比（USD）</h3><canvas id="cFxAmt"></canvas></div>
  <h3>分析人明细</h3>
''' + make_table(
    ['分析人','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比'],
    FX_DATA
) + '''
</div>

<!-- ===== sec3: 拓展类型 ===== -->
<div class="section" id="sec3">
  <h2>🔄 拓展类型维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各类型出单率（%）</h3><canvas id="cTzRate"></canvas></div>
  <div class="chart-box"><h3>各类型销量对比</h3><canvas id="cTzSales"></canvas></div>
  <h3>拓展类型明细</h3>
''' + make_table(
    ['拓展类型','本周SKU','本周出单','出单率','上周出单率','出单率环比','本周销量','上周销量','本周销售额','上周销售额','销售额环比'],
    TZ_DATA
) + '''
</div>

<!-- ===== sec4: 分析及时率 ===== -->
<div class="section" id="sec4">
  <h2>⏱ 分析及时率（截止5.6）</h2>
  <div class="chart-box"><h3>各分析人及时分析情况（SKU数）</h3><canvas id="cJlStack"></canvas></div>
  <div class="chart-box"><h3>各分析人及时率（%）</h3><canvas id="cJlRate"></canvas></div>
  <h3>分析及时率明细</h3>
''' + make_table(
    ['分析人','截止5.6SKU','及时分析','8日内无分析','超7日未分析','及时率','上周及时率','变化'],
    JL_DATA
) + '''
</div>

<!-- ===== sec5: 低占比新品 ===== -->
<div class="section" id="sec5">
  <h2>⚠ 低占比新品明细（共''' + str(len(DY_DATA)) + '''条）</h2>
''' + make_table(
    ['编号','SKU','上架日期','分析人','品类','拓展类型','销量','销量环比','销售额','销售额环比',
     '对手销量','对手销量环比','市占比','市占比环比','8日出单','7日频次','7日新品频次',
     '市场状态1','操作判断','市场状态2','开启PLP','PLG费率'],
    DY_DATA,
    low_row_highlight
) + '''
</div>

<!-- ===== sec6: 新品PLP ===== -->
<div class="section" id="sec6">
  <h2>📢 新品PLP数据（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>广告活动数</h3><div class="val">''' + str(PLP_ACT) + '''</div><div class="mom">上周：47</div></div>
    <div class="kpi-card alt"><h3>广告链接数</h3><div class="val">''' + str(PLP_LINK) + '''</div><div class="mom">上周：63</div></div>
    <div class="kpi-card"><h3>曝光量</h3><div class="val">''' + '{:,}'.format(PLP_IMP) + '''</div></div>
    <div class="kpi-card alt"><h3>ROAS</h3><div class="val">''' + str(PLP_ROAS) + '''x</div><div class="mom">上周：14.16x</div></div>
  </div>
  <div class="chart-box"><h3>PLP总数据：本周 vs 上周</h3><canvas id="cPlpTotal"></canvas></div>
  <h3>PLP分析人维度</h3>
''' + make_table(
    ['分析人','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'],
    PLP_AN
) + '''
  <h3>PLP品线维度</h3>
''' + make_table(
    ['品线','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'],
    PLP_PX
) + '''
  <h3>PLP拓展类型维度</h3>
''' + make_table(
    ['拓展类型','广告活动','链接','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','CPC','CPA','ACOS'],
    PLP_TZ
) + '''
</div>

<!-- ===== sec7: 新品出单情况 ===== -->
<div class="section" id="sec7">
  <h2>📋 新品出单情况（有对手口径）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>有对手总SKU</h3><div class="val">43</div><div class="mom">上周：32（+11）</div></div>
    <div class="kpi-card alt"><h3>有销量SKU</h3><div class="val">27</div><div class="mom">上周：21（+6）</div></div>
    <div class="kpi-card"><h3>出单率</h3><div class="val">62.8%</div></div>
  </div>
  <div class="chart-box"><h3>有对手SKU出单分布</h3><canvas id="cChPie"></canvas></div>
  <h3>出单情况明细</h3>
''' + make_table(
    ['指标','本周','上周','变化'],
    CD_DATA[:13]  # 前13行是出单情况指标
) + '''
</div>

<!-- ===== sec8: 未出单原因 ===== -->
<div class="section" id="sec8">
  <h2>🔍 新品未出单原因分析</h2>
  <div class="chart-box"><h3>未出单原因分布</h3><canvas id="cRsPie"></canvas></div>
  <h3>未出单原因明细</h3>
''' + make_table(
    ['市场状态','SKU数量','占比','上周数量','上周占比','变化'],
    YY_DATA[:3]  # 前3行是汇总
) + '''
</div>

<!-- ===== sec9: PLG维度 ===== -->
<div class="section" id="sec9">
  <h2>🎯 新品PLG维度明细（共''' + str(len(PLG_DATA)) + '''条）</h2>
  <p style="color:#666;font-size:13px;margin-bottom:12px;">
    ● <span style="background:#FFE0B2;padding:2px 8px;border-radius:3px">橙色</span> PLP=Y 且 PLG费率&gt;0% &nbsp;&nbsp;
    ● <span style="background:#FCE4EC;padding:2px 8px;border-radius:3px">粉红</span> PLP=N 且 8日出单=未出单 &nbsp;&nbsp;
    ● <span style="background:#E8F5E9;padding:2px 8px;border-radius:3px">绿色</span> PLP=N 且 PLG费率&gt;0%
  </p>
''' + make_table(
    ['编号','SKU','上架日期','首次出单','分析人','品类','拓展类型','8日出单','销量','销售额','对手销量','市占比','市场状态','操作判断','开启PLP','PLG费率'],
    PLG_DATA,
    plg_row_highlight
) + '''
</div>

</div><!-- /main -->

<script>
/* ===== 导航 ===== */
function showSec(id, el) {
  document.querySelectorAll('.section').forEach(function(s) { s.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(function(a) { a.classList.remove('active'); });
  if (el) el.classList.add('active');
}

/* ===== 颜色 ===== */
const P = ['#7B1FA2','#BA68C8','#AB47BC','#CE93D8','#E1BEE7','#4A148C','#FFD54F','#FF8A65','#4FC3F7'];

/* ===== KPI ===== */
document.getElementById('kSku').textContent = ''' + str(SKU_THIS) + ''';
document.getElementById('kSkuP').textContent = '上周：''' + str(SKU_PREV) + '''';
document.getElementById('kSq').textContent = ''' + str(SQ_THIS) + ''';
document.getElementById('kSqP').textContent = '上周：''' + str(SQ_PREV) + '''（环比+29.1%）';
document.getElementById('kSa').textContent = '$' + ('''+str(SA_THIS)+''').toLocaleString('en',{minimumFractionDigits:2});
document.getElementById('kSaP').textContent = '上周：$' + ('''+str(SA_PREV)+''').toLocaleString('en',{minimumFractionDigits:2}) + '（环比+15.9%）';

/* ===== Chart.js 全局 ===== */
Chart.defaults.font.family = "'Segoe UI','Microsoft YaHei',sans-serif";
Chart.defaults.color = '#333';

/* ===== sec0: 总览 ===== */
new Chart(document.getElementById('cOverview'), {
  type: 'bar',
  data: {
    labels: ['累计SKU','总销量','销售额(/100)'],
    datasets: [
      { label:'4.30-5.6', data:[''' + str(SKU_THIS) + ',' + str(SQ_THIS) + ',' + str(SA_THIS/100) + '''], backgroundColor:P[0] },
      { label:'4.23-4.29', data:[''' + str(SKU_PREV) + ',' + str(SQ_PREV) + ',' + str(SA_PREV/100) + '''], backgroundColor:P[1] }
    ]
  },
  options: { responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ===== sec1: 品线 ===== */
new Chart(document.getElementById('cPxSales'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(PX_LAB) + ''',
    datasets:[
      {label:'本周销量', data:''' + json2.dumps(PX_SQ) + ''', backgroundColor:P[0]},
      {label:'上周销量', data:''' + json2.dumps(PX_SQ_P) + ''', backgroundColor:P[1]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
new Chart(document.getElementById('cPxAmt'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(PX_LAB) + ''',
    datasets:[
      {label:'本周销售额', data:''' + json2.dumps(PX_SA) + ''', backgroundColor:P[2]},
      {label:'上周销售额', data:''' + json2.dumps(PX_SA_P) + ''', backgroundColor:P[3]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ===== sec2: 分析人 ===== */
new Chart(document.getElementById('cFxSales'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(FX_LAB) + ''',
    datasets:[
      {label:'本周销量', data:''' + json2.dumps(FX_SQ) + ''', backgroundColor:P[0]},
      {label:'上周销量', data:''' + json2.dumps(FX_SQ_P) + ''', backgroundColor:P[1]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
new Chart(document.getElementById('cFxAmt'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(FX_LAB) + ''',
    datasets:[
      {label:'本周销售额', data:''' + json2.dumps(FX_SA) + ''', backgroundColor:P[2]},
      {label:'上周销售额', data:''' + json2.dumps(FX_SA_P) + ''', backgroundColor:P[3]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ===== sec3: 拓展类型 ===== */
new Chart(document.getElementById('cTzRate'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(TZ_LAB) + ''',
    datasets:[
      {label:'本周出单率(%)', data:''' + json2.dumps(TZ_RATE) + ''', backgroundColor:P[0]},
      {label:'上周出单率(%)', data:''' + json2.dumps(TZ_RP) + ''', backgroundColor:P[1]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true,max:100}} }
});
new Chart(document.getElementById('cTzSales'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(TZ_LAB) + ''',
    datasets:[
      {label:'本周销量', data:''' + json2.dumps(TZ_SQ) + ''', backgroundColor:P[2]},
      {label:'上周销量', data:''' + json2.dumps(TZ_SQ_P) + ''', backgroundColor:P[3]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ===== sec4: 分析及时率 ===== */
new Chart(document.getElementById('cJlStack'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(JL_LAB) + ''',
    datasets:[
      {label:'及时分析', data:''' + json2.dumps(JL_OK) + ''', backgroundColor:P[0], stack:'a'},
      {label:'8日内无分析', data:''' + json2.dumps(JL_8) + ''', backgroundColor:'#FFD54F', stack:'a'},
      {label:'超7日未分析', data:''' + json2.dumps(JL_7) + ''', backgroundColor:'#E53935', stack:'a'}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});
new Chart(document.getElementById('cJlRate'), {
  type:'bar',
  data:{
    labels: ''' + json2.dumps(JL_LAB) + ''',
    datasets:[
      {label:'及时率(%)', data:''' + json2.dumps(JL_RATE) + ''', backgroundColor:P.slice(0,''' + str(len(JL_LAB)) + ''')}
    ]
  },
  options:{ responsive:true, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,max:100}} }
});

/* ===== sec6: PLP 总数据 ===== */
new Chart(document.getElementById('cPlpTotal'), {
  type:'bar',
  data:{
    labels: ['广告活动','链接','曝光量(/1000)','点击量','售出数','ROAS','CVR%','ACOS%'],
    datasets:[
      {label:'4.30-5.6', data:[''' + str(PLP_ACT) + ',' + str(PLP_LINK) + ',' + str(PLP_IMP/1000) + ',429,27,' + str(PLP_ROAS) + ',6.29,15.54], backgroundColor:P[0]},
      {label:'4.23-4.29', data:[47,63,139.169,425,40,14.16,9.41,7.06], backgroundColor:P[1]}
    ]
  },
  options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true}} }
});

/* ===== sec7: 出单饼图 ===== */
new Chart(document.getElementById('cChPie'), {
  type:'doughnut',
  data:{
    labels:['有销量SKU(27)','未出单SKU(13)','8日内(6)'],
    datasets:[{ data:[27,13,6], backgroundColor:[P[0],'#E53935','#FFD54F'] }]
  },
  options:{ responsive:true, plugins:{legend:{position:'right'}} }
});

/* ===== sec8: 未出单原因饼图 ===== */
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

print('\nDone! File:', DST)
print('Size:', len(html), 'bytes')
