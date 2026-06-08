# -*- coding: utf-8 -*-
import pandas as pd
import json

# 读取Excel
df = pd.read_excel('新品月报数据.xlsx', engine='openpyxl')

# 确定月份批次
def get_batch(date):
    if pd.isna(date):
        return None
    month = pd.to_datetime(date).month
    if month == 1:
        return '1'
    elif month == 2:
        return '2'
    elif month == 3:
        return '3'
    return None

df['批次'] = df['最新上架日期'].apply(get_batch)

# 筛选1-3月新品
df_123 = df[df['批次'].notna() & (df['批次'].isin(['1', '2', '3']))].copy()

# 各批次汇总
batch_stats = {}
for batch in ['1', '2', '3']:
    sub = df_123[df_123['批次'] == batch]
    sku = len(sub)
    qty = int(sub['3月销量'].sum())
    amt = float(sub['3月销售额'].sum())
    comp = int(sub['3月对手出单'].sum())
    ordered = len(sub[sub['3月 8日出单'].isin(['Y'])])
    unorder = len(sub[sub['3月 8日出单'].isin(['N'])])
    not_order = len(sub[sub['3月 8日出单'].isin(['未出单'])])
    rate = round(ordered / sku * 100, 1) if sku > 0 else 0
    self_sales = sub['3月销量'].fillna(0)
    comp_sales = pd.to_numeric(sub['3月对手出单'], errors='coerce').fillna(0)
    total = self_sales + comp_sales
    share = round((self_sales / total.replace(0, 1)).mean() * 100, 1)
    batch_stats[batch] = {
        'sku': sku, 'qty': qty, 'amt': amt, 'comp': comp,
        'ordered': ordered, 'unorder': unorder, 'not_order': not_order,
        'rate': rate, 'share': share
    }

print("=== 批次统计 ===")
for k, v in batch_stats.items():
    print(f"{k}月: {v}")

# 分析人维度
print("\n=== 分析人统计 ===")
analyst_stats = {}
analysts = df_123['3月分析人'].dropna().unique()
for analyst in analysts:
    sub = df_123[df_123['3月分析人'] == analyst]
    sku = len(sub)
    qty = int(sub['3月销量'].sum())
    amt = float(sub['3月销售额'].sum())
    ordered = len(sub[sub['3月 8日出单'].isin(['Y'])])
    rate = round(ordered / sku * 100, 1) if sku > 0 else 0
    analyst_stats[analyst] = {'sku': sku, 'qty': qty, 'amt': amt, 'rate': rate}
    print(f"{analyst}: SKU={sku}, 销量={qty}, 销售额={amt:.2f}, 出单率={rate}%")

# 品线维度
print("\n=== 品线统计 ===")
cat_stats = {}
categories = df_123['品类'].dropna().unique()
for cat in categories:
    sub = df_123[df_123['品类'] == cat]
    sku = len(sub)
    qty = int(sub['3月销量'].sum())
    amt = float(sub['3月销售额'].sum())
    ordered = len(sub[sub['3月 8日出单'].isin(['Y'])])
    rate = round(ordered / sku * 100, 1) if sku > 0 else 0
    cat_stats[cat] = {'sku': sku, 'qty': qty, 'amt': amt, 'rate': rate}
    print(f"{cat}: SKU={sku}, 销量={qty}, 销售额={amt:.2f}, 出单率={rate}%")

# 拓展类型维度
print("\n=== 拓展类型统计 ===")
expand_stats = {}
expands = df_123['产品拓展'].dropna().unique()
for exp in expands:
    sub = df_123[df_123['产品拓展'] == exp]
    sku = len(sub)
    qty = int(sub['3月销量'].sum())
    ordered = len(sub[sub['3月 8日出单'].isin(['Y'])])
    rate = round(ordered / sku * 100, 1) if sku > 0 else 0
    self_sales = sub['3月销量'].fillna(0)
    comp_sales = pd.to_numeric(sub['3月对手出单'], errors='coerce').fillna(0)
    total = self_sales + comp_sales
    share = round((self_sales / total.replace(0, 1)).mean() * 100, 1)
    expand_stats[exp] = {'sku': sku, 'qty': qty, 'rate': rate, 'share': share}
    print(f"{exp}: SKU={sku}, 销量={qty}, 出单率={rate}%, 市占={share}%")

# 市场状态分布
print("\n=== 市场状态分布 ===")
market_dist = df_123['3月市场状态'].value_counts().to_dict()
print(market_dist)

# 出单情况分布
print("\n=== 出单情况分布 ===")
order_dist = df_123['3月 8日出单'].value_counts().to_dict()
print(order_dist)

# 低占比新品
print("\n=== 低占比新品 ===")
low_share = []
for idx, row in df_123.iterrows():
    self_s = float(row['3月销量']) if pd.notna(row['3月销量']) else 0
    comp_s = float(row['3月对手出单']) if pd.notna(row['3月对手出单']) else 0
    share = self_s / (self_s + comp_s) if (self_s + comp_s) > 0 else 0
    if share < 0.75 and comp_s > 0:
        low_share.append({
            '销售编号': str(row['销售编号']),
            'sku': str(row['SKU']),
            '批次': row['批次'],
            'cat': str(row['品类']) if pd.notna(row['品类']) else '',
            'analyst': str(row['3月分析人']) if pd.notna(row['3月分析人']) else '',
            'expand': str(row['产品拓展']) if pd.notna(row['产品拓展']) else '',
            'qty': int(self_s),
            'comp': int(comp_s),
            'share': round(share, 4),
            'order': str(row['3月 8日出单']),
            'status': str(row['3月市场状态']) if pd.notna(row['3月市场状态']) else ''
        })

print(f"低占比新品总数: {len(low_share)}")
for b in ['1', '2', '3']:
    count = len([x for x in low_share if x['批次'] == b])
    print(f"  {b}月: {count}个")

# 汇总数据
summary = {
    'total_sku': len(df_123),
    'ordered_sku': len(df_123[df_123['3月 8日出单'].isin(['Y'])]),
    'unordered_sku': len(df_123[df_123['3月 8日出单'].isin(['N', '未出单'])]),
    'total_qty': int(df_123['3月销量'].sum()),
    'total_amt': float(df_123['3月销售额'].sum()),
    'batch_stats': batch_stats,
    'analyst_stats': analyst_stats,
    'cat_stats': cat_stats,
    'expand_stats': expand_stats,
    'market_dist': market_dist,
    'order_dist': order_dist,
    'low_share': low_share
}

# 输出JSON
with open('report_data.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("\n数据已保存到 report_data.json")
