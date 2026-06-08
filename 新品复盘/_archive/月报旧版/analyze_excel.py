import pandas as pd
import json, math

df = pd.read_excel('新品月报数据.xlsx', sheet_name='源数据')

def get_batch(row):
    sid = row['销售编号']
    if sid < 11900:
        return '1月'
    elif sid < 12100:
        return '2月'
    else:
        return '3月'

df['批次'] = df.apply(get_batch, axis=1)
df['分析人'] = df['3月分析人']

print('批次分布:')
print(df['批次'].value_counts())
print()

# 检查源数据中的分析人列
print('分析人唯一值:', df['3月分析人'].unique())
print('2月分析人唯一值:', df['2月分析人'].unique())
print()

# 源数据全量列名
print('全部列名:')
for c in df.columns:
    print(f'  [{c}]')

print()
print('=== 3月各批次统计 ===')
col_qty = '3月销量'
col_amt = '3月销售额'
col_comp = '3月对手出单'
col_order = '3月 8日出单'
col_mkt = '3月市场状态'
col_share = '3月市占比'

for batch_label in ['1月', '2月', '3月', '全部']:
    if batch_label == '全部':
        bdf = df
    else:
        bdf = df[df['批次'] == batch_label]
    total = len(bdf)
    qty = bdf[col_qty].sum()
    amt = bdf[col_amt].sum()
    comp = bdf[col_comp].sum()
    y = (bdf[col_order] == 'Y').sum()
    n = (bdf[col_order] == 'N').sum()
    not_order = (bdf[col_order] == '未出单').sum()
    rate = round((y + n) / total * 100, 1) if total > 0 else 0
    share_mean = round(pd.to_numeric(bdf[col_share], errors='coerce').mean() * 100, 1)
    print(f'{batch_label}: SKU={total}, 3月销量={qty:.0f}, 3月销售额={amt:.2f}, 对手出单={comp:.0f}')
    print(f'  8日出单: Y={y} N={n} 未出单={not_order}, 出单率={rate}%, 平均市占比={share_mean}%')
print()

# 品线维度（含3月数据）
print('=== 品线维度3月统计 ===')
cats = df['品类'].unique()
for cat in sorted(cats):
    cdf = df[df['品类'] == cat]
    total = len(cdf)
    qty = cdf[col_qty].sum()
    amt = cdf[col_amt].sum()
    comp = cdf[col_comp].sum()
    y = (cdf[col_order] == 'Y').sum()
    n = (cdf[col_order] == 'N').sum()
    not_order = (cdf[col_order] == '未出单').sum()
    rate = round((y + n) / total * 100, 1) if total > 0 else 0
    print(f'{cat}: sku={total}, qty={qty:.0f}, amt={amt:.2f}, comp={comp:.0f}, Y={y}, N={n}, 未出单={not_order}, 出单率={rate}%')

print()
print('=== 分析人维度3月统计 ===')
analysts = df['3月分析人'].dropna().unique()
for a in sorted(analysts):
    adf = df[df['3月分析人'] == a]
    total = len(adf)
    qty = adf[col_qty].sum()
    amt = adf[col_amt].sum()
    comp = adf[col_comp].sum()
    y = (adf[col_order] == 'Y').sum()
    n = (adf[col_order] == 'N').sum()
    not_order = (adf[col_order] == '未出单').sum()
    rate = round((y + n) / total * 100, 1) if total > 0 else 0
    freq = round(adf['3月分析频次'].mean(), 2)
    price = round(amt / qty, 2) if qty > 0 else 0
    print(f'{a}: sku={total}, qty={qty:.0f}, amt={amt:.2f}, comp={comp:.0f}, Y={y}, N={n}, 未出单={not_order}, 出单率={rate}%, 均价={price}, 平均频次={freq}')

print()
print('=== 拓展类型维度3月统计 ===')
expands = df['产品拓展'].unique()
for ex in sorted(expands):
    edf = df[df['产品拓展'] == ex]
    total = len(edf)
    qty = edf[col_qty].sum()
    amt = edf[col_amt].sum()
    comp = edf[col_comp].sum()
    y = (edf[col_order] == 'Y').sum()
    n = (edf[col_order] == 'N').sum()
    not_order = (edf[col_order] == '未出单').sum()
    rate = round((y + n) / total * 100, 1) if total > 0 else 0
    print(f'{ex}: sku={total}, qty={qty:.0f}, comp={comp:.0f}, Y={y}, N={n}, 未出单={not_order}, 出单率={rate}%')

print()
print('=== 出单情况维度3月统计 ===')
for order_label in ['Y', 'N', '未出单']:
    odf = df[df[col_order] == order_label]
    print(f'{order_label}: count={len(odf)}, pct={round(len(odf)/len(df)*100,1)}%')

print()
print('=== 未出单情况维度3月统计 ===')
unord_df = df[df[col_order] == '未出单']
print(f'未出单总数: {len(unord_df)}')
for mkt in unord_df[col_mkt].unique():
    mdf = unord_df[unord_df[col_mkt] == mkt]
    print(f'  {mkt}: count={len(mdf)}, pct={round(len(mdf)/len(unord_df)*100,1)}%')
