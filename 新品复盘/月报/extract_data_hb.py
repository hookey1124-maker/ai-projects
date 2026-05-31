import pandas as pd
import json

df = pd.read_excel('新品月报数据.xlsx')

# 确定月份批次
def get_batch(date):
    if pd.isna(date):
        return None
    month = pd.to_datetime(date).month
    if month == 1:
        return '1月'
    elif month == 2:
        return '2月'
    elif month == 3:
        return '3月'
    return None

df['批次'] = df['最新上架日期'].apply(get_batch)
df_123 = df[df['批次'].notna() & (df['批次'].isin(['1月', '2月', '3月']))].copy()

result = {'batch': {}, 'category': {}, 'analyst': {}, 'expand': {}, 'order': {}, 'market': {}, 'low_share': []}

# 各批次汇总数据（含环比）
for batch in ['1月', '2月', '3月']:
    sub = df_123[df_123['批次'] == batch]
    sku = len(sub)
    qty = int(sub['3月销量'].sum())
    amt = float(sub['3月销售额'].sum())
    comp = int(pd.to_numeric(sub['3月对手出单'], errors='coerce').sum())
    ordered = len(sub[sub['3月 8日出单'].isin(['Y'])])
    unorder = len(sub[sub['3月 8日出单'].isin(['N'])])
    not_order = len(sub[sub['3月 8日出单'].isin(['未出单'])])
    rate = round(ordered / sku * 100, 1) if sku > 0 else 0
    self_sales = sub['3月销量'].fillna(0)
    comp_sales = pd.to_numeric(sub['3月对手出单'], errors='coerce').fillna(0)
    total = self_sales + comp_sales
    share = round((self_sales / total.replace(0, 1)).mean() * 100, 1)
    result['batch'][batch] = {'sku': sku, 'qty': qty, 'amt': amt, 'comp': comp, 'ordered': ordered, 'unorder': unorder, 'not_order': not_order, 'rate': rate, 'share': share}

# 计算环比
batch_order = ['1月', '2月', '3月']
for i, b in enumerate(batch_order):
    if i == 0:
        result['batch'][b]['qty_hb'] = '-'
        result['batch'][b]['rate_hb'] = '-'
        result['batch'][b]['share_hb'] = '-'
    else:
        prev = batch_order[i-1]
        qty_hb = result['batch'][b]['qty'] - result['batch'][prev]['qty']
        rate_hb = result['batch'][b]['rate'] - result['batch'][prev]['rate']
        share_hb = result['batch'][b]['share'] - result['batch'][prev]['share']
        result['batch'][b]['qty_hb'] = qty_hb
        result['batch'][b]['rate_hb'] = round(rate_hb, 1)
        result['batch'][b]['share_hb'] = round(share_hb, 1)

# 品线维度（含环比）
for cat in df_123['品类'].dropna().unique():
    sub = df_123[df_123['品类'] == cat]
    cat_data = {'qty_1': 0, 'qty_2': 0, 'qty_3': 0, 'rate_1': 0, 'rate_2': 0, 'rate_3': 0}
    for b in ['1月', '2月', '3月']:
        s = sub[sub['批次'] == b]
        sku = len(s)
        ordered = len(s[s['3月 8日出单'].isin(['Y'])])
        cat_data['qty_' + b[0]] = int(s['3月销量'].sum())
        cat_data['rate_' + b[0]] = round(ordered / sku * 100, 1) if sku > 0 else 0
    cat_data['qty_hb'] = cat_data['qty_3'] - cat_data['qty_2']
    cat_data['rate_hb'] = round(cat_data['rate_3'] - cat_data['rate_2'], 1)
    result['category'][cat] = cat_data

# 分析人维度
for analyst in df_123['3月分析人'].dropna().unique():
    sub = df_123[df_123['3月分析人'] == analyst]
    ana_data = {'qty_1': 0, 'qty_2': 0, 'qty_3': 0, 'rate_1': 0, 'rate_2': 0, 'rate_3': 0, 'sku_1': 0, 'sku_2': 0, 'sku_3': 0}
    for b in ['1月', '2月', '3月']:
        s = sub[sub['批次'] == b]
        sku = len(s)
        ordered = len(s[s['3月 8日出单'].isin(['Y'])])
        ana_data['qty_' + b[0]] = int(s['3月销量'].sum())
        ana_data['rate_' + b[0]] = round(ordered / sku * 100, 1) if sku > 0 else 0
        ana_data['sku_' + b[0]] = sku
    ana_data['qty_hb'] = ana_data['qty_3'] - ana_data['qty_2']
    ana_data['rate_hb'] = round(ana_data['rate_3'] - ana_data['rate_2'], 1)
    result['analyst'][analyst] = ana_data

# 拓展类型维度
for exp in df_123['产品拓展'].dropna().unique():
    sub = df_123[df_123['产品拓展'] == exp]
    exp_data = {'qty_1': 0, 'qty_2': 0, 'qty_3': 0, 'rate_1': 0, 'rate_2': 0, 'rate_3': 0, 'sku_1': 0, 'sku_2': 0, 'sku_3': 0}
    for b in ['1月', '2月', '3月']:
        s = sub[sub['批次'] == b]
        sku = len(s)
        ordered = len(s[s['3月 8日出单'].isin(['Y'])])
        exp_data['qty_' + b[0]] = int(s['3月销量'].sum())
        exp_data['rate_' + b[0]] = round(ordered / sku * 100, 1) if sku > 0 else 0
        exp_data['sku_' + b[0]] = sku
    exp_data['qty_hb'] = exp_data['qty_3'] - exp_data['qty_2']
    exp_data['rate_hb'] = round(exp_data['rate_3'] - exp_data['rate_2'], 1)
    result['expand'][exp] = exp_data

# 出单情况分布
for b in ['1月', '2月', '3月']:
    sub = df_123[df_123['批次'] == b]
    result['order'][b] = {
        'Y': len(sub[sub['3月 8日出单'].isin(['Y'])]),
        'N': len(sub[sub['3月 8日出单'].isin(['N'])]),
        '未出单': len(sub[sub['3月 8日出单'].isin(['未出单'])])
    }

# 市场状态分布
for b in ['1月', '2月', '3月']:
    sub = df_123[df_123['批次'] == b]
    result['market'][b] = sub['3月市场状态'].value_counts().to_dict()

# 低占比新品（市占<0.75 且 对手有出单）
for idx, row in df_123.iterrows():
    self_s = float(row['3月销量']) if pd.notna(row['3月销量']) else 0
    comp_s = float(row['3月对手出单']) if pd.notna(row['3月对手出单']) else 0
    share = self_s / (self_s + comp_s) if (self_s + comp_s) > 0 else 0
    if share < 0.75 and comp_s > 0:
        result['low_share'].append({
            'sku': row['SKU'],
            'cat': row['品类'],
            'analyst': row['3月分析人'],
            'expand': row['产品拓展'],
            'qty': self_s,
            'comp': comp_s,
            'share': round(share * 100, 1),
            'order': row['3月 8日出单'],
            'status': row['3月市场状态'],
            'batch': row['批次']
        })

with open('report_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('数据提取完成！')
print('低占比新品总数:', len(result['low_share']))
for b in ['1月', '2月', '3月']:
    count = len([x for x in result['low_share'] if x['batch'] == b])
    print('  ' + b + ': ' + str(count) + '个')
