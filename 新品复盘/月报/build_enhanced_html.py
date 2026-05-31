"""
从Excel源数据提取完整数据，生成增强版月报HTML
补充遗漏字段：销售额、均价、分析频次、市占比、各月完整对比数据
"""
import pandas as pd
import json
import re

# ============ 读取数据 ============
df = pd.read_excel('新品月报数据.xlsx', sheet_name='源数据')
df['批次月'] = pd.to_datetime(df['最新上架日期']).dt.month
df['批次'] = df['批次月'].map({1: '1月', 2: '2月', 3: '3月'})

# 数值化处理
num_cols = [
    '1月销量','2月销量','3月销量',
    '1月销售额','2月销售额','3月销售额',
    '1月对手出单','2月对手出单','3月对手出单',
    '1月市占比','2月市占比','3月市占比',
    '1月分析频次','2月分析频次','3月分析频次'
]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

def safe_rate(y, n, total):
    return round((y + n) / total * 100, 1) if total > 0 else 0

def safe_mean_share(series):
    v = pd.to_numeric(series, errors='coerce').dropna()
    return round(float(v.mean()) * 100, 1) if len(v) > 0 else 0

# 货币转换：RMB -> USD (约7.2汇率)

def safe_price(amt, qty):
    return round(float(amt) / float(qty), 2) if qty > 0 else 0

# ============ 批次概况 ============
batch_stats = {}
for m_label, m_num in [('1', '1月'), ('2', '2月'), ('3', '3月')]:
    bdf = df[df['批次'] == m_num]
    total = len(bdf)
    qty3 = float(bdf['3月销量'].sum())
    amt3 = round(float(bdf['3月销售额'].sum()), 2)
    comp3 = float(bdf['3月对手出单'].sum())
    y3 = int((bdf['3月 8日出单'] == 'Y').sum())
    n3 = int((bdf['3月 8日出单'] == 'N').sum())
    uo3 = int((bdf['3月 8日出单'] == '未出单').sum())
    share3 = safe_mean_share(bdf['3月市占比'])
    batch_stats[m_label] = {
        'sku': total,
        'qty': qty3, 'amt': amt3, 'comp': comp3,
        'ordered': y3, 'unorder': n3, 'not_order': uo3,
        'rate': safe_rate(y3, n3, total),
        'share': share3
    }

# ============ 全量明细 ============
all_data = []
for _, row in df.iterrows():
    all_data.append({
        'sku_id': str(row['销售编号']),
        'sku': str(row['SKU']),
        'batch': row['批次'],
        'analyst': str(row['3月分析人']) if pd.notna(row['3月分析人']) else '',
        'analyst2': str(row['2月分析人']) if pd.notna(row['2月分析人']) else '',
        'cat': str(row['品类']),
        'expand': str(row['产品拓展']),
        'onshelf': str(row['最新上架日期'])[:10] if pd.notna(row['最新上架日期']) else '',
        'first_order': str(row['首次出单时间'])[:10] if pd.notna(row['首次出单时间']) else '-',
        # 1月
        'freq1': int(row['1月分析频次']), 'qty1': float(row['1月销量']),
        'amt1': round(float(row['1月销售额']), 2), 'comp1': float(row['1月对手出单']),
        'order1': str(row['1月 8日出单']), 'status1': str(row['1月市场状态']),
        'share1': round(float(pd.to_numeric(row['1月市占比'], errors='coerce') or 0) * 100, 1),
        # 2月
        'freq2': int(row['2月分析频次']), 'qty2': float(row['2月销量']),
        'amt2': round(float(row['2月销售额']), 2), 'comp2': float(row['2月对手出单']),
        'order2': str(row['2月 8日出单']), 'status2': str(row['2月市场状态']),
        'share2': round(float(pd.to_numeric(row['2月市占比'], errors='coerce') or 0) * 100, 1),
        # 3月
        'freq3': int(row['3月分析频次']), 'qty3': float(row['3月销量']),
        'amt3': round(float(row['3月销售额']), 2), 'comp3': float(row['3月对手出单']),
        'order3': str(row['3月 8日出单']), 'status3': str(row['3月市场状态']),
        'share3': round(float(pd.to_numeric(row['3月市占比'], errors='coerce') or 0) * 100, 1),
    })

# ============ 低占比新品 ============
low_share = []
for item in all_data:
    if item['share3'] < 75 and item['comp3'] > 0:
        low_share.append({
            'sku_id': item['sku_id'], 'sku': item['sku'], 'batch': item['batch'],
            'cat': item['cat'], 'analyst': item['analyst'], 'expand': item['expand'],
            'qty': item['qty3'], 'comp': item['comp3'],
            'share': round(item['share3'], 1),
            'order': item['order3'], 'status': item['status3']
        })

# ============ 品线维度 ============
cat_data = {}
for cat in sorted(df['品类'].unique()):
    cdf = df[df['品类'] == cat]
    row = {}
    for m in ['1','2','3']:
        ml = f'{m}月'
        mdf = df[(df['品类'] == cat) & (df['批次'] == ml)]
        all_m = cdf  # 全量在该月的数据
        total_m = len(mdf)
        y = int((mdf[f'{m}月 8日出单'] == 'Y').sum())
        n = int((mdf[f'{m}月 8日出单'] == 'N').sum())
        uo = int((mdf[f'{m}月 8日出单'] == '未出单').sum())
        row[f'sku_{m}'] = total_m
        row[f'qty_{m}'] = round(float(mdf[f'{m}月销量'].sum()), 1)
        row[f'amt_{m}'] = round(float(mdf[f'{m}月销售额'].sum()), 2)
        row[f'comp_{m}'] = round(float(mdf[f'{m}月对手出单'].sum()), 1)
        row[f'rate_{m}'] = safe_rate(y, n, total_m)
        row[f'share_{m}'] = safe_mean_share(mdf[f'{m}月市占比'])
        row[f'y_{m}'] = y; row[f'n_{m}'] = n; row[f'uo_{m}'] = uo
    cat_data[cat] = row

# 计算环比（3月vs2月，用该品线3月批次的3月销量 vs 2月批次的3月销量）
for cat in cat_data:
    q2 = cat_data[cat].get('qty_2', 0)
    q3 = cat_data[cat].get('qty_3', 0)
    cat_data[cat]['qty_hb'] = round((q3 - q2) / q2 * 100, 1) if q2 > 0 else None
    r2 = cat_data[cat].get('rate_2', 0)
    r3 = cat_data[cat].get('rate_3', 0)
    cat_data[cat]['rate_hb'] = round(r3 - r2, 1)

# ============ 分析人维度 ============
analyst_data = {}
analysts = [a for a in df['3月分析人'].dropna().unique() if str(a) != 'nan']
for analyst in sorted(analysts):
    adf = df[df['3月分析人'] == analyst]
    row = {}
    for m in ['1','2','3']:
        ml = f'{m}月'
        mdf = df[(df['3月分析人'] == analyst) & (df['批次'] == ml)]
        total_m = len(mdf)
        y = int((mdf[f'{m}月 8日出单'] == 'Y').sum())
        n = int((mdf[f'{m}月 8日出单'] == 'N').sum())
        uo = int((mdf[f'{m}月 8日出单'] == '未出单').sum())
        qty = round(float(mdf[f'{m}月销量'].sum()), 1)
        amt = round(float(mdf[f'{m}月销售额'].sum()), 2)
        freq = round(float(pd.to_numeric(mdf[f'{m}月分析频次'], errors='coerce').mean() or 0), 2) if total_m > 0 else 0
        row[f'sku_{m}'] = total_m
        row[f'qty_{m}'] = qty
        row[f'amt_{m}'] = amt
        row[f'comp_{m}'] = round(float(mdf[f'{m}月对手出单'].sum()), 1)
        row[f'rate_{m}'] = safe_rate(y, n, total_m)
        row[f'share_{m}'] = safe_mean_share(mdf[f'{m}月市占比'])
        row[f'freq_{m}'] = freq
        row[f'price_{m}'] = safe_price(amt, qty)
        row[f'y_{m}'] = y; row[f'n_{m}'] = n; row[f'uo_{m}'] = uo
    row['qty_hb'] = round((row['qty_3'] - row['qty_2']) / row['qty_2'] * 100, 1) if row['qty_2'] > 0 else None
    row['rate_hb'] = round(row['rate_3'] - row['rate_2'], 1)
    analyst_data[analyst] = row

# ============ 拓展类型维度 ============
expand_data = {}
for ex in sorted(df['产品拓展'].unique()):
    edf = df[df['产品拓展'] == ex]
    row = {}
    for m in ['1','2','3']:
        ml = f'{m}月'
        mdf = df[(df['产品拓展'] == ex) & (df['批次'] == ml)]
        total_m = len(mdf)
        y = int((mdf[f'{m}月 8日出单'] == 'Y').sum())
        n = int((mdf[f'{m}月 8日出单'] == 'N').sum())
        uo = int((mdf[f'{m}月 8日出单'] == '未出单').sum())
        row[f'sku_{m}'] = total_m
        row[f'qty_{m}'] = round(float(mdf[f'{m}月销量'].sum()), 1)
        row[f'amt_{m}'] = round(float(mdf[f'{m}月销售额'].sum()), 2)
        row[f'comp_{m}'] = round(float(mdf[f'{m}月对手出单'].sum()), 1)
        row[f'rate_{m}'] = safe_rate(y, n, total_m)
        row[f'share_{m}'] = safe_mean_share(mdf[f'{m}月市占比'])
        row[f'y_{m}'] = y; row[f'n_{m}'] = n; row[f'uo_{m}'] = uo
    row['qty_hb'] = round((row['qty_3'] - row['qty_2']) / row['qty_2'] * 100, 1) if row['qty_2'] > 0 else None
    row['rate_hb'] = round(row['rate_3'] - row['rate_2'], 1)
    expand_data[ex] = row

# ============ 出单情况维度 ============
order_dist = {}
for label in ['Y', 'N', '未出单']:
    row = {}
    for m in ['1','2','3']:
        mdf = df[df['批次'] == f'{m}月']
        cnt = int((mdf[f'{m}月 8日出单'] == label).sum())
        total_m = len(mdf)
        row[f'cnt_{m}'] = cnt
        row[f'pct_{m}'] = round(cnt / total_m * 100, 1) if total_m > 0 else 0
    order_dist[label] = row

# ============ 未出单情况维度 ============
unorder_dist = {}
unord_df = df[df['3月 8日出单'] == '未出单']
for label in unord_df['3月市场状态'].unique():
    row = {}
    for m in ['1','2','3']:
        mdf = df[(df['批次'] == f'{m}月') & (df[f'{m}月 8日出单'] == '未出单')]
        total_uo = len(mdf)
        cnt = int((mdf[f'{m}月市场状态'] == label).sum())
        row[f'cnt_{m}'] = cnt
        row[f'pct_{m}'] = round(cnt / total_uo * 100, 1) if total_uo > 0 else 0
    unorder_dist[str(label)] = row

# ============ 汇总数据 ============
summary = {
    'total_sku': 156,
    'batch_1': 53, 'batch_2': 36, 'batch_3': 67,
    'ordered_sku': int((df['3月 8日出单'] == 'Y').sum()),
    'unordered_sku': int((df['3月 8日出单'] == 'N').sum()),
    'not_order_sku': int((df['3月 8日出单'] == '未出单').sum()),
    'total_qty': float(df['3月销量'].sum()),
    # 3月总销售额：所有156个SKU的3月销售额之和（换算USD）
    'total_amt': round(float(df['3月销售额'].sum()), 0),
    'total_comp': float(df['3月对手出单'].sum()),
    'order_rate': round((df['3月 8日出单'].isin(['Y','N'])).sum() / 156 * 100, 1),
    'avg_share': safe_mean_share(df['3月市占比']),
    'low_share_cnt': len(low_share)
}

print("数据提取完成")
print(f"全量明细: {len(all_data)}条")
print(f"低占比: {len(low_share)}条")
print(f"品线: {list(cat_data.keys())}")
print(f"分析人: {list(analyst_data.keys())}")
print(f"拓展类型: {list(expand_data.keys())}")
print(f"出单分布: {order_dist}")
print(f"未出单分布: {list(unorder_dist.keys())}")
print(f"批次统计: {batch_stats}")

# 保存到JSON供后续使用
output = {
    'summary': summary,
    'batch_stats': batch_stats,
    'cat_data': cat_data,
    'analyst_data': analyst_data,
    'expand_data': expand_data,
    'order_dist': order_dist,
    'unorder_dist': unorder_dist,
    'all_data': all_data,
    'low_share': low_share
}
with open('full_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\nfull_data.json 已保存")
