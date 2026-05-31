# -*- coding: utf-8 -*-
"""修复PLP统计和获取完整数据"""
import pandas as pd
from datetime import datetime, date

# 读取数据
df_plp = pd.read_excel(r'C:\Users\Administrator\Desktop\三部周报v1\新品周报全流程\新品检查周源数据和PLP数据.xlsx', 
                         sheet_name='PLP明细', header=0)

cutoff_curr = date(2026, 5, 6)

def get_date(v):
    if pd.isna(v): return None
    if isinstance(v, datetime): return v.date()
    if isinstance(v, date): return v
    try:
        if isinstance(v, str): return datetime.strptime(v, '%Y-%m-%d').date()
    except: pass
    return None

def num(v, default=0):
    try:
        if pd.isna(v): return default
        return float(v)
    except: return default

print("=" * 80)
print("【PLP广告统计 - 4.30-5.6】")
print("=" * 80)

df_plp_curr = df_plp[df_plp['统计周期'] == '4.30-5.6']
print(f"PLP活动数: {len(df_plp_curr)}")

# 过滤掉上架日期>5.6的SKU (处理NaN)
def valid_date(x):
    d = get_date(x)
    return d is not None and d <= cutoff_curr

df_plp_valid = df_plp_curr[df_plp_curr['实际上架日期'].apply(valid_date)]
print(f"有效PLP SKU(排除未来上架): {len(df_plp_valid)}")

# 汇总统计
total_exposure = df_plp_valid['广告曝光量'].apply(num).sum()
total_clicks = df_plp_valid['广告点击量'].apply(num).sum()
total_sold = df_plp_valid['广告售出数'].apply(num).sum()
total_spend = df_plp_valid['广告花费'].apply(num).sum()
total_plp_rev = df_plp_valid['广告销售额'].apply(num).sum()
total_all_rev = df_plp_valid['总销售额'].apply(num).sum()

avg_roas = total_spend > 0 and total_plp_rev/total_spend or 0
avg_acos = total_plp_rev > 0 and total_spend/total_plp_rev*100 or 0
avg_acoas = total_all_rev > 0 and total_spend/total_all_rev*100 or 0
avg_cvr = total_clicks > 0 and total_sold/total_clicks*100 or 0
avg_ctr = total_exposure > 0 and total_clicks/total_exposure*100 or 0

print(f"广告曝光量: {total_exposure:,.0f}")
print(f"广告点击量: {total_clicks:.0f}")
print(f"广告售出数: {total_sold:.0f}")
print(f"广告花费: ${total_spend:.2f}")
print(f"广告销售额: ${total_plp_rev:.2f}")
print(f"ROAS: {avg_roas:.2f}")
print(f"ACOS: {avg_acos:.2f}%")
print(f"ACOAS: {avg_acoas:.2f}%")
print(f"CVR: {avg_cvr:.2f}%")
print(f"CTR: {avg_ctr:.4f}%")

# 按分析人统计PLP
print("\n" + "=" * 80)
print("【PLP按分析人维度】")
print("=" * 80)
plp_an_groups = {}
for _, r in df_plp_valid.iterrows():
    key = str(r.iloc[8]).strip()
    if key not in plp_an_groups:
        plp_an_groups[key] = {'sku': 0, 'exposure': 0, 'clicks': 0, 'sold': 0, 'spend': 0, 'plp_rev': 0, 'all_rev': 0}
    plp_an_groups[key]['sku'] += 1
    plp_an_groups[key]['exposure'] += num(r.iloc[11])
    plp_an_groups[key]['clicks'] += num(r.iloc[12])
    plp_an_groups[key]['sold'] += num(r.iloc[13])
    plp_an_groups[key]['spend'] += num(r.iloc[14])
    plp_an_groups[key]['plp_rev'] += num(r.iloc[15])
    plp_an_groups[key]['all_rev'] += num(r.iloc[16])

for an, data in sorted(plp_an_groups.items()):
    roas = data['spend'] > 0 and data['plp_rev']/data['spend'] or 0
    acos = data['plp_rev'] > 0 and data['spend']/data['plp_rev']*100 or 0
    acoas = data['all_rev'] > 0 and data['spend']/data['all_rev']*100 or 0
    cvr = data['clicks'] > 0 and data['sold']/data['clicks']*100 or 0
    ctr = data['exposure'] > 0 and data['clicks']/data['exposure']*100 or 0
    cpc = data['clicks'] > 0 and data['spend']/data['clicks'] or 0
    cpa = data['sold'] > 0 and data['spend']/data['sold'] or 0
    print(f"{an}: SKU={data['sku']}, 曝光={data['exposure']:.0f}, 点击={data['clicks']:.0f}, 售出={data['sold']:.0f}, 花费=${data['spend']:.2f}, ROAS={roas:.2f}, ACOS={acos:.2f}%, ACOAS={acoas:.2f}%, CVR={cvr:.2f}%, CTR={ctr:.4f}%, CPC=${cpc:.2f}, CPA=${cpa:.2f}")

# 按品线统计PLP
print("\n" + "=" * 80)
print("【PLP按品线维度】")
print("=" * 80)
plp_cat_groups = {}
for _, r in df_plp_valid.iterrows():
    key = str(r.iloc[9]).strip() or '未知'
    if key not in plp_cat_groups:
        plp_cat_groups[key] = {'sku': 0, 'exposure': 0, 'clicks': 0, 'sold': 0, 'spend': 0, 'plp_rev': 0, 'all_rev': 0}
    plp_cat_groups[key]['sku'] += 1
    plp_cat_groups[key]['exposure'] += num(r.iloc[11])
    plp_cat_groups[key]['clicks'] += num(r.iloc[12])
    plp_cat_groups[key]['sold'] += num(r.iloc[13])
    plp_cat_groups[key]['spend'] += num(r.iloc[14])
    plp_cat_groups[key]['plp_rev'] += num(r.iloc[15])
    plp_cat_groups[key]['all_rev'] += num(r.iloc[16])

for cat, data in sorted(plp_cat_groups.items()):
    roas = data['spend'] > 0 and data['plp_rev']/data['spend'] or 0
    acos = data['plp_rev'] > 0 and data['spend']/data['plp_rev']*100 or 0
    acoas = data['all_rev'] > 0 and data['spend']/data['all_rev']*100 or 0
    cvr = data['clicks'] > 0 and data['sold']/data['clicks']*100 or 0
    ctr = data['exposure'] > 0 and data['clicks']/data['exposure']*100 or 0
    cpc = data['clicks'] > 0 and data['spend']/data['clicks'] or 0
    cpa = data['sold'] > 0 and data['spend']/data['sold'] or 0
    print(f"{cat}: SKU={data['sku']}, 曝光={data['exposure']:.0f}, 点击={data['clicks']:.0f}, 售出={data['sold']:.0f}, 花费=${data['spend']:.2f}, ROAS={roas:.2f}, ACOS={acos:.2f}%, ACOAS={acoas:.2f}%, CVR={cvr:.2f}%, CTR={ctr:.4f}%, CPC=${cpc:.2f}, CPA=${cpa:.2f}")

# PLP明细表
print("\n" + "=" * 80)
print("【PLP明细 - 按分析人】")
print("=" * 80)
for an, data in sorted(plp_an_groups.items()):
    roas = data['spend'] > 0 and data['plp_rev']/data['spend'] or 0
    acos = data['plp_rev'] > 0 and data['spend']/data['plp_rev']*100 or 0
    acoas = data['all_rev'] > 0 and data['spend']/data['all_rev']*100 or 0
    cvr = data['clicks'] > 0 and data['sold']/data['clicks']*100 or 0
    ctr = data['exposure'] > 0 and data['clicks']/data['exposure']*100 or 0
    cpc = data['clicks'] > 0 and data['spend']/data['clicks'] or 0
    cpa = data['sold'] > 0 and data['spend']/data['sold'] or 0
    print(f"{an}: {data['sku']}个SKU | 曝光:{data['exposure']:,.0f} | 点击:{data['clicks']:.0f} | ROAS:{roas:.2f} | ACOS:{acos:.2f}% | ACOAS:{acoas:.2f}% | CVR:{cvr:.2f}% | CTR:{ctr:.4f}% | CPC:${cpc:.2f} | CPA:${cpa:.2f} | 花费:${data['spend']:.2f}")

print("\n" + "=" * 80)
print("【PLP明细 - 按品线】")
print("=" * 80)
for cat, data in sorted(plp_cat_groups.items()):
    roas = data['spend'] > 0 and data['plp_rev']/data['spend'] or 0
    acos = data['plp_rev'] > 0 and data['spend']/data['plp_rev']*100 or 0
    acoas = data['all_rev'] > 0 and data['spend']/data['all_rev']*100 or 0
    cvr = data['clicks'] > 0 and data['sold']/data['clicks']*100 or 0
    ctr = data['exposure'] > 0 and data['clicks']/data['exposure']*100 or 0
    cpc = data['clicks'] > 0 and data['spend']/data['clicks'] or 0
    cpa = data['sold'] > 0 and data['spend']/data['sold'] or 0
    print(f"{cat}: {data['sku']}个SKU | 曝光:{data['exposure']:,.0f} | 点击:{data['clicks']:.0f} | ROAS:{roas:.2f} | ACOS:{acos:.2f}% | ACOAS:{acoas:.2f}% | CVR:{cvr:.2f}% | CTR:{ctr:.4f}% | CPC:${cpc:.2f} | CPA:${cpa:.2f} | 花费:${data['spend']:.2f}")
