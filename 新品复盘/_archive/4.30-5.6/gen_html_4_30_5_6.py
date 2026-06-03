"""
根据 report_data_4_30_5_6.json 生成新品周报 HTML
"""
import json, datetime

with open(r'c:\Users\Hardy\ai-projects\新品复盘\report_data_4_30_5_6.json', 'r', encoding='utf-8') as f:
    D = json.load(f)

P = D['periods']
K = D['kpi']
cats = D['cats']
analysts = D['analysts']
exps = D['exps']

def hb_cls(v, is_pct=False):
    """环比样式"""
    if v > 0: return 'hb-up' if not is_pct else 'hb-up'
    if v < 0: return 'hb-down'
    return 'hb-flat'

def hb_sign(v, is_pct=False):
    if v is None or v == 0: return '持平' if v == 0 else '-'
    s = '+' if v > 0 else ''
    if is_pct: return f'{s}{v:.1f}%'
    return f'{s}{v:.0f}'

def fmt_usd(v):
    return f'${v:,.0f}' if v >= 1000 else f'${v:.2f}'

# ── 构建品类明细表HTML ──────────────────────────────────
cat_rows_html = ''
for cat in cats:
    d = D['cat_data'][cat]
    q_chg = d['qtys'][-1] - d['qtys'][-2]
    r_chg = d['rates'][-1] - d['rates'][-2]
    cat_rows_html += f'''<tr>
      <td><b>{cat}</b></td><td>{d['skus']}</td>
      <td>{d['qtys'][0]:.0f}</td><td>{fmt_usd(d['amts'][0])}</td><td>{d['rates'][0]}%</td>
      <td>{d['qtys'][1]:.0f}</td><td>{fmt_usd(d['amts'][1])}</td><td>{d['rates'][1]}%</td>
      <td>{d['qtys'][2]:.0f}</td><td>{fmt_usd(d['amts'][2])}</td><td>{d['rates'][2]}%</td>
      <td>{d['qtys'][3]:.0f}</td><td>{fmt_usd(d['amts'][3])}</td><td>{d['rates'][3]}%</td>
      <td><span class="{hb_cls(q_chg)}">{hb_sign(q_chg)}</span></td>
      <td><span class="{hb_cls(r_chg, True)}">{hb_sign(r_chg, True)}</span></td>
    </tr>'''

# 品类合计行
total_qty_sum = [sum(D['cat_data'][c]['qtys'][i] for c in cats) for i in range(4)]
total_amt_sum = [sum(D['cat_data'][c]['amts'][i] if i == 3 else D['cat_data'][c]['amts'][0 if i == 0 else (0 if 'amts' not in D['cat_data'][c] else i)] for c in cats) for i in range(4)]
total_qty_4p = [sum(D['cat_data'][c]['qtys'][i] for c in cats) for i in range(4)]
total_amt_4p = [round(sum(D['cat_data'][c]['amts'][i] for c in cats), 2) for i in range(4)]
total_qty_chg = total_qty_4p[-1] - total_qty_4p[-2]
total_rate_per_p = []
for i in range(4):
    total_y = sum(D['cat_data'][c]['rates'][i] * D['cat_data'][c]['skus'] / 100 for c in cats)
    total_rate_per_p.append(round(total_y / K['total_skus'] * 100, 1) if K['total_skus'] else 0)
total_rate_chg = total_rate_per_p[-1] - total_rate_per_p[-2]

cat_total_row = f'''<tr style="background:#f5f5f5; font-weight:700;">
  <td><b>合计</b></td><td>{K['total_skus']}</td>
  <td>{total_qty_4p[0]:.0f}</td><td>-</td><td>{total_rate_per_p[0]}%</td>
  <td>{total_qty_4p[1]:.0f}</td><td>-</td><td>{total_rate_per_p[1]}%</td>
  <td>{total_qty_4p[2]:.0f}</td><td>-</td><td>{total_rate_per_p[2]}%</td>
  <td>{total_qty_4p[3]:.0f}</td><td>-</td><td>{total_rate_per_p[3]}%</td>
  <td><span class="{hb_cls(total_qty_chg)}">{hb_sign(total_qty_chg)}</span></td>
  <td><span class="{hb_cls(total_rate_chg, True)}">{hb_sign(total_rate_chg, True)}</span></td>
</tr>'''

# ── 构建分析人明细表HTML ────────────────────────────────
ana_rows_html = ''
for ana in analysts:
    d = D['ana_data'][ana]
    q_chg = d['qtys'][-1] - d['qtys'][-2]
    r_chg = d['rates'][-1] - d['rates'][-2]
    # Y counts per period
    y_vals = [round(d['rates'][i] * d['skus'] / 100) for i in range(4)]
    ana_rows_html += f'''<tr>
      <td><b>{ana}</b></td><td>{d['skus']}</td>
      <td>{d['qtys'][0]:.0f}</td><td>{y_vals[0]}</td><td>{d['rates'][0]}%</td>
      <td>{d['qtys'][1]:.0f}</td><td>{y_vals[1]}</td><td>{d['rates'][1]}%</td>
      <td>{d['qtys'][2]:.0f}</td><td>{y_vals[2]}</td><td>{d['rates'][2]}%</td>
      <td>{d['qtys'][3]:.0f}</td><td>{y_vals[3]}</td><td>{d['rates'][3]}%</td>
      <td><span class="{hb_cls(q_chg)}">{hb_sign(q_chg)}</span></td>
      <td><span class="{hb_cls(r_chg, True)}">{hb_sign(r_chg, True)}</span></td>
    </tr>'''

# ── 构建拓展类型明细表HTML ──────────────────────────────
exp_rows_html = ''
for exp in exps:
    d = D['exp_data'][exp]
    if d['skus'] == 0: continue
    q_chg = d['qtys'][-1] - d['qtys'][-2]
    r_chg = d['rates'][-1] - d['rates'][-2]
    exp_rows_html += f'''<tr>
      <td><b>{exp}</b></td><td>{d['skus']}</td>
      <td>{d['qtys'][0]:.0f}</td><td>{d['rates'][0]}%</td>
      <td>{d['qtys'][1]:.0f}</td><td>{d['rates'][1]}%</td>
      <td>{d['qtys'][2]:.0f}</td><td>{d['rates'][2]}%</td>
      <td>{d['qtys'][3]:.0f}</td><td>{d['rates'][3]}%</td>
      <td><span class="{hb_cls(q_chg)}">{hb_sign(q_chg)}</span></td>
      <td><span class="{hb_cls(r_chg, True)}">{hb_sign(r_chg, True)}</span></td>
    </tr>'''

# ── 构建低占比新品表格HTML ──────────────────────────────
low_rows_html = ''
for r in D['low_share_rows']:
    mzb_str = r[9]
    try:
        mzb_val = float(str(mzb_str).replace('%',''))
        clr = '#c0392b' if mzb_val < 25 else ('#e07b24' if mzb_val < 50 else '#888')
    except: clr = '#888'
    low_rows_html += f'''<tr>
      <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td>
      <td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td>
      <td>{r[7]}</td><td>{r[8]}</td>
      <td style="color:{clr};font-weight:700;">{mzb_str}</td>
      <td>{r[10]}</td><td>{r[11]}</td><td>{r[12]}</td>
    </tr>'''

# ── PLP表格行 ────────────────────────────────────────────
def plp_table_rows(data_dict):
    html = ''
    for k, d in data_dict.items():
        html += f'''<tr>
          <td><b>{k}</b></td><td>{d.get('skus', '-')}</td>
          <td>{d['imp']:,}</td><td>{d['clk']:,}</td><td>{d['ord']}</td>
          <td>${d['spend']}</td><td>${d['sales']}</td>
          <td>{d['roas']}</td><td>{d['cvr']}%</td><td>{d['ctr']:.2f}%</td><td>{d['acos']}%</td>
        </tr>'''
    return html

# ── PLG费率行 ────────────────────────────────────────────
def plg_table_rows(data_dict):
    html = ''
    for k, d in data_dict.items():
        html += f'''<tr>
          <td><b>{k}</b></td><td>{d['count']}</td><td>{d['avg']}%</td><td>{d['max']}%</td>
        </tr>'''
    return html

# ── 分析及时率表格 ──────────────────────────────────────
timely_labels = ['及时分析', '超7日未分析', '8日内新品无分析']
timely_rows_html = ''
for i, lbl in enumerate(timely_labels):
    vals = [D['timely_in'][i], D['timely_over7'][i], D['timely_new'][i]]
    timely_data = [D['timely_in'], D['timely_over7'], D['timely_new']]
    v0, v1, v2, v3 = timely_data[i]
    chg = v3 - v2
    timely_rows_html += f'''<tr>
      <td><b>{lbl}</b></td>
      <td>{v0}</td><td>{v1}</td><td>{v2}</td><td>{v3}</td>
      <td><span class="{hb_cls(chg)}">{hb_sign(chg)}</span></td>
    </tr>'''

# ── 新品出单情况表格 ────────────────────────────────────
order_rows_html = ''
for lbl, vals in [('8日出单(Y)', D['order_y']), ('8日外出单(N)', D['order_n']), ('未出单', D['order_un'])]:
    chg = vals[-1] - vals[-2]
    order_rows_html += f'''<tr>
      <td><b>{lbl}</b></td>
      <td>{vals[0]}</td><td>{vals[1]}</td><td>{vals[2]}</td><td>{vals[3]}</td>
      <td><span class="{hb_cls(chg)}">{hb_sign(chg)}</span></td>
    </tr>'''

# ── 新品未出单表格 ──────────────────────────────────────
unorder_reasons = ['竞争无优势', '无市场', '站内无价格优势', '站外出单']
unorder_rows_html = ''
for rsn in unorder_reasons:
    vals = D['unorder_data'].get(rsn, [0,0,0,0])
    chg = vals[-1] - vals[-2]
    unorder_rows_html += f'''<tr>
      <td><b>{rsn}</b></td>
      <td>{vals[0]}</td><td>{vals[1]}</td><td>{vals[2]}</td><td>{vals[3]}</td>
      <td><span class="{hb_cls(chg)}">{hb_sign(chg)}</span></td>
    </tr>'''

# ── 品类出单率JSON (for JS charts) ──────────────────────
cat_rates_json = json.dumps({c: D['cat_data'][c]['rates'] for c in cats}, ensure_ascii=False)
cat_qtys_json = json.dumps({c: D['cat_data'][c]['qtys'] for c in cats}, ensure_ascii=False)
ana_rates_json = json.dumps({a: D['ana_data'][a]['rates'] for a in analysts}, ensure_ascii=False)
ana_qtys_json = json.dumps({a: D['ana_data'][a]['qtys'] for a in analysts}, ensure_ascii=False)
exp_rates_json = json.dumps({e: D['exp_data'][e]['rates'] for e in exps if D['exp_data'][e]['skus'] > 0}, ensure_ascii=False)
exp_qtys_json = json.dumps({e: D['exp_data'][e]['qtys'] for e in exps if D['exp_data'][e]['skus'] > 0}, ensure_ascii=False)

# ── KPI环比文本 ──────────────────────────────────────────
qty_hb_text = f'较上周 {hb_sign(K["qty_chg"])}' if K['qty_chg'] != 0 else '持平上周'
amt_hb_text = f'较上周 {hb_sign(K["amt_chg"])}' if K['amt_chg'] != 0 else '持平上周'
rate_all_chg = D['rate_all'][-1] - D['rate_all'][-2]
rate_hb_text = f'较上周 {hb_sign(rate_all_chg, True)}' if rate_all_chg != 0 else '持平上周'
rate_all_hb_cls = hb_cls(rate_all_chg, True)
rival_rate_hb_text = f'有对手出单率 {K["rate_new"]}%(环比{hb_sign(K["rate_chg"], True)})'
mzb_hb_text = f'较上周 {hb_sign(K["mzb_chg"], True)}' if K['mzb_chg'] != 0 else '持平上周'
y_hb_text = f'较上周 {hb_sign(K["y_all_new"] - K["y_all_prev"])}'
n_hb_text = f'较上周 {hb_sign(K["n_all_new"] - K["n_all_prev"])}'
un_hb_text = f'较上周 {hb_sign(K["un_all_new"] - K["un_all_prev"])}'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品周报 · 4.30-5.6</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 28px 40px; }}
.header h1 {{ font-size: 26px; font-weight: 700; letter-spacing: 2px; }}
.header .subtitle {{ font-size: 13px; opacity: 0.75; margin-top: 6px; }}
.container {{ display: flex; min-height: calc(100vh - 80px); }}
.sidebar {{ width: 230px; background: #fff; border-right: 1px solid #e8e8e8; padding: 20px 0; position: sticky; top: 0; height: 100vh; overflow-y: auto; flex-shrink: 0; }}
.sidebar ul {{ list-style: none; }}
.sidebar li a {{ display: block; padding: 10px 20px; font-size: 13px; color: #555; text-decoration: none; border-left: 3px solid transparent; transition: all 0.2s; cursor: pointer; }}
.sidebar li a:hover, .sidebar li a.active {{ background: #f0f6ff; color: #0f3460; border-left-color: #0f3460; font-weight: 600; }}
.main-content {{ flex: 1; padding: 24px; overflow: auto; }}
.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 14px; margin-bottom: 24px; }}
.kpi-card {{ background: white; border-radius: 10px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
.kpi-card .val {{ font-size: 26px; font-weight: 700; color: #0f3460; }}
.kpi-card .label {{ font-size: 12px; color: #888; margin-top: 6px; }}
.kpi-card .hb {{ font-size: 11px; margin-top: 4px; font-weight: 600; }}
.kpi-card.green .val {{ color: #08845a; }}
.kpi-card.orange .val {{ color: #e07b24; }}
.kpi-card.red .val {{ color: #c0392b; }}
.kpi-card.purple .val {{ color: #8e44ad; }}
.section {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.section h3 {{ font-size: 16px; font-weight: 700; color: #0f3460; padding-bottom: 12px; border-bottom: 2px solid #e8f0fe; margin-bottom: 16px; }}
.sub-module {{ margin-bottom: 20px; }}
.sub-module h4 {{ font-size: 13px; font-weight: 600; color: #444; margin-bottom: 10px; padding: 6px 12px; background: #f5f7ff; border-radius: 4px; border-left: 3px solid #0f3460; }}
.chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }}
.chart-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.chart-card h4 {{ font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 14px; }}
.chart-card canvas {{ max-height: 260px; }}
.chart-card-wide {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); grid-column: 1 / -1; }}
.chart-card-wide h4 {{ font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 14px; }}
.chart-card-wide canvas {{ max-height: 300px; }}
.table-wrap {{ overflow-x: auto; }}
.data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.data-table th {{ background: #0f3460; color: white; padding: 8px 8px; text-align: center; white-space: nowrap; font-weight: 600; }}
.data-table th.p1 {{ background: #6c757d; }}
.data-table th.p2 {{ background: #667eea; }}
.data-table th.p3 {{ background: #2980b9; }}
.data-table th.p4 {{ background: #c0392b; }}
.data-table th.hb {{ background: #e07b24; }}
.data-table td {{ padding: 6px 8px; text-align: center; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }}
.data-table tr:hover td {{ background: #f5f7ff; }}
.hb-up {{ color: #c0392b; font-weight: 700; }}
.hb-down {{ color: #08845a; font-weight: 700; }}
.hb-flat {{ color: #888; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: white; font-weight: 600; }}
.badge-y {{ background: #08845a; }}
.badge-n {{ background: #e07b24; }}
.badge-un {{ background: #c0392b; }}
select {{ padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; font-size: 13px; background: white; cursor: pointer; }}
select:focus {{ outline: none; border-color: #0f3460; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #f1f1f1; }}
::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 3px; }}
@media (max-width: 900px) {{ .sidebar {{ display: none; }} .chart-grid {{ grid-template-columns: 1fr; }} .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
.section-wrap {{ display: block; }}
.note {{ font-size: 12px; color: #888; margin-bottom: 10px; }}
.plp-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px; }}
.plp-card {{ background: white; border-radius: 10px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #8e44ad; }}
.plp-card h4 {{ font-size: 13px; font-weight: 600; color: #0f3460; margin-bottom: 12px; }}
.plp-metric {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #f0f0f0; font-size: 12px; }}
.plp-metric:last-child {{ border-bottom: none; }}
.plp-metric .lbl {{ color: #666; }}
.plp-metric .val {{ font-weight: 600; color: #1a1a2e; }}
.plp-highlight {{ background: #f5f0ff; border-radius: 6px; padding: 10px; margin-top: 10px; }}
.plp-highlight .val {{ color: #8e44ad; font-weight: 700; }}
</style>
</head>
<body>

<div class="header">
  <h1>&#x1F4CA; 新品周报 &middot; 4.30-5.6</h1>
  <div class="subtitle">统计周期：2026年4月30日 - 5月6日 &nbsp;|&nbsp; 在跟SKU：{K['total_skus']} &nbsp;|&nbsp; 环比近三个周期：4.9-4.15 / 4.16-4.22 / 4.23-4.29 &nbsp;|&nbsp; 生成：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>

<div class="container">
<nav class="sidebar">
  <ul>
    <li><a onclick="showSection('overview',this)" class="active">&#x1F4CA; 数据总览</a></li>
    <li><a onclick="showSection('pinxian',this)">&#x1F3F7;&#xFE0F; 品线维度</a></li>
    <li><a onclick="showSection('analyst',this)">&#x1F464; 分析人维度</a></li>
    <li><a onclick="showSection('expand',this)">&#x1F516; 拓展类型</a></li>
    <li><a onclick="showSection('timely',this)">&#x23F1;&#xFE0F; 分析及时率</a></li>
    <li><a onclick="showSection('order',this)">&#x1F4E6; 新品出单情况</a></li>
    <li><a onclick="showSection('unorder',this)">&#x274C; 新品未出单</a></li>
    <li><a onclick="showSection('lowshare',this)">&#x1F4C9; 低占比新品</a></li>
    <li><a onclick="showSection('plp',this)">&#x1F4B0; PLP复盘</a></li>
  </ul>
</nav>

<div class="main-content">

<!-- KPI总览 -->
<div class="kpi-grid">
  <div class="kpi-card"><div class="val">{K['total_skus']}</div><div class="label">在跟SKU总数</div><div class="hb" style="color:#888">原开品{D['exp_data']['原开品']['skus']} · 拓展品{D['exp_data']['拓展品']['skus']} · 组合件{D['exp_data']['组合件']['skus']}</div></div>
  <div class="kpi-card green"><div class="val">{K['y_all_new']}</div><div class="label">5.6已出单(Y)</div><div class="hb {hb_cls(K["y_all_new"]-K["y_all_prev"])}">{y_hb_text}</div></div>
  <div class="kpi-card orange"><div class="val">{K['n_all_new']}</div><div class="label">5.6八日外(N)</div><div class="hb {hb_cls(K["n_all_new"]-K["n_all_prev"])}">{n_hb_text}</div></div>
  <div class="kpi-card red"><div class="val">{K['un_all_new']}</div><div class="label">5.6未出单</div><div class="hb {hb_cls(K["un_all_new"]-K["un_all_prev"])}">{un_hb_text}</div></div>
  <div class="kpi-card orange"><div class="val">{D['rate_all'][-1]}%</div><div class="label">5.6全量出单率</div><div class="hb {rate_all_hb_cls}">{rate_hb_text}</div></div>
  <div class="kpi-card"><div class="val">{K['qty_new']}</div><div class="label">4.30-5.6总销量</div><div class="hb {hb_cls(K["qty_chg"])}">{qty_hb_text}</div></div>
  <div class="kpi-card purple"><div class="val">{fmt_usd(K['amt_new'])}</div><div class="label">4.30-5.6总销售额</div><div class="hb {hb_cls(K["amt_chg"])}">{amt_hb_text}</div></div>
  <div class="kpi-card"><div class="val">{K['mzb_new']}%</div><div class="label">5.6平均市占比</div><div class="hb {hb_cls(K["mzb_chg"], True)}">{mzb_hb_text}</div></div>
  <div class="kpi-card red"><div class="val">{K['low_cnt']}</div><div class="label">低占比新品</div><div class="hb" style="color:#888">5.6市占&lt;75%</div></div>
</div>

<!-- 数据总览 -->
<div id="section-overview" class="section-wrap">
  <div class="section">
    <h3>&#x1F4CA; 数据总览 · 图形可视化</h3>
    <div class="chart-grid">
      <div class="chart-card"><h4>&#x1F4C8; 四周期总销量对比</h4><canvas id="chartTotalQty"></canvas></div>
      <div class="chart-card"><h4>&#x1F4B0; 四周期总销售额对比(USD)</h4><canvas id="chartTotalAmt"></canvas></div>
      <div class="chart-card"><h4>&#x1F4E6; 四周期全量出单率趋势</h4><canvas id="chartOrderRate"></canvas></div>
      <div class="chart-card"><h4>&#x1F4CC; 四周期平均市占比趋势</h4><canvas id="chartMzb"></canvas></div>
      <div class="chart-card"><h4>&#x1F4CA; 4.30-5.6出单分布</h4><canvas id="chartOrderPie"></canvas></div>
      <div class="chart-card"><h4>&#x1F3F7; 4.30-5.6品类出单率</h4><canvas id="chartCatRate"></canvas></div>
    </div>
  </div>
</div>

<!-- 品线维度 -->
<div id="section-pinxian" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x1F3F7;&#xFE0F; 品线维度</h3>
    <p class="note">各品线在跟SKU数量及四周期出单率、销量对比</p>
    <div class="sub-module">
      <h4>四周期各品线销量与出单率</h4>
      <div class="chart-grid">
        <div class="chart-card"><h4>各品线四周期出单率趋势</h4><canvas id="chartCatRateTrend"></canvas></div>
        <div class="chart-card"><h4>4.30-5.6各品线销量分布</h4><canvas id="chartCatQty"></canvas></div>
      </div>
    </div>
    <div class="sub-module">
      <h4>品线数据明细表（四周期对比）</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th rowspan="2">品类</th><th rowspan="2">SKU数</th>
              <th colspan="3" class="p1">{P[0]}</th>
              <th colspan="3" class="p2">{P[1]}</th>
              <th colspan="3" class="p3">{P[2]}</th>
              <th colspan="3" class="p4">{P[3]}</th>
              <th colspan="2" class="hb">环比({P[3].split('-')[1]} vs {P[2].split('-')[1]})</th>
            </tr>
            <tr>
              <th class="p1">销量</th><th class="p1">销售额</th><th class="p1">出单率</th>
              <th class="p2">销量</th><th class="p2">销售额</th><th class="p2">出单率</th>
              <th class="p3">销量</th><th class="p3">销售额</th><th class="p3">出单率</th>
              <th class="p4">销量</th><th class="p4">销售额</th><th class="p4">出单率</th>
              <th class="hb">销量&#x21D5;</th><th class="hb">出单率&#x21D5;</th>
            </tr>
          </thead>
          <tbody>
            {cat_rows_html}
            {cat_total_row}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- 分析人维度 -->
<div id="section-analyst" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x1F464; 分析人维度</h3>
    <p class="note">各分析人负责SKU的出单率和销量表现（四周期对比，数据来自4月分析人列）</p>
    <div class="chart-grid">
      <div class="chart-card"><h4>分析人四周期出单率趋势</h4><canvas id="chartAnalystRate"></canvas></div>
      <div class="chart-card"><h4>4.30-5.6各分析人销量对比</h4><canvas id="chartAnalystQty"></canvas></div>
    </div>
    <div class="sub-module">
      <h4>分析人数据明细（四周期对比）</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th rowspan="2">分析人</th><th rowspan="2">负责SKU</th>
              <th colspan="3" class="p1">{P[0]}</th>
              <th colspan="3" class="p2">{P[1]}</th>
              <th colspan="3" class="p3">{P[2]}</th>
              <th colspan="3" class="p4">{P[3]}</th>
              <th colspan="2" class="hb">环比</th>
            </tr>
            <tr>
              <th class="p1">销量</th><th class="p1">Y</th><th class="p1">出单率</th>
              <th class="p2">销量</th><th class="p2">Y</th><th class="p2">出单率</th>
              <th class="p3">销量</th><th class="p3">Y</th><th class="p3">出单率</th>
              <th class="p4">销量</th><th class="p4">Y</th><th class="p4">出单率</th>
              <th class="hb">销量&#x21D5;</th><th class="hb">出单率&#x21D5;</th>
            </tr>
          </thead>
          <tbody>
            {ana_rows_html}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- 拓展类型 -->
<div id="section-expand" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x1F516; 拓展类型维度</h3>
    <p class="note">原开品 / 拓展品 / 组合件的四周期对比</p>
    <div class="chart-grid">
      <div class="chart-card"><h4>拓展类型四周期出单率趋势</h4><canvas id="chartExpRate"></canvas></div>
      <div class="chart-card"><h4>4.30-5.6各拓展类型销量</h4><canvas id="chartExpQty"></canvas></div>
    </div>
    <div class="sub-module">
      <h4>拓展类型数据明细</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th rowspan="2">拓展类型</th><th rowspan="2">SKU数</th>
              <th colspan="2" class="p1">{P[0]}</th>
              <th colspan="2" class="p2">{P[1]}</th>
              <th colspan="2" class="p3">{P[2]}</th>
              <th colspan="2" class="p4">{P[3]}</th>
              <th colspan="2" class="hb">环比</th>
            </tr>
            <tr>
              <th class="p1">销量</th><th class="p1">出单率</th>
              <th class="p2">销量</th><th class="p2">出单率</th>
              <th class="p3">销量</th><th class="p3">出单率</th>
              <th class="p4">销量</th><th class="p4">出单率</th>
              <th class="hb">销量&#x21D5;</th><th class="hb">出单率&#x21D5;</th>
            </tr>
          </thead>
          <tbody>
            {exp_rows_html}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- 分析及时率 -->
<div id="section-timely" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x23F1;&#xFE0F; 分析及时率维度</h3>
    <p class="note">基于7天频次标签统计分析及时率（正常=及时分析，异常=超7日未分析，无数据=8日内新品无分析）</p>
    <div class="chart-grid">
      <div class="chart-card"><h4>四周期分析及时率趋势</h4><canvas id="chartTimelyRate"></canvas></div>
      <div class="chart-card"><h4>4.30-5.6分析情况分布</h4><canvas id="chartTimelyPie"></canvas></div>
    </div>
    <div class="sub-module">
      <h4>分析及时率数据明细</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>分析情况</th>
              <th class="p1">{P[0]}</th>
              <th class="p2">{P[1]}</th>
              <th class="p3">{P[2]}</th>
              <th class="p4">{P[3]}</th>
              <th class="hb">环比</th>
            </tr>
          </thead>
          <tbody>{timely_rows_html}</tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- 新品出单情况 -->
<div id="section-order" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x1F4E6; 新品出单情况维度</h3>
    <p class="note">基于新品检查记录统计（含无对手未归因产品），数据来源：新品周报数据.xlsx + 本期实测</p>
    <div class="chart-grid">
      <div class="chart-card"><h4>四周期出单情况趋势</h4><canvas id="chartOrderTrend"></canvas></div>
      <div class="chart-card"><h4>4.30-5.6出单分布</h4><canvas id="chartOrderDist"></canvas></div>
    </div>
    <div class="sub-module">
      <h4>出单情况数据明细</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>出单情况</th>
              <th class="p1">{P[0]}</th>
              <th class="p2">{P[1]}</th>
              <th class="p3">{P[2]}</th>
              <th class="p4">{P[3]}</th>
              <th class="hb">环比</th>
            </tr>
          </thead>
          <tbody>{order_rows_html}</tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- 新品未出单 -->
<div id="section-unorder" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x274C; 新品未出单维度</h3>
    <p class="note">未出单SKU按市场状态分类（数据来源：四三数据累计主表）</p>
    <div class="chart-grid">
      <div class="chart-card"><h4>四周期未出单原因趋势</h4><canvas id="chartUnorderTrend"></canvas></div>
      <div class="chart-card"><h4>4.30-5.6未出单原因分布</h4><canvas id="chartUnorderPie"></canvas></div>
    </div>
    <div class="sub-module">
      <h4>未出单原因数据明细</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>未出单原因</th>
              <th class="p1">{P[0]}</th>
              <th class="p2">{P[1]}</th>
              <th class="p3">{P[2]}</th>
              <th class="p4">{P[3]}</th>
              <th class="hb">环比</th>
            </tr>
          </thead>
          <tbody>{unorder_rows_html}</tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- 低占比新品 -->
<div id="section-lowshare" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x1F4C9; 低占比新品明细（5.6市占比&lt;75% + 有竞品订单）</h3>
    <p class="note">共 {D['low_skus_cnt']} 个SKU，按市占比从低到高排列</p>
    <div class="sub-module">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>销售编号</th><th>SKU</th><th>品类</th><th>拓展类型</th>
              <th>上架日期</th><th>首次出单</th><th>分析人</th>
              <th>4.30-5.6销量</th><th>5.6对手销量</th>
              <th>5.6市占比</th>
              <th>8日出单</th><th>市场状态</th><th>操作判断</th>
            </tr>
          </thead>
          <tbody>{low_rows_html}</tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- PLP复盘 -->
<div id="section-plp" class="section-wrap" style="display:none">
  <div class="section">
    <h3>&#x1F4B0; PLP广告复盘 · 4.30-5.6</h3>
    <p class="note">数据来源：新品检查周源数据和PLP数据.xlsx PLP明细Sheet，本期共 {D['plp']['total']['skus']} 个广告SKU</p>
    <div class="plp-grid">
      <div class="plp-card">
        <h4>&#x1F4CA; PLP总览</h4>
        <div class="plp-metric"><span class="lbl">广告SKU数</span><span class="val">{D['plp']['total']['skus']}</span></div>
        <div class="plp-metric"><span class="lbl">曝光量</span><span class="val">{D['plp']['total']['imp']:,}</span></div>
        <div class="plp-metric"><span class="lbl">点击量</span><span class="val">{D['plp']['total']['clk']:,}</span></div>
        <div class="plp-metric"><span class="lbl">订单数</span><span class="val">{D['plp']['total']['ord']}</span></div>
        <div class="plp-metric"><span class="lbl">花费</span><span class="val">${D['plp']['total']['spend']}</span></div>
        <div class="plp-metric"><span class="lbl">销售额</span><span class="val">${D['plp']['total']['sales']}</span></div>
        <div class="plp-highlight">
          <div class="plp-metric"><span class="lbl">ROAS</span><span class="val">{D['plp']['total']['roas']}</span></div>
          <div class="plp-metric"><span class="lbl">CVR</span><span class="val">{D['plp']['total']['cvr']}%</span></div>
          <div class="plp-metric"><span class="lbl">ACOS</span><span class="val">{D['plp']['total']['acos']}%</span></div>
        </div>
      </div>
      <div class="plp-card">
        <h4>&#x1F4B9; PLG费率总览</h4>
        <div class="plp-metric"><span class="lbl">有效费率SKU</span><span class="val">{D['plg']['total']}</span></div>
      </div>
    </div>
    <div class="sub-module">
      <h4>PLP按分析人维度</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>分析人</th><th>广告SKU</th><th>曝光</th><th>点击</th><th>订单</th><th>花费</th><th>销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>ACOS</th></tr>
          </thead>
          <tbody>{plp_table_rows(D['plp']['by_analyst'])}</tbody>
        </table>
      </div>
    </div>
    <div class="sub-module">
      <h4>PLP按品类维度</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>品类</th><th>广告SKU</th><th>曝光</th><th>点击</th><th>订单</th><th>花费</th><th>销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>ACOS</th></tr>
          </thead>
          <tbody>{plp_table_rows(D['plp']['by_cat'])}</tbody>
        </table>
      </div>
    </div>
    <div class="sub-module">
      <h4>PLP按拓展类型维度</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>拓展类型</th><th>广告SKU</th><th>曝光</th><th>点击</th><th>订单</th><th>花费</th><th>销售额</th><th>ROAS</th><th>CVR</th><th>CTR</th><th>ACOS</th></tr>
          </thead>
          <tbody>{plp_table_rows(D['plp']['by_expn'])}</tbody>
        </table>
      </div>
    </div>
    <div class="sub-module">
      <h4>PLG最高费率 · 按分析人</h4>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>分析人</th><th>SKU数</th><th>平均费率</th><th>最高费率</th></tr></thead>
          <tbody>{plg_table_rows(D['plg']['by_analyst'])}</tbody>
        </table>
      </div>
    </div>
  </div>
</div>

</div></div>

<script>
// ── 导航切换（最先定义，确保交互不中断）──
const sections = ['overview','pinxian','analyst','expand','timely','order','unorder','lowshare','plp'];
function showSection(name, el) {{
  sections.forEach(s => {{
    var wrap = document.getElementById('section-' + s);
    if (wrap) wrap.style.display = s === name ? 'block' : 'none';
  }});
  document.querySelectorAll('.sidebar a').forEach(function(a) {{ a.classList.remove('active'); }});
  if (el) el.classList.add('active');
  return false;
}}

// ── 图表数据与渲染（在DOM加载后执行）──
(function() {{
  if (typeof Chart === 'undefined') {{
    console.warn('Chart.js 未加载，图表将不显示。请检查网络连接。');
    return;
  }}

  var P = {json.dumps(P, ensure_ascii=False)};
  var COLORS = ['#0f3460','#e07b24','#08845a','#c0392b','#8e44ad','#2980b9','#16a085','#d35400','#7f8c8d'];

  function mkBar(id, labels, datasets, horiz) {{
    var ctx = document.getElementById(id);
    if (!ctx) return null;
    try {{ return new Chart(ctx, {{
      type: 'bar',
      data: {{ labels: labels, datasets: datasets }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        indexAxis: horiz ? 'y' : 'x',
        plugins: {{ legend: {{ display: datasets.length > 1, position: 'top', labels: {{ font: {{ size: 10 }} }} }} }},
        scales: {{ x: {{ ticks: {{ font: {{ size: 10 }}, maxRotation: 30 }} }}, y: {{ ticks: {{ font: {{ size: 10 }}, beginAtZero: true }} }} }}
      }}
    }}); }} catch(e) {{ console.warn('Chart error ' + id + ': ' + e.message); return null; }}
  }}

  function mkLine(id, labels, datasets) {{
    var ctx = document.getElementById(id);
    if (!ctx) return null;
    try {{ return new Chart(ctx, {{
      type: 'line',
      data: {{ labels: labels, datasets: datasets }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: datasets.length > 1, position: 'top', labels: {{ font: {{ size: 10 }} }} }} }},
        scales: {{ x: {{ ticks: {{ font: {{ size: 10 }}, maxRotation: 30 }} }}, y: {{ ticks: {{ font: {{ size: 10 }}, beginAtZero: true }} }} }}
      }}
    }}); }} catch(e) {{ console.warn('Chart error ' + id + ': ' + e.message); return null; }}
  }}

  function mkPie(id, labels, data, pos) {{
    var ctx = document.getElementById(id);
    if (!ctx) return null;
    try {{ return new Chart(ctx, {{
      type: 'doughnut',
      data: {{ labels: labels, datasets: [{{ data: data, backgroundColor: COLORS, borderWidth: 1 }}] }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ position: pos || 'right', labels: {{ font: {{ size: 10 }}, boxWidth: 12 }} }} }}
      }}
    }}); }} catch(e) {{ console.warn('Chart error ' + id + ': ' + e.message); return null; }}
  }}

  // ── 总览图表 ──
  mkBar('chartTotalQty', P, [{{ label: '总销量', data: {json.dumps([int(x) for x in D['qty_list']])}, backgroundColor: ['#6c757d','#667eea','#2980b9','#c0392b'] }}]);
  mkBar('chartTotalAmt', P, [{{ label: '总销售额(USD)', data: {json.dumps(D['amt_list'])}, backgroundColor: ['#6c757d','#667eea','#2980b9','#c0392b'] }}]);
  mkLine('chartOrderRate', P, [{{ label: '全量出单率(%)', data: {json.dumps(D['rate_all'])}, borderColor: '#e07b24', backgroundColor: 'rgba(224,123,36,0.1)', fill: true, tension: 0.3, pointRadius: 4 }}]);
  mkLine('chartMzb', P, [{{ label: '平均市占比(%)', data: {json.dumps(D['mzb_list'])}, borderColor: '#0f3460', backgroundColor: 'rgba(15,52,96,0.1)', fill: true, tension: 0.3, pointRadius: 4 }}]);
  mkPie('chartOrderPie', ['8日出单(Y)','8日外出单(N)','未出单'], [{K['y_all_new']}, {K['n_all_new']}, {K['un_all_new']}]);

  var catRates = {json.dumps({c: D['cat_data'][c]['rates'][-1] for c in cats}, ensure_ascii=False)};
  mkBar('chartCatRate', Object.keys(catRates), [{{ label: '出单率(%)', data: Object.values(catRates), backgroundColor: COLORS }}]);

  // ── 品线图表 ──
  var catRateDatasets = {json.dumps(cats, ensure_ascii=False)}.map(function(cat, i) {{ return {{
    label: cat, data: {json.dumps({c: D['cat_data'][c]['rates'] for c in cats}, ensure_ascii=False)}[cat],
    borderColor: COLORS[i], backgroundColor: 'transparent', tension: 0.3, pointRadius: 4
  }}; }});
  mkLine('chartCatRateTrend', P, catRateDatasets);
  mkBar('chartCatQty', {json.dumps(cats, ensure_ascii=False)}, [{{ label: '4.30-5.6销量', data: {json.dumps([D['cat_data'][c]['qtys'][-1] for c in cats])}, backgroundColor: COLORS }}]);

  // ── 分析人图表 ──
  var anaRateDatasets = {json.dumps(analysts, ensure_ascii=False)}.map(function(a, i) {{ return {{
    label: a, data: {json.dumps({a: D['ana_data'][a]['rates'] for a in analysts}, ensure_ascii=False)}[a],
    borderColor: COLORS[i], backgroundColor: 'transparent', tension: 0.3, pointRadius: 4
  }}; }});
  mkLine('chartAnalystRate', P, anaRateDatasets);
  mkBar('chartAnalystQty', {json.dumps(analysts, ensure_ascii=False)}, [{{ label: '4.30-5.6销量', data: {json.dumps([D['ana_data'][a]['qtys'][-1] for a in analysts])}, backgroundColor: COLORS }}]);

  // ── 拓展类型图表 ──
  var activeExps = {json.dumps(exps, ensure_ascii=False)}.filter(function(e) {{ return {json.dumps({e: D['exp_data'][e]['skus'] for e in exps}, ensure_ascii=False)}[e] > 0; }});
  var expRateDatasets = activeExps.map(function(e, i) {{ return {{
    label: e, data: {json.dumps({e: D['exp_data'][e]['rates'] for e in exps}, ensure_ascii=False)}[e],
    borderColor: COLORS[i], backgroundColor: 'transparent', tension: 0.3, pointRadius: 4
  }}; }});
  mkLine('chartExpRate', P, expRateDatasets);
  mkBar('chartExpQty', activeExps, [{{ label: '4.30-5.6销量', data: activeExps.map(function(e) {{ return {json.dumps({e: D['exp_data'][e]['qtys'][-1] for e in exps}, ensure_ascii=False)}[e]; }}), backgroundColor: COLORS }}]);

  // ── 分析及时率图表 ──
  mkLine('chartTimelyRate', P, [
    {{ label: '及时分析', data: {json.dumps(D['timely_in'])}, borderColor: '#08845a', backgroundColor: 'rgba(8,132,90,0.1)', fill: true, tension: 0.3, pointRadius: 4 }},
    {{ label: '超7日未分析', data: {json.dumps(D['timely_over7'])}, borderColor: '#e07b24', backgroundColor: 'rgba(224,123,36,0.1)', fill: true, tension: 0.3, pointRadius: 4 }},
    {{ label: '8日内新品无分析', data: {json.dumps(D['timely_new'])}, borderColor: '#c0392b', backgroundColor: 'rgba(192,57,43,0.1)', fill: true, tension: 0.3, pointRadius: 4 }}
  ]);
  mkPie('chartTimelyPie', ['及时分析','超7日未分析','8日内新品无分析'], [{D['timely_in'][-1]}, {D['timely_over7'][-1]}, {D['timely_new'][-1]}]);

  // ── 出单情况图表 ──
  mkLine('chartOrderTrend', P, [
    {{ label: '8日出单(Y)', data: {json.dumps(D['order_y'])}, borderColor: '#08845a', backgroundColor: 'rgba(8,132,90,0.1)', fill: true, tension: 0.3, pointRadius: 4 }},
    {{ label: '8日外出单(N)', data: {json.dumps(D['order_n'])}, borderColor: '#e07b24', backgroundColor: 'rgba(224,123,36,0.1)', fill: true, tension: 0.3, pointRadius: 4 }},
    {{ label: '未出单', data: {json.dumps(D['order_un'])}, borderColor: '#c0392b', backgroundColor: 'rgba(192,57,43,0.1)', fill: true, tension: 0.3, pointRadius: 4 }}
  ]);
  mkPie('chartOrderDist', ['8日出单(Y)','8日外出单(N)','未出单'], [{D['order_y'][-1]}, {D['order_n'][-1]}, {D['order_un'][-1]}]);

  // ── 未出单图表 ──
  var unorderReasons = ['竞争无优势','无市场','站内无价格优势','站外出单'];
  var uoDatasets = unorderReasons.map(function(r, i) {{ return {{
    label: r, data: {json.dumps(D['unorder_data'], ensure_ascii=False)}[r] || [0,0,0,0],
    backgroundColor: COLORS[i]
  }}; }});
  mkBar('chartUnorderTrend', P, uoDatasets);

  var uoLast = unorderReasons.map(function(r) {{ var d = {json.dumps(D['unorder_data'], ensure_ascii=False)}; return d[r] ? d[r][3] : 0; }});
  mkPie('chartUnorderPie', unorderReasons, uoLast);
}})();
</script>
</body>
</html>'''

output_path = r'c:\Users\Hardy\ai-projects\新品复盘\新品周报_4.30-5.6.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'HTML report generated: {output_path}')
print(f'File size: {len(html):,} bytes')
