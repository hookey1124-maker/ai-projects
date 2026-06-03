import pandas as pd
import json

# 读取所有数据
file1 = r'c:\Users\Hardy\ai-projects\三部周报v1\新品周报全流程\新品检查周源数据和PLP数据.xlsx'
file3 = r'c:\Users\Hardy\ai-projects\三部周报v1\新品周报全流程\新品周报数据_4.30-5.6.xlsx'

# ========== 1. 四三累计数据（109条）==========
df_cum43 = pd.read_excel(file1, sheet_name='四三数据累计')
key_cols = ['SKU', '实际上架日期', '首次出单日期', '4月分析人', '品类', '产品拓展',
            '4.30-5.6销量', '4.30-5.6销售额', '5.6对手销量', '5.6市占比', '5.6市场状态', '5.6 8日出单情况']
df_cum43_filtered = df_cum43[key_cols].copy()
df_cum43_filtered.columns = ['sku', 'launchDate', 'firstSaleDate', 'analyst', 'category', 'expandType',
                              'salesQty', 'revenue', 'competitorQty', 'marketShare', 'marketStatus', 'ord8Status']
df_cum43_filtered['salesQty'] = pd.to_numeric(df_cum43_filtered['salesQty'], errors='coerce').fillna(0)
df_cum43_filtered['revenue'] = pd.to_numeric(df_cum43_filtered['revenue'], errors='coerce').fillna(0)
df_cum43_filtered['competitorQty'] = pd.to_numeric(df_cum43_filtered['competitorQty'], errors='coerce').fillna(0)
df_cum43_filtered['marketShare'] = pd.to_numeric(df_cum43_filtered['marketShare'], errors='coerce').fillna(0)
df_cum43_filtered['launchDate'] = df_cum43_filtered['launchDate'].astype(str).str[:10]
df_cum43_filtered['firstSaleDate'] = df_cum43_filtered['firstSaleDate'].astype(str).str[:10]

cum43_data = []
for _, row in df_cum43_filtered.iterrows():
    cum43_data.append({
        "SKU": row['sku'],
        "实际上架日期": row['launchDate'],
        "首次出单日期": row['firstSaleDate'],
        "4月分析人": row['analyst'],
        "品类": row['category'],
        "产品拓展": row['expandType'],
        "4.30-5.6销量": int(row['salesQty']),
        "4.30-5.6销售额": float(row['revenue']),
        "5.6对手销量": int(row['competitorQty']),
        "5.6市占比": round(float(row['marketShare']) * 100, 1),
        "5.6市场状态": row['marketStatus'],
        "5.6 8日出单情况": row['ord8Status']
    })

cum43_stats = {
    "total": len(cum43_data),
    "yCount": len([x for x in cum43_data if x["5.6 8日出单情况"] == "Y"]),
    "nCount": len([x for x in cum43_data if x["5.6 8日出单情况"] == "N"]),
    "unCount": len([x for x in cum43_data if x["5.6 8日出单情况"] == "未出单"]),
    "normalCount": len([x for x in cum43_data if x["5.6市场状态"] == "正常"]),
    "competitiveCount": len([x for x in cum43_data if x["5.6市场状态"] == "竞争无优势"]),
    "noMarketCount": len([x for x in cum43_data if x["5.6市场状态"] == "无市场"])
}

print(f"四三累计: {cum43_stats}")

# ========== 2. 低占比新品数据（39条）==========
df_low = pd.read_excel(file3, sheet_name='低占比新品')
df_low_data = df_low.iloc[1:].copy()

low_share_data = []
for _, row in df_low_data.iterrows():
    low_share_data.append({
        "salesCode": str(row.iloc[0]),
        "sku": str(row.iloc[1]),
        "launchDate": str(row.iloc[2])[:10] if pd.notna(row.iloc[2]) else "",
        "analyst": str(row.iloc[3]),
        "category": str(row.iloc[4]),
        "expandType": str(row.iloc[5]),
        "curSalesQty": int(row.iloc[6]) if pd.notna(row.iloc[6]) else 0,
        "salesQtyChange": str(row.iloc[7]) if pd.notna(row.iloc[7]) else "-",
        "curRevenue": float(row.iloc[8]) if pd.notna(row.iloc[8]) else 0,
        "revenueChange": str(row.iloc[9]) if pd.notna(row.iloc[9]) else "-",
        "prevCompetitorQty": int(row.iloc[10]) if pd.notna(row.iloc[10]) else 0,
        "curCompetitorQty": int(row.iloc[11]) if pd.notna(row.iloc[11]) else 0,
        "competitorQtyChange": str(row.iloc[12]) if pd.notna(row.iloc[12]) else "-",
        "prevMarketShare": str(row.iloc[13]) if pd.notna(row.iloc[13]) else "-",
        "curMarketShare": str(row.iloc[14]) if pd.notna(row.iloc[14]) else "-",
        "marketShareChange": str(row.iloc[15]) if pd.notna(row.iloc[15]) else "-",
        "cur8dStatus": str(row.iloc[16]) if pd.notna(row.iloc[16]) else "-",
        "cur7dFreqTag": str(row.iloc[17]) if pd.notna(row.iloc[17]) else "-",
        "prevMarketStatus": str(row.iloc[18]) if pd.notna(row.iloc[18]) else "-",
        "curOperation": str(row.iloc[19]) if pd.notna(row.iloc[19]) else "-",
        "curMarketStatus": str(row.iloc[20]) if pd.notna(row.iloc[20]) else "-",
        "plpEnabled": str(row.iloc[21]) if pd.notna(row.iloc[21]) else "N",
        "plgFee": str(row.iloc[22]) if pd.notna(row.iloc[22]) else "0%"
    })

print(f"低占比新品: {len(low_share_data)} 条")

# ========== 3. PLP数据（包含品线维度和分析人维度）==========
# 修正ACOAS为百分比格式 (0.042377 -> "4.24%")
def format_acoas(val):
    """将小数转换为百分比格式"""
    try:
        f = float(val)
        return f"{f * 100:.2f}%"
    except:
        return str(val) if val else "-"

plp_total = {
    "campaignCount": 42, "linkCount": 53, "impression": 119686, "click": 429, "sold": 27,
    "cost": 272.56, "revenue": 1754.44, "roas": "6.44", "cvr": "6.29%", "ctr": "0.36%",
    "cpc": "$0.64", "cpa": "$10.09", "acos": "15.54%", "acoas": "4.24%"  # 修正为百分比
}
plp_prev_total = {
    "campaignCount": 47, "linkCount": 63, "impression": 139169, "click": 425, "sold": 40,
    "cost": 240.26, "revenue": 3401.59, "roas": "14.16", "cvr": "9.41%", "ctr": "0.31%",
    "cpc": "$0.57", "cpa": "$6.01", "acos": "7.06%", "acoas": "2.54%"  # 修正为百分比
}

# 品线维度
plp_categories = [
    {"category": "车门系统", "campaignCount": 6, "linkCount": 8, "impression": 64284, "click": 94, "sold": 2, "cost": 65.31, "revenue": 79.32, "roas": "1.21", "cvr": "2.13%", "ctr": "0.15%", "cpc": "$0.69", "cpa": "$32.65", "acos": "82.34%", "acoas": "6.05%"},
    {"category": "车身外扩件", "campaignCount": 7, "linkCount": 7, "impression": 36778, "click": 138, "sold": 1, "cost": 115.38, "revenue": 135.31, "roas": "1.17", "cvr": "0.72%", "ctr": "0.38%", "cpc": "$0.84", "cpa": "$115.38", "acos": "85.27%", "acoas": "72.11%"},
    {"category": "挡泥板", "campaignCount": 5, "linkCount": 5, "impression": 1259, "click": 12, "sold": 1, "cost": 8.81, "revenue": 129, "roas": "14.64", "cvr": "8.33%", "ctr": "0.95%", "cpc": "$0.73", "cpa": "$8.81", "acos": "6.83%", "acoas": "2.50%"},
    {"category": "机盖及附件", "campaignCount": 5, "linkCount": 5, "impression": 1788, "click": 49, "sold": 12, "cost": 17.21, "revenue": 720.98, "roas": "41.89", "cvr": "24.49%", "ctr": "2.74%", "cpc": "$0.35", "cpa": "$1.43", "acos": "2.39%", "acoas": "1.31%"},
    {"category": "牌照板支架", "campaignCount": 1, "linkCount": 1, "impression": 527, "click": 6, "sold": 1, "cost": 2.32, "revenue": 48.71, "roas": "21", "cvr": "16.67%", "ctr": "1.14%", "cpc": "$0.39", "cpa": "$2.32", "acos": "4.76%", "acoas": "1.66%"},
    {"category": "其他", "campaignCount": 10, "linkCount": 15, "impression": 6674, "click": 80, "sold": 2, "cost": 45.52, "revenue": 320.06, "roas": "7.03", "cvr": "2.5%", "ctr": "1.2%", "cpc": "$0.57", "cpa": "$22.76", "acos": "14.22%", "acoas": "2.44%"},
    {"category": "饰条", "campaignCount": 8, "linkCount": 12, "impression": 8376, "click": 50, "sold": 8, "cost": 18.01, "revenue": 321.06, "roas": "17.83", "cvr": "16.0%", "ctr": "0.6%", "cpc": "$0.36", "cpa": "$2.25", "acos": "5.61%", "acoas": "-"},
]

# 分析人维度 - 从原始Excel读取
# 假设sheet名称为"PLP分析人维度"
try:
    df_plp_analyst = pd.read_excel(file1, sheet_name='PLP分析人维度')
    plp_analysts = []
    for _, row in df_plp_analyst.iterrows():
        name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        if name and name not in ['姓名', '分析人', '合计', '总计', '上周']:
            plp_analysts.append({
                "analyst": name,
                "sku": int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0,
                "campaignCount": int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0,
                "impression": int(row.iloc[3]) if pd.notna(row.iloc[3]) else 0,
                "click": int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0,
                "sold": int(row.iloc[5]) if pd.notna(row.iloc[5]) else 0,
                "cost": float(row.iloc[6]) if pd.notna(row.iloc[6]) else 0,
                "revenue": float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0,
                "roas": str(round(float(row.iloc[8]), 2)) if pd.notna(row.iloc[8]) else "-",
                "cvr": str(row.iloc[9]) if pd.notna(row.iloc[9]) else "-",
                "ctr": str(row.iloc[10]) if pd.notna(row.iloc[10]) else "-",
                "cpc": f"${row.iloc[11]:.2f}" if pd.notna(row.iloc[11]) else "-",
                "cpa": f"${row.iloc[12]:.2f}" if pd.notna(row.iloc[12]) else "-",
                "acos": str(row.iloc[13]) if pd.notna(row.iloc[13]) else "-",
                "acoas": str(row.iloc[14]) if pd.notna(row.iloc[14]) else "-"
            })
    print(f"PLP分析人维度: {len(plp_analysts)} 条")
except Exception as e:
    print(f"读取PLP分析人维度失败: {e}")
    plp_analysts = []

print(f"PLP品线维度: {len(plp_categories)} 条")

# ========== 4. 有对手未出单数据（修正 -36 错误）==========
# 从 cum43Data 中提取有对手但未出单的新品
has_competitor_unsold = [x for x in cum43_data if x["5.6对手销量"] > 0 and x["5.6 8日出单情况"] == "未出单"]
unsold_has_competitor = {
    "total": len(has_competitor_unsold),
    "prevTotal": 15,  # 上周数据，需要根据实际情况调整
    "change": len(has_competitor_unsold) - 15,
    "reasons": [
        {"reason": "竞争无优势", "curCount": len([x for x in has_competitor_unsold if x["5.6市场状态"] == "竞争无优势"]), "curRatio": "100.0%", "prevCount": 15, "prevRatio": "100.0%", "change": len(has_competitor_unsold) - 15},
    ],
    "byAnalyst": [],
    "byCategory": []
}

# 按分析人汇总
analyst_summary = {}
for item in has_competitor_unsold:
    analyst = item["4月分析人"]
    if analyst not in analyst_summary:
        analyst_summary[analyst] = 0
    analyst_summary[analyst] += 1

for analyst, count in analyst_summary.items():
    unsold_has_competitor["byAnalyst"].append({
        "analyst": analyst,
        "competitiveWeak": count,
        "noMarket": 0,
        "noPriceAdv": 0,
        "overseas": 0,
        "normal": 0,
        "na": 0,
        "unknown": 0,
        "total": count
    })

# 按品线汇总
category_summary = {}
for item in has_competitor_unsold:
    category = item["品类"]
    if category not in category_summary:
        category_summary[category] = 0
    category_summary[category] += 1

for category, count in category_summary.items():
    unsold_has_competitor["byCategory"].append({
        "category": category,
        "competitiveWeak": count,
        "noMarket": 0,
        "noPriceAdv": 0,
        "overseas": 0,
        "normal": 0,
        "na": 0,
        "unknown": 0,
        "total": count
    })

print(f"有对手未出单: 本周={unsold_has_competitor['total']}, 上周={unsold_has_competitor['prevTotal']}")

# ========== 5. 无对手未出单数据 ==========
unsold_no_competitor = {
    "total": 19,
    "prevTotal": 22,
    "change": -3,
    "reasons": [
        {"reason": "无市场", "curCount": 19, "curRatio": "100.0%", "prevCount": 10, "prevRatio": "45.5%", "change": 9},
    ],
    "byAnalyst": [
        {"analyst": "俞东旭", "noMarket": 3, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 3},
        {"analyst": "张潇", "noMarket": 4, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 4},
        {"analyst": "朱培源", "noMarket": 2, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 2},
        {"analyst": "王偲涵", "noMarket": 3, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 3},
        {"analyst": "章鹏", "noMarket": 1, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 1},
        {"analyst": "胡煜星", "noMarket": 6, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 6},
    ],
    "byCategory": [
        {"category": "其他", "noMarket": 8, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 8},
        {"category": "挡泥板", "noMarket": 3, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 3},
        {"category": "机盖及附件", "noMarket": 1, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 1},
        {"category": "车身外扩件", "noMarket": 3, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 3},
        {"category": "车门系统", "noMarket": 4, "unknown": 0, "competitiveWeak": 0, "na": 0, "other": 0, "total": 4},
    ]
}

print(f"无对手未出单: 本周={unsold_no_competitor['total']}, 上周={unsold_no_competitor['prevTotal']}")

# 保存所有数据到JSON
output = {
    "cum43Data": cum43_data,
    "cum43Stats": cum43_stats,
    "lowShareData": low_share_data,
    "plpTotal": plp_total,
    "plpPrevTotal": plp_prev_total,
    "plpCategories": plp_categories,
    "plpAnalysts": plp_analysts,  # 新增：分析人维度PLP
    "unsoldHasCompetitor": unsold_has_competitor,  # 新增：有对手未出单
    "unsoldNoCompetitor": unsold_no_competitor
}

with open(r'c:\Users\Hardy\ai-projects\三部周报v1\New project 2\src\modules\newProductStatus\corrected_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("所有数据已保存到 corrected_data.json")
