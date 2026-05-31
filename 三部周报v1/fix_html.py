# -*- coding: utf-8 -*-
import re

html_path = 'C:/Users/Administrator/Desktop/三部周报v1/New project 2-新品板块已放入/src/modules/newProductStatus/新品板块_4.30-5.6_v3.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix block1: single-quoted multiline string -> backtick template literal on single line
old1 = """  const block1 = `【核心指标】
本周期累计在售新品${s.total}款，出单${s.yCount}款，出单率${soldRate}（环比${prevWeekKpi.salesQtyChange}）。总销量${fmtNum(totalQty)}件（环比${prevWeekKpi.salesQtyChange}），总销售额${fmtMoney(totalRev)}（环比${prevWeekKpi.revenueChange}）。分析及时率${timelyRate}（环比${timelinessData.total.change}）。`;"""
new1 = "  const block1 = `【核心指标】\\n本周期累计在售新品${s.total}款，出单${s.yCount}款，出单率${soldRate}（环比${prevWeekKpi.salesQtyChange}）。总销量${fmtNum(totalQty)}件（环比${prevWeekKpi.salesQtyChange}），总销售额${fmtMoney(totalRev)}（环比${prevWeekKpi.revenueChange}）。分析及时率${timelyRate}（环比${timelinessData.total.change}）。`;"

# Fix block2
old2 = """  const block2 = `【风险预警】
` + risks.map(r => r.text).join('
');"""
new2 = "  const block2 = `【风险预警】\\n` + risks.map(r => r.text).join('\\n');"

# Fix block3
old3 = """  const block3 = `【主要发现】
` + findings.join('
');"""
new3 = "  const block3 = `【主要发现】\\n` + findings.join('\\n');"

# Fix block4
old4 = """  const block4 = `【品类维度】
` + categoryRevenueData.map(r => r.category+'：SKU '+Math.round(r.curSku)+'，销量'+fmtNum(r.curSalesQty)+'件（'+r.salesQtyChange+'），销售额'+fmtMoney(r.curRevenue)+'（'+r.revenueChange+'）').join('
');"""
new4 = "  const block4 = `【品类维度】\\n` + categoryRevenueData.map(r => r.category+'：SKU '+Math.round(r.curSku)+'，销量'+fmtNum(r.curSalesQty)+'件（'+r.salesQtyChange+'），销售额'+fmtMoney(r.curRevenue)+'（'+r.revenueChange+'）').join('\\n');"

# Fix block5
old5 = """  const block5 = `【下周重点动作】
` + actions.join('
');"""
new5 = "  const block5 = `【下周重点动作】\\n` + actions.join('\\n');"

for old, new in [(old1, new1), (old2, new2), (old3, new3), (old4, new4), (old5, new5)]:
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed block')
    else:
        print(f'Block not found (may already be fixed or different format)')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
