# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('新品月报数据.xlsx', sheet_name='源数据')
for col in ['1月销售额','2月销售额','3月销售额']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

RATE = 7.2
total_3 = df['3月销售额'].sum()
print('所有156个SKU的3月总销售额 (RMB):', total_3)
print('换算USD:', round(total_3/RATE, 2))
print('KPI应显示: $' + str(round(total_3/RATE, 0)) + ' (约$' + str(round(total_3/RATE/1000, 1)) + 'K)')

# 各批次
df['批次'] = pd.to_datetime(df['最新上架日期']).dt.month.map({1:'1月',2:'2月',3:'3月'})
for b in ['1月','2月','3月']:
    sub = df[df['批次']==b]
    amt_rmb = sub['3月销售额'].sum()
    amt_usd = amt_rmb / RATE
    print(b + '批次各SKU的3月销售额: RMB ' + str(round(amt_rmb,2)) + ' = USD ' + str(round(amt_usd,2)))
