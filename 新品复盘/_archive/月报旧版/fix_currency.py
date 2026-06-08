# -*- coding: utf-8 -*-
"""修复增强版HTML：
1. 所有 ¥ 改成 $
2. 重新计算拓展类型维度的3月销售额（从源数据精确计算）"""
import re

# ========== 1. 从源数据重新计算各维度数据 ==========
import pandas as pd

df = pd.read_excel('新品月报数据.xlsx', sheet_name='源数据')
df['批次'] = pd.to_datetime(df['最新上架日期']).dt.month.map({1:'1月',2:'2月',3:'3月'})

# 数值化
for col in ['1月销售额','2月销售额','3月销售额','1月对手出单','2月对手出单','3月对手出单',
            '1月市占比','2月市占比','3月市占比','1月分析频次','2月分析频次','3月分析频次']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

ext_col = '拓展类型'

# 按拓展类型+批次分组
exp_data = {}
for ext in sorted(df[ext_col].dropna().unique()):
    sub = df[df[ext_col] == ext]
    row = {}
    for m in ['1','2','3']:
        bm = f'{m}月'
        bsub = sub[sub['批次'] == bm]
        row[f'sku_{m}'] = int(len(bsub))
        row[f'qty_{m}'] = float(bsub[f'{m}月销量'].sum())
        row[f'amt_{m}'] = round(float(bsub[f'{m}月销售额'].sum()), 2)
        row[f'comp_{m}'] = float(bsub[f'{m}月对手出单'].sum())
        y = int((bsub[f'{m}月 8日出单'] == 'Y').sum())
        n = int((bsub[f'{m}月 8日出单'] == 'N').sum())
        uo = int((bsub[f'{m}月 8日出单'] == '未出单').sum())
        total = int(len(bsub))
        row[f'y_{m}'] = y; row[f'n_{m}'] = n; row[f'uo_{m}'] = uo
        row[f'rate_{m}'] = round((y+n)/total*100, 1) if total > 0 else 0
        shares = pd.to_numeric(bsub[f'{m}月市占比'], errors='coerce').dropna()
        row[f'share_{m}'] = round(float(shares.mean())*100, 1) if len(shares)>0 else 0
    exp_data[ext] = row
    print(f'{ext}: 1月={row[\"sku_1\"]}个/¥{row[\"amt_1\"]} | 2月={row[\"sku_2\"]}个/¥{row[\"amt_2\"]} | 3月={row[\"sku_3\"]}个/¥{row[\"amt_3\"]}')

# 汇总行
total_row = {'sku_1': sum(v['sku_1'] for v in exp_data.values()),
             'sku_2': sum(v['sku_2'] for v in exp_data.values()),
             'sku_3': sum(v['sku_3'] for v in exp_data.values()),
             'qty_1': sum(v['qty_1'] for v in exp_data.values()),
             'qty_2': sum(v['qty_2'] for v in exp_data.values()),
             'qty_3': sum(v['qty_3'] for v in exp_data.values()),
             'amt_1': round(sum(v['amt_1'] for v in exp_data.values()), 2),
             'amt_2': round(sum(v['amt_2'] for v in exp_data.values()), 2),
             'amt_3': round(sum(v['amt_3'] for v in exp_data.values()), 2),
             'comp_1': sum(v['comp_1'] for v in exp_data.values()),
             'comp_2': sum(v['comp_2'] for v in exp_data.values()),
             'comp_3': sum(v['comp_3'] for v in exp_data.values()),
             'rate_1': round(sum(v['sku_1']*v['rate_1'] for v in exp_data.values())/total_row['sku_1'] if total_row['sku_1']>0 else 0, 1) if 'total_row' else 0,
             'share_1': 0, 'share_2': 0, 'share_3': 0}
# 重新算加权平均
for m in ['1','2','3']:
    sk = total_row[f'sku_{m}']
    total_row[f'rate_{m}'] = round(sum(v['sku_{m}']*v[f'rate_{m}'] for v in exp_data.values())/sk, 1) if sk>0 else 0
    shares_list = [v[f'share_{m}'] for v in exp_data.values() if v[f'sku_{m}']>0]
    total_row[f'share_{m}'] = round(sum(shares_list)/len(shares_list), 1) if shares_list else 0
exp_data['商品维度汇总'] = total_row

print(f'\n汇总: 1月={total_row[\"sku_1\"]}个/¥{total_row[\"amt_1\"]} | 2月={total_row[\"sku_2\"]}个/¥{total_row[\"amt_2\"]} | 3月={total_row[\"sku_3\"]}个/¥{total_row[\"amt_3\"]}')
print('\n数据提取完成！')

# ========== 2. 读取HTML，把 ¥ 替换成 $ ==========
with open('新品月报_2026年3月_增强版.html', encoding='utf-8') as f:
    html = f.read()

print(f'\n原始HTML大小: {len(html)} 字符')
html_fixed = html.replace('¥', '$')
print(f'替换后HTML大小: {len(html_fixed)} 字符')
print(f'替换 ¥->$ 次数: {html.count("¥")}')

# ========== 3. 写入修复后的HTML ==========
with open('新品月报_2026年3月_增强版.html', 'w', encoding='utf-8') as f:
    f.write(html_fixed)

print('\n✅ 货币单位已从 ¥ 改为 $')
