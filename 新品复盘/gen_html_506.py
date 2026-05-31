#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 sheets_506.json 生成带图表的HTML可视化报告"""

import json, os

with open('sheets_506.json', 'r', encoding='utf-8') as f:
    S = json.load(f)  # S = sheets

# ========== 工具函数 ==========
def safe(v, default=0):
    """把 Excel 读出来的 None/空 转成可用值"""
    if v is None or v == '':
        return default
    return v

def num(v, default=0):
    """强转数字"""
    try:
        return float(str(v).replace('%','').replace(',',''))
    except:
        return default

def row_has(row, *texts):
    """row[0] 是否等于其中某个字符串"""
    v = str(row[0]).strip() if row and row[0] else ''
    return v in texts

# ========== 读取各 Sheet 有效数据 ==========

# 1. 总体概况
z = {}
for row in S['总体数据']:
    k = str(row[0]).strip() if row and row[0] else ''
    if '累计SKU' in k:  z['sku']=safe(row[1]); z['sku_prev']=safe(row[2])
    if '新上架'   in k:  z['new']=safe(row[1])
    if '总销量'  in k and '售额' not in k: z['sq']=safe(row[1]); z['sq_prev']=safe(row[2])
    if '总销售额' in k:  z['sa']=safe(row[1]); z['sa_prev']=safe(row[2])
    if '低占比'   in k:  z['low']=safe(row[1])
    if '有对手SKU' in k and '数' not in k: z['rival']=safe(row[1]); z['rival_prev']=safe(row[2])

# 2. 品线维度
px_labels=[]; px_sq=[]; px_sq_p=[]; px_sa=[]; px_sa_p=[]; px_rows=[]
for row in S['品线维度']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v in ('品线维度汇总 - 4.30-5.6','品线','合计'): continue
    px_labels.append(v)
    px_sq.append(safe(row[3]));  px_sq_p.append(safe(row[4]))
    px_sa.append(safe(row[6])); px_sa_p.append(safe(row[7]))
    px_rows.append(row)

# 3. 分析人维度
an_labels=[]; an_sq=[]; an_sq_p=[]; an_sa=[]; an_sa_p=[]; an_rows=[]
for row in S['分析人维度']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v in ('分析人维度汇总 - 4.30-5.6','分析人','合计'): continue
    an_labels.append(v)
    an_sq.append(safe(row[3]));  an_sq_p.append(safe(row[4]))
    an_sa.append(safe(row[6]));  an_sa_p.append(safe(row[7]))
    an_rows.append(row)

# 4. 拓展类型
tz_labels=[]; tz_rate=[]; tz_rate_p=[]; tz_sq=[]; tz_sq_p=[]; tz_rows=[]
for row in S['拓展类型']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v in ('拓展类型维度汇总 - 4.30-5.6','拓展类型','合计'): continue
    tz_labels.append(v)
    tz_rate.append(num(row[4]));  tz_rate_p.append(num(row[6]))
    tz_sq.append(safe(row[8]));   tz_sq_p.append(safe(row[9]))
    tz_rows.append(row)

# 5. 分析及时率
tl_labels=[]; tl_ok=[]; tl_8=[]; tl_7=[]; tl_rate=[]; tl_rows=[]
for row in S['分析及时率']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v in ('分析及时率汇总 - 4.30-5.6','分析人','合计'): continue
    tl_labels.append(v)
    tl_ok.append(safe(row[2])); tl_8.append(safe(row[3])); tl_7.append(safe(row[4]))
    tl_rate.append(num(row[5]))
    tl_rows.append(row)

# 6. 低占比新品
low_rows = [r for r in S['低占比新品'][2:] if r and r[0]]

# 7. 新品PLP
plp_total = None
plp_an_names=[]; plp_an_roas=[]; plp_an_roas_p=[]
plp_px_labels=[]; plp_px_roas=[]; plp_px_roas_p=[]
for row in S['新品PLP']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v == '总计':
        plp_total = row
    if v in an_labels:
        plp_an_names.append(v)
        plp_an_roas.append(num(row[8]))
        plp_an_roas_p.append(num(row[21]) if len(row)>21 else 0)

# 8. 新品出单情况
ch_labels=[]; ch_this=[]; ch_last=[]; ch_rows=[]
for row in S['新品出单情况']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v in ('新品出单情况汇总 - 4.30-5.6（有对手口径）',
             '【总体出单情况】','【拓展类型出单】','指标',
             '-- 8日外 --','-- 8日内 --','#N/A'):
        continue
    if row[1] != '':
        ch_labels.append(v)
        ch_this.append(safe(row[1]))
        ch_last.append(safe(row[2]))
        ch_rows.append(row)

# 9. 新品未出单原因
rs_labels=[]; rs_counts=[]; rs_rows=[]
for row in S['新品未出单原因']:
    if not row or not row[0]: continue
    v = str(row[0]).strip()
    if v in ('新品未出单原因分析 - 4.30-5.6',
             '【未出单原因分布（全部有对手SKU）','市场状态',
             '#N/A','未知'):
        continue
    if row[1] != '' and num(row[1]) > 0:
        rs_labels.append(v)
        rs_counts.append(safe(row[1]))
        rs_rows.append(row)

# 10. PLG维度
plg_rows = [r for r in S['新品PLG维度'][3:] if r and r[0]]


# ========== 高亮判断 ==========
def low_cls(r):
    plp = r[15] if len(r)>15 else ''
    plg = str(r[16]) if len(r)>16 and r[16]!='' else ''
    chd = r[11] if len(r)>11 else ''
    if plp == 'Y' and plg.replace('%','') not in ('0','','0%'):
        try:
            if float(plg.replace('%',''))>0: return 'highlight-orange'
        except: pass
    if plp == 'N' and chd == '未出单': return 'highlight-pink'
    if plp == 'N' and plg.replace('%','') not in ('0','','0%'):
        try:
            if float(plg.replace('%',''))>0: return 'highlight-green'
        except: pass
    return ''

def plg_cls(r):
    plp = r[14] if len(r)>14 else ''
    plg = str(r[15]) if len(r)>15 and r[15]!='' else ''
    chd = r[7]  if len(r)>7  else ''
    if plp == 'Y' and plg.replace('%','') not in ('0','','0%'):
        try:
            if float(plg.replace('%',''))>0: return 'highlight-orange'
        except: pass
    if plp == 'N' and chd == '未出单': return 'highlight-pink'
    if plp == 'N' and plg.replace('%','') not in ('0','','0%'):
        try:
            if float(plg.replace('%',''))>0: return 'highlight-green'
        except: pass
    return ''


# ========== 构建 HTML ==========
CSS = '''
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI','Microsoft YaHei',sans-serif; background:#f5f0fa; color:#333; }
.sidebar { position:fixed; left:0; top:0; width:200px; height:100vh; background:linear-gradient(180deg,#4A148C,#7B1FA2); color:#fff; padding:20px 0; overflow-y:auto; z-index:100; }
.sidebar h2 { text-align:center; font-size:14px; padding:0 10px 15px; border-bottom:1px solid rgba(255,255,255,0.2); margin-bottom:10px; line-height:1.6; }
.sidebar a { display:block; color:rgba(255,255,255,0.85); text-decoration:none; padding:9px 16px; font-size:13px; transition:0.2s; }
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
'''

def make_table(headers, rows, cls_fn=None):
    """生成 HTML table，cls_fn(row) 返回 tr 的 class"""
    th = ''.join(f'<th>{h}</th>' for h in headers)
    tb = f'<table><thead><tr>{th}</tr></thead><tbody>'
    for row in rows:
        cls = cls_fn(row) if cls_fn else ''
        c = ''.join(f'<td>{c}</td>' for c in row)
        tb += f'<tr class="{cls}">{c}</tr>'
    tb += '</tbody></table>'
    return tb

# -- sections --
sec0 = f'''
<div class="section active" id="sec0">
  <h2>📈 总体概况（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>累计SKU数</h3><div class="val" id="kSku"></div><div class="mom" id="kSkuP"></div></div>
    <div class="kpi-card alt"><h3>总销量</h3><div class="val" id="kSq"></div><div class="mom" id="kSqP"></div></div>
    <div class="kpi-card"><h3>总销售额(USD)</h3><div class="val" id="kSa"></div><div class="mom" id="kSaP"></div></div>
  </div>
  <div class="chart-box"><h3>核心指标：本周 vs 上周</h3><canvas id="cOverview"></canvas></div>
</div>
'''

sec1 = f'''
<div class="section" id="sec1">
  <h2>📊 品线维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各品线销量对比</h3><canvas id="cPxSales"></canvas></div>
  <div class="chart-box"><h3>各品线销售额对比（USD）</h3><canvas id="cPxAmt"></canvas></div>
  <h3>品线明细</h3>
  {make_table(['品线','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比','本周有对手'], px_rows)}
</div>
'''

sec2 = f'''
<div class="section" id="sec2">
  <h2>👤 分析人维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各分析人销量对比</h3><canvas id="cAnSales"></canvas></div>
  <div class="chart-box"><h3>各分析人销售额对比（USD）</h3><canvas id="cAnAmt"></canvas></div>
  <h3>分析人明细</h3>
  {make_table(['分析人','本周SKU','新上架','本周销量','上周销量','销量环比','本周销售额','上周销售额','销售额环比'], an_rows)}
</div>
'''

sec3 = f'''
<div class="section" id="sec3">
  <h2>🔄 拓展类型维度（4.30-5.6）</h2>
  <div class="chart-box"><h3>各类型出单率（%）</h3><canvas id="cTzRate"></canvas></div>
  <div class="chart-box"><h3>各类型销量对比</h3><canvas id="cTzSales"></canvas></div>
  <h3>拓展类型明细</h3>
  {make_table(['拓展类型','本周SKU','本周出单','出单率','上周出单率','本周销量','上周销量','本周销售额','上周销售额'], tz_rows)}
</div>
'''

sec4 = f'''
<div class="section" id="sec4">
  <h2>⏱ 分析及时率（截止5.6）</h2>
  <div class="chart-box"><h3>各分析人及时分析情况（SKU数）</h3><canvas id="cTlStack"></canvas></div>
  <div class="chart-box"><h3>各分析人及时率（%）</h3><canvas id="cTlRate"></canvas></div>
  <h3>分析及时率明细</h3>
  {make_table(['分析人','截止5.6SKU','及时分析','8日内无分析','超7日未分析','及时率','上周及时率','变化'], tl_rows)}
</div>
'''

sec5 = f'''
<div class="section" id="sec5">
  <h2>⚠ 低占比新品明细（共{len(low_rows)}条）</h2>
  {make_table(['编号','SKU','上架日期','分析人','品类','拓展类型','销量','销量环比','销售额','销售额环比','对手销量','市占比','市占比环比','8日出单','7日频次','市场状态','操作判断','市场状态2','开启PLP','PLG费率'], low_rows, low_cls)}
</div>
'''

# PLP KPI
plp_act=42; plp_link=53; plp_imp=119686; plp_roas=6.44
sec6 = f'''
<div class="section" id="sec6">
  <h2>📢 新品PLP数据（4.30-5.6）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>广告活动数</h3><div class="val">{plp_act}</div><div class="mom">上周：47</div></div>
    <div class="kpi-card alt"><h3>广告链接数</h3><div class="val">{plp_link}</div><div class="mom">上周：63</div></div>
    <div class="kpi-card"><h3>曝光量</h3><div class="val">{plp_imp:,}</div></div>
    <div class="kpi-card alt"><h3>ROAS</h3><div class="val">{plp_roas}x</div><div class="mom">上周：14.16x</div></div>
  </div>
  <div class="chart-box"><h3>PLP总数据：本周 vs 上周</h3><canvas id="cPlpTotal"></canvas></div>
  <div class="chart-box"><h3>各分析人ROAS对比</h3><canvas id="cPlpAnalyst"></canvas></div>
  <h3>PLP总数据明细</h3>
  <table><thead><tr><th>维度</th><th>广告活动</th><th>链接</th><th>曝光量</th><th>点击量</th><th>售出数</th><th>花费</th><th>销售额</th><th>ROAS</th><th>CVR%</th><th>CTR%</th><th>CPC</th><th>CPA</th><th>ACOS%</th></tr></thead><tbody>
  <tr>{''.join(f'<td>{c}</td>' for c in (plp_total[1:15] if plp_total else []))}</tr>
  </tbody></table>
</div>
'''

ch_y=27; ch_n=13
sec7 = f'''
<div class="section" id="sec7">
  <h2>📋 新品出单情况（有对手口径）</h2>
  <div class="kpi-row">
    <div class="kpi-card"><h3>有对手总SKU</h3><div class="val">43</div><div class="mom">上周：32（+11）</div></div>
    <div class="kpi-card alt"><h3>有销量SKU</h3><div class="val">{ch_y}</div><div class="mom">上周：21（+6）</div></div>
    <div class="kpi-card"><h3>出单率</h3><div class="val">62.8%</div></div>
  </div>
  <div class="chart-box"><h3>有对手SKU出单分布</h3><canvas id="cChPie"></canvas></div>
  <div class="chart-box"><h3>各指标本周 vs 上周</h3><canvas id="cChBar"></canvas></div>
  <h3>出单情况明细</h3>
  {make_table(['指标','本周','上周','变化'], ch_rows)}
</div>
'''

sec8 = f'''
<div class="section" id="sec8">
  <h2>🔍 新品未出单原因分析</h2>
  <div class="chart-box"><h3>未出单原因分布</h3><canvas id="cRsPie"></canvas></div>
  <h3>未出单原因明细</h3>
  {make_table(['市场状态','SKU数量','占比','上周数量','上周占比','变化'], rs_rows)}
</div>
'''

sec9 = f'''
<div class="section" id="sec9">
  <h2>🎯 新品PLG维度明细（共{len(plg_rows)}条）</h2>
  <p style="color:#666;font-size:13px;margin-bottom:12px;">
    ● <span style="background:#FFE0B2;padding:2px 8px;border-radius:3px">橙色</span> PLP=Y 且 PLG费率&gt;0% &nbsp;&nbsp;
    ● <span style="background:#FCE4EC;padding:2px 8px;border-radius:3px">粉红</span> PLP=N 且 8日出单=未出单 &nbsp;&nbsp;
    ● <span style="background:#E8F5E9;padding:2px 8px;border-radius:3px">绿色</span> PLP=N 且 PLG费率&gt;0%
  </p>
  {make_table(['编号','SKU','上架日期','首次出单','分析人','品类','拓展类型','8日出单','销量','销售额','对手销量','市占比','市场状态','操作判断','开启PLP','PLG费率'], plg_rows, plg_cls)}
</div>
'''

# sidebar
nav = '<div class="sidebar"><h2>📊 新品周报<br/>4.30-5.6</h2>'
tabs = [('📈 总体概况','sec0'),('📊 品线维度','sec1'),('👤 分析人维度','sec2'),
        ('🔄 拓展类型','sec3'),('⏱ 分析及时率','sec4'),('⚠ 低占比新品','sec5'),
        ('📢 新品PLP','sec6'),('📋 新品出单情况','sec7'),('🔍 未出单原因','sec8'),('🎯 新品PLG维度','sec9')]
for label,sid in tabs:
    cls = ' class="active"' if sid=='sec0' else ''
    nav += f'<a href="#" id="nav_{sid}"{cls} onclick="showSec(\'{sid}\',this)">{label}</a>'
nav += '</div>'

main = '<div class="main">' + sec0+sec1+sec2+sec3+sec4+sec5+sec6+sec7+sec8+sec9 + '</div>'


# ========== JS 数据 + 图表代码 ==========
def j(v):
    return json.dumps(v, ensure_ascii=False)

JS = '''
function showSec(id,el){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.sidebar a').forEach(a=>a.classList.remove('active'));
  if(el) el.classList.add('active');
}
// KPI
document.getElementById('kSku').textContent = SKU;
document.getElementById('kSkuP').textContent = '上周：'+SKU_PREV;
document.getElementById('kSq').textContent = SQ;
document.getElementById('kSqP').textContent = '上周：'+SQ_PREV+'（环比+29.1%）';
document.getElementById('kSa').textContent = '$'+SA.toLocaleString('en',{minimumFractionDigits:2});
document.getElementById('kSaP').textContent = '上周：$'+SA_PREV.toLocaleString('en',{minimumFractionDigits:2})+'(环比+15.9%）';

const P = ['#7B1FA2','#BA68C8','#AB47BC','#CE93D8','#E1BEE7','#4A148C','#FFD54F','#FF8A65','#4FC3F7'];
Chart.defaults.font.family = "'Segoe UI','Microsoft YaHei',sans-serif";
Chart.defaults.color = '#333';

// Overview
new Chart(document.getElementById('cOverview'),{type:'bar',data:{labels:['累计SKU','总销量','销售额(/100)'],datasets:[{label:'4.30-5.6',data:[SKU,SQ,SA/100],backgroundColor:P[0]},{label:'4.23-4.29',data:[SKU_PREV,SQ_PREV,SA_PREV/100],backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});

// 品线销量
new Chart(document.getElementById('cPxSales'),{type:'bar',data:{labels:PX_LAB,datasets:[{label:'本周销量',data:PX_SQ,backgroundColor:P[0]},{label:'上周销量',data:PX_SQ_P,backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});
// 品线销售额
new Chart(document.getElementById('cPxAmt'),{type:'bar',data:{labels:PX_LAB,datasets:[{label:'本周销售额',data:PX_SA,backgroundColor:P[2]},{label:'上周销售额',data:PX_SA_P,backgroundColor:P[3]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});

// 分析人销量
new Chart(document.getElementById('cAnSales'),{type:'bar',data:{labels:AN_LAB,datasets:[{label:'本周销量',data:AN_SQ,backgroundColor:P[0]},{label:'上周销量',data:AN_SQ_P,backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});
// 分析人销售额
new Chart(document.getElementById('cAnAmt'),{type:'bar',data:{labels:AN_LAB,datasets:[{label:'本周销售额',data:AN_SA,backgroundColor:P[2]},{label:'上周销售额',data:AN_SA_P,backgroundColor:P[3]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});

// 拓展类型出单率
new Chart(document.getElementById('cTzRate'),{type:'bar',data:{labels:TZ_LAB,datasets:[{label:'本周出单率(%)',data:TZ_RATE,backgroundColor:P[0]},{label:'上周出单率(%)',data:TZ_RATE_P,backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true,max:100}}}});
// 拓展类型销量
new Chart(document.getElementById('cTzSales'),{type:'bar',data:{labels:TZ_LAB,datasets:[{label:'本周销量',data:TZ_SQ,backgroundColor:P[2]},{label:'上周销量',data:TZ_SQ_P,backgroundColor:P[3]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});

// 及时率堆叠
new Chart(document.getElementById('cTlStack'),{type:'bar',data:{labels:TL_LAB,datasets:[{label:'及时分析',data:TL_OK,backgroundColor:P[0],stack:'a'},{label:'8日内无分析',data:TL_8,backgroundColor:'#FFD54F',stack:'a'},{label:'超7日未分析',data:TL_7,backgroundColor:'#E53935',stack:'a'}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{stacked:true,beginAtZero:true}}}});
// 及时率%
new Chart(document.getElementById('cTlRate'),{type:'bar',data:{labels:TL_LAB,datasets:[{label:'及时率(%)',data:TL_RATE,backgroundColor:P.slice(0,TL_LAB.length)}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100}}}});

// PLP总数据
new Chart(document.getElementById('cPlpTotal'),{type:'bar',data:{labels:['广告活动','链接','曝光量(/1000)','点击量','售出数','ROAS','CVR%','ACOS%'],datasets:[{label:'4.30-5.6',data:[42,53,119686/1000,429,27,6.44,6.29,15.54],backgroundColor:P[0]},{label:'4.23-4.29',data:[47,63,139169/1000,425,40,14.16,9.41,7.06],backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});
// PLP分析人ROAS
new Chart(document.getElementById('cPlpAnalyst'),{type:'bar',data:{labels:PLP_AN_LAB,datasets:[{label:'本周ROAS',data:PLP_AN_ROAS,backgroundColor:P[0]},{label:'上周ROAS',data:PLP_AN_ROAS_P,backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});

// 出单饼图
new Chart(document.getElementById('cChPie'),{type:'doughnut',data:{labels:['有销量SKU(27)','未出单SKU(13)','其他(3)'],datasets:[{data:[27,13,3],backgroundColor:[P[0],'#E53935','#FFD54F']}]},options:{responsive:true,plugins:{legend:{position:'right'}}}}});
// 出单柱状图
new Chart(document.getElementById('cChBar'),{type:'bar',data:{labels:CH_LAB,datasets:[{label:'本周',data:CH_THIS,backgroundColor:P[0]},{label:'上周',data:CH_LAST,backgroundColor:P[1]}]},options:{responsive:true,plugins:{legend:{position:'top'}},scales:{y:{beginAtZero:true}}}});

// 未出单原因饼图
new Chart(document.getElementById('cRsPie'),{type:'pie',data:{labels:RS_LAB,datasets:[{data:RS_CNT,backgroundColor:P.slice(0,RS_LAB.length)}]},options:{responsive:true,plugins:{legend:{position:'right'}}}});
'''

# 把 Python 变量注入 JS（放在 <script> 最前面）
js_vars = f'''
const SKU={j(z.get('sku',101))}, SKU_PREV={j(z.get('sku_prev',90))};
const SQ={j(z.get('sq',195))}, SQ_PREV={j(z.get('sq_prev',151))};
const SA={j(z.get('sa',20494.85))}, SA_PREV={j(z.get('sa_prev',17671.42))};
const PX_LAB={j(px_labels)}; const PX_SQ={j(px_sq)}; const PX_SQ_P={j(px_sq_p)};
const PX_SA={j(px_sa)}; const PX_SA_P={j(px_sa_p)};
const AN_LAB={j(an_labels)}; const AN_SQ={j(an_sq)}; const AN_SQ_P={j(an_sq_p)};
const AN_SA={j(an_sa)}; const AN_SA_P={j(an_sa_p)};
const TZ_LAB={j(tz_labels)}; const TZ_RATE={j(tz_rate)}; const TZ_RATE_P={j(tz_rate_p)};
const TZ_SQ={j(tz_sq)}; const TZ_SQ_P={j(tz_sq_p)};
const TL_LAB={j(tl_labels)}; const TL_OK={j(tl_ok)}; const TL_8={j(tl_8)};
const TL_7={j(tl_7)}; const TL_RATE={j(tl_rate)};
const PLP_AN_LAB={j(plp_an_names)}; const PLP_AN_ROAS={j(plp_an_roas)}; const PLP_AN_ROAS_P={j(plp_an_roas_p)};
const CH_LAB={j(ch_labels)}; const CH_THIS={j(ch_this)}; const CH_LAST={j(ch_last)};
const RS_LAB={j(rs_labels)}; const RS_CNT={j(rs_counts)};
'''

# ========== 写出 HTML ==========
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报可视化报告 - 4.30-5.6</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>''' + CSS + '''</style>
</head>
<body>
<button class="nav-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>
''' + nav + main + '''
<script>''' + js_vars + JS + '''</script>
</body>
</html>'''

with open('新品周报_4.30-5.6_可视化.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ 生成完毕：新品周报_4.30-5.6_可视化.html')
print(f'  总体概况: SKU={z.get("sku")}, 销量={z.get("sq")}, 销售额={z.get("sa")}')
print(f'  品线维度: {len(px_rows)} 行')
print(f'  低占比新品: {len(low_rows)} 行')
print(f'  PLG维度: {len(plg_rows)} 行')
