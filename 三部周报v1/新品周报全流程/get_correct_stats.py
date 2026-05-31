# -*- coding: utf-8 -*-
"""从Excel获取正确统计数据"""
import pandas as pd
from datetime import datetime, date

# 读取数据
df_main = pd.read_excel(r'C:\Users\Administrator\Desktop\三部周报v1\新品周报全流程\新品检查周源数据和PLP数据.xlsx', 
                          sheet_name='四三数据累计', header=0)
df_plp = pd.read_excel(r'C:\Users\Administrator\Desktop\三部周报v1\新品周报全流程\新品检查周源数据和PLP数据.xlsx', 
                         sheet_name='PLP明细', header=0)

# 周期定义
cutoff_curr = date(2026, 5, 6)
cutoff_prev = date(2026, 4, 29)

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

# 列索引
col_list_date = 2  # 实际上架日期
col_analyst = 4    # 4月分析人
col_cat = 5         # 品类
col_expand = 6     # 产品拓展
col_sales_curr = 15 # 4.30-5.6销量
col_rev_curr = 25   # 4.30-5.6销售额
col_rival_curr = 35 # 5.6对手销量
col_share_curr = 44 # 5.6市占比
col_ord8_curr = 62  # 5.6 8日出单情况
col_freq7_curr = 71 # 5.6 7日频次标签
col_nfreq7_curr = 80 # 5.6 7日新品频次标签
col_market_curr = 90 # 5.6市场状态
col_plg_curr = 106   # 4.30-5.6PLG最高费率

# 过滤：只统计截止日期前上架的SKU
df_curr = df_main[df_main.iloc[:, col_list_date].apply(lambda x: get_date(x) and get_date(x) <= cutoff_curr)]
df_prev = df_main[df_main.iloc[:, col_list_date].apply(lambda x: get_date(x) and get_date(x) <= cutoff_prev)]

print("=" * 80)
print("【基础统计】")
print("=" * 80)
total_sku = len(df_curr)
new_listed = len(df_curr[df_curr.iloc[:, col_list_date].apply(lambda x: get_date(x) and get_date(x) > cutoff_prev)])
print(f"累计SKU（截止5.6）：{total_sku}")
print(f"本周新上架：{new_listed}")

# 有对手/无对手
has_rival = df_curr[df_curr.iloc[:, col_rival_curr].apply(lambda x: num(x) > 0)]
no_rival = df_curr[df_curr.iloc[:, col_rival_curr].apply(lambda x: num(x) == 0)]
print(f"有对手SKU：{len(has_rival)}")
print(f"无对手SKU：{len(no_rival)}")

# 销量/销售额
total_sales = df_curr.iloc[:, col_sales_curr].apply(num).sum()
total_rev = df_curr.iloc[:, col_rev_curr].apply(num).sum()
print(f"总销量：{total_sales}")
print(f"总销售额：${total_rev:.2f}")

# 出单情况统计（8日出单）
def count_ord8(df, col):
    y = n = no = 0
    for _, r in df.iterrows():
        v = str(r.iloc[col] if not pd.isna(r.iloc[col]) else '').strip()
        if v == 'Y': y += 1
        elif v == 'N': n += 1  # N是已出单
        elif v == '未出单': no += 1
    return y, n, no

y, n, no_order = count_ord8(has_rival, col_ord8_curr)
y_no, n_no, no_no = count_ord8(no_rival, col_ord8_curr)
total_ordered = y + n + y_no + n_no
total_no = no_order + no_no
print(f"\n【有对手口径】8日Y: {y}, 8日N: {n}, 未出单: {no_order}")
print(f"【无对手口径】8日Y: {y_no}, 8日N: {n_no}, 未出单: {no_no}")
print(f"有对手出单率: {round((y+n)/len(has_rival)*100, 1)}%")
print(f"总已出单: {total_ordered}, 总未出单: {total_no}")

# 分析及时率
def count_timeliness(df, freq7_col, nfreq7_col):
    timely = no_8d = no_7d = 0
    for _, r in df.iterrows():
        freq = str(r.iloc[freq7_col] if not pd.isna(r.iloc[freq7_col]) else '').strip()
        nfreq = str(r.iloc[nfreq7_col] if not pd.isna(r.iloc[nfreq7_col]) else '').strip()
        if nfreq == '异常': no_8d += 1
        elif freq == '异常': no_7d += 1
        else: timely += 1
    return timely, no_8d, no_7d

timely, no_8d, no_7d = count_timeliness(df_curr, col_freq7_curr, col_nfreq7_curr)
timely_rate = round(timely/total_sku*100, 1)
print(f"\n【分析及时率】及时: {timely}, 8日内无分析: {no_8d}, 超7日未分析: {no_7d}")
print(f"及时率: {timely_rate}%")

# 低占比新品（市场<75%且有对手）
low_share = df_curr[(df_curr.iloc[:, col_share_curr].apply(num) < 0.75) & 
                     (df_curr.iloc[:, col_rival_curr].apply(num) > 0)]
print(f"\n【低占比新品】共 {len(low_share)} 个")
# 低占比新品中有对手未出单
low_share_no_order = low_share[low_share.iloc[:, col_ord8_curr].apply(lambda x: str(x).strip() == '未出单')]
print(f"低占比新品中有对手未出单: {len(low_share_no_order)} 个")

print("\n" + "=" * 80)
print("【低占比新品明细】")
print("=" * 80)
for _, r in low_share.iterrows():
    print(f"  {r.iloc[1]} | {r.iloc[5]} | {r.iloc[4]} | 市占:{num(r.iloc[col_share_curr]):.1%} | 对手:{num(r.iloc[col_rival_curr])} | 出单:{r.iloc[col_ord8_curr]}")

print("\n" + "=" * 80)
print("【分析人维度】")
print("=" * 80)
an_groups = {}
for _, r in df_curr.iterrows():
    key = str(r.iloc[col_analyst]).strip()
    if key not in an_groups:
        an_groups[key] = {'skus': 0, 'new': 0, 'sales': 0, 'rev': 0, 'has_rival': 0, 'timely': 0, 'no_8d': 0, 'no_7d': 0}
    an_groups[key]['skus'] += 1
    an_groups[key]['sales'] += num(r.iloc[col_sales_curr])
    an_groups[key]['rev'] += num(r.iloc[col_rev_curr])
    if num(r.iloc[col_rival_curr]) > 0:
        an_groups[key]['has_rival'] += 1
    if get_date(r.iloc[col_list_date]) and get_date(r.iloc[col_list_date]) > cutoff_prev:
        an_groups[key]['new'] += 1
    freq = str(r.iloc[col_freq7_curr] if not pd.isna(r.iloc[col_freq7_curr]) else '').strip()
    nfreq = str(r.iloc[col_nfreq7_curr] if not pd.isna(r.iloc[col_nfreq7_curr]) else '').strip()
    if nfreq == '异常': an_groups[key]['no_8d'] += 1
    elif freq == '异常': an_groups[key]['no_7d'] += 1
    else: an_groups[key]['timely'] += 1

for an, data in sorted(an_groups.items()):
    rate = round(data['timely']/data['skus']*100, 1) if data['skus'] > 0 else 0
    print(f"{an}: SKU={data['skus']}, 新上架={data['new']}, 销量={data['sales']}, 有对手={data['has_rival']}, 及时={data['timely']}, 及时率={rate}%")

print("\n" + "=" * 80)
print("【品线维度】")
print("=" * 80)
cat_groups = {}
for _, r in df_curr.iterrows():
    key = str(r.iloc[col_cat]).strip() or '未知'
    if key not in cat_groups:
        cat_groups[key] = {'skus': 0, 'new': 0, 'sales': 0, 'rev': 0, 'has_rival': 0}
    cat_groups[key]['skus'] += 1
    cat_groups[key]['sales'] += num(r.iloc[col_sales_curr])
    cat_groups[key]['rev'] += num(r.iloc[col_rev_curr])
    if num(r.iloc[col_rival_curr]) > 0:
        cat_groups[key]['has_rival'] += 1
    if get_date(r.iloc[col_list_date]) and get_date(r.iloc[col_list_date]) > cutoff_prev:
        cat_groups[key]['new'] += 1

for cat, data in sorted(cat_groups.items()):
    print(f"{cat}: SKU={data['skus']}, 新上架={data['new']}, 销量={data['sales']}, 有对手={data['has_rival']}, 销售额=${data['rev']:.2f}")

print("\n" + "=" * 80)
print("【拓展类型维度】")
print("=" * 80)
ex_groups = {}
for _, r in df_curr.iterrows():
    key = str(r.iloc[col_expand]).strip() or '未知'
    if key not in ex_groups:
        ex_groups[key] = {'skus': 0, 'sales': 0, 'rev': 0, 'has_rival': 0, 'y': 0, 'n': 0, 'no': 0}
    ex_groups[key]['skus'] += 1
    ex_groups[key]['sales'] += num(r.iloc[col_sales_curr])
    ex_groups[key]['rev'] += num(r.iloc[col_rev_curr])
    if num(r.iloc[col_rival_curr]) > 0:
        ex_groups[key]['has_rival'] += 1
    v = str(r.iloc[col_ord8_curr] if not pd.isna(r.iloc[col_ord8_curr]) else '').strip()
    if v == 'Y': ex_groups[key]['y'] += 1
    elif v == 'N': ex_groups[key]['n'] += 1
    elif v == '未出单': ex_groups[key]['no'] += 1

for ex, data in sorted(ex_groups.items()):
    ordered = data['y'] + data['n']
    rate = round(ordered/data['has_rival']*100, 1) if data['has_rival'] > 0 else 0
    print(f"{ex}: SKU={data['skus']}, 有对手={data['has_rival']}, Y={data['y']}, N={data['n']}, 未={data['no']}, 出单率={rate}%")

print("\n" + "=" * 80)
print("【新品未出单原因分析】")
print("=" * 80)
# 有对手未出单
has_rival_no = has_rival[has_rival.iloc[:, col_ord8_curr].apply(lambda x: str(x).strip() == '未出单')]
# 无对手未出单
no_rival_no = no_rival[no_rival.iloc[:, col_ord8_curr].apply(lambda x: str(x).strip() == '未出单')]

print(f"有对手未出单: {len(has_rival_no)} 个")
for _, r in has_rival_no.iterrows():
    mkt = str(r.iloc[col_market_curr]).strip() if not pd.isna(r.iloc[col_market_curr]) else ''
    print(f"  {r.iloc[1]} | {r.iloc[5]} | {r.iloc[4]} | 市场状态:{mkt}")

print(f"\n无对手未出单: {len(no_rival_no)} 个")
# 无对手未出单 - 按市场状态分类
ws_no = no_rival_no[no_rival_no.iloc[:, col_market_curr].apply(lambda x: str(x).strip() == '无市场')]
jz_no = no_rival_no[no_rival_no.iloc[:, col_market_curr].apply(lambda x: str(x).strip() == '竞争无优势')]
print(f"  无市场: {len(ws_no)} 个")
print(f"  竞争无优势: {len(jz_no)} 个")

print("\n" + "=" * 80)
print("【PLP广告统计 - 4.30-5.6】")
print("=" * 80)
df_plp_curr = df_plp[df_plp['统计周期'] == '4.30-5.6']
print(f"PLP活动数: {len(df_plp_curr)}")
# 过滤掉上架日期>5.6的SKU
df_plp_valid = df_plp_curr[df_plp_curr['实际上架日期'].apply(lambda x: get_date(x) and get_date(x) <= cutoff_curr)]
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

print("\n" + "=" * 80)
print("【PLG费率统计 - 4.30-5.6】")
print("=" * 80)
# 从主数据获取PLG费率
df_curr_plg = df_curr[df_curr.iloc[:, col_plg_curr].apply(lambda x: not pd.isna(x) and num(x) > 0)]
print(f"有PLG费率的SKU数: {len(df_curr_plg)}")
for _, r in df_curr_plg.iterrows():
    plg = num(r.iloc[col_plg_curr])
    print(f"  {r.iloc[1]} | {r.iloc[4]} | PLG费率: {plg:.3f}")

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
    print(f"{an}: SKU={data['sku']}, 曝光={data['exposure']:.0f}, 点击={data['clicks']:.0f}, 售出={data['sold']:.0f}, 花费=${data['spend']:.2f}, ROAS={roas:.2f}, ACOS={acos:.2f}%, ACOAS={acoas:.2f}%")

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
    print(f"{cat}: SKU={data['sku']}, 曝光={data['exposure']:.0f}, 点击={data['clicks']:.0f}, 售出={data['sold']:.0f}, 花费=${data['spend']:.2f}, ROAS={roas:.2f}, ACOS={acos:.2f}%, ACOAS={acoas:.2f}%")

print("\n" + "=" * 80)
print("【5.9日上架的新品 - 应排除】")
print("=" * 80)
df_after = df_main[df_main.iloc[:, col_list_date].apply(lambda x: get_date(x) and get_date(x) > cutoff_curr)]
print(f"5.6之后上架的SKU数: {len(df_after)}")
for _, r in df_after.iterrows():
    print(f"  {r.iloc[1]} | 实际上架日期: {r.iloc[col_list_date]}")
