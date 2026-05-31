# -*- coding: utf-8 -*-
import pandas as pd
import json
from datetime import datetime

# 读取源数据
xlsx = pd.ExcelFile('新品月报数据.xlsx')
df = pd.read_excel(xlsx, sheet_name='源数据')

# 转换日期
df['最新上架日期'] = pd.to_datetime(df['最新上架日期'], errors='coerce')

# 提取月份
def get_month(date):
    if pd.isna(date):
        return None
    return date.month

df['上架月份'] = df['最新上架日期'].apply(get_month)

# 1月新品：上架月份=1
jan_df = df[df['上架月份'] == 1].copy()
# 2月新品：上架月份=2
feb_df = df[df['上架月份'] == 2].copy()
# 3月新品：上架月份=3
mar_df = df[df['上架月份'] == 3].copy()

print("=== 数据统计 ===")
print(f"1月新品数量: {len(jan_df)}")
print(f"2月新品数量: {len(feb_df)}")
print(f"3月新品数量: {len(mar_df)}")

# 统计各批次数据
def calc_batch_stats(batch_df, month_col):
    if len(batch_df) == 0:
        return {'sku': 0, 'qty': 0, 'amt': 0, 'order_8y': 0, 'order_8n': 0, 'unorder': 0, 'rate': 0, 'low_share': 0, 'share_rate': 0}
    
    qty_col = f'{month_col}销量'
    amt_col = f'{month_col}销售额'
    order_col = f'{month_col} 8日出单'
    comp_col = f'{month_col}对手出单'
    share_col = f'{month_col}市占比'
    
    sku = len(batch_df)
    qty = batch_df[qty_col].sum() if qty_col in batch_df.columns else 0
    amt = batch_df[amt_col].sum() if amt_col in batch_df.columns else 0
    
    # 8日出单统计
    if order_col in batch_df.columns:
        y_count = len(batch_df[batch_df[order_col] == 'Y'])
        n_count = len(batch_df[batch_df[order_col] == 'N'])
        unorder_count = len(batch_df[(batch_df[order_col] == '未出单') | (batch_df[order_col].isna())])
    else:
        y_count, n_count, unorder_count = 0, 0, sku
    
    # 出单率
    if sku > 0:
        rate = (y_count / sku) * 100
    else:
        rate = 0
    
    # 自身低占比且对手有出单的新品
    if share_col in batch_df.columns and comp_col in batch_df.columns:
        # 转换为数值类型
        batch_df_copy = batch_df.copy()
        batch_df_copy[share_col] = pd.to_numeric(batch_df_copy[share_col], errors='coerce')
        batch_df_copy[comp_col] = pd.to_numeric(batch_df_copy[comp_col], errors='coerce')
        
        low_share_df = batch_df_copy[
            (batch_df_copy[comp_col] > 0) &  # 对手有出单
            (batch_df_copy[share_col] < 0.75) &  # 自身市占比低于75%
            (batch_df_copy[share_col] > 0)  # 排除0占比
        ]
        low_share_count = len(low_share_df)
    else:
        low_share_count = 0
    
    # 计算市占比
    if qty_col in batch_df.columns and comp_col in batch_df.columns:
        total = qty + batch_df[comp_col].sum()
        if total > 0:
            share_rate = (qty / total) * 100
        else:
            share_rate = 0
    else:
        share_rate = 0
    
    return {
        'sku': sku, 
        'qty': int(qty), 
        'amt': float(amt), 
        'order_8y': y_count, 
        'order_8n': n_count, 
        'unorder': unorder_count,
        'rate': float(rate),
        'low_share': low_share_count,
        'share_rate': float(share_rate)
    }

jan_stats = calc_batch_stats(jan_df, '1月')
feb_stats = calc_batch_stats(feb_df, '2月')
mar_stats = calc_batch_stats(mar_df, '3月')

print("\n=== 各批次统计 ===")
print(f"1月新品: SKU={jan_stats['sku']}, 销量={jan_stats['qty']}, 销售额={jan_stats['amt']:.2f}, 出单率={jan_stats['rate']:.1f}%, 市占比={jan_stats['share_rate']:.1f}%")
print(f"2月新品: SKU={feb_stats['sku']}, 销量={feb_stats['qty']}, 销售额={feb_stats['amt']:.2f}, 出单率={feb_stats['rate']:.1f}%, 市占比={feb_stats['share_rate']:.1f}%")
print(f"3月新品: SKU={mar_stats['sku']}, 销量={mar_stats['qty']}, 销售额={mar_stats['amt']:.2f}, 出单率={mar_stats['rate']:.1f}%, 市占比={mar_stats['share_rate']:.1f}%")

# 按品线统计
def calc_category_stats(batch_df, month_col):
    if len(batch_df) == 0:
        return {}
    
    qty_col = f'{month_col}销量'
    order_col = f'{month_col} 8日出单'
    comp_col = f'{month_col}对手出单'
    amt_col = f'{month_col}销售额'
    
    stats = {}
    for cat in batch_df['品类'].dropna().unique():
        cat_df = batch_df[batch_df['品类'] == cat]
        sku_count = len(cat_df)
        qty = cat_df[qty_col].sum() if qty_col in cat_df.columns else 0
        amt = cat_df[amt_col].sum() if amt_col in cat_df.columns else 0
        comp_qty = cat_df[comp_col].sum() if comp_col in cat_df.columns else 0
        
        # 出单率
        if order_col in cat_df.columns:
            y_count = len(cat_df[cat_df[order_col] == 'Y'])
            rate = (y_count / sku_count * 100) if sku_count > 0 else 0
        else:
            rate = 0
        
        # 市占比
        total = qty + comp_qty
        share = (qty / total * 100) if total > 0 else 0
        
        stats[cat] = {'sku': sku_count, 'qty': int(qty), 'amt': float(amt), 'rate': float(rate), 'share': float(share)}
    
    return stats

jan_cat = calc_category_stats(jan_df, '1月')
feb_cat = calc_category_stats(feb_df, '2月')
mar_cat = calc_category_stats(mar_df, '3月')

print("\n=== 品线统计 ===")
all_cats = set(list(jan_cat.keys()) + list(feb_cat.keys()) + list(mar_cat.keys()))
for cat in sorted(all_cats):
    j = jan_cat.get(cat, {'sku': 0, 'qty': 0, 'rate': 0, 'share': 0, 'amt': 0})
    f = feb_cat.get(cat, {'sku': 0, 'qty': 0, 'rate': 0, 'share': 0, 'amt': 0})
    m = mar_cat.get(cat, {'sku': 0, 'qty': 0, 'rate': 0, 'share': 0, 'amt': 0})
    print(f"{cat}: 1月(sku={j['sku']},qty={j['qty']},rate={j['rate']:.1f}%,share={j['share']:.1f}%), 2月(sku={f['sku']},qty={f['qty']},rate={f['rate']:.1f}%,share={f['share']:.1f}%), 3月(sku={m['sku']},qty={m['qty']},rate={m['rate']:.1f}%,share={m['share']:.1f}%)")

# 按拓展类型统计
def calc_expand_stats(batch_df, month_col):
    if len(batch_df) == 0:
        return {}
    
    qty_col = f'{month_col}销量'
    order_col = f'{month_col} 8日出单'
    comp_col = f'{month_col}对手出单'
    
    stats = {}
    for exp in batch_df['产品拓展'].dropna().unique():
        exp_df = batch_df[batch_df['产品拓展'] == exp]
        sku_count = len(exp_df)
        qty = exp_df[qty_col].sum() if qty_col in exp_df.columns else 0
        comp_qty = exp_df[comp_col].sum() if comp_col in exp_df.columns else 0
        
        # 出单率
        if order_col in exp_df.columns:
            y_count = len(exp_df[exp_df[order_col] == 'Y'])
            rate = (y_count / sku_count * 100) if sku_count > 0 else 0
        else:
            rate = 0
        
        # 市占比
        total = qty + comp_qty
        share = (qty / total * 100) if total > 0 else 0
        
        stats[exp] = {'sku': sku_count, 'qty': int(qty), 'rate': float(rate), 'share': float(share)}
    
    return stats

jan_exp = calc_expand_stats(jan_df, '1月')
feb_exp = calc_expand_stats(feb_df, '2月')
mar_exp = calc_expand_stats(mar_df, '3月')

print("\n=== 拓展类型统计 ===")
for exp in ['原开品', '拓展品', '组合件']:
    j = jan_exp.get(exp, {'sku': 0, 'qty': 0, 'rate': 0, 'share': 0})
    f = feb_exp.get(exp, {'sku': 0, 'qty': 0, 'rate': 0, 'share': 0})
    m = mar_exp.get(exp, {'sku': 0, 'qty': 0, 'rate': 0, 'share': 0})
    print(f"{exp}: 1月(sku={j['sku']},qty={j['qty']},rate={j['rate']:.1f}%), 2月(sku={f['sku']},qty={f['qty']},rate={f['rate']:.1f}%), 3月(sku={m['sku']},qty={m['qty']},rate={m['rate']:.1f}%)")

# 统计低占比新品（自身<75%且对手有出单）
def get_low_share_sku(batch_df, month_col):
    if len(batch_df) == 0:
        return []
    
    share_col = f'{month_col}市占比'
    comp_col = f'{month_col}对手出单'
    qty_col = f'{month_col}销量'
    amt_col = f'{month_col}销售额'
    order_col = f'{month_col} 8日出单'
    status_col = f'{month_col}市场状态'
    
    results = []
    for _, row in batch_df.iterrows():
        share = row.get(share_col, 0)
        comp = row.get(comp_col, 0)
        qty = row.get(qty_col, 0)
        amt = row.get(amt_col, 0)
        order = row.get(order_col, '')
        status = row.get(status_col, '')
        sku = row['SKU']
        cat = row.get('品类', '')
        exp = row.get('产品拓展', '')
        
        # 转换为数值
        try:
            share = float(share)
        except:
            share = 0
        try:
            comp = float(comp) if pd.notna(comp) else 0
        except:
            comp = 0
        try:
            qty = float(qty) if pd.notna(qty) else 0
        except:
            qty = 0
        try:
            amt = float(amt) if pd.notna(amt) else 0
        except:
            amt = 0
        
        # 条件：自身市占比低于75%，且高于0，且对手有出单
        if share > 0 and share < 0.75 and comp > 0:
            results.append({
                'sku': str(sku),
                'cat': str(cat) if pd.notna(cat) else '',
                'exp': str(exp) if pd.notna(exp) else '',
                'qty': int(qty),
                'comp': int(comp),
                'amt': float(amt),
                'share': float(share),
                'order': str(order) if pd.notna(order) else '',
                'status': str(status) if pd.notna(status) else ''
            })
    
    # 按市占比升序排列
    results.sort(key=lambda x: x['share'])
    return results

jan_low = get_low_share_sku(jan_df, '1月')
feb_low = get_low_share_sku(feb_df, '2月')
mar_low = get_low_share_sku(mar_df, '3月')

print(f"\n=== 低占比新品统计（自身<75%且对手有出单）===")
print(f"1月低占比新品: {len(jan_low)}个")
print(f"2月低占比新品: {len(feb_low)}个")
print(f"3月低占比新品: {len(mar_low)}个")

# 打印低占比新品明细
if mar_low:
    print("\n3月低占比新品明细:")
    for item in mar_low[:15]:
        print(f"  {item['sku']}: {item['cat']}, 市占={item['share']*100:.1f}%, 对手={item['comp']}")
    if len(mar_low) > 15:
        print(f"  ... 还有{len(mar_low)-15}个")

# 统计未出单市场状态
def get_noorder_status(batch_df, month_col):
    if len(batch_df) == 0:
        return {}
    
    status_col = f'{month_col}市场状态'
    order_col = f'{month_col} 8日出单'
    
    # 只统计未出单的产品
    noorder_df = batch_df[(batch_df[order_col] == '未出单') | (batch_df[order_col].isna())]
    
    status_counts = {}
    for _, row in noorder_df.iterrows():
        status = row.get(status_col, '未知')
        if pd.notna(status):
            status_counts[status] = status_counts.get(status, 0) + 1
    
    return status_counts

jan_noorder = get_noorder_status(jan_df, '1月')
feb_noorder = get_noorder_status(feb_df, '2月')
mar_noorder = get_noorder_status(mar_df, '3月')

print("\n=== 未出单市场状态分布 ===")
print(f"1月未出单: {jan_noorder}")
print(f"2月未出单: {feb_noorder}")
print(f"3月未出单: {mar_noorder}")

# 保存结果到JSON供后续使用
result = {
    'jan_stats': jan_stats,
    'feb_stats': feb_stats,
    'mar_stats': mar_stats,
    'jan_cat': jan_cat,
    'feb_cat': feb_cat,
    'mar_cat': mar_cat,
    'jan_exp': jan_exp,
    'feb_exp': feb_exp,
    'mar_exp': mar_exp,
    'jan_low': jan_low,
    'feb_low': feb_low,
    'mar_low': mar_low,
    'jan_noorder': jan_noorder,
    'feb_noorder': feb_noorder,
    'mar_noorder': mar_noorder,
    'all_sku_data': []
}

# 获取全量SKU数据
def safe_to_num(val, default=0):
    try:
        result = float(val)
        return result if pd.notna(result) else default
    except:
        return default

for _, row in df.iterrows():
    sku = row['SKU']
    cat = row.get('品类', '')
    exp = row.get('产品拓展', '')
    
    # 判断上架月份
    month = row.get('上架月份', 0)
    if month == 1:
        batch = '1月新品'
        qty = safe_to_num(row.get('1月销量', 0))
        comp = safe_to_num(row.get('1月对手出单', 0))
        amt = safe_to_num(row.get('1月销售额', 0))
        share = safe_to_num(row.get('1月市占比', 0))
        order = row.get('1月 8日出单', '')
        status = row.get('1月市场状态', '')
    elif month == 2:
        batch = '2月新品'
        qty = safe_to_num(row.get('2月销量', 0))
        comp = safe_to_num(row.get('2月对手出单', 0))
        amt = safe_to_num(row.get('2月销售额', 0))
        share = safe_to_num(row.get('2月市占比', 0))
        order = row.get('2月 8日出单', '')
        status = row.get('2月市场状态', '')
    elif month == 3:
        batch = '3月新品'
        qty = safe_to_num(row.get('3月销量', 0))
        comp = safe_to_num(row.get('3月对手出单', 0))
        amt = safe_to_num(row.get('3月销售额', 0))
        share = safe_to_num(row.get('3月市占比', 0))
        order = row.get('3月 8日出单', '')
        status = row.get('3月市场状态', '')
    else:
        batch = '未知'
        qty, comp, amt, share = 0, 0, 0, 0
        order, status = '', ''
    
    result['all_sku_data'].append({
        'batch': batch,
        'sku': str(sku) if pd.notna(sku) else '',
        'cat': str(cat) if pd.notna(cat) else '',
        'exp': str(exp) if pd.notna(exp) else '',
        'qty': int(qty),
        'comp': int(comp),
        'amt': float(amt),
        'share': float(share),
        'order': str(order) if pd.notna(order) else '',
        'status': str(status) if pd.notna(status) else ''
    })

# 保存JSON
with open('report_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== 数据已保存到 report_data.json ===")
