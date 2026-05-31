
# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('新品月报数据.xlsx', sheet_name='源数据')
print('列名:', list(df.columns))

df['批次'] = pd.to_datetime(df['最新上架日期']).dt.month.map({1:'1月',2:'2月',3:'3月'})

for col in ['1月销售额','2月销售额','3月销售额']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 找拓展类型列
ext_col = [c for c in df.columns if '拓展' in c]
print('拓展类型列:', ext_col)

ext_col = ext_col[0] if ext_col else None
if ext_col:
    print('\n=== 拓展类型维度 各月销售额 ===')
    for ext in sorted(df[ext_col].dropna().unique()):
        sub = df[df[ext_col] == ext]
        print(f'{ext} | 1月: {sub["1月销售额"].sum():.2f} | 2月: {sub["2月销售额"].sum():.2f} | 3月: {sub["3月销售额"].sum():.2f}')

# 看Excel里的拓展类型维度sheet
df_ex = pd.read_excel('新品月报数据.xlsx', sheet_name='拓展类型维度')
print('\n=== Excel拓展类型维度sheet ===')
print(df_ex.to_string())
