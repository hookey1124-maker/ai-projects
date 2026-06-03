#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 4.30-5.6 可视化 HTML 报告
参考 新品周报_4.9-4.15.html 风格
"""

import json

JSON = r"c:/Users/Hardy/ai-projects/新品复盘/sheets_506.json"
DST  = r"c:/Users/Hardy/ai-projects/新品复盘/新品周报_4.30-5.6_可视化.html"

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

# ── 读取各 Sheet ──────────────────────────────────────────────────────────────
PX = sheets.get('品线维度', [])
FX = sheets.get('分析人维度', [])
TZ = sheets.get('拓展类型', [])
JL = sheets.get('分析及时率', [])
DY = sheets.get('低占比新品', [])
PLP = sheets.get('新品PLP', [])
CD = sheets.get('新品出单情况', [])
YY = sheets.get('新品未出单原因', [])
PLG = sheets.get('新品PLG维度', [])

def data_rows(rows):
    return [r for r in rows[1:] if r and r[0] and str(r[0]).strip() not in ('合计','维度')]

PX_DATA = data_rows(PX)
FX_DATA = data_rows(FX)
TZ_DATA = data_rows(TZ)
JL_DATA = data_rows(JL)
DY_DATA = data_rows(DY)
PLG_DATA = data_rows(PLG)

# ── PLP 分块 ──────────────────────────────────────────────────────────────────
PLP_TOTAL, PLP_AN, PLP_PX, PLP_TZ = [], [], [], []
block = None
for r in PLP:
    if not r or not r[0]: continue
    lab = str(r[0]).strip()
    if lab == '维度': block = None; continue
    if lab == '【总数据】': block = 'total'; continue
    if lab in ('【分析人维度】','分析人维度'): block = 'an'; continue
    if lab in ('【品线维度】','品线维度'):   block = 'px'; continue
    if lab in ('【拓展类型维度】','拓展类型维度'): block = 'tz'; continue
    if lab in ('合计','总计'):   block = None; continue
    if block == 'total' and lab == '总计':
        PLP_TOTAL.append(r)
    elif block == 'an' and lab in ['俞东旭','张潇','朱培源','王偲涵','章鹏','胡煜星']:
        PLP_AN.append(r)
    elif block == 'px' and lab not in ('合计','','【品线维度】'):
        PLP_PX.append(r)
    elif block == 'tz' and lab not in ('合计','','【拓展类型维度】'):
        PLP_TZ.append(r)

if not PLP_TOTAL:
    for r in PLP:
        if r and str(safe(r[0])).strip() == '总计':
            PLP_TOTAL.append(r)
            break

# ── 核心 KPI ──────────────────────────────────────────────────────────────────
# 分析及时率（JL_DATA合计行 = 最后一行）
jl_total_row = JL_DATA[-1] if JL_DATA else []
jl_total_sku = int(num(safe(jl_total_row[1], 0), 0))   # 截止5.6 SKU
jl_ok        = int(num(safe(jl_total_row[2], 0), 0))   # 及时分析
jl_8n        = int(num(safe(jl_total_row[3], 0), 0))   # 8日内无分析
jl_7n        = int(num(safe(jl_total_row[4], 0), 0))   # 超7日未分析
jl_rate      = str(safe(jl_total_row[5], '0%'))         # 及时率
jl_rate_p    = str(safe(jl_total_row[8], '0%'))         # 上周及时率
jl_chg       = str(safe(jl_total_row[9], '-'))          # 环比

# ═══ 新品出单情况（正确规则）══════════════════════════════════════════════════════
# 8日出单情况列含义：
#   Y = 8日内出单（上架8天内出单）
#   N = 8日外出单（已出单但超过8天）
#   未出单 = 真正未出单

col_8day = 16  # DY表"5.6 8日出单"列索引

dy_y_count   = 0   # Y：8日内出单
dy_n_count   = 0   # N：8日外出单
dy_no_count  = 0   # 未出单
dy_y_skus    = []  # Y的SKU列表
dy_n_skus    = []  # N的SKU列表
dy_no_skus   = []  # 未出单的SKU列表

for r in DY_DATA:
    if len(r) <= col_8day: continue
    v = str(safe(r[col_8day])).strip()
    sku = str(safe(r[1], '')).strip()  # SKU列
    market = str(safe(r[20], '')).strip() if len(r) > 20 else ''  # 市场状态列
    if v == 'Y':
        dy_y_count += 1
        dy_y_skus.append({'sku': sku, 'market': market})
    elif v == 'N':
        dy_n_count += 1
        dy_n_skus.append({'sku': sku, 'market': market})
    elif v == '未出单':
        dy_no_count += 1
        dy_no_skus.append({'sku': sku, 'market': market})

dy_total_count = dy_y_count + dy_n_count + dy_no_count  # 低占比新品总计

# 从CD表提取全局数据
cd_dict = {}
for r in CD:
    if not r or not r[0]: continue
    lab = str(safe(r[0],'')).strip()
    if lab == '有对手总SKU':   cd_dict['total']  = int(num(safe(r[1],0),0))
    if lab == '有销量SKU（Y）': cd_dict['sale']   = int(num(safe(r[1],0),0))
    if lab == '未出单SKU（N）': cd_dict['no']     = int(num(safe(r[1],0),0))
    if lab == '出单率':          cd_dict['rate']   = str(safe(r[1],'0%'))
    if lab == '8日外有销量':     cd_dict['sale8w'] = int(num(safe(r[1],0),0))
    if lab == '8日外出单率':     cd_dict['rate8w'] = str(safe(r[1],'0%'))
    if lab == '8日内有销量':     cd_dict['sale8']  = int(num(safe(r[1],0),0))
    if lab == '8日内出单率':     cd_dict['rate8']  = str(safe(r[1],'0%'))

has_cd_total = cd_dict.get('total', 0)  # 全局有对手总SKU

# 全局8日出单情况（正确规则解读）
# CD表"有销量SKU（Y）"= 27 实际 = 8日外出单（N）= 已出单但超8天
# CD表"未出单SKU（N）"= 13 实际 = 8日外出单数
# 全局8日出单（Y）= CD表"8日内有销量"= 4
# 全局8日外出单（N）= CD表"8日外有销量"= 23
# 全局真正未出单 = has_cd_total - 4 - 23 = 16

cd_8_sale    = cd_dict.get('sale8', 0)   # 8日内有销量 = 8日出单(Y)
cd_8w_sale   = cd_dict.get('sale8w', 0)  # 8日外有销量 = 8日外出单(N)
cd_true_no   = has_cd_total - cd_8_sale - cd_8w_sale  # 真正的未出单
cd_y_rate    = f'{cd_8_sale/has_cd_total*100:.1f}%' if has_cd_total > 0 else '0%'
cd_n_rate    = f'{cd_8w_sale/has_cd_total*100:.1f}%' if has_cd_total > 0 else '0%'
cd_no_rate   = f'{cd_true_no/has_cd_total*100:.1f}%' if has_cd_total > 0 else '0%'

# 低占比新品中真正未出单的市场状态（用于未出单原因板块）
dy_no_market = {}  # {'市场状态': 数量}
for item in dy_no_skus:
    m = item['market']
    dy_no_market[m] = dy_no_market.get(m, 0) + 1

# 低占比新品中8日外出单(N)的市场状态
dy_n_market = {}
for item in dy_n_skus:
    m = item['market']
    dy_n_market[m] = dy_n_market.get(m, 0) + 1

# 低占比新品中8日内出单(Y)的市场状态
dy_y_market = {}
for item in dy_y_skus:
    m = item['market']
    dy_y_market[m] = dy_y_market.get(m, 0) + 1

# 未出单原因（真正未出单的SKU市场状态）
yy_labs = list(dy_no_market.keys())
yy_vals = list(dy_no_market.values())

# 总体数据
zt_data = {}
for r in sheets.get('总体数据', []):
    if not r or not r[0]: continue
    lab = str(safe(r[0],'')).strip()
    if lab == '累计SKU数': zt_data['total_sku'] = int(num(safe(r[1],0),0))
    if lab == '本周新上架SKU': zt_data['new_sku'] = int(num(safe(r[1],0),0))
    if lab == '总销量': zt_data['total_qty'] = int(num(safe(r[1],0),0))
    if lab == '总销售额(USD)': zt_data['total_amt'] = num(safe(r[1],0),0)
    if lab == '有对手SKU数': zt_data['has_comp'] = int(num(safe(r[1],0),0))
    if lab == '无对手SKU数': zt_data['no_comp'] = int(num(safe(r[1],0),0))

total_sku  = zt_data.get('total_sku', jl_total_sku)
new_sku    = zt_data.get('new_sku', 0)
total_qty  = zt_data.get('total_qty', 0)
total_amt  = zt_data.get('total_amt', 0)
has_comp   = zt_data.get('has_comp', 0)
no_comp    = zt_data.get('no_comp', 0)

# 低占比新品数
lowshare_cnt = len(DY_DATA)

# PLP KPI
plp_act   = int(num(safe(PLP_TOTAL[0][1] if PLP_TOTAL else 0), 0))
plp_link  = int(num(safe(PLP_TOTAL[0][2] if PLP_TOTAL else 0), 0))
plp_imp   = int(num(safe(PLP_TOTAL[0][3] if PLP_TOTAL else 0), 0))
plp_clicks= int(num(safe(PLP_TOTAL[0][4] if PLP_TOTAL else 0), 0))
plp_sales_num = int(num(safe(PLP_TOTAL[0][5] if PLP_TOTAL else 0), 0))
plp_cost  = num(safe(PLP_TOTAL[0][6] if PLP_TOTAL else 0), 0)
plp_sa    = num(safe(PLP_TOTAL[0][7] if PLP_TOTAL else 0), 0)
plp_roas  = num(safe(PLP_TOTAL[0][8] if PLP_TOTAL else 0), 0)
plp_cv    = str(safe(PLP_TOTAL[0][9], '0%'))
plp_ctr   = str(safe(PLP_TOTAL[0][10], '0%'))
plp_cpc   = num(safe(PLP_TOTAL[0][11], 0), 0)
plp_cpa   = num(safe(PLP_TOTAL[0][12], 0), 0)
plp_acos  = str(safe(PLP_TOTAL[0][13], '0%'))

# 上周PLP
plp_roas_p = num(safe(PLP_TOTAL[0][21] if PLP_TOTAL else 0), 0)

# 开启PLP数
plp_on = sum(1 for r in DY_DATA if str(safe(r[13])).strip() == 'Y') if DY_DATA else 0

# PLG统计
plg_vals = [num(safe(r[14]),0) for r in PLG_DATA if num(safe(r[14]),0) > 0]
plg_avg  = f"{sum(plg_vals)/len(plg_vals):.2f}%" if plg_vals else "0.00%"
plg_max  = f"{max(plg_vals):.2f}%" if plg_vals else "0.00%"
plg_min  = f"{min(plg_vals):.2f}%" if plg_vals else "0.00%"

# ── 辅助函数 ──────────────────────────────────────────────────────────────────
def td(c):
    return '<td>' + safe(c) + '</td>'

def hb_class(val_str, reverse=False):
    """根据环比值返回CSS类名"""
    s = str(val_str).replace('%','').replace('+','').strip()
    if s.startswith('-'):
        return 'hb-down' if not reverse else 'hb-up'
    elif s == '0' or s == '0.0%' or s == '0.0':
        return 'hb-flat'
    else:
        return 'hb-up' if not reverse else 'hb-down'

# ── 未出单原因 ─────────────────────────────────────────────────────────────────
yy_vals = []; yy_labs = []
for r in YY[3:10]:
    if not r: continue
    lab = str(safe(r[0],'')).strip()
    val = int(num(safe(r[1],0),0))
    if val > 0 and lab not in ('合计','#N/A'):
        yy_labs.append(lab)
        yy_vals.append(val)

# ── JS 数据 ────────────────────────────────────────────────────────────────────
JL_OK_ARR  = json.dumps([int(num(safe(r[2],0),0)) for r in JL_DATA if str(safe(r[0])) not in ('合计','维度')])
JL_8N_ARR  = json.dumps([int(num(safe(r[3],0),0)) for r in JL_DATA if str(safe(r[0])) not in ('合计','维度')])
JL_7N_ARR  = json.dumps([int(num(safe(r[4],0),0)) for r in JL_DATA if str(safe(r[0])) not in ('合计','维度')])
JL_LAB_ARR = json.dumps([str(safe(r[0])) for r in JL_DATA if str(safe(r[0])) not in ('合计','维度')])

YY_LAB_ARR = json.dumps(yy_labs)
YY_VAL_ARR = json.dumps(yy_vals)

PLP_AN_LAB  = json.dumps([str(safe(r[0])) for r in PLP_AN])
PLP_AN_ROAS = json.dumps([num(safe(r[8]),0) for r in PLP_AN])
PLP_AN_COST = json.dumps([str(safe(r[6])) for r in PLP_AN])
PLP_PX_LAB  = json.dumps([str(safe(r[0])) for r in PLP_PX])
PLP_PX_ROAS = json.dumps([num(safe(r[8]),0) for r in PLP_PX])

# ══════════════════════════════════════════════════════════════════════════════════════
# 生成 HTML（字符串拼接，无 f-string）
# ══════════════════════════════════════════════════════════════════════════════════════
lines = []
W = lines.append

# ── HTML Head ─────────────────────────────────────────────────────────────────
W('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报 · 4.30-5.6</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }
.header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 28px 40px; }
.header h1 { font-size: 26px; font-weight: 700; letter-spacing: 2px; }
.header .subtitle { font-size: 13px; opacity: 0.75; margin-top: 6px; }
.container { display: flex; min-height: calc(100vh - 80px); }
.sidebar { width: 230px; background: #fff; border-right: 1px solid #e8e8e8; padding: 20px 0; position: sticky; top: 0; height: 100vh; overflow-y: auto; flex-shrink: 0; }
.sidebar ul { list-style: none; }
.sidebar li a { display: block; padding: 10px 20px; font-size: 13px; color: #555; text-decoration: none; border-left: 3px solid transparent; transition: all 0.2s; }
.sidebar li a:hover, .sidebar li a.active { background: #f0f6ff; color: #0f3460; border-left-color: #0f3460; font-weight: 600; }
.main-content { flex: 1; padding: 24px; overflow: auto; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 14px; margin-bottom: 24px; }
.kpi-card { background: white; border-radius: 10px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }
.kpi-card .val { font-size: 26px; font-weight: 700; color: #0f3460; }
.kpi-card .label { font-size: 12px; color: #888; margin-top: 6px; }
.kpi-card .hb { font-size: 11px; margin-top: 4px; font-weight: 600; }
.kpi-card.green .val { color: #08845a; }
.kpi-card.orange .val { color: #e07b24; }
.kpi-card.red .val { color: #c0392b; }
.kpi-card.purple .val { color: #8e44ad; }
.section { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section h3 { font-size: 16px; font-weight: 700; color: #0f3460; padding-bottom: 12px; border-bottom: 2px solid #e8f0fe; margin-bottom: 16px; }
.sub-module { margin-bottom: 20px; }
.sub-module h4 { font-size: 13px; font-weight: 600; color: #444; margin-bottom: 10px; padding: 6px 12px; background: #f5f7ff; border-radius: 4px; border-left: 3px solid #0f3460; }
.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }
.chart-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.chart-card h4 { font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 14px; }
.chart-card canvas { max-height: 260px; }
.chart-card-wide { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); grid-column: 1 / -1; }
.chart-card-wide h4 { font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 14px; }
.chart-card-wide canvas { max-height: 300px; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th { background: #0f3460; color: white; padding: 8px 8px; text-align: center; white-space: nowrap; font-weight: 600; }
.data-table th.p1 { background: #6c757d; }
.data-table th.p2 { background: #667eea; }
.data-table th.p3 { background: #2980b9; }
.data-table th.p4 { background: #c0392b; }
.data-table th.hb { background: #e07b24; }
.data-table td { padding: 6px 8px; text-align: center; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }
.data-table tr:hover td { background: #f5f7ff; }
.hb-up { color: #c0392b; font-weight: 700; }
.hb-down { color: #08845a; font-weight: 700; }
.hb-flat { color: #888; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: white; font-weight: 600; }
.badge-y { background: #08845a; }
.badge-n { background: #e07b24; }
.badge-un { background: #c0392b; }
.badge-normal { background: #2980b9; }
select { padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; font-size: 13px; background: white; cursor: pointer; }
select:focus { outline: none; border-color: #0f3460; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
@media (max-width: 900px) { .sidebar { display: none; } .chart-grid { grid-template-columns: 1fr; } .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.section-wrap { display: block; }
.note { font-size: 12px; color: #888; margin-bottom: 10px; }
.pl1 { background: #6c757d; }
.pl2 { background: #667eea; }
.pl3 { background: #2980b9; }
.pl4 { background: #c0392b; }
.plp-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px; }
.plp-card { background: white; border-radius: 10px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #8e44ad; }
.plp-card h4 { font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 12px; }
.plp-metric { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #f0f0f0; font-size: 12px; }
.plp-metric:last-child { border-bottom: none; }
.plp-metric .lbl { color: #666; }
.plp-metric .val { font-weight: 600; color: #1a1a2e; }
.plp-highlight { background: #f5f0ff; border-radius: 6px; padding: 10px; margin-top: 10px; }
.plp-highlight .val { color: #8e44ad; font-weight: 700; }
</style>
</head>
<body>

<div class="header">
  <h1>&#x1F4CA; 新品周报 &middot; 4.30-5.6</h1>
  <div class="subtitle">统计周期：2026年4月30日 - 5月6日 &nbsp;|&nbsp; 在跟SKU：''' + str(total_sku) + ''' &nbsp;|&nbsp; 生成：2026-05-11</div>
</div>

<div class="container">
<nav class="sidebar">
  <ul>
    <li><a href="#" onclick="showSection('overview',this)" class="active">&#x1F4CA; 数据总览</a></li>
    <li><a href="#" onclick="showSection('pinxian',this)">&#x1F3F7;&#xFE0F; 品线维度</a></li>
    <li><a href="#" onclick="showSection('analyst',this)">&#x1F464; 分析人维度</a></li>
    <li><a href="#" onclick="showSection('expand',this)">&#x1F516; 拓展类型</a></li>
    <li><a href="#" onclick="showSection('timely',this)">&#x23F1;&#xFE0F; 分析及时率</a></li>
    <li><a href="#" onclick="showSection('order',this)">&#x1F4E6; 新品出单情况</a></li>
    <li><a href="#" onclick="showSection('unorder',this)">&#x274C; 新品未出单</a></li>
    <li><a href="#" onclick="showSection('lowshare',this)">&#x1F4C9; 低占比新品</a></li>
    <li><a href="#" onclick="showSection('plp',this)">&#x1F4B0; PLP复盘</a></li>
  </ul>
</nav>

<div class="main-content">
''')

# ═══ KPI总览 ═══════════════════════════════════════════════════════════════════
# 正确规则：Y=8日内出单，N=8日外出单，未出单=真正未出单
W('<!-- KPI总览 -->')
W('<div class="kpi-grid">')
W('  <div class="kpi-card"><div class="val">' + str(total_sku) + '</div><div class="label">在跟SKU总数</div><div class="hb" style="color:#888">本周新上架 ' + str(new_sku) + '</div></div>')
# 出单情况KPI（正确规则）
W('  <div class="kpi-card green"><div class="val">' + str(cd_8_sale) + '</div><div class="label">5.6已出单（Y=8日内）</div><div class="hb hb-flat" style="color:#888">占 ' + cd_y_rate + '</div></div>')
W('  <div class="kpi-card orange"><div class="val">' + str(cd_8w_sale) + '</div><div class="label">5.6已出单（N=8日外）</div><div class="hb hb-flat" style="color:#888">占 ' + cd_n_rate + '</div></div>')
W('  <div class="kpi-card red"><div class="val">' + str(cd_true_no) + '</div><div class="label">5.6真正未出单</div><div class="hb hb-flat" style="color:#888">占 ' + cd_no_rate + '</div></div>')
W('  <div class="kpi-card"><div class="val">' + str(cd_8_sale + cd_8w_sale) + '</div><div class="label">已出单合计(Y+N)</div><div class="hb hb-flat" style="color:#888">/ ' + str(has_cd_total) + ' 有对手SKU</div></div>')
W('  <div class="kpi-card"><div class="val">' + str(total_qty) + '</div><div class="label">4.30-5.6总销量</div><div class="hb" style="color:#888">及时分析 ' + str(jl_ok) + '</div></div>')
W('  <div class="kpi-card purple"><div class="val">$' + f'{total_amt:,.0f}' + '</div><div class="label">4.30-5.6总销售额</div><div class="hb" style="color:#888">有对手 ' + str(has_comp) + ' / 无对手 ' + str(no_comp) + '</div></div>')
W('  <div class="kpi-card red"><div class="val">' + str(lowshare_cnt) + '</div><div class="label">低占比新品(mzb&lt;75%)</div><div class="hb" style="color:#888">Y=' + str(dy_y_count) + ' N=' + str(dy_n_count) + ' 未=' + str(dy_no_count) + '</div></div>')
W('</div>')

# ═══ 数据总览 ═══════════════════════════════════════════════════════════════════
W('<!-- 数据总览 -->')
W('<div id="section-overview" class="section-wrap">')
W('  <div class="section">')
W('    <h3>&#x1F4CA; 数据总览 · 图形可视化</h3>')
W('    <div class="chart-grid">')
W('      <div class="chart-card">')
W('        <h4>&#x1F4E6; 5.6出单分布</h4>')
W('        <canvas id="chartOrderPie"></canvas>')
W('      </div>')
W('      <div class="chart-card">')
W('        <h4>&#x274C; 未出单原因分布</h4>')
W('        <canvas id="chartUnorderPie"></canvas>')
W('      </div>')
W('      <div class="chart-card">')
W('        <h4>&#x23F1;&#xFE0F; 分析情况分布</h4>')
W('        <canvas id="chartTimelyPie"></canvas>')
W('      </div>')
W('      <div class="chart-card">')
W('        <h4>&#x1F4C9; 低占比新品分布</h4>')
W('        <canvas id="chartLowShareCat"></canvas>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 品线维度 ═══════════════════════════════════════════════════════════════════
# PX_DATA列：品线/本周SKU/本周新上架/本周销量/上周销量/销量环比/本周销售额/上周销售额/销售额环比/本周有对手/上周有对手
px_labs = json.dumps([str(r[0]) for r in PX_DATA])
px_qty_cur = json.dumps([int(num(safe(r[3],0),0)) for r in PX_DATA])
px_qty_pre = json.dumps([int(num(safe(r[4],0),0)) for r in PX_DATA])

W('<div id="section-pinxian" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x1F3F7;&#xFE0F; 品线维度</h3>')
W('    <p class="note">各品线在跟SKU数量及销量对比</p>')
W('    <div class="sub-module">')
W('      <h4>各品线销量对比</h4>')
W('      <div class="chart-grid">')
W('        <div class="chart-card">')
W('          <h4>本周 vs 上周 销量对比</h4>')
W('          <canvas id="chartCatQty"></canvas>')
W('        </div>')
W('        <div class="chart-card">')
W('          <h4>本周各品线销量占比</h4>')
W('          <canvas id="chartCatPie"></canvas>')
W('        </div>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>品线数据明细</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th rowspan="2">品类</th>')
W('              <th rowspan="2">本周SKU</th>')
W('              <th rowspan="2">本周新上架</th>')
W('              <th colspan="2" class="p3">本周</th>')
W('              <th colspan="2" class="p2">上周</th>')
W('              <th colspan="2" class="hb">环比</th>')
W('            </tr>')
W('            <tr>')
W('              <th class="p3">销量</th><th class="p3">销售额</th>')
W('              <th class="p2">销量</th><th class="p2">销售额</th>')
W('              <th class="hb">销量变化</th><th class="hb">销售额变化</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
for r in PX_DATA:
    cur_qty = int(num(safe(r[3],0),0))
    pre_qty = int(num(safe(r[4],0),0))
    cur_amt = safe(r[6],'')
    pre_amt = safe(r[7],'')
    qty_chg = safe(r[5],'')
    amt_chg = safe(r[8],'')
    qty_cls = hb_class(qty_chg)
    amt_cls = hb_class(amt_chg)
    W('            <tr><td><b>' + str(r[0]) + '</b></td><td>' + str(r[1]) + '</td><td>' + str(r[2]) + '</td><td>' + str(cur_qty) + '</td><td>' + str(cur_amt) + '</td><td>' + str(pre_qty) + '</td><td>' + str(pre_amt) + '</td><td><span class="' + qty_cls + '">' + str(qty_chg) + '</span></td><td><span class="' + amt_cls + '">' + str(amt_chg) + '</span></td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 分析人维度 ═══════════════════════════════════════════════════════════════════
# FX_DATA列：分析人/本周SKU/本周销量/上周销量/销量环比/本周销售额/上周销售额/销售额环比
fx_labs = json.dumps([str(r[0]) for r in FX_DATA])
fx_qty_cur = json.dumps([int(num(safe(r[2],0),0)) for r in FX_DATA])
fx_qty_pre = json.dumps([int(num(safe(r[3],0),0)) for r in FX_DATA])

W('<div id="section-analyst" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x1F464; 分析人维度</h3>')
W('    <p class="note">各分析人负责SKU的销量表现</p>')
W('    <div class="sub-module">')
W('      <h4>各分析人销量对比</h4>')
W('      <div class="chart-grid">')
W('        <div class="chart-card">')
W('          <h4>本周 vs 上周 销量对比</h4>')
W('          <canvas id="chartAnQty"></canvas>')
W('        </div>')
W('        <div class="chart-card">')
W('          <h4>本周各分析人销量占比</h4>')
W('          <canvas id="chartAnPie"></canvas>')
W('        </div>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>分析人数据明细</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th rowspan="2">分析人</th>')
W('              <th rowspan="2">本周SKU</th>')
W('              <th colspan="2" class="p4">本周</th>')
W('              <th colspan="2" class="p2">上周</th>')
W('              <th colspan="2" class="hb">环比</th>')
W('            </tr>')
W('            <tr>')
W('              <th class="p4">销量</th><th class="p4">销售额</th>')
W('              <th class="p2">销量</th><th class="p2">销售额</th>')
W('              <th class="hb">销量变化</th><th class="hb">销售额变化</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
for r in FX_DATA:
    cur_qty = int(num(safe(r[2],0),0))
    pre_qty = int(num(safe(r[3],0),0))
    cur_amt = safe(r[5],'')
    pre_amt = safe(r[6],'')
    qty_chg = safe(r[4],'')
    amt_chg = safe(r[7],'')
    qty_cls = hb_class(qty_chg)
    amt_cls = hb_class(amt_chg)
    W('            <tr><td><b>' + str(r[0]) + '</b></td><td>' + str(r[1]) + '</td><td>' + str(cur_qty) + '</td><td>' + str(cur_amt) + '</td><td>' + str(pre_qty) + '</td><td>' + str(pre_amt) + '</td><td><span class="' + qty_cls + '">' + str(qty_chg) + '</span></td><td><span class="' + amt_cls + '">' + str(amt_chg) + '</span></td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 拓展类型 ═══════════════════════════════════════════════════════════════════
# TZ_DATA列：类型/本周SKU/本周出单/出单率/上周出单率/出单率环比/本周销量/上周销量/销量环比/本周销售额/上周销售额/销售额环比
tz_labs  = json.dumps([str(r[0]) for r in TZ_DATA])
tz_rate_cur = json.dumps([str(safe(r[3],'0%')) for r in TZ_DATA])
tz_rate_pre = json.dumps([str(safe(r[4],'0%')) for r in TZ_DATA])
tz_qty_cur  = json.dumps([int(num(safe(r[6],0),0)) for r in TZ_DATA])

W('<div id="section-expand" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x1F516; 拓展类型维度</h3>')
W('    <p class="note">原开品 / 拓展品 / 组合件 的出单率及销量表现</p>')
W('    <div class="sub-module">')
W('      <h4>拓展类型出单率对比</h4>')
W('      <div class="chart-grid">')
W('        <div class="chart-card">')
W('          <h4>本周 vs 上周 出单率</h4>')
W('          <canvas id="chartTzRate"></canvas>')
W('        </div>')
W('        <div class="chart-card">')
W('          <h4>本周销量分布</h4>')
W('          <canvas id="chartTzPie"></canvas>')
W('        </div>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>拓展类型数据明细</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th rowspan="2">类型</th>')
W('              <th rowspan="2">本周SKU</th>')
W('              <th colspan="2" class="p4">本周</th>')
W('              <th class="p2">上周</th>')
W('              <th class="hb">出单率环比</th>')
W('              <th colspan="2" class="p4">本周</th>')
W('              <th class="p2">上周</th>')
W('              <th class="hb">销量环比</th>')
W('            </tr>')
W('            <tr>')
W('              <th class="p4">出单SKU</th><th class="p4">出单率</th>')
W('              <th class="p2">出单率</th>')
W('              <th class="hb">变化</th>')
W('              <th class="p4">销量</th>')
W('              <th class="p2">销量</th>')
W('              <th class="hb">变化</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
for r in TZ_DATA:
    rate_cls = hb_class(safe(r[5],''))
    qty_cls  = hb_class(safe(r[8],''))
    W('            <tr><td><b>' + str(r[0]) + '</b></td><td>' + str(r[1]) + '</td><td>' + str(r[2]) + '</td><td>' + str(r[3]) + '</td><td>' + str(r[4]) + '</td><td><span class="' + rate_cls + '">' + str(r[5]) + '</span></td><td>' + str(r[6]) + '</td><td>' + str(r[7]) + '</td><td><span class="' + qty_cls + '">' + str(r[8]) + '</span></td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 分析及时率 ═══════════════════════════════════════════════════════════════════
W('<div id="section-timely" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x23F1;&#xFE0F; 分析及时率</h3>')
W('    <p class="note">统计周期内分析人对在跟SKU的跟进及时程度（基于5.6检查表）</p>')
W('    <div class="sub-module">')
W('      <h4>分析及时率汇总</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th rowspan="2">分析情况</th>')
W('              <th colspan="2" class="p4">5.6（本周）</th>')
W('              <th colspan="2" class="p2">4.29（上周）</th>')
W('              <th class="hb">环比(计数)</th>')
W('              <th class="hb">环比(占比)</th>')
W('            </tr>')
W('            <tr>')
W('              <th class="p4">计数</th><th class="p4">占比</th>')
W('              <th class="p2">计数</th><th class="p2">占比</th>')
W('              <th class="hb">5.6 vs 4.29</th>')
W('              <th class="hb">5.6 vs 4.29</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
W('            <tr><td><b>及时分析产品</b></td><td>' + str(jl_ok) + '</td><td>' + jl_rate + '</td><td>-</td><td>-</td><td><span class="hb-flat">-</span></td><td><span class="hb-flat">-</span></td></tr>')
W('            <tr><td><b>超7日未分析产品</b></td><td>' + str(jl_7n) + '</td><td>-</td><td>-</td><td>-</td><td><span class="hb-flat">-</span></td><td><span class="hb-flat">-</span></td></tr>')
W('            <tr><td><b>8日内新品无分析</b></td><td>' + str(jl_8n) + '</td><td>-</td><td>-</td><td>-</td><td><span class="hb-flat">-</span></td><td><span class="hb-flat">-</span></td></tr>')
W('            <tr style="background:#f5f5f5; font-weight:700;"><td><b>合计</b></td><td>' + str(jl_total_sku) + '</td><td>100%</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>各分析人及时率（4.30-5.6）</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th>分析人</th><th>负责SKU</th>')
W('              <th>及时分析</th><th>及时率</th>')
W('              <th>超7日未分析</th><th>8日内无分析</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
for r in JL_DATA:
    name = str(safe(r[0],''))
    if name in ('合计','维度'): continue
    sku = safe(r[1],'')
    ok = safe(r[2],'')
    rate = safe(r[5],'')
    over7 = safe(r[4],'')
    new8 = safe(r[3],'')
    rate_cls = 'hb-up' if num(rate,0) >= 70 else 'hb-down' if num(rate,0) > 0 else 'hb-flat'
    W('            <tr><td>' + name + '</td><td>' + str(sku) + '</td><td>' + str(ok) + '</td><td class="' + rate_cls + '">' + str(rate) + '</td><td>' + str(over7) + '</td><td>' + str(new8) + '</td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 新品出单情况 ═══════════════════════════════════════════════════════════════
# 正确规则：Y=8日内出单（上架8天内出单），N=8日外出单（已出单但超过8天），未出单=真正未出单
W('<div id="section-order" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x1F4E6; 新品出单情况</h3>')
W('    <p class="note"><b>规则说明：</b>Y=8日内出单（上架8天内出单）｜N=8日外出单（已出单但超8天）｜未出单=真正未出单</p>')
W('    <div class="chart-grid">')
W('      <div class="chart-card">')
W('        <h4>5.6出单情况分布（有对手口径，共' + str(has_cd_total) + '个SKU）</h4>')
W('        <canvas id="chartOrderDist"></canvas>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>5.6新品出单数据明细</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th>指标</th>')
W('              <th class="p4">数量</th>')
W('              <th class="p4">占比</th>')
W('              <th class="p2">说明</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
cd_tbl2 = [
    ('有对手总SKU', str(has_cd_total), '100%', '全部有竞争对手的SKU'),
    ('8日内出单（Y）', str(cd_8_sale), cd_y_rate, '上架8天内出单'),
    ('8日外出单（N）', str(cd_8w_sale), cd_n_rate, '已出单但超过8天'),
    ('真正未出单', str(cd_true_no), cd_no_rate, '从未出单的新品'),
    ('已出单合计(Y+N)', str(cd_8_sale + cd_8w_sale), str(f'{(cd_8_sale+cd_8w_sale)/has_cd_total*100:.1f}%') if has_cd_total > 0 else '0%', 'Y+N'),
]
for label, cnt, rate, note in cd_tbl2:
    row_cls = 'background:#e8f5e9' if '未出单' not in label and label != '有对手总SKU' else ''
    W('            <tr style="' + row_cls + '"><td><b>' + label + '</b></td><td>' + cnt + '</td><td>' + rate + '</td><td style="color:#666;font-size:11px">' + note + '</td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 新品未出单 ═══════════════════════════════════════════════════════════════════
# 正确规则：只统计DY表中"5.6 8日出单"列值为"未出单"的SKU
W('<div id="section-unorder" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x274C; 新品未出单原因分析（真正未出单）</h3>')
W('    <p class="note"><b>统计口径：</b>只包含DY表中"5.6 8日出单"=未出单的SKU，共 <b>' + str(dy_no_count) + '</b> 个</p>')
W('    <div class="chart-grid">')
W('      <div class="chart-card">')
W('        <h4>真正未出单SKU的市场状态分布</h4>')
W('        <canvas id="chartUnorderDist"></canvas>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>未出单原因数据明细</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th>未出单原因（市场状态）</th>')
W('              <th class="p4">SKU数量</th>')
W('              <th class="p4">占比</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
for lab, val in zip(yy_labs, yy_vals):
    rate = f'{val/dy_no_count*100:.1f}%' if dy_no_count > 0 else '0%'
    W('            <tr><td><b>' + lab + '</b></td><td>' + str(val) + '</td><td>' + rate + '</td></tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>未出单SKU明细（DY表"5.6 8日出单"=未出单）</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th>SKU</th><th>品类</th><th>分析人</th><th>拓展类型</th>')
W('              <th>上架日期</th><th>市场状态</th><th>操作判断</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
for item in dy_no_skus:
    W('            <tr>')
    W('              <td style="text-align:left">' + item['sku'] + '</td>')
    W('              <td>-</td><td>-</td><td>-</td><td>-</td>')
    W('              <td><span class="badge badge-un">' + item['market'] + '</span></td><td>-</td>')
    W('            </tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ 低占比新品 ═══════════════════════════════════════════════════════════════════
W('<div id="section-lowshare" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x1F4C9; 低占比新品</h3>')
W('    <p class="note">5.6市占比 &lt; 75% 且存在对手销量的产品，共 <strong>' + str(lowshare_cnt) + '</strong> 个</p>')
W('    <div class="chart-grid">')
W('      <div class="chart-card">')
W('        <h4>低占比产品按品类分布</h4>')
W('        <canvas id="chartLowCat"></canvas>')
W('      </div>')
W('      <div class="chart-card">')
W('        <h4>低占比产品按出单状态分布</h4>')
W('        <canvas id="chartLowOrder"></canvas>')
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>低占比新品明细（5.6市占比 &lt; 75%，有对手销量）</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th>编号</th><th>SKU</th><th>品类</th><th>拓展类型</th>')
W('              <th>上架日期</th><th>分析人</th>')
W('              <th>销量</th><th>销售额</th>')
W('              <th>对手销量</th><th>市占比</th>')
W('              <th>8日出单</th><th>7日频次</th><th>市场状态</th><th>操作判断</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody id="lowShareTableBody">')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

# ═══ PLP复盘 ═══════════════════════════════════════════════════════════════════════
# 构建分析人ROAS和花费
an_roas_html = ''
an_cost_html = ''
for r in PLP_AN:
    name = str(safe(r[0],''))
    roas = num(safe(r[8],0),0)
    cost = safe(r[6],'')
    roas_cls = 'color:#08845a' if roas >= 10 else ''
    an_roas_html += '<div class="plp-metric"><span class="lbl">' + name + '</span><span class="val" style="' + roas_cls + '">ROAS ' + str(roas) + '</span></div>\n'
    an_cost_html += '<div class="plp-metric"><span class="lbl">' + name + '花费</span><span class="val">$' + str(cost) + '</span></div>\n'

# 构建品线ROAS和花费
px_roas_html = ''
px_cost_html = ''
for r in PLP_PX:
    name = str(safe(r[0],''))
    roas = num(safe(r[8],0),0)
    cost = safe(r[6],'')
    roas_cls = 'color:#08845a' if roas >= 10 else ''
    px_roas_html += '<div class="plp-metric"><span class="lbl">' + name + 'ROAS</span><span class="val" style="' + roas_cls + '">' + str(roas) + '</span></div>\n'
    px_cost_html += '<div class="plp-metric"><span class="lbl">' + name + '花费</span><span class="val">$' + str(cost) + '</span></div>\n'

W('<div id="section-plp" class="section-wrap" style="display:none">')
W('  <div class="section">')
W('    <h3>&#x1F4B0; PLP广告复盘 · 4.30-5.6</h3>')
W('    <p class="note">' + str(plp_act) + '个SKU参与PLP广告，总花费$' + f'{plp_cost:,.2f}' + '，ROAS ' + f'{plp_roas:.2f}' + '，ACOS ' + plp_acos + '</p>')
W('    <div class="plp-grid">')
W('      <div class="plp-card">')
W('        <h4>总览指标</h4>')
W('        <div class="plp-metric"><span class="lbl">参与SKU</span><span class="val">' + str(plp_act) + '</span></div>')
W('        <div class="plp-metric"><span class="lbl">广告曝光量</span><span class="val">' + f'{plp_imp:,}' + '</span></div>')
W('        <div class="plp-metric"><span class="lbl">广告点击量</span><span class="val">' + str(plp_clicks) + '</span></div>')
W('        <div class="plp-metric"><span class="lbl">广告售出数</span><span class="val">' + str(plp_sales_num) + '</span></div>')
W('        <div class="plp-highlight">')
W('          <div class="plp-metric"><span class="lbl">ROAS</span><span class="val">' + f'{plp_roas:.2f}' + '</span></div>')
W('          <div class="plp-metric"><span class="lbl">ACOS</span><span class="val">' + plp_acos + '</span></div>')
W('          <div class="plp-metric"><span class="lbl">CVR</span><span class="val">' + plp_cv + '</span></div>')
W('          <div class="plp-metric"><span class="lbl">CTR</span><span class="val">' + plp_ctr + '</span></div>')
W('          <div class="plp-metric"><span class="lbl">花费</span><span class="val">$' + f'{plp_cost:,.2f}' + '</span></div>')
W('        </div>')
W('      </div>')
W('      <div class="plp-card" style="border-top-color:#c0392b;">')
W('        <h4>按分析人维度</h4>')
W(an_roas_html)
W(an_cost_html)
W('      </div>')
W('      <div class="plp-card" style="border-top-color:#2980b9;">')
W('        <h4>按品线维度</h4>')
W(px_roas_html)
W(px_cost_html)
W('      </div>')
W('    </div>')
W('    <div class="sub-module">')
W('      <h4>PLP广告明细表</h4>')
W('      <div class="table-wrap">')
W('        <table class="data-table">')
W('          <thead>')
W('            <tr>')
W('              <th colspan="5" class="p4">按分析人</th>')
W('              <th colspan="5" class="p2">按品线</th>')
W('              <th colspan="3" class="hb">综合指标</th>')
W('            </tr>')
W('            <tr>')
W('              <th>分析人</th><th>SKU</th><th>ROAS</th><th>ACOS</th><th>花费</th>')
W('              <th>品线</th><th>SKU</th><th>ROAS</th><th>ACOS</th><th>花费</th>')
W('              <th>CVR</th><th>CTR</th><th>CPA</th>')
W('            </tr>')
W('          </thead>')
W('          <tbody>')
max_rows = max(len(PLP_AN), len(PLP_PX))
for i in range(max_rows):
    an_r = PLP_AN[i] if i < len(PLP_AN) else [''] * 14
    px_r = PLP_PX[i] if i < len(PLP_PX) else [''] * 14
    an_roas = num(safe(an_r[8],0),0)
    px_roas = num(safe(px_r[8],0),0)
    an_roas_cls = 'style="color:#08845a;font-weight:700"' if an_roas >= 10 else ''
    px_roas_cls = 'style="color:#08845a;font-weight:700"' if px_roas >= 10 else ''
    W('            <tr>')
    W('              <td>' + str(safe(an_r[0],'')) + '</td><td>' + str(safe(an_r[1],'')) + '</td><td ' + an_roas_cls + '>' + str(safe(an_r[8],'')) + '</td><td>' + str(safe(an_r[13],'')) + '</td><td>$' + str(safe(an_r[6],'')) + '</td>')
    W('              <td>' + str(safe(px_r[0],'')) + '</td><td>' + str(safe(px_r[1],'')) + '</td><td ' + px_roas_cls + '>' + str(safe(px_r[8],'')) + '</td><td>' + str(safe(px_r[13],'')) + '</td><td>$' + str(safe(px_r[6],'')) + '</td>')
    if i == 0:
        W('              <td rowspan="' + str(max_rows) + '">' + plp_cv + '</td><td rowspan="' + str(max_rows) + '">' + plp_ctr + '</td><td rowspan="' + str(max_rows) + '">$' + f'{plp_cpa:.2f}' + '</td>')
    W('            </tr>')
W('          </tbody>')
W('        </table>')
W('      </div>')
W('    </div>')
W('  </div>')
W('</div>')

W('</div><!-- end main-content -->')
W('</div><!-- end container -->')

# ═══ JS 代码 ═══════════════════════════════════════════════════════════════════════
JS_SCRIPT = '''
<script>
// ===== 导航 =====
function showSection(id, el) {
  document.querySelectorAll('.section-wrap').forEach(s => s.style.display = 'none');
  document.querySelectorAll('.sidebar li a').forEach(a => a.classList.remove('active'));
  document.getElementById('section-' + id).style.display = 'block';
  if(el) el.classList.add('active');
}

// ===== 数据定义 =====
const P_COLORS = ['rgba(102,126,234,0.8)', 'rgba(41,128,185,0.8)', 'rgba(192,57,43,0.8)', 'rgba(142,68,173,0.8)'];
const P_COLORS_BORDER = ['#667eea', '#2980b9', '#c0392b', '#8e44ad'];

// 品线
const catLabs = ''' + px_labs + ''';
const catQtyCur = ''' + px_qty_cur + ''';
const catQtyPre = ''' + px_qty_pre + ''';

// 分析人
const anLabs = ''' + fx_labs + ''';
const anQtyCur = ''' + fx_qty_cur + ''';
const anQtyPre = ''' + fx_qty_pre + ''';

// 拓展类型
const tzLabs = ''' + tz_labs + ''';
const tzRateCur = ''' + tz_rate_cur + ''';
const tzRatePre = ''' + tz_rate_pre + ''';
const tzQtyCur = ''' + tz_qty_cur + ''';

// 分析及时率
const timelyLabs = ''' + JL_LAB_ARR + ''';
const timelyOk = ''' + JL_OK_ARR + ''';
const timelyOver7 = ''' + JL_7N_ARR + ''';
const timelyNew8 = ''' + JL_8N_ARR + ''';

// 低占比新品明细
const lowShareData = ''' + json.dumps([
    [str(safe(r[0])), str(safe(r[1])), str(safe(r[4])), str(safe(r[5])),
     str(safe(r[2])), str(safe(r[3])), str(safe(r[6])), str(safe(r[7])),
     str(safe(r[9])), str(safe(r[10])), str(safe(r[11])), str(safe(r[12])),
     str(safe(r[13])), str(safe(r[14]))]
    for r in DY_DATA
]) + ''';

// ═══ 初始化 ═══
window.onload = function() {
  initOverviewCharts();
  initOrderCharts();
  initCatCharts();
  initAnCharts();
  initTzCharts();
  initLowShareCharts();
  buildLowShareTable();
};

function initOverviewCharts() {
  // 出单分布（正确规则：Y=8日内出单，N=8日外出单，未出单=真正未出单）
  new Chart(document.getElementById('chartOrderPie'), {
    type: 'doughnut',
    data: {
      labels: ['8日内出单(Y)', '8日外出单(N)', '真正未出单'],
      datasets: [{ data: [''' + str(cd_8_sale) + ', ' + str(cd_8w_sale) + ', ' + str(cd_true_no) + '''], backgroundColor: ['#08845a', '#e07b24', '#c0392b'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });

  // 未出单原因（真正未出单的SKU市场状态）
  new Chart(document.getElementById('chartUnorderPie'), {
    type: 'doughnut',
    data: {
      labels: ''' + YY_LAB_ARR + ''',
      datasets: [{ data: ''' + YY_VAL_ARR + ''', backgroundColor: ['#c0392b', '#2980b9', '#27ae60', '#e07b24'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });

  // 分析情况
  new Chart(document.getElementById('chartTimelyPie'), {
    type: 'doughnut',
    data: {
      labels: ['及时分析', '超7日未分析', '8日内无分析'],
      datasets: [{ data: [''' + str(jl_ok) + ', ' + str(jl_7n) + ', ' + str(jl_8n) + '''], backgroundColor: ['#08845a', '#c0392b', '#e07b24'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });

  // 低占比品类分布
  const catCount = {};
  lowShareData.forEach(r => { catCount[r[2]] = (catCount[r[2]] || 0) + 1; });
  new Chart(document.getElementById('chartLowShareCat'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(catCount),
      datasets: [{ data: Object.values(catCount), backgroundColor: ['#c0392b', '#2980b9', '#e07b24', '#27ae60', '#8e44ad', '#f39c12'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function initCatCharts() {
  const colors = ['#e07b24', '#8e44ad', '#08845a', '#c0392b', '#2980b9', '#27ae60'];
  new Chart(document.getElementById('chartCatQty'), {
    type: 'bar',
    data: {
      labels: catLabs,
      datasets: [
        { label: '本周销量', data: catQtyCur, backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
        { label: '上周销量', data: catQtyPre, backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
      ]
    },
    options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
  });

  new Chart(document.getElementById('chartCatPie'), {
    type: 'doughnut',
    data: {
      labels: catLabs,
      datasets: [{ data: catQtyCur, backgroundColor: colors.map(c => c + '99'), borderColor: colors, borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function initAnCharts() {
  const colors = ['#c0392b', '#2980b9', '#e07b24', '#8e44ad', '#27ae60', '#f39c12'];
  new Chart(document.getElementById('chartAnQty'), {
    type: 'bar',
    data: {
      labels: anLabs,
      datasets: [
        { label: '本周销量', data: anQtyCur, backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
        { label: '上周销量', data: anQtyPre, backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
      ]
    },
    options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
  });

  new Chart(document.getElementById('chartAnPie'), {
    type: 'doughnut',
    data: {
      labels: anLabs,
      datasets: [{ data: anQtyCur, backgroundColor: colors.map(c => c + '99'), borderColor: colors, borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function initTzCharts() {
  const colors = ['#c0392b', '#2980b9', '#f39c12'];
  new Chart(document.getElementById('chartTzRate'), {
    type: 'bar',
    data: {
      labels: tzLabs,
      datasets: [
        { label: '本周出单率', data: tzRateCur.map(v => parseFloat(v)), backgroundColor: 'rgba(192,57,43,0.8)', borderColor: '#c0392b', borderWidth: 2 },
        { label: '上周出单率', data: tzRatePre.map(v => parseFloat(v)), backgroundColor: 'rgba(41,128,185,0.8)', borderColor: '#2980b9', borderWidth: 2 }
      ]
    },
    options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { min: 0, max: 100, ticks: { callback: v => v + '%' } } } }
  });

  new Chart(document.getElementById('chartTzPie'), {
    type: 'doughnut',
    data: {
      labels: tzLabs,
      datasets: [{ data: tzQtyCur, backgroundColor: colors, borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function initLowShareCharts() {
  // 按品类
  const catCount = {};
  lowShareData.forEach(r => { catCount[r[2]] = (catCount[r[2]] || 0) + 1; });
  new Chart(document.getElementById('chartLowCat'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(catCount),
      datasets: [{ data: Object.values(catCount), backgroundColor: ['#c0392b', '#2980b9', '#e07b24', '#27ae60', '#8e44ad', '#f39c12'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });

  // 按出单状态
  const orderCount = { 'Y': 0, 'N': 0, '未出单': 0 };
  lowShareData.forEach(r => {
    const s = r[10];
    if (s === 'Y') orderCount['Y']++;
    else if (s === 'N') orderCount['N']++;
    else orderCount['未出单']++;
  });
  new Chart(document.getElementById('chartLowOrder'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(orderCount),
      datasets: [{ data: Object.values(orderCount), backgroundColor: ['#08845a', '#e07b24', '#c0392b'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function initOrderCharts() {
  // 出单情况分布图（正确规则）
  new Chart(document.getElementById('chartOrderDist'), {
    type: 'doughnut',
    data: {
      labels: ['8日内出单(Y)', '8日外出单(N)', '真正未出单'],
      datasets: [{ data: [''' + str(cd_8_sale) + ', ' + str(cd_8w_sale) + ', ' + str(cd_true_no) + '''], backgroundColor: ['#08845a', '#e07b24', '#c0392b'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });

  // 未出单原因分布图（真正未出单的SKU）
  new Chart(document.getElementById('chartUnorderDist'), {
    type: 'doughnut',
    data: {
      labels: ''' + YY_LAB_ARR + ''',
      datasets: [{ data: ''' + YY_VAL_ARR + ''', backgroundColor: ['#c0392b', '#2980b9', '#27ae60', '#e07b24'], borderWidth: 2 }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function buildLowShareTable() {
  const tbody = document.getElementById('lowShareTableBody');
  lowShareData.forEach((r, i) => {
    const mzb = parseFloat(r[8]) || 0;
    const mzbClass = mzb < 25 ? 'hb-down' : mzb < 50 ? 'hb-up' : 'hb-flat';
    const order = r[10];
    const badge = order === 'Y' ? '<span class="badge badge-y">Y</span>' : order === 'N' ? '<span class="badge badge-n">N</span>' : '<span class="badge badge-un">未出单</span>';
    tbody.innerHTML += '<tr>' +
      '<td>' + (i+1) + '</td>' +
      '<td style="text-align:left">' + r[1] + '</td>' +
      '<td>' + r[2] + '</td>' +
      '<td>' + r[3] + '</td>' +
      '<td>' + r[4] + '</td>' +
      '<td>' + r[5] + '</td>' +
      '<td>' + r[6] + '</td>' +
      '<td>' + r[7] + '</td>' +
      '<td>' + r[8] + '</td>' +
      '<td><span class="' + mzbClass + '">' + r[9] + '%</span></td>' +
      '<td>' + badge + '</td>' +
      '<td>' + r[11] + '</td>' +
      '<td>' + r[12] + '</td>' +
      '<td>' + r[13] + '</td>' +
      '</tr>';
  });
}
</script>
</body>
</html>'''

lines.append(JS_SCRIPT)

content = '\n'.join(lines)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!', DST)
print('Size:', len(content), 'bytes')
