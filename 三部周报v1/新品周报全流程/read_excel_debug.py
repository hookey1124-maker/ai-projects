# -*- coding: utf-8 -*-
"""读取Excel文件获取准确数据"""
import pandas as pd
from datetime import datetime, date

# 读取源数据
wb_main = pd.read_excel(r'C:\Users\Administrator\Desktop\三部周报v1\新品周报全流程\新品检查周源数据和PLP数据.xlsx', 
                          sheet_name='四三数据累计', header=0)
wb_plp = pd.read_excel(r'C:\Users\Administrator\Desktop\三部周报v1\新品周报全流程\新品检查周源数据和PLP数据.xlsx', 
                         sheet_name='PLP明细', header=0)

print("=" * 80)
print("四三数据累计 - 列名:")
print("=" * 80)
for i, col in enumerate(wb_main.columns):
    print(f"{i}: {col}")

print("\n" + "=" * 80)
print("四三数据累计 - 前3行数据:")
print("=" * 80)
print(wb_main.head(3).to_string())

print("\n" + "=" * 80)
print("PLP明细 - 列名:")
print("=" * 80)
for i, col in enumerate(wb_plp.columns):
    print(f"{i}: {col}")

print("\n" + "=" * 80)
print("PLP明细 - 前3行数据:")
print("=" * 80)
print(wb_plp.head(3).to_string())
