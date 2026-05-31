"""
给HTML看板中所有表格添加合计行(tfoot)
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html'
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ============================================================
# 1. 品线维度表 (t1-cat-table) — 加tfoot合计行
# ============================================================
old = "catHtml += '</tbody></table>';"
new = """catHtml += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + categoryRevenueData.reduce(function(s,d){return s+d.curSku;},0) + '</td><td>' + categoryRevenueData.reduce(function(s,d){return s+d.curNewSku;},0) + '</td><td>' + fmtNum(categoryRevenueData.reduce(function(s,d){return s+d.curSalesQty;},0)) + '</td><td>' + fmtNum(categoryRevenueData.reduce(function(s,d){return s+d.prevSalesQty;},0)) + '</td><td>-</td><td>' + fmtMoney(categoryRevenueData.reduce(function(s,d){return s+d.curRevenue;},0)) + '</td><td>' + fmtMoney(categoryRevenueData.reduce(function(s,d){return s+d.prevRevenue;},0)) + '</td><td>-</td><td>-</td><td>-</td><td>-</td></tr></tfoot></table>';"""
html = html.replace(old, new, 1)
changes += 1

# ============================================================
# 2. 分析人维度表 (t1-an-table) — 加tfoot合计行
# ============================================================
old2 = "anHtml += '</tbody></table>';"
new2 = """anHtml += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + analystRevenueData.reduce(function(s,d){return s+d.curSku;},0) + '</td><td>' + analystRevenueData.reduce(function(s,d){return s+d.curNewSku;},0) + '</td><td>' + fmtNum(analystRevenueData.reduce(function(s,d){return s+d.curSalesQty;},0)) + '</td><td>' + fmtNum(analystRevenueData.reduce(function(s,d){return s+d.prevSalesQty;},0)) + '</td><td>-</td><td>' + fmtMoney(analystRevenueData.reduce(function(s,d){return s+d.curRevenue;},0)) + '</td><td>' + fmtMoney(analystRevenueData.reduce(function(s,d){return s+d.prevRevenue;},0)) + '</td><td>-</td><td>-</td><td>-</td><td>-</td></tr></tfoot></table>';"""
html = html.replace(old2, new2, 1)
changes += 1

# ============================================================
# 3. 拓展类型表 (t1-exp-table) — 加tfoot合计行
# ============================================================
old3 = "expHtml += '</tbody></table>';"
new3 = """expHtml += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + expandTypeData.reduce(function(s,d){return s+d.curSku;},0) + '</td><td>' + expandTypeData.reduce(function(s,d){return s+d.prevSku;},0) + '</td><td>' + expandTypeData.reduce(function(s,d){return s+d.curSalesSku;},0) + '</td><td>-</td><td>-</td><td>' + fmtNum(expandTypeData.reduce(function(s,d){return s+d.curSalesQty;},0)) + '</td><td>' + fmtNum(expandTypeData.reduce(function(s,d){return s+d.prevSalesQty;},0)) + '</td><td>-</td><td>' + fmtMoney(expandTypeData.reduce(function(s,d){return s+d.curRevenue;},0)) + '</td><td>' + fmtMoney(expandTypeData.reduce(function(s,d){return s+d.prevRevenue;},0)) + '</td><td>-</td></tr></tfoot></table>';"""
html = html.replace(old3, new3, 1)
changes += 1

# ============================================================
# 4. 市场状态明细表 (t2-mkt-table) — 加tfoot合计行
# ============================================================
old4 = "mh += '</tbody></table></div>';"
new4 = """mh += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + mktDistOverall.curTotal + '</td><td>100%</td><td>' + mktDistOverall.prevTotal + '</td><td>100%</td><td>' + (mktDistOverall.curTotal - mktDistOverall.prevTotal >= 0 ? '+' : '') + (mktDistOverall.curTotal - mktDistOverall.prevTotal) + '</td></tr></tfoot></table></div>';"""
html = html.replace(old4, new4, 1)
changes += 1

# ============================================================
# 5. 货值明细表 (t2-price-table) — 加tfoot合计行
# ============================================================
old5 = "ph += '</tbody></table></div>';"
new5 = """ph += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + (priceOverview.distribution.reduce(function(s,d){return s+d.count;},0)) + '</td><td>100%</td></tr></tfoot></table></div>';"""
html = html.replace(old5, new5, 1)
changes += 1

# ============================================================
# 6. 市占比分布表 (t2-share-tier-table) — 加tfoot合计行
# ============================================================
old6 = "sh += '</tbody></table></div>';"
new6 = """sh += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + shareTierOverview.byCategory.reduce(function(s,d){return s+d.total;},0) + '</td><td>' + shareTierOverview.byCategory.reduce(function(s,d){return s+d.high;},0) + '</td><td>' + shareTierOverview.byCategory.reduce(function(s,d){return s+d.mid;},0) + '</td><td>' + shareTierOverview.byCategory.reduce(function(s,d){return s+d.low;},0) + '</td></tr></tfoot></table></div>';"""
html = html.replace(old6, new6, 1)
changes += 1

# ============================================================
# 7. PLP分析人维度表 (t4-plp-an) — 修改renderPlpDim函数加合计
# ============================================================
old7 = "h += '</tbody></table>';"
new7 = """var _totalCost = data.reduce(function(s,d){return s+parseFloat(d.cost)||0;},0);
    var _totalRev = data.reduce(function(s,d){return s+parseFloat(d.revenue)||0;},0);
    var _totalROAS = _totalCost > 0 ? (_totalRev/_totalCost).toFixed(2) : '-';
    h += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + data.reduce(function(s,d){return s+d.campaignCount;},0) + '</td><td>' + data.reduce(function(s,d){return s+d.linkCount;},0) + '</td><td>' + fmtNum(data.reduce(function(s,d){return s+d.impression;},0)) + '</td><td>' + fmtNum(data.reduce(function(s,d){return s+d.click;},0)) + '</td><td>' + data.reduce(function(s,d){return s+d.sold;},0) + '</td><td>' + fmtMoney(_totalCost) + '</td><td>' + fmtMoney(_totalRev) + '</td><td>' + _totalROAS + '</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr></tfoot></table>';"""
html = html.replace(old7, new7, 1)
changes += 1

# ============================================================
# 8. PLG费率分布表 (t4-plg) — 加tfoot合计行
# ============================================================
old8 = "plgHtml += '</tbody></table>';"
new8 = """plgHtml += '</tbody><tfoot><tr class="total-row"><td>合计</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.total;},0) + '</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.plpAndPlgBoth;},0) + '</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.singleLinkPlpPlg;},0) + '</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.plgOnly;},0) + '</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.plpOnly;},0) + '</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.noAd;},0) + '</td><td>' + pg.byAnalyst.reduce(function(s,d){return s+d.plpDisabledNoSale;},0) + '</td></tr></tfoot></table>';"""
html = html.replace(old8, new8, 1)
changes += 1

# ============================================================
# 9. PLG按分析人表 (t4-plg-an) — 已有合计行(在JS中手动写了)
# ============================================================

print(f"共修改 {changes} 处")

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("完成！已给HTML看板表格添加合计行")
