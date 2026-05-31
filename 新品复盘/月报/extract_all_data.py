# -*- coding: utf-8 -*-
import json
import pandas as pd

# 读取原始Excel
df = pd.read_excel('新品月报数据.xlsx')

# 处理批次
def get_batch(date):
    if pd.isna(date):
        return None
    date_str = str(date)
    if '2026-01' in date_str or '2026/01' in date_str:
        return '1月'
    elif '2026-02' in date_str or '2026/02' in date_str:
        return '2月'
    elif '2026-03' in date_str or '2026/03' in date_str:
        return '3月'
    return None

df['批次'] = df['最新上架日期'].apply(get_batch)

# 准备全量明细数据
all_detail = []
def safe_float(val):
    if pd.isna(val):
        return 0
    try:
        return float(val)
    except:
        return 0

for _, row in df.iterrows():
    all_detail.append({
        'sku': str(row['销售编号']),
        'batch': row['批次'] or '未知',
        'analyst': str(row['3月分析人']) if not pd.isna(row['3月分析人']) else '',
        'cat': str(row['品类']) if not pd.isna(row['品类']) else '',
        'expand': str(row['产品拓展']) if not pd.isna(row['产品拓展']) else '',
        'qty': safe_float(row['3月销量']),
        'comp': safe_float(row['3月对手出单']),
        'share': safe_float(row['3月市占比']),
        'order': str(row['3月 8日出单']) if not pd.isna(row['3月 8日出单']) else '',
        'status': str(row['3月市场状态']) if not pd.isna(row['3月市场状态']) else ''
    })

print(f'全量明细: {len(all_detail)}条')
print(f'1月: {len([x for x in all_detail if x["batch"]=="1月"])}')
print(f'2月: {len([x for x in all_detail if x["batch"]=="2月"])}')
print(f'3月: {len([x for x in all_detail if x["batch"]=="3月"])}')

# 低占比新品
with open('temp_data.json', 'r', encoding='utf-8') as f:
    temp_data = json.load(f)
low_share = temp_data['low_share']
print(f'低占比新品: {len(low_share)}条')

# 保存更新后的数据
with open('temp_data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'low_share': low_share,
        'all_detail': all_detail
    }, f, ensure_ascii=False, indent=2)

print('数据已更新!')
