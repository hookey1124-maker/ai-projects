#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 4.30-5.6 新品周报 HTML 可视化看板
遵循 Skill v3.0.0 规范：深蓝头部 + 白色侧边栏 + 9板块 + Chart.js
"""
import json, datetime

JSON = r"C:/Users/Administrator/Desktop/新品复盘/sheets_506.json"
DST  = r"C:/Users/Administrator/Desktop/新品复盘/新品周报_4.30-5.6_看板.html"

with open(JSON, encoding='utf-8') as f:
    sheets = json.load(f)

def safe(v, default=''):
    if v is None or v == '': return default
    return str(v)

def num(v, default=0.0):
    if v is None or v == '': return default
    s = str(v).replace('%','').replace('$','').replace(',','').strip()
    try: return float(s)
    except: return default

def intn(v, default=0):
    return int(num(v, default))

SHEET_NAMES = list(sheets.keys())
S1 = sheets[SHEET_NAMES[0]]
S2 = sheets[SHEET_NAMES[1]]
S3 = sheets[SHEET_NAMES[2]]
S4 = sheets[SHEET_NAMES[3]]
S5 = sheets[SHEET_NAMES[4]]
S6 = sheets[SHEET_NAMES[5]]
S7 = sheets[SHEET_NAMES[6]]
S8 = sheets[SHEET_NAMES[7]]
S9 = sheets[SHEET_NAMES[8]]
S10 = sheets[SHEET_NAMES[9]]

# ═══════════════════ Data Extraction ═══════════════════

# Sheet 1: KPI
sku_total  = intn(S1[4][4])
new_listed = intn(S1[5][4])
sales_curr = intn(S1[6][4]); sales_prev = intn(S1[6][3])
rev_curr   = num(S1[7][4]); rev_prev = num(S1[7][3])
has_curr   = intn(S1[9][4]); has_prev = intn(S1[9][3])
no_curr    = intn(S1[10][4])
timely_cnt = intn(S1[14][4])
no8d_cnt   = intn(S1[15][4]); no7d_cnt = intn(S1[16][4])
timely_rate= safe(S1[17][4])
order_y    = intn(S1[23][4]); order_n = intn(S1[24][4]); order_no = intn(S1[25][4])
order_rate = safe(S1[26][4])

# 4-period data for trend charts
sp = [intn(S1[4][i]) for i in range(1,5)]
hp = [intn(S1[9][i]) for i in range(1,5)]
qp = [intn(S1[6][i]) for i in range(1,5)]
rp = [round(num(S1[7][i])/100,1) for i in range(1,5)]
tp = [intn(S1[14][i]) for i in range(1,5)]
d8 = [intn(S1[15][i]) for i in range(1,5)]
d7 = [intn(S1[16][i]) for i in range(1,5)]
oy = [intn(S1[23][i]) for i in range(1,5)]
on_= [intn(S1[24][i]) for i in range(1,5)]
oo = [intn(S1[25][i]) for i in range(1,5)]

# Sheet 2: PX
PX_DATA = [r for r in S2[2:] if r[0] and safe(r[0]) not in ('合计',)]
PX_LAB = json.dumps([safe(r[0]) for r in PX_DATA])
PX_SQ4 = json.dumps([intn(r[18]) for r in PX_DATA])
PX_SQ3 = json.dumps([intn(r[13]) for r in PX_DATA])
PX_SA4 = json.dumps([round(num(r[19]),2) for r in PX_DATA])
PX_SA3 = json.dumps([round(num(r[14]),2) for r in PX_DATA])

# Sheet 3: FX
FX_DATA = [r for r in S3[2:] if r[0] and safe(r[0]) not in ('合计',)]
FX_LAB = json.dumps([safe(r[0]) for r in FX_DATA])
FX_SQ4 = json.dumps([intn(r[11]) for r in FX_DATA])
FX_SQ3 = json.dumps([intn(r[8]) for r in FX_DATA])
FX_SA4 = json.dumps([round(num(r[12]),2) for r in FX_DATA])
FX_SA3 = json.dumps([round(num(r[9]),2) for r in FX_DATA])

# Sheet 4: TZ
TZ_DATA = [r for r in S4[2:] if r[0] and safe(r[0]) not in ('合计',)]
TZ_LAB = json.dumps([safe(r[0]) for r in TZ_DATA])
TZ_RT4 = json.dumps([num(r[13]) for r in TZ_DATA])
TZ_RT3 = json.dumps([num(r[10]) for r in TZ_DATA])
TZ_SQ4 = json.dumps([intn(r[12]) for r in TZ_DATA])
TZ_SQ3 = json.dumps([intn(r[9]) for r in TZ_DATA])

# Sheet 5: JL
JL_DATA = []
for r in S5:
    nm = safe(r[2])
    if nm in ('俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'):
        JL_DATA.append([nm, r[3], r[4], r[5], r[6], r[7]])
JL_LAB = json.dumps([safe(r[0]) for r in JL_DATA])
JL_OK = json.dumps([intn(r[2]) for r in JL_DATA])
JL_8  = json.dumps([intn(r[3]) for r in JL_DATA])
JL_7  = json.dumps([intn(r[4]) for r in JL_DATA])
JL_RT = json.dumps([num(r[5]) for r in JL_DATA])

# Sheet 6: DY
DY_DATA = [r for r in S6[2:] if r[0] and safe(r[0]) not in ('合计','销售编号','')]
from collections import Counter
dy_cat = Counter(safe(r[4]) for r in DY_DATA)
dy_ord = Counter(safe(r[17]) for r in DY_DATA)
DY_CAT_LAB = json.dumps([k for k,v in dy_cat.most_common(10)])
DY_CAT_VAL = json.dumps([v for k,v in dy_cat.most_common(10)])
DY_ORD_LAB = json.dumps([k for k,v in dy_ord.items()])
DY_ORD_VAL = json.dumps([v for k,v in dy_ord.items()])

# Sheet 7: PLP
PLP_OV = {}
for r in S7[4:16]:
    k = safe(r[0])
    if k: PLP_OV[k] = {'c': safe(r[1]), 'p': safe(r[2]), 'h': safe(r[3])}
def pv(key): return PLP_OV.get(key,{})

psku   = intn(pv('广告SKU数').get('c',0)); psku_p = intn(pv('广告SKU数').get('p',0))
pimp   = pv('曝光量').get('c','0');   pimp_p = pv('曝光量').get('p','0')
pclick = pv('点击量').get('c','0');   pclick_p=pv('点击量').get('p','0')
psold  = pv('售出数').get('c','0');   psold_p = pv('售出数').get('p','0')
pcost  = pv('花费 (USD)').get('c','0'); pcost_p=pv('花费 (USD)').get('p','0')
prev   = pv('销售额 (USD)').get('c','0'); prev_p=pv('销售额 (USD)').get('p','0')
proas  = pv('ROAS').get('c','0');     proas_p=pv('ROAS').get('p','0')
pcvr   = pv('CVR').get('c','0');      pcvr_p = pv('CVR').get('p','0')
pctr   = pv('CTR').get('c','0');      pctr_p = pv('CTR').get('p','0')
pcpc   = pv('CPC').get('c','0')
pcpa   = pv('CPA').get('c','0')
pacos  = pv('ACOS').get('c','0');     pacos_p=pv('ACOS').get('p','0')

PLP_AN, PLP_PX, PLP_TZ = [], [], []
block = None
for r in S7:
    lab = safe(r[0]).strip()
    if '分析人' in lab: block = 'an'; continue
    if '品线' in lab and '拓展' not in lab: block = 'px'; continue
    if '拓展类型' in lab: block = 'tz'; continue
    if lab in ('合计','总计','指标','', '维度'): continue
    if block == 'an' and lab in ('俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星'):
        PLP_AN.append(r)
    elif block == 'px': PLP_PX.append(r)
    elif block == 'tz': PLP_TZ.append(r)

# Sheet 8: CD
CD_DATA = [r for r in S8[1:] if r[0] and safe(r[0]) not in ('维度','合计')]

# Sheet 9: YY
YY_HAS, YY_NO = [], []
ia, ib = False, False
for r in S9:
    lab = safe(r[0]).strip()
    if 'A1' in lab: ia = True; ib = False; continue
    if 'A2' in lab or 'A3' in lab: ia = False; continue
    if 'B1' in lab: ia = False; ib = True; continue
    if 'B2' in lab or 'B3' in lab: ib = False; continue
    if ia and r[0] and safe(r[0]) not in ('原因','市场状态','合计',''): YY_HAS.append(r)
    if ib and r[0] and safe(r[0]) not in ('原因','市场状态','合计',''): YY_NO.append(r)
YHL = json.dumps([safe(r[0]) for r in YY_HAS]); YHV = json.dumps([intn(r[1]) for r in YY_HAS])
YNL = json.dumps([safe(r[0]) for r in YY_NO]);  YNV = json.dumps([intn(r[1]) for r in YY_NO])

# Sheet 10: PLG
PLG_DATA = [r for r in S10[3:] if r[1] and safe(r[1]) not in ('合计','')]

print(f"PX={len(PX_DATA)} FX={len(FX_DATA)} TZ={len(TZ_DATA)} JL={len(JL_DATA)} DY={len(DY_DATA)}")
print(f"PLP_AN={len(PLP_AN)} PLP_PX={len(PLP_PX)} PLP_TZ={len(PLP_TZ)} CD={len(CD_DATA)}")
print(f"YY_HAS={len(YY_HAS)} YY_NO={len(YY_NO)} PLG={len(PLG_DATA)}")

# ═══════════════════ HTML ═══════════════════
L = []
W = L.append

W('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报看板 - 4.30-5.6</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;background:#f0f2f5;color:#1a1a2e}
.header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);color:#fff;padding:28px 40px}
.header h1{font-size:26px;font-weight:700;letter-spacing:2px}
.header .subtitle{font-size:13px;opacity:.75;margin-top:6px}
.container{display:flex;min-height:calc(100vh - 90px)}
.sidebar{width:220px;min-width:220px;background:#fff;border-right:1px solid #e8e8e8;padding:16px 0;position:sticky;top:0;height:100vh;overflow-y:auto}
.sidebar h3{font-size:13px;color:#0f3460;padding:8px 20px;margin-bottom:4px}
.sidebar ul{list-style:none}
.sidebar li a{display:block;padding:10px 20px;font-size:13px;color:#555;text-decoration:none;border-left:3px solid transparent;transition:all .2s;cursor:pointer}
.sidebar li a:hover,.sidebar li a.active{background:#f0f6ff;color:#0f3460;border-left-color:#0f3460;font-weight:600}
.main{flex:1;padding:24px;overflow-y:auto;max-height:calc(100vh - 90px)}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-bottom:24px}
.kpi-card{background:#fff;border-radius:10px;padding:18px;box-shadow:0 2px 8px rgba(0,0,0,.06);text-align:center;transition:transform .2s,box-shadow .2s;animation:fadeInUp .5s ease-out forwards}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,.12)}
.kpi-card .val{font-size:26px;font-weight:700;color:#0f3460}
.kpi-card .label{font-size:12px;color:#888;margin-top:6px}
.kpi-card .hb{font-size:11px;margin-top:4px;font-weight:600}
.kpi-card.green .val{color:#08845a}
.kpi-card.orange .val{color:#e07b24}
.kpi-card.red .val{color:#c0392b}
.kpi-card.purple .val{color:#8e44ad}
.section-wrap{display:none}
.section-wrap.active{display:block}
.section{background:#fff;border-radius:10px;padding:20px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.section h3{font-size:16px;font-weight:700;color:#0f3460;padding-bottom:12px;border-bottom:2px solid #e8f0fe;margin-bottom:16px}
.sub-module h4{font-size:13px;font-weight:600;color:#444;margin:16px 0 10px;padding:6px 12px;background:#f5f7ff;border-radius:4px;border-left:3px solid #0f3460}
.chart-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:20px;margin-bottom:20px}
.chart-card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.chart-card h4{font-size:13px;font-weight:600;color:#0f3460;margin-bottom:14px}
.chart-card canvas{max-height:260px}
.table-wrap{overflow-x:auto;margin-top:12px}
.data-table{width:100%;border-collapse:collapse;font-size:11px}
.data-table th{background:#0f3460;color:#fff;padding:7px 6px;text-align:center;white-space:nowrap;font-weight:600}
.data-table td{padding:5px 6px;text-align:center;border-bottom:1px solid #f0f0f0;white-space:nowrap}
.data-table tr:hover td{background:#f5f7ff}
.data-table td:first-child{text-align:left;font-weight:600}
.ab-box{border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-bottom:16px}
.ab-box.a{border-left:4px solid #c0392b}
.ab-box.b{border-left:4px solid #08845a}
.ab-box h4{font-size:14px;font-weight:700;margin-bottom:12px;padding:0;background:none;border-left:none}
.ab-box.a h4{color:#c0392b}
.ab-box.b h4{color:#08845a}
.plp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px}
.plp-card{background:#fff;border-radius:10px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.06);border-top:3px solid #8e44ad;text-align:center}
.plp-card h4{font-size:11px;color:#888;margin-bottom:4px}
.plp-card .v{font-size:22px;font-weight:700;color:#8e44ad}
.plp-card .s{font-size:11px;color:#aaa;margin-top:2px}
.hl-orange{background:#fff3e0!important}
.hl-pink{background:#fce4ec!important}
.hl-green{background:#e8f5e9!important}
@keyframes fadeInUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:900px){.sidebar{display:none}.chart-grid{grid-template-columns:1fr}.kpi-grid{grid-template-columns:repeat(2,1fr)}}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#f1f1f1}
::-webkit-scrollbar-thumb{background:#ccc;border-radius:3px}
</style>
</head>
<body>
''')

W(f'''<div class="header">
  <h1>新品周报 - 4.30-5.6</h1>
  <div class="subtitle">统计周期：2026年4月30日 - 5月6日 | 在跟SKU：{sku_total} | 生成：{datetime.date.today()}</div>
</div>
<div class="container">
<nav class="sidebar">
  <h3>NAVIGATION</h3>
  <ul>
    <li><a onclick="S('overview',this)" class="active">数据总览</a></li>
    <li><a onclick="S('pinxian',this)">品线维度</a></li>
    <li><a onclick="S('analyst',this)">分析人维度</a></li>
    <li><a onclick="S('expand',this)">拓展类型</a></li>
    <li><a onclick="S('timely',this)">分析及时率</a></li>
    <li><a onclick="S('order',this)">新品出单情况</a></li>
    <li><a onclick="S('unorder',this)">新品未出单原因</a></li>
    <li><a onclick="S('lowshare',this)">低占比新品</a></li>
    <li><a onclick="S('plp',this)">PLP复盘</a></li>
  </ul>
</nav>
<div class="main">
''')

# KPI Cards
sq_chg = f"+{sales_curr-sales_prev:.0f}" if sales_curr>=sales_prev else f"{sales_curr-sales_prev:.0f}"
rv_chg_v = rev_curr-rev_prev
rv_chg = f"+${rv_chg_v:,.0f}" if rv_chg_v>=0 else f"-${abs(rv_chg_v):,.0f}"
hs_chg_v = has_curr-has_prev
hs_chg = f"+{hs_chg_v}" if hs_chg_v>=0 else str(hs_chg_v)

W(f'''<div class="kpi-grid">
  <div class="kpi-card"><div class="val">{sku_total}</div><div class="label">累计SKU数</div><div class="hb">本周新上架+{new_listed}</div></div>
  <div class="kpi-card green"><div class="val">{sales_curr}</div><div class="label">本周销量</div><div class="hb">上周{sales_prev}（{sq_chg}）</div></div>
  <div class="kpi-card green"><div class="val">${rev_curr:,.0f}</div><div class="label">本周销售额(USD)</div><div class="hb">上周${rev_prev:,.0f}（{rv_chg}）</div></div>
  <div class="kpi-card purple"><div class="val">{has_curr}</div><div class="label">有对手SKU</div><div class="hb">上周{has_prev}（{hs_chg}）</div></div>
  <div class="kpi-card orange"><div class="val">{no_curr}</div><div class="label">无对手SKU</div><div class="hb">占比{round(no_curr/sku_total*100,1)}%</div></div>
  <div class="kpi-card green"><div class="val">{order_rate}</div><div class="label">有对手出单率</div><div class="hb">Y:{order_y} N:{order_n} 未:{order_no}</div></div>
  <div class="kpi-card green"><div class="val">{timely_rate}</div><div class="label">分析及时率</div><div class="hb">及时{timely_cnt} 超期{no8d_cnt+no7d_cnt}</div></div>
  <div class="kpi-card"><div class="val">{intn(S1[8][4])}</div><div class="label">有销量SKU</div><div class="hb">上周{safe(S1[8][3])}</div></div>
  <div class="kpi-card orange"><div class="val">{len(DY_DATA)}</div><div class="label">低占比新品</div><div class="hb">市占比&lt;75%且有对手</div></div>
</div>
''')

def tbl(hdrs, rows, cfn=None, cc=None):
    th = ''.join(f'<th>{h}</th>' for h in hdrs)
    trs = ''
    for i,r in enumerate(rows):
        cls = cfn(i,r) if cfn else ''
        cells = ''.join(f'<td>{safe(c)}</td>' for c in (r[:cc] if cc else r))
        trs += f'<tr class="{cls}">{cells}</tr>'
    return f'<div class="table-wrap"><table class="data-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

# Sec 1
W('''<div class="section-wrap active" id="section-overview">
<div class="section"><h3>数据总览</h3>
<div class="chart-grid">
  <div class="chart-card"><h4>SKU数量趋势</h4><canvas id="cSku"></canvas></div>
  <div class="chart-card"><h4>销量与销售额趋势</h4><canvas id="cSales"></canvas></div>
  <div class="chart-card"><h4>出单分布</h4><canvas id="cOrdPie"></canvas></div>
  <div class="chart-card"><h4>分析及时率趋势</h4><canvas id="cTim"></canvas></div>
</div>
</div>
</div>
''')

# Sec 2
W(f'''<div class="section-wrap" id="section-pinxian">
<div class="section"><h3>品线维度</h3>
<div class="chart-grid">
  <div class="chart-card"><h4>各品线本周 vs 上周 销量</h4><canvas id="cPxS"></canvas></div>
  <div class="chart-card"><h4>各品线本周 vs 上周 销售额(USD)</h4><canvas id="cPxA"></canvas></div>
</div>
<div class="sub-module"><h4>品线明细表</h4></div>
{tbl(['品线','累计SKU','4.9|SKU','4.9|销量','4.9|销售额','4.9|有对手','4.9|出单率','4.16|SKU','4.16|销量','4.16|销售额','4.16|有对手','4.16|出单率','4.23|SKU','4.23|销量','4.23|销售额','4.23|有对手','4.23|出单率','4.30|SKU','4.30|销量','4.30|销售额','4.30|有对手','4.30|出单率'], PX_DATA)}
</div>
</div>
''')

# Sec 3
W(f'''<div class="section-wrap" id="section-analyst">
<div class="section"><h3>分析人维度</h3>
<div class="chart-grid">
  <div class="chart-card"><h4>各分析人本周 vs 上周 销量</h4><canvas id="cFxS"></canvas></div>
  <div class="chart-card"><h4>各分析人本周 vs 上周 销售额(USD)</h4><canvas id="cFxA"></canvas></div>
</div>
<div class="sub-module"><h4>分析人明细表</h4></div>
{tbl(['分析人','累计SKU','4.9|SKU','4.9|销量','4.9|出单率','4.16|SKU','4.16|销量','4.16|出单率','4.23|SKU','4.23|销量','4.23|出单率','4.30|SKU','4.30|销量','4.30|出单率'], FX_DATA)}
</div>
</div>
''')

# Sec 4
W(f'''<div class="section-wrap" id="section-expand">
<div class="section"><h3>拓展类型</h3>
<div class="chart-grid">
  <div class="chart-card"><h4>各类型出单率对比(%)</h4><canvas id="cTzR"></canvas></div>
  <div class="chart-card"><h4>各类型销量对比</h4><canvas id="cTzS"></canvas></div>
</div>
<div class="sub-module"><h4>拓展类型明细表</h4></div>
{tbl(['拓展类型','累计SKU','4.9|SKU','4.9|销量','4.9|出单率','4.16|SKU','4.16|销量','4.16|出单率','4.23|SKU','4.23|销量','4.23|出单率','4.30|SKU','4.30|销量','4.30|出单率','变化'], TZ_DATA)}
</div>
</div>
''')

# Sec 5
W(f'''<div class="section-wrap" id="section-timely">
<div class="section"><h3>分析及时率</h3>
<div class="chart-grid">
  <div class="chart-card"><h4>各分析人及时分析分布</h4><canvas id="cJlS"></canvas></div>
  <div class="chart-card"><h4>各分析人及时率(%)</h4><canvas id="cJlR"></canvas></div>
</div>
<div class="sub-module"><h4>分析及时率明细表</h4></div>
{tbl(['分析人','截止SKU','及时分析','8日内无分析','超7日未分析','及时率'], JL_DATA)}
</div>
</div>
''')

# Sec 6
W(f'''<div class="section-wrap" id="section-order">
<div class="section"><h3>新品出单情况 - 有对手口径</h3>
<div class="kpi-grid" style="margin-bottom:20px">
  <div class="kpi-card"><div class="val">{has_curr}</div><div class="label">有对手SKU</div><div class="hb">上周{has_prev}</div></div>
  <div class="kpi-card green"><div class="val">{order_y+order_n}</div><div class="label">已出单(Y+N)</div><div class="hb">Y:{order_y} N:{order_n}</div></div>
  <div class="kpi-card red"><div class="val">{order_no}</div><div class="label">未出单</div><div class="hb">{order_rate}</div></div>
</div>
<div class="chart-grid">
  <div class="chart-card"><h4>出单分布</h4><canvas id="cOrdD"></canvas></div>
  <div class="chart-card"><h4>出单趋势</h4><canvas id="cOrdT"></canvas></div>
</div>
<div class="sub-module"><h4>出单情况明细表</h4></div>
{tbl(['指标','4.9-4.15','占比','4.16-4.22','占比','4.23-4.29','占比','4.30-5.6','占比','变化'], CD_DATA)}
</div>
</div>
''')

# Sec 7
W(f'''<div class="section-wrap" id="section-unorder">
<div class="section"><h3>新品未出单原因 - A/B双板块</h3>
<div class="ab-box a">
  <h4>A. 有对手未出单 - 本周:{order_no}个</h4>
  <div class="chart-grid"><div class="chart-card"><h4>原因分布</h4><canvas id="cUnA"></canvas></div></div>
  {tbl(['市场状态','本周SKU','占比','上周SKU','上周占比','变化'], YY_HAS, cc=6)}
</div>
<div class="ab-box b">
  <h4>B. 无对手未出单</h4>
  <div class="chart-grid"><div class="chart-card"><h4>原因分布</h4><canvas id="cUnB"></canvas></div></div>
  {tbl(['市场状态','本周SKU','占比','上周SKU','上周占比','变化'], YY_NO, cc=6)}
</div>
</div>
</div>
''')

# Sec 8
def dy_cls(i,r):
    plp=safe(r[18]);plg=num(r[19]);bd=safe(r[17])
    if plp=='Y' and plg>0: return 'hl-orange'
    if plp=='N' and bd=='未出单': return 'hl-pink'
    if plp=='N' and plg>0: return 'hl-green'
    return ''

W(f'''<div class="section-wrap" id="section-lowshare">
<div class="section"><h3>低占比新品 - 市占比&lt;75%且有对手（共{len(DY_DATA)}个）</h3>
<div class="chart-grid">
  <div class="chart-card"><h4>品类分布</h4><canvas id="cLowC"></canvas></div>
  <div class="chart-card"><h4>出单状态分布</h4><canvas id="cLowO"></canvas></div>
</div>
<div class="sub-module"><h4>低占比新品明细表</h4></div>
{tbl(['编号','SKU','上架日期','分析人','品类','拓展类型','销量','销量环比','销售额','销售额环比','对手销量','对手销量环比','市占比','市占比环比','8日出单','7日频次','新品频次','市场状态1','操作判断','市场状态2','开启PLP','PLG费率'], DY_DATA, dy_cls)}
<p style="font-size:11px;color:#888;margin-top:8px">
  <span style="background:#fff3e0;padding:2px 6px;border-radius:3px">橙</span>PLP=Y且PLG&gt;0 &nbsp;
  <span style="background:#fce4ec;padding:2px 6px;border-radius:3px">粉</span>PLP=N且未出单 &nbsp;
  <span style="background:#e8f5e9;padding:2px 6px;border-radius:3px">绿</span>PLP=N且PLG&gt;0
</p>
</div>
</div>
''')

# Sec 9: PLP
W(f'''<div class="section-wrap" id="section-plp">
<div class="section"><h3>PLP广告复盘 - 4.30-5.6 vs 4.23-4.29</h3>
<div class="plp-grid">
  <div class="plp-card"><h4>广告SKU数</h4><div class="v">{psku}</div><div class="s">上周:{psku_p}</div></div>
  <div class="plp-card"><h4>曝光量</h4><div class="v">{pimp}</div><div class="s">上周:{pimp_p}</div></div>
  <div class="plp-card"><h4>点击量</h4><div class="v">{pclick}</div><div class="s">上周:{pclick_p}</div></div>
  <div class="plp-card"><h4>售出数</h4><div class="v">{psold}</div><div class="s">上周:{psold_p}</div></div>
  <div class="plp-card"><h4>广告花费</h4><div class="v">{pcost}</div><div class="s">上周:{pcost_p}</div></div>
  <div class="plp-card"><h4>PLP销售额</h4><div class="v">{prev}</div><div class="s">上周:{prev_p}</div></div>
  <div class="plp-card"><h4>ROAS</h4><div class="v">{proas}x</div><div class="s">上周:{proas_p}x</div></div>
  <div class="plp-card"><h4>ACOS</h4><div class="v">{pacos}</div><div class="s">上周:{pacos_p}</div></div>
</div>
<div class="chart-grid">
  <div class="chart-card"><h4>效率指标对比</h4><canvas id="cPlpE"></canvas></div>
  <div class="chart-card"><h4>量级指标对比</h4><canvas id="cPlpV"></canvas></div>
</div>
<div class="sub-module"><h4>分析人维度</h4></div>
{tbl(['分析人','SKU','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','ACOS%'], PLP_AN, cc=11)}
<div class="sub-module"><h4>品线维度</h4></div>
{tbl(['品线','SKU','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','ACOS%'], PLP_PX, cc=11)}
<div class="sub-module"><h4>拓展类型维度</h4></div>
{tbl(['拓展类型','SKU','曝光量','点击量','售出数','花费','销售额','ROAS','CVR%','CTR%','ACOS%'], PLP_TZ, cc=11)}
</div>
</div>
</div><!-- /main -->
</div><!-- /container -->
''')

# ═══════════════ JS ═══════════════
CB = ['#0f3460','#2980b9','#c0392b','#8e44ad','#e07b24','#08845a']
CA = ['rgba(15,52,96,0.8)','rgba(41,128,185,0.8)','rgba(192,57,43,0.8)','rgba(142,68,173,0.8)','rgba(224,123,36,0.8)','rgba(8,132,90,0.8)']

W(f'''<script>
function S(id,el){{document.querySelectorAll(".section-wrap").forEach(function(s){{s.classList.remove("active")}});var t=document.getElementById("section-"+id);if(t)t.classList.add("active");document.querySelectorAll(".sidebar li a").forEach(function(a){{a.classList.remove("active")}});if(el)el.classList.add("active")}}
Chart.defaults.font.family="'Microsoft YaHei','PingFang SC',sans-serif";
Chart.defaults.color="#444";
var CB={json.dumps(CB)},C={json.dumps(CA)};
function P(c){{var t=c.dataset.data.reduce(function(a,b){{return a+b}},0);return c.label+": "+c.raw+" ("+(c.raw/t*100).toFixed(1)+"%)"}}

// sec0
new Chart(document.getElementById('cSku'),{{type:"line",data:{{labels:["4.9-4.15","4.16-4.22","4.23-4.29","4.30-5.6"],datasets:[{{label:"SKU总数",data:{json.dumps(sp)},borderColor:CB[0],backgroundColor:"rgba(15,52,96,0.1)",fill:true,tension:.3}},{{label:"有对手SKU",data:{json.dumps(hp)},borderColor:CB[3],backgroundColor:"rgba(142,68,173,0.1)",fill:true,tension:.3}}]}}}})
new Chart(document.getElementById('cSales'),{{type:"bar",data:{{labels:["4.9-4.15","4.16-4.22","4.23-4.29","4.30-5.6"],datasets:[{{label:"销量",data:{json.dumps(qp)},backgroundColor:C[0],yAxisID:"y"}},{{label:"销售额(USD/100)",data:{json.dumps(rp)},backgroundColor:C[1],yAxisID:"y1"}}]}},options:{{scales:{{y:{{beginAtZero:true,position:"left",title:{{display:true,text:"销量"}}}},y1:{{beginAtZero:true,position:"right",grid:{{display:false}},title:{{display:true,text:"销售额/100"}}}}}}}}}})
new Chart(document.getElementById('cOrdPie'),{{type:"doughnut",data:{{labels:["Y(8日内)","N(8日外)","未出单"],datasets:[{{data:[{order_y},{order_n},{order_no}],backgroundColor:[CB[5],CB[4],CB[2]],borderWidth:2,borderColor:"#fff"}}]}},options:{{plugins:{{legend:{{position:"bottom"}},tooltip:{{callbacks:{{label:P}}}}}},animation:{{animateRotate:true,animateScale:true,duration:800}}}}}})
new Chart(document.getElementById('cTim'),{{type:"line",data:{{labels:["4.9-4.15","4.16-4.22","4.23-4.29","4.30-5.6"],datasets:[{{label:"及时分析",data:{json.dumps(tp)},borderColor:CB[5],backgroundColor:"rgba(8,132,90,0.1)",fill:true,tension:.3}},{{label:"8日内无分析",data:{json.dumps(d8)},borderColor:CB[4],backgroundColor:"rgba(224,123,36,0.1)",fill:true,tension:.3}},{{label:"超7日未分析",data:{json.dumps(d7)},borderColor:CB[2],backgroundColor:"rgba(192,57,43,0.1)",fill:true,tension:.3}}]}}}})

// sec1
new Chart(document.getElementById('cPxS'),{{type:"bar",data:{{labels:{PX_LAB},datasets:[{{label:"本周销量",data:{PX_SQ4},backgroundColor:C[0]}},{{label:"上周销量",data:{PX_SQ3},backgroundColor:C[1]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})
new Chart(document.getElementById('cPxA'),{{type:"bar",data:{{labels:{PX_LAB},datasets:[{{label:"本周销售额",data:{PX_SA4},backgroundColor:C[2]}},{{label:"上周销售额",data:{PX_SA3},backgroundColor:C[3]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})

// sec2
new Chart(document.getElementById('cFxS'),{{type:"bar",data:{{labels:{FX_LAB},datasets:[{{label:"本周销量",data:{FX_SQ4},backgroundColor:C[0]}},{{label:"上周销量",data:{FX_SQ3},backgroundColor:C[1]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})
new Chart(document.getElementById('cFxA'),{{type:"bar",data:{{labels:{FX_LAB},datasets:[{{label:"本周销售额",data:{FX_SA4},backgroundColor:C[2]}},{{label:"上周销售额",data:{FX_SA3},backgroundColor:C[3]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})

// sec3
new Chart(document.getElementById('cTzR'),{{type:"bar",data:{{labels:{TZ_LAB},datasets:[{{label:"本周出单率(%)",data:{TZ_RT4},backgroundColor:C[0]}},{{label:"上周出单率(%)",data:{TZ_RT3},backgroundColor:C[1]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true,max:100}}}}}}}})
new Chart(document.getElementById('cTzS'),{{type:"bar",data:{{labels:{TZ_LAB},datasets:[{{label:"本周销量",data:{TZ_SQ4},backgroundColor:C[0]}},{{label:"上周销量",data:{TZ_SQ3},backgroundColor:C[1]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})

// sec4
new Chart(document.getElementById('cJlS'),{{type:"bar",data:{{labels:{JL_LAB},datasets:[{{label:"及时分析",data:{JL_OK},backgroundColor:CB[5]}},{{label:"8日内无分析",data:{JL_8},backgroundColor:CB[4]}},{{label:"超7日未分析",data:{JL_7},backgroundColor:CB[2]}}]}},options:{{scales:{{x:{{stacked:true}},y:{{stacked:true,beginAtZero:true}}}},plugins:{{legend:{{position:"top"}}}}}}}})
new Chart(document.getElementById('cJlR'),{{type:"bar",data:{{labels:{JL_LAB},datasets:[{{label:"及时率(%)",data:{JL_RT},backgroundColor:CB.slice(0,{len(JL_DATA)}),borderRadius:4}}]}},options:{{plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,max:100}}}}}}}})

// sec5
new Chart(document.getElementById('cOrdD'),{{type:"doughnut",data:{{labels:["Y(8日内)","N(8日外)","未出单"],datasets:[{{data:[{order_y},{order_n},{order_no}],backgroundColor:[CB[5],CB[4],CB[2]],borderWidth:2,borderColor:"#fff"}}]}},options:{{plugins:{{legend:{{position:"bottom"}},tooltip:{{callbacks:{{label:P}}}}}},animation:{{animateRotate:true,animateScale:true,duration:800}}}}}})
new Chart(document.getElementById('cOrdT'),{{type:"line",data:{{labels:["4.9-4.15","4.16-4.22","4.23-4.29","4.30-5.6"],datasets:[{{label:"Y(8日内)",data:{json.dumps(oy)},borderColor:CB[5],tension:.3}},{{label:"N(8日外)",data:{json.dumps(on_)},borderColor:CB[4],tension:.3}},{{label:"未出单",data:{json.dumps(oo)},borderColor:CB[2],tension:.3}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})

// sec6
new Chart(document.getElementById('cUnA'),{{type:"pie",data:{{labels:{YHL},datasets:[{{data:{YHV},backgroundColor:CB.slice(0,{len(YY_HAS)}),borderWidth:2,borderColor:"#fff"}}]}},options:{{plugins:{{legend:{{position:"right"}},tooltip:{{callbacks:{{label:P}}}}}},animation:{{animateRotate:true,animateScale:true,duration:800}}}}}})
new Chart(document.getElementById('cUnB'),{{type:"pie",data:{{labels:{YNL},datasets:[{{data:{YNV},backgroundColor:[CB[5],CB[1],CB[4],CB[3],CB[0],CB[2]].slice(0,{len(YY_NO)}),borderWidth:2,borderColor:"#fff"}}]}},options:{{plugins:{{legend:{{position:"right"}},tooltip:{{callbacks:{{label:P}}}}}},animation:{{animateRotate:true,animateScale:true,duration:800}}}}}})

// sec7
new Chart(document.getElementById('cLowC'),{{type:"bar",data:{{labels:{DY_CAT_LAB},datasets:[{{label:"低占比SKU数",data:{DY_CAT_VAL},backgroundColor:CB[2],borderRadius:4}}]}},options:{{indexAxis:"y",plugins:{{legend:{{display:false}}}},scales:{{x:{{beginAtZero:true}}}}}}}})
new Chart(document.getElementById('cLowO'),{{type:"doughnut",data:{{labels:{DY_ORD_LAB},datasets:[{{data:{DY_ORD_VAL},backgroundColor:[CB[5],CB[4],CB[2],CB[1]],borderWidth:2,borderColor:"#fff"}}]}},options:{{plugins:{{legend:{{position:"bottom"}}}},animation:{{animateRotate:true,animateScale:true,duration:800}}}}}})

// sec8: PLP
new Chart(document.getElementById('cPlpE'),{{type:"bar",data:{{labels:["ROAS","CVR%","CTR%","ACOS%"],datasets:[{{label:"本周",data:[{num(proas)},{num(pcvr)},{num(pctr)},{num(pacos)}],backgroundColor:C[0]}},{{label:"上周",data:[{num(proas_p)},{num(pcvr_p)},{num(pctr_p)},{num(pacos_p)}],backgroundColor:C[1]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})
new Chart(document.getElementById('cPlpV'),{{type:"bar",data:{{labels:["广告SKU","曝光量(/1000)","点击量","售出数","花费(USD)","销售额(USD)"],datasets:[{{label:"本周",data:[{psku},{round(num(pimp)/1000,1)},{intn(pclick)},{intn(psold)},{num(pcost)},{num(prev)}],backgroundColor:C[0]}},{{label:"上周",data:[{psku_p},{round(num(pimp_p)/1000,1)},{intn(pclick_p)},{intn(psold_p)},{num(pcost_p)},{num(prev_p)}],backgroundColor:C[1]}}]}},options:{{plugins:{{legend:{{position:"top"}}}},scales:{{y:{{beginAtZero:true}}}}}}}})
</script>
</body>
</html>''')

# Write output
content = '\n'.join(L)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone! {DST}')
print(f'Size: {len(content):,} bytes')
