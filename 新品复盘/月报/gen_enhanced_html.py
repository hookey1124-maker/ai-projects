"""
生成增强版月报HTML：
补充遗漏字段：
1. 品线维度：增加销售额、对手出单、平均市占比（三个月分列对比）
2. 分析人维度：增加销售额、均价、平均分析频次、对手出单、市占比
3. 拓展类型维度：增加销售额、对手出单、市占比
4. 全量明细：增加销售编号、上架日期、首次出单、销售额、1/2/3月分列、分析频次
5. 未出单市场：三个月对比
"""
import json, re

# 读取完整数据
with open('full_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

summary = data['summary']
batch_stats = data['batch_stats']
cat_data = data['cat_data']
analyst_data = data['analyst_data']
expand_data = data['expand_data']
order_dist = data['order_dist']
unorder_dist = data['unorder_dist']
all_data = data['all_data']
low_share = data['low_share']

def hb_fmt(val, suffix=''):
    if val is None: return '-'
    s = f'+{val}{suffix}' if val > 0 else f'{val}{suffix}'
    return s

# ============ 生成 HTML ============
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新品月报 · 2026年3月（增强版）</title>
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
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th { background: #0f3460; color: white; padding: 8px 8px; text-align: center; white-space: nowrap; font-weight: 600; }
.data-table th.m1 { background: #6c757d; }
.data-table th.m2 { background: #667eea; }
.data-table th.m3 { background: #c0392b; }
.data-table th.hb { background: #e07b24; }
.data-table td { padding: 6px 8px; text-align: center; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }
.data-table tr:hover td { background: #f5f7ff; }
.data-table .row-ordered { background: #f0fff4; }
.data-table .row-unorder { background: #fff8f0; }
.hb-up { color: #c0392b; font-weight: 700; }
.hb-down { color: #08845a; font-weight: 700; }
.hb-flat { color: #888; }
.batch-tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: white; font-weight: 600; }
.b1 { background: #6c757d; }
.b2 { background: #667eea; }
.b3 { background: #c0392b; }
select { padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; font-size: 13px; background: white; cursor: pointer; }
select:focus { outline: none; border-color: #0f3460; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
@media (max-width: 900px) { .sidebar { display: none; } .chart-grid { grid-template-columns: 1fr; } .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.section-wrap { display: block; }
.note { font-size: 12px; color: #888; margin-bottom: 10px; }
.warning { font-size: 12px; color: #e07b24; margin-bottom: 10px; }
</style>
</head>
<body>

<div class="header">
  <h1>🚀 新品月报 · 2026年3月（增强版）</h1>
  <div class="subtitle">统计周期：2026年3月 | 在跟SKU：156 | 1月批次：53 | 2月批次：36 | 3月批次：67 | 生成：2026-04-09</div>
</div>

<div class="container">
<nav class="sidebar">
  <ul>
    <li><a href="#" onclick="showSection('overview',this)" class="active">📊 数据总览</a></li>
    <li><a href="#" onclick="showSection('pinxian',this)">🏷️ 品线维度</a></li>
    <li><a href="#" onclick="showSection('analyst',this)">👤 分析人维度</a></li>
    <li><a href="#" onclick="showSection('expand',this)">🔖 拓展类型维度</a></li>
    <li><a href="#" onclick="showSection('order',this)">📦 出单情况分析</a></li>
    <li><a href="#" onclick="showSection('unorder',this)">❌ 未出单市场</a></li>
    <li><a href="#" onclick="showSection('lowshare',this)">📉 低占比新品</a></li>
    <li><a href="#" onclick="showSection('detail',this)">📋 全量明细</a></li>
  </ul>
</nav>

<div class="main-content">
'''

# KPI卡片
s = summary
html += f'''<!-- KPI -->
<div class="kpi-grid">
  <div class="kpi-card"><div class="val">156</div><div class="label">在跟SKU总数</div><div class="hb" style="color:#888">1月53 · 2月36 · 3月67</div></div>
  <div class="kpi-card green"><div class="val">{s["ordered_sku"]}</div><div class="label">3月8日已出单(Y)</div></div>
  <div class="kpi-card orange"><div class="val">{s["unordered_sku"]}</div><div class="label">3月8日未出单(N)</div></div>
  <div class="kpi-card red"><div class="val">{s["not_order_sku"]}</div><div class="label">3月未出单</div></div>
  <div class="kpi-card orange"><div class="val">{s["order_rate"]}%</div><div class="label">3月新品出单率(Y+N)</div></div>
  <div class="kpi-card"><div class="val">{int(s["total_qty"])}</div><div class="label">3月总销量</div></div>
  <div class="kpi-card purple"><div class="val">${int(s["total_amt"])}</div><div class="label">3月总销售额(USD)</div></div>
  <div class="kpi-card"><div class="val">{s["avg_share"]}%</div><div class="label">3月平均市占比</div></div>
  <div class="kpi-card red"><div class="val">{s["low_share_cnt"]}</div><div class="label">低占比新品</div></div>
</div>

'''

# ========== 数据总览 ==========
html += '''<div id="section-overview" class="section-wrap">
  <div class="section">
    <h3>📊 数据总览 · 图形可视化</h3>
    <div class="chart-grid">
      <div class="chart-card"><h4>📈 各批次3月销量/销售额对比</h4><canvas id="chartBatchQty"></canvas></div>
      <div class="chart-card"><h4>🏷️ 各品类三个月销量对比</h4><canvas id="chartCategoryQty"></canvas></div>
      <div class="chart-card"><h4>📊 各品类三个月出单率对比</h4><canvas id="chartCategoryRate"></canvas></div>
      <div class="chart-card"><h4>👤 分析人三个月销量对比</h4><canvas id="chartAnalystQty"></canvas></div>
      <div class="chart-card"><h4>🔖 拓展类型三个月销量对比</h4><canvas id="chartExpandQty"></canvas></div>
      <div class="chart-card"><h4>📦 各批次出单情况（3月）</h4><canvas id="chartOrderDist"></canvas></div>
    </div>
  </div>
</div>
'''

# ========== 品线维度 ==========
cat_rows = ''
cats = list(cat_data.keys())
for cat in cats:
    d = cat_data[cat]
    def fmt_hb(val):
        if val is None: return '<span class="hb-flat">-</span>'
        cls = 'hb-up' if val > 0 else ('hb-down' if val < 0 else 'hb-flat')
        sign = '+' if val > 0 else ''
        return f'<span class="{cls}">{sign}{val}</span>'
    cat_rows += f'''<tr>
      <td><b>{cat}</b></td>
      <td>{d["sku_1"]}</td><td>{int(d["qty_1"])}</td><td>${int(d["amt_1"])}</td><td>{d["share_1"]}%</td><td>{d["rate_1"]}%</td>
      <td>{d["sku_2"]}</td><td>{int(d["qty_2"])}</td><td>${int(d["amt_2"])}</td><td>{d["share_2"]}%</td><td>{d["rate_2"]}%</td>
      <td>{d["sku_3"]}</td><td>{int(d["qty_3"])}</td><td>${int(d["amt_3"])}</td><td>{d["share_3"]}%</td><td>{d["rate_3"]}%</td>
      <td>{fmt_hb(d.get("qty_hb"))}</td><td>{fmt_hb(d.get("rate_hb"))}</td>
    </tr>'''

html += f'''<div id="section-pinxian" class="section-wrap" style="display:none">
  <div class="section">
    <h3>🏷️ 品线维度</h3>
    <div class="sub-module">
      <h4>各品类三个月完整数据对比（含销售额、市占比、出单率）</h4>
      <p class="note">销量为该维度在各月所有批次新品的累计销量；SKU数为该月上架批次数量</p>
      <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th rowspan="2">品类</th>
            <th colspan="5" class="m1">1月新品(共53个)</th>
            <th colspan="5" class="m2">2月新品(共36个)</th>
            <th colspan="5" class="m3">3月新品(共67个)</th>
            <th colspan="2" class="hb">环比(3月vs2月)</th>
          </tr>
          <tr>
            <th class="m1">SKU</th><th class="m1">3月销量</th><th class="m1">3月销售额</th><th class="m1">平均市占比</th><th class="m1">出单率</th>
            <th class="m2">SKU</th><th class="m2">3月销量</th><th class="m2">3月销售额</th><th class="m2">平均市占比</th><th class="m2">出单率</th>
            <th class="m3">SKU</th><th class="m3">3月销量</th><th class="m3">3月销售额</th><th class="m3">平均市占比</th><th class="m3">出单率</th>
            <th class="hb">销量↕</th><th class="hb">出单率↕</th>
          </tr>
        </thead>
        <tbody>{cat_rows}</tbody>
      </table>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h4>📈 各品类三个月销量对比</h4><canvas id="chartCatQty"></canvas></div>
      <div class="chart-card"><h4>💰 各品类三个月销售额对比</h4><canvas id="chartCatAmt"></canvas></div>
      <div class="chart-card"><h4>📊 各品类三个月出单率对比</h4><canvas id="chartCatRate"></canvas></div>
      <div class="chart-card"><h4>🎯 各品类3月平均市占比</h4><canvas id="chartCatShare"></canvas></div>
    </div>
  </div>
</div>
'''

# ========== 分析人维度 ==========
analyst_rows = ''
for analyst in analyst_data:
    d = analyst_data[analyst]
    def fmt_hb(val):
        if val is None: return '<span class="hb-flat">-</span>'
        cls = 'hb-up' if val > 0 else ('hb-down' if val < 0 else 'hb-flat')
        sign = '+' if val > 0 else ''
        return f'<span class="{cls}">{sign}{val}</span>'
    analyst_rows += f'''<tr>
      <td><b>{analyst}</b></td>
      <td>{d["sku_1"]}</td><td>{int(d["qty_1"])}</td><td>${int(d["amt_1"])}</td><td>${d["price_1"]}</td><td>{d["freq_1"]}</td><td>{d["share_1"]}%</td><td>{d["rate_1"]}%</td>
      <td>{d["sku_2"]}</td><td>{int(d["qty_2"])}</td><td>${int(d["amt_2"])}</td><td>${d["price_2"]}</td><td>{d["freq_2"]}</td><td>{d["share_2"]}%</td><td>{d["rate_2"]}%</td>
      <td>{d["sku_3"]}</td><td>{int(d["qty_3"])}</td><td>${int(d["amt_3"])}</td><td>${d["price_3"]}</td><td>{d["freq_3"]}</td><td>{d["share_3"]}%</td><td>{d["rate_3"]}%</td>
      <td>{fmt_hb(d.get("qty_hb"))}</td><td>{fmt_hb(d.get("rate_hb"))}</td>
    </tr>'''

html += f'''<div id="section-analyst" class="section-wrap" style="display:none">
  <div class="section">
    <h3>👤 分析人维度</h3>
    <div class="sub-module">
      <h4>各分析人三个月完整绩效（含销售额、均价、分析频次、市占比）</h4>
      <p class="note">均价=销售额/销量；分析频次为该批次新品的平均跟进次数</p>
      <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th rowspan="2">分析人</th>
            <th colspan="7" class="m1">1月新品</th>
            <th colspan="7" class="m2">2月新品</th>
            <th colspan="7" class="m3">3月新品</th>
            <th colspan="2" class="hb">环比(3月vs2月)</th>
          </tr>
          <tr>
            <th class="m1">SKU</th><th class="m1">3月销量</th><th class="m1">3月销售额</th><th class="m1">均价</th><th class="m1">平均频次</th><th class="m1">市占比</th><th class="m1">出单率</th>
            <th class="m2">SKU</th><th class="m2">3月销量</th><th class="m2">3月销售额</th><th class="m2">均价</th><th class="m2">平均频次</th><th class="m2">市占比</th><th class="m2">出单率</th>
            <th class="m3">SKU</th><th class="m3">3月销量</th><th class="m3">3月销售额</th><th class="m3">均价</th><th class="m3">平均频次</th><th class="m3">市占比</th><th class="m3">出单率</th>
            <th class="hb">销量↕</th><th class="hb">出单率↕</th>
          </tr>
        </thead>
        <tbody>{analyst_rows}</tbody>
      </table>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h4>👤 各分析人三个月销量对比</h4><canvas id="chartAnalystQty2"></canvas></div>
      <div class="chart-card"><h4>💰 各分析人三个月销售额对比</h4><canvas id="chartAnalystAmt"></canvas></div>
      <div class="chart-card"><h4>📊 各分析人三个月出单率对比</h4><canvas id="chartAnalystRate"></canvas></div>
      <div class="chart-card"><h4>🔄 各分析人3月平均分析频次</h4><canvas id="chartAnalystFreq"></canvas></div>
    </div>
  </div>
</div>
'''

# ========== 拓展类型维度 ==========
expand_rows = ''
for ex in expand_data:
    d = expand_data[ex]
    def fmt_hb(val):
        if val is None: return '<span class="hb-flat">-</span>'
        cls = 'hb-up' if val > 0 else ('hb-down' if val < 0 else 'hb-flat')
        sign = '+' if val > 0 else ''
        return f'<span class="{cls}">{sign}{val}</span>'
    expand_rows += f'''<tr>
      <td><b>{ex}</b></td>
      <td>{d["sku_1"]}</td><td>{int(d["qty_1"])}</td><td>${int(d["amt_1"])}</td><td>{d["comp_1"]:.0f}</td><td>{d["share_1"]}%</td><td>{d["rate_1"]}%</td>
      <td>{d["sku_2"]}</td><td>{int(d["qty_2"])}</td><td>${int(d["amt_2"])}</td><td>{d["comp_2"]:.0f}</td><td>{d["share_2"]}%</td><td>{d["rate_2"]}%</td>
      <td>{d["sku_3"]}</td><td>{int(d["qty_3"])}</td><td>${int(d["amt_3"])}</td><td>{d["comp_3"]:.0f}</td><td>{d["share_3"]}%</td><td>{d["rate_3"]}%</td>
      <td>{fmt_hb(d.get("qty_hb"))}</td><td>{fmt_hb(d.get("rate_hb"))}</td>
    </tr>'''

html += f'''<div id="section-expand" class="section-wrap" style="display:none">
  <div class="section">
    <h3>🔖 拓展类型维度</h3>
    <div class="sub-module">
      <h4>各拓展类型三个月完整数据（含销售额、对手出单、市占比）</h4>
      <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th rowspan="2">拓展类型</th>
            <th colspan="6" class="m1">1月新品</th>
            <th colspan="6" class="m2">2月新品</th>
            <th colspan="6" class="m3">3月新品</th>
            <th colspan="2" class="hb">环比</th>
          </tr>
          <tr>
            <th class="m1">SKU</th><th class="m1">3月销量</th><th class="m1">3月销售额</th><th class="m1">对手出单</th><th class="m1">市占比</th><th class="m1">出单率</th>
            <th class="m2">SKU</th><th class="m2">3月销量</th><th class="m2">3月销售额</th><th class="m2">对手出单</th><th class="m2">市占比</th><th class="m2">出单率</th>
            <th class="m3">SKU</th><th class="m3">3月销量</th><th class="m3">3月销售额</th><th class="m3">对手出单</th><th class="m3">市占比</th><th class="m3">出单率</th>
            <th class="hb">销量↕</th><th class="hb">出单率↕</th>
          </tr>
        </thead>
        <tbody>{expand_rows}</tbody>
      </table>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h4>📈 各拓展类型三个月销量对比</h4><canvas id="chartExpandQty2"></canvas></div>
      <div class="chart-card"><h4>📊 各拓展类型三个月出单率对比</h4><canvas id="chartExpandRate"></canvas></div>
    </div>
  </div>
</div>
'''

# ========== 出单情况 ==========
order_rows = ''
bs = batch_stats
for m, ml in [('1','1月'),('2','2月'),('3','3月')]:
    d = bs[m]
    qty_hb = d.get('qty_hb')
    rate_hb = d.get('rate_hb')
    def fmt_hb(val):
        if val is None: return '<span class="hb-flat">-</span>'
        cls = 'hb-up' if val > 0 else ('hb-down' if val < 0 else 'hb-flat')
        sign = '+' if val > 0 else ''
        return f'<span class="{cls}">{sign}{val}</span>'
    # 环比
    if m == '1':
        qty_hb_str = '<span class="hb-flat">-</span>'
        rate_hb_str = '<span class="hb-flat">-</span>'
        amt_hb_str = '<span class="hb-flat">-</span>'
    else:
        prev = bs[str(int(m)-1)]
        qty_hb_v = round(d['qty'] - prev['qty'], 0)
        rate_hb_v = round(d['rate'] - prev['rate'], 1)
        amt_hb_v = round((d['amt'] - prev['amt'])/prev['amt']*100, 1) if prev['amt'] > 0 else 0
        qty_hb_str = fmt_hb(qty_hb_v)
        rate_hb_str = fmt_hb(rate_hb_v)
        amt_hb_str = fmt_hb(amt_hb_v)

    tag_cls = f'b{m}'
    order_rows += f'''<tr>
      <td><span class="batch-tag {tag_cls}">{ml}</span></td>
      <td>{d["sku"]}</td>
      <td>{int(d["qty"])}</td><td>{qty_hb_str}</td>
      <td>${int(d["amt"])}</td><td>{amt_hb_str}%</td>
      <td style="color:#08845a;font-weight:600">{d["ordered"]}</td>
      <td style="color:#e07b24">{d["unorder"]}</td>
      <td style="color:#c0392b">{d["not_order"]}</td>
      <td><b>{d["rate"]}%</b></td><td>{rate_hb_str}</td>
    </tr>'''

html += f'''<div id="section-order" class="section-wrap" style="display:none">
  <div class="section">
    <h3>📦 出单情况分析</h3>
    <div class="sub-module">
      <h4>各批次3月出单情况（含销量、销售额及环比）</h4>
      <p class="note">Y=8日内有出单；N=注册8日内无出单但有历史出单；未出单=完全没出单</p>
      <div class="table-wrap">
      <table class="data-table">
        <thead><tr>
          <th>批次</th><th>SKU数</th>
          <th>3月销量</th><th>销量环比</th>
          <th>3月销售额</th><th>销售额环比</th>
          <th style="color:#a8e6cf">Y出单</th><th style="color:#ffd3a5">N出单</th><th style="color:#ffb3b3">未出单</th>
          <th>出单率(Y+N)</th><th>出单率环比</th>
        </tr></thead>
        <tbody>{order_rows}</tbody>
      </table>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h4>📊 各批次出单状态分布</h4><canvas id="chartOrderBatch"></canvas></div>
      <div class="chart-card"><h4>📈 各批次出单率趋势（三批对比）</h4><canvas id="chartOrderRate"></canvas></div>
      <div class="chart-card"><h4>💰 各批次销售额对比</h4><canvas id="chartOrderAmt"></canvas></div>
    </div>
  </div>
</div>
'''

# ========== 未出单市场 ==========
unorder_rows = ''
for label in unorder_dist:
    d = unorder_dist[label]
    unorder_rows += f'''<tr>
      <td><b>{label}</b></td>
      <td>{d["cnt_1"]}</td><td>{d["pct_1"]}%</td>
      <td>{d["cnt_2"]}</td><td>{d["pct_2"]}%</td>
      <td>{d["cnt_3"]}</td><td>{d["pct_3"]}%</td>
    </tr>'''

# 3月全量市场状态（不限未出单）
all_3 = [r for r in all_data if True]
from collections import Counter
status3_cnt = Counter(r['status3'] for r in all_3)
market_rows = ''
for k, v in sorted(status3_cnt.items(), key=lambda x: -x[1]):
    pct = round(v/len(all_3)*100, 1)
    market_rows += f'<tr><td>{k}</td><td>{v}</td><td>{pct}%</td></tr>'

html += f'''<div id="section-unorder" class="section-wrap" style="display:none">
  <div class="section">
    <h3>❌ 未出单市场状态分布</h3>
    <div class="sub-module">
      <h4>全量新品3月市场状态（156个SKU）</h4>
      <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>市场状态</th><th>数量</th><th>占比</th></tr></thead>
        <tbody>{market_rows}</tbody>
      </table>
      </div>
    </div>
    <div class="sub-module">
      <h4>各月未出单新品市场状态三月对比</h4>
      <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th rowspan="2">市场状态</th>
            <th colspan="2" class="m1">1月未出单</th>
            <th colspan="2" class="m2">2月未出单</th>
            <th colspan="2" class="m3">3月未出单</th>
          </tr>
          <tr>
            <th class="m1">数量</th><th class="m1">占比</th>
            <th class="m2">数量</th><th class="m2">占比</th>
            <th class="m3">数量</th><th class="m3">占比</th>
          </tr>
        </thead>
        <tbody>{unorder_rows}</tbody>
      </table>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h4>🥧 3月市场状态分布</h4><canvas id="chartMarketPie"></canvas></div>
      <div class="chart-card"><h4>📊 各月未出单状态对比</h4><canvas id="chartUnorderCompare"></canvas></div>
    </div>
  </div>
</div>
'''

# ========== 低占比新品 ==========
low_1 = [x for x in low_share if x['batch']=='1月']
low_2 = [x for x in low_share if x['batch']=='2月']
low_3 = [x for x in low_share if x['batch']=='3月']
html += f'''<div id="section-lowshare" class="section-wrap" style="display:none">
  <div class="section">
    <h3>📉 低市占比新品清单（阈值75% · 对手有出单）</h3>
    <p class="warning">⚠️ 筛选条件：自身3月市占比 &lt; 75% 且 3月对手出单 &gt; 0 | 共{len(low_share)}个SKU</p>
    <div style="margin-bottom:10px;">
      <select id="low-share-batch" onchange="renderLowShare()">
        <option value="all">全部批次（{len(low_share)}个SKU）</option>
        <option value="1月">1月新品（{len(low_1)}个SKU）</option>
        <option value="2月">2月新品（{len(low_2)}个SKU）</option>
        <option value="3月">3月新品（{len(low_3)}个SKU）</option>
      </select>
    </div>
    <div class="table-wrap">
    <table class="data-table">
    <thead><tr><th>批次</th><th>SKU</th><th>品类</th><th>分析人</th><th>拓展类型</th><th>3月销量</th><th>对手出单</th><th>市占比</th><th>8日出单</th><th>市场状态</th></tr></thead>
    <tbody id="lowmkt-tbody"></tbody>
    </table>
    </div>
  </div>
</div>
'''

# ========== 全量明细 ==========
html += f'''<div id="section-detail" class="section-wrap" style="display:none">
  <div class="section">
    <h3>📋 全量SKU明细（共156个SKU）</h3>
    <p class="note">绿色=3月8日已出单(Y) | 橙色=有出单历史(N) | 白色=完全未出单</p>
    <div style="margin-bottom:10px;">
      <select id="detail-batch" onchange="renderDetailTable()">
        <option value="all">全部批次（156个SKU）</option>
        <option value="1月">1月新品（53个SKU）</option>
        <option value="2月">2月新品（36个SKU）</option>
        <option value="3月">3月新品（67个SKU）</option>
      </select>
      &nbsp;
      <select id="detail-cat" onchange="renderDetailTable()">
        <option value="all">全部品类</option>
        {''.join(f'<option value="{c}">{c}</option>' for c in sorted(set(r["cat"] for r in all_data)))}
      </select>
      &nbsp;
      <select id="detail-analyst" onchange="renderDetailTable()">
        <option value="all">全部分析人</option>
        {''.join(f'<option value="{a}">{a}</option>' for a in sorted(set(r["analyst"] for r in all_data if r["analyst"])))}
      </select>
    </div>
    <div class="table-wrap">
    <table class="data-table">
    <thead>
      <tr>
        <th rowspan="2">销售编号</th>
        <th rowspan="2">SKU</th>
        <th rowspan="2">批次</th>
        <th rowspan="2">分析人</th>
        <th rowspan="2">品类</th>
        <th rowspan="2">拓展类型</th>
        <th rowspan="2">上架日期</th>
        <th rowspan="2">首次出单</th>
        <th colspan="4" class="m1">1月数据</th>
        <th colspan="4" class="m2">2月数据</th>
        <th colspan="4" class="m3">3月数据</th>
      </tr>
      <tr>
        <th class="m1">销量</th><th class="m1">销售额</th><th class="m1">8日</th><th class="m1">市场状态</th>
        <th class="m2">销量</th><th class="m2">销售额</th><th class="m2">8日</th><th class="m2">市场状态</th>
        <th class="m3">销量</th><th class="m3">销售额</th><th class="m3">8日</th><th class="m3">市场状态</th>
      </tr>
    </thead>
    <tbody id="detail-tbody"></tbody>
    </table>
    </div>
  </div>
</div>

</div><!-- main-content -->
</div><!-- container -->
'''

# ========== JavaScript 数据和逻辑 ==========
low_share_js = json.dumps(low_share, ensure_ascii=False)
all_data_js = json.dumps(all_data, ensure_ascii=False)
cat_data_js = json.dumps(cat_data, ensure_ascii=False)
analyst_data_js = json.dumps(analyst_data, ensure_ascii=False)
expand_data_js = json.dumps(expand_data, ensure_ascii=False)
batch_stats_js = json.dumps(batch_stats, ensure_ascii=False)
unorder_dist_js = json.dumps(unorder_dist, ensure_ascii=False)
status3_js = json.dumps(dict(status3_cnt), ensure_ascii=False)

html += f'''
<script>
var LOW_SHARE_DATA = {low_share_js};
var ALL_DATA = {all_data_js};
var CAT_DATA = {cat_data_js};
var ANALYST_DATA = {analyst_data_js};
var EXPAND_DATA = {expand_data_js};
var BATCH_STATS = {batch_stats_js};
var UNORDER_DIST = {unorder_dist_js};
var MARKET3 = {status3_js};

var C1 = '#adb5bd'; // 1月色
var C2 = '#667eea'; // 2月色
var C3 = '#e74c3c'; // 3月色
var CA = '#08845a'; // 绿
var CB = '#e07b24'; // 橙

// ========== 工具函数 ==========
function fmtHb(val, suffix) {{
  suffix = suffix || '';
  if (val === null || val === undefined) return '<span class="hb-flat">-</span>';
  var s = (val > 0 ? '+' : '') + val + suffix;
  var cls = val > 0 ? 'hb-up' : (val < 0 ? 'hb-down' : 'hb-flat');
  return '<span class="' + cls + '">' + s + '</span>';
}}

function mkBar(id, labels, datasets) {{
  var ctx = document.getElementById(id);
  if (!ctx) return null;
  return new Chart(ctx, {{
    type: 'bar',
    data: {{ labels: labels, datasets: datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: datasets.length > 1, position: 'top', labels: {{ font: {{ size: 10 }} }} }},
        tooltip: {{
          callbacks: {{
            label: function(ctx) {{
              var v = ctx.raw;
              if (typeof v === 'number') return ' ' + ctx.dataset.label + ': $' + v.toLocaleString();
              return ' ' + ctx.dataset.label + ': ' + v;
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ ticks: {{ font: {{ size: 10 }}, maxRotation: 30 }} }},
        y: {{ ticks: {{ font: {{ size: 10 }} }}, beginAtZero: true }}
      }}
    }}
  }});
}}

function mkLine(id, labels, datasets) {{
  var ctx = document.getElementById(id);
  if (!ctx) return null;
  return new Chart(ctx, {{
    type: 'line',
    data: {{ labels: labels, datasets: datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: true, position: 'top', labels: {{ font: {{ size: 10 }} }} }},
        tooltip: {{
          callbacks: {{
            label: function(ctx) {{
              var v = ctx.raw;
              if (typeof v === 'number') return ' ' + ctx.dataset.label + ': $' + v.toLocaleString();
              return ' ' + ctx.dataset.label + ': ' + v;
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ ticks: {{ font: {{ size: 10 }} }} }},
        y: {{ ticks: {{ font: {{ size: 10 }} }}, beginAtZero: true }}
      }}
    }}
  }});
}}

function mkPie(id, labels, vals, colors) {{
  var ctx = document.getElementById(id);
  if (!ctx) return null;
  return new Chart(ctx, {{
    type: 'pie',
    data: {{ labels: labels, datasets: [{{ data: vals, backgroundColor: colors }}] }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: 'right', labels: {{ font: {{ size: 10 }} }} }},
        tooltip: {{
          callbacks: {{
            label: function(ctx) {{
              var v = ctx.raw;
              return ' ' + ctx.label + ': $' + Number(v).toLocaleString();
            }}
          }}
        }}
      }}
    }}
  }});
}}

// ========== 渲染低占比新品 ==========
function renderLowShare() {{
  var batch = document.getElementById('low-share-batch').value;
  var filtered = batch === 'all' ? LOW_SHARE_DATA : LOW_SHARE_DATA.filter(function(d){{ return d.batch === batch; }});
  var html = '';
  for (var i = 0; i < filtered.length; i++) {{
    var d = filtered[i];
    var shareColor = d.share < 30 ? '#c0392b' : (d.share < 50 ? '#e07b24' : '#888');
    var orderColor = d.order === 'Y' ? '#08845a' : (d.order === 'N' ? '#e07b24' : '#c0392b');
    var batchCls = d.batch === '1月' ? 'b1' : (d.batch === '2月' ? 'b2' : 'b3');
    html += '<tr><td><span class="batch-tag ' + batchCls + '">' + d.batch + '</span></td>' +
      '<td style="text-align:left;font-weight:600">' + d.sku + '</td>' +
      '<td>' + d.cat + '</td><td>' + d.analyst + '</td><td>' + d.expand + '</td>' +
      '<td>' + d.qty + '</td><td>' + d.comp + '</td>' +
      '<td style="color:' + shareColor + ';font-weight:700">' + d.share + '%</td>' +
      '<td style="color:' + orderColor + ';font-weight:600">' + d.order + '</td>' +
      '<td>' + d.status + '</td></tr>';
  }}
  document.getElementById('lowmkt-tbody').innerHTML = html;
}}

// ========== 渲染全量明细 ==========
function renderDetailTable() {{
  var batch = document.getElementById('detail-batch').value;
  var cat = document.getElementById('detail-cat').value;
  var analyst = document.getElementById('detail-analyst').value;
  var filtered = ALL_DATA.filter(function(d) {{
    return (batch === 'all' || d.batch === batch) &&
           (cat === 'all' || d.cat === cat) &&
           (analyst === 'all' || d.analyst === analyst);
  }});
  var html = '';
  for (var i = 0; i < filtered.length; i++) {{
    var d = filtered[i];
    var bgClass = d.order3 === 'Y' ? 'row-ordered' : (d.order3 === 'N' ? 'row-unorder' : '');
    var batchCls = d.batch === '1月' ? 'b1' : (d.batch === '2月' ? 'b2' : 'b3');
    var s3color = d.share3 < 50 ? '#c0392b' : (d.share3 < 75 ? '#e07b24' : '#08845a');
    html += '<tr class="' + bgClass + '">' +
      '<td>' + d.sku_id + '</td>' +
      '<td style="text-align:left;font-weight:600">' + d.sku + '</td>' +
      '<td><span class="batch-tag ' + batchCls + '">' + d.batch + '</span></td>' +
      '<td>' + d.analyst + '</td>' +
      '<td>' + d.cat + '</td>' +
      '<td>' + d.expand + '</td>' +
      '<td>' + d.onshelf + '</td>' +
      '<td>' + d.first_order + '</td>' +
      '<td>' + d.qty1 + '</td><td>$' + d.amt1 + '</td><td>' + d.order1 + '</td><td>' + d.status1 + '</td>' +
      '<td>' + d.qty2 + '</td><td>$' + d.amt2 + '</td><td>' + d.order2 + '</td><td>' + d.status2 + '</td>' +
      '<td>' + d.qty3 + '</td><td>$' + d.amt3 + '</td>' +
      '<td style="color:' + (d.order3==='Y'?'#08845a':d.order3==='N'?'#e07b24':'#c0392b') + ';font-weight:600">' + d.order3 + '</td>' +
      '<td style="color:' + s3color + '">' + (d.share3 > 0 ? d.share3 + '%' : '-') + '</td>' +
    '</tr>';
  }}
  if (!html) html = '<tr><td colspan="20" style="text-align:center;color:#888;padding:20px">暂无数据</td></tr>';
  document.getElementById('detail-tbody').innerHTML = html;
}}

// ========== 图表渲染 ==========
function renderAllCharts() {{
  var cats = Object.keys(CAT_DATA);
  var analysts = Object.keys(ANALYST_DATA);
  var expands = Object.keys(EXPAND_DATA);

  // 总览图表
  mkBar('chartBatchQty', ['1月批次','2月批次','3月批次'], [
    {{ label: '3月销量', data: [BATCH_STATS['1'].qty, BATCH_STATS['2'].qty, BATCH_STATS['3'].qty], backgroundColor: [C1,C2,C3] }},
    {{ label: '出单率%', data: [BATCH_STATS['1'].rate, BATCH_STATS['2'].rate, BATCH_STATS['3'].rate], backgroundColor: 'rgba(231,76,60,0.3)', type:'line', yAxisID:'y1', borderColor:C3, tension:0.3 }}
  ]);

  mkBar('chartCategoryQty', cats, [
    {{ label: '1月新品', data: cats.map(function(c){{return CAT_DATA[c].qty_1;}}), backgroundColor: C1 }},
    {{ label: '2月新品', data: cats.map(function(c){{return CAT_DATA[c].qty_2;}}), backgroundColor: C2 }},
    {{ label: '3月新品', data: cats.map(function(c){{return CAT_DATA[c].qty_3;}}), backgroundColor: C3 }}
  ]);

  mkLine('chartCategoryRate', cats, [
    {{ label: '1月出单率', data: cats.map(function(c){{return CAT_DATA[c].rate_1;}}), borderColor: C1, backgroundColor: C1+'33', tension:0.3 }},
    {{ label: '2月出单率', data: cats.map(function(c){{return CAT_DATA[c].rate_2;}}), borderColor: C2, backgroundColor: C2+'33', tension:0.3 }},
    {{ label: '3月出单率', data: cats.map(function(c){{return CAT_DATA[c].rate_3;}}), borderColor: C3, backgroundColor: C3+'33', tension:0.3 }}
  ]);

  mkBar('chartAnalystQty', analysts, [
    {{ label: '1月新品', data: analysts.map(function(a){{return ANALYST_DATA[a].qty_1;}}), backgroundColor: C1 }},
    {{ label: '2月新品', data: analysts.map(function(a){{return ANALYST_DATA[a].qty_2;}}), backgroundColor: C2 }},
    {{ label: '3月新品', data: analysts.map(function(a){{return ANALYST_DATA[a].qty_3;}}), backgroundColor: C3 }}
  ]);

  mkBar('chartExpandQty', expands, [
    {{ label: '1月新品', data: expands.map(function(e){{return EXPAND_DATA[e].qty_1;}}), backgroundColor: C1 }},
    {{ label: '2月新品', data: expands.map(function(e){{return EXPAND_DATA[e].qty_2;}}), backgroundColor: C2 }},
    {{ label: '3月新品', data: expands.map(function(e){{return EXPAND_DATA[e].qty_3;}}), backgroundColor: C3 }}
  ]);

  mkBar('chartOrderDist', ['1月批次','2月批次','3月批次'], [
    {{ label: 'Y出单', data: [BATCH_STATS['1'].ordered, BATCH_STATS['2'].ordered, BATCH_STATS['3'].ordered], backgroundColor: CA }},
    {{ label: 'N出单', data: [BATCH_STATS['1'].unorder, BATCH_STATS['2'].unorder, BATCH_STATS['3'].unorder], backgroundColor: CB }},
    {{ label: '未出单', data: [BATCH_STATS['1'].not_order, BATCH_STATS['2'].not_order, BATCH_STATS['3'].not_order], backgroundColor: '#c0392b' }}
  ]);

  // 品线图表
  mkBar('chartCatQty', cats, [
    {{ label: '1月新品', data: cats.map(function(c){{return CAT_DATA[c].qty_1;}}), backgroundColor: C1 }},
    {{ label: '2月新品', data: cats.map(function(c){{return CAT_DATA[c].qty_2;}}), backgroundColor: C2 }},
    {{ label: '3月新品', data: cats.map(function(c){{return CAT_DATA[c].qty_3;}}), backgroundColor: C3 }}
  ]);

  mkBar('chartCatAmt', cats, [
    {{ label: '1月销售额', data: cats.map(function(c){{return CAT_DATA[c].amt_1;}}), backgroundColor: C1+'bb' }},
    {{ label: '2月销售额', data: cats.map(function(c){{return CAT_DATA[c].amt_2;}}), backgroundColor: C2+'bb' }},
    {{ label: '3月销售额', data: cats.map(function(c){{return CAT_DATA[c].amt_3;}}), backgroundColor: C3+'bb' }}
  ]);

  mkLine('chartCatRate', cats, [
    {{ label: '1月', data: cats.map(function(c){{return CAT_DATA[c].rate_1;}}), borderColor: C1, tension:0.3 }},
    {{ label: '2月', data: cats.map(function(c){{return CAT_DATA[c].rate_2;}}), borderColor: C2, tension:0.3 }},
    {{ label: '3月', data: cats.map(function(c){{return CAT_DATA[c].rate_3;}}), borderColor: C3, tension:0.3 }}
  ]);

  mkBar('chartCatShare', cats, [
    {{ label: '1月市占比%', data: cats.map(function(c){{return CAT_DATA[c].share_1;}}), backgroundColor: C1+'bb' }},
    {{ label: '2月市占比%', data: cats.map(function(c){{return CAT_DATA[c].share_2;}}), backgroundColor: C2+'bb' }},
    {{ label: '3月市占比%', data: cats.map(function(c){{return CAT_DATA[c].share_3;}}), backgroundColor: C3+'bb' }}
  ]);

  // 分析人图表
  mkBar('chartAnalystQty2', analysts, [
    {{ label: '1月', data: analysts.map(function(a){{return ANALYST_DATA[a].qty_1;}}), backgroundColor: C1 }},
    {{ label: '2月', data: analysts.map(function(a){{return ANALYST_DATA[a].qty_2;}}), backgroundColor: C2 }},
    {{ label: '3月', data: analysts.map(function(a){{return ANALYST_DATA[a].qty_3;}}), backgroundColor: C3 }}
  ]);

  mkBar('chartAnalystAmt', analysts, [
    {{ label: '1月销售额', data: analysts.map(function(a){{return ANALYST_DATA[a].amt_1;}}), backgroundColor: C1+'bb' }},
    {{ label: '2月销售额', data: analysts.map(function(a){{return ANALYST_DATA[a].amt_2;}}), backgroundColor: C2+'bb' }},
    {{ label: '3月销售额', data: analysts.map(function(a){{return ANALYST_DATA[a].amt_3;}}), backgroundColor: C3+'bb' }}
  ]);

  mkLine('chartAnalystRate', analysts, [
    {{ label: '1月出单率', data: analysts.map(function(a){{return ANALYST_DATA[a].rate_1;}}), borderColor: C1, tension:0.3 }},
    {{ label: '2月出单率', data: analysts.map(function(a){{return ANALYST_DATA[a].rate_2;}}), borderColor: C2, tension:0.3 }},
    {{ label: '3月出单率', data: analysts.map(function(a){{return ANALYST_DATA[a].rate_3;}}), borderColor: C3, tension:0.3 }}
  ]);

  mkBar('chartAnalystFreq', analysts, [
    {{ label: '1月平均频次', data: analysts.map(function(a){{return ANALYST_DATA[a].freq_1;}}), backgroundColor: C1 }},
    {{ label: '2月平均频次', data: analysts.map(function(a){{return ANALYST_DATA[a].freq_2;}}), backgroundColor: C2 }},
    {{ label: '3月平均频次', data: analysts.map(function(a){{return ANALYST_DATA[a].freq_3;}}), backgroundColor: C3 }}
  ]);

  // 拓展类型图表
  mkBar('chartExpandQty2', expands, [
    {{ label: '1月', data: expands.map(function(e){{return EXPAND_DATA[e].qty_1;}}), backgroundColor: C1 }},
    {{ label: '2月', data: expands.map(function(e){{return EXPAND_DATA[e].qty_2;}}), backgroundColor: C2 }},
    {{ label: '3月', data: expands.map(function(e){{return EXPAND_DATA[e].qty_3;}}), backgroundColor: C3 }}
  ]);

  mkLine('chartExpandRate', expands, [
    {{ label: '1月', data: expands.map(function(e){{return EXPAND_DATA[e].rate_1;}}), borderColor: C1, tension:0.3 }},
    {{ label: '2月', data: expands.map(function(e){{return EXPAND_DATA[e].rate_2;}}), borderColor: C2, tension:0.3 }},
    {{ label: '3月', data: expands.map(function(e){{return EXPAND_DATA[e].rate_3;}}), borderColor: C3, tension:0.3 }}
  ]);

  // 出单情况图表
  mkBar('chartOrderBatch', ['1月批次','2月批次','3月批次'], [
    {{ label: 'Y出单', data: [BATCH_STATS['1'].ordered, BATCH_STATS['2'].ordered, BATCH_STATS['3'].ordered], backgroundColor: CA }},
    {{ label: 'N出单', data: [BATCH_STATS['1'].unorder, BATCH_STATS['2'].unorder, BATCH_STATS['3'].unorder], backgroundColor: CB }},
    {{ label: '未出单', data: [BATCH_STATS['1'].not_order, BATCH_STATS['2'].not_order, BATCH_STATS['3'].not_order], backgroundColor: '#c0392b' }}
  ]);

  mkLine('chartOrderRate', ['1月批次','2月批次','3月批次'], [
    {{ label: '出单率(Y+N)%', data: [BATCH_STATS['1'].rate, BATCH_STATS['2'].rate, BATCH_STATS['3'].rate], borderColor: C3, backgroundColor: C3+'33', tension:0.3, fill:true }}
  ]);

  mkBar('chartOrderAmt', ['1月批次','2月批次','3月批次'], [
    {{ label: '3月销售额', data: [BATCH_STATS['1'].amt, BATCH_STATS['2'].amt, BATCH_STATS['3'].amt], backgroundColor: [C1,C2,C3] }}
  ]);

  // 未出单图表
  var mkLabels = Object.keys(MARKET3);
  var mkVals = mkLabels.map(function(k){{return MARKET3[k];}});
  var mkColors = ['#08845a','#adb5bd','#c0392b','#e07b24','#667eea','#f1c40f'];
  mkPie('chartMarketPie', mkLabels, mkVals, mkColors);

  var uLabels = Object.keys(UNORDER_DIST);
  mkBar('chartUnorderCompare', uLabels, [
    {{ label: '1月', data: uLabels.map(function(k){{return UNORDER_DIST[k].cnt_1;}}), backgroundColor: C1 }},
    {{ label: '2月', data: uLabels.map(function(k){{return UNORDER_DIST[k].cnt_2;}}), backgroundColor: C2 }},
    {{ label: '3月', data: uLabels.map(function(k){{return UNORDER_DIST[k].cnt_3;}}), backgroundColor: C3 }}
  ]);
}}

// ========== 导航切换 ==========
var sections = ['overview','pinxian','analyst','expand','order','unorder','lowshare','detail'];
var chartsRendered = false;

function showSection(name, el) {{
  for (var i = 0; i < sections.length; i++) {{
    var s = sections[i];
    var wrap = document.getElementById('section-' + s);
    if (wrap) wrap.style.display = s === name ? 'block' : 'none';
  }}
  var links = document.querySelectorAll('.sidebar a');
  for (var j = 0; j < links.length; j++) links[j].classList.remove('active');
  if (el) el.classList.add('active');
}}

// ========== 初始化 ==========
renderLowShare();
renderDetailTable();
renderAllCharts();
</script>
</body>
</html>'''

# 写出文件
out_path = '新品月报_2026年3月_增强版.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'已生成: {out_path}')
print(f'文件大小: {len(html)//1024} KB')
