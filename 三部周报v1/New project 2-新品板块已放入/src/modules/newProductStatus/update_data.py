import json
import re

# 读取 corrected_data.json
with open(r'c:\Users\Hardy\ai-projects\三部周报v1\New project 2\src\modules\newProductStatus\corrected_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取 NewProductStatusPage.tsx
with open(r'c:\Users\Hardy\ai-projects\三部周报v1\New project 2\src\modules\newProductStatus\NewProductStatusPage.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 更新四三累计数据（从10条更新为109条）
cum43_data_str = json.dumps(data['cum43Data'], ensure_ascii=False, indent=2)
# 替换 cum43Data 数组
pattern = r'const cum43Data = \[.*?\];'
replacement = f'const cum43Data = {cum43_data_str};'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 2. 更新四三累计统计
cum43_stats = data['cum43Stats']
stats_pattern = r'const cum43Stats = \{.*?\};'
stats_replacement = f'''const cum43Stats = {{
  total: {cum43_stats['total']},
  yCount: {cum43_stats['yCount']},
  nCount: {cum43_stats['nCount']},
  unCount: {cum43_stats['unCount']},
  normalCount: {cum43_stats['normalCount']},
  competitiveCount: {cum43_stats['competitiveCount']},
  noMarketCount: {cum43_stats['noMarketCount']}
}};'''
content = re.sub(stats_pattern, stats_replacement, content, flags=re.DOTALL)

# 3. 更新低占比新品数据
low_share_data = data['lowShareData']
low_share_str = json.dumps(low_share_data, ensure_ascii=False, indent=2)
# 转换格式以匹配现有代码
low_share_converted = []
for item in low_share_data:
    low_share_converted.append({
        "id": item["salesCode"],
        "sku": item["sku"],
        "cat": item["category"],
        "an": item["analyst"],
        "listDate": item["launchDate"],
        "qty": item["curSalesQty"],
        "rev": item["curRevenue"],
        "rivalQty": item["curCompetitorQty"],
        "share": item["curMarketShare"],
        "ord8": item["cur8dStatus"],
        "status": item["curMarketStatus"]
    })

low_share_converted_str = json.dumps(low_share_converted, ensure_ascii=False, indent=2)
pattern = r'const lowShareData = \[.*?\];'
replacement = f'const lowShareData = {low_share_converted_str};'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 4. 更新未出单数据 - 合并有对手和无对手数据
unsold_has_comp = data.get('unsoldHasCompetitor', {'total': 0, 'byAnalyst': [], 'byCategory': []})
unsold_no_comp = data.get('unsoldNoCompetitor', {})

# 更新未出单-按分析人数据
unorder_analysts = []
all_analysts = {}

# 合并有对手未出单分析人
for item in unsold_has_comp.get('byAnalyst', []):
    all_analysts[item['analyst']] = {'hasComp': item, 'noComp': None}

# 合并无对手未出单分析人
for item in unsold_no_comp.get('byAnalyst', []):
    if item['analyst'] in all_analysts:
        all_analysts[item['analyst']]['noComp'] = item
    else:
        all_analysts[item['analyst']] = {'hasComp': None, 'noComp': item}

for analyst, data_pair in all_analysts.items():
    has_comp = data_pair['hasComp']
    no_comp = data_pair['noComp']
    unorder_analysts.append({
        "name": analyst,
        "a_jz": has_comp['competitiveWeak'] if has_comp else 0,  # 有对手-竞争无优势
        "a_ws": has_comp['noMarket'] if has_comp else 0,  # 有对手-无市场
        "a_total": has_comp['total'] if has_comp else 0,  # 有对手总计
        "b_ws": no_comp['noMarket'] if no_comp else 0,  # 无对手-无市场
        "b_jz": no_comp['competitiveWeak'] if no_comp else 0,  # 无对手-竞争无优势
        "b_total": no_comp['total'] if no_comp else 0,  # 无对手总计
        "total": (has_comp['total'] if has_comp else 0) + (no_comp['total'] if no_comp else 0)  # 总计
    })

unorder_an_str = json.dumps(unorder_analysts, ensure_ascii=False, indent=2)
pattern = r'const unorderAnData = \[.*?\];'
replacement = f'const unorderAnData = {unorder_an_str};'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 更新未出单-按品线数据
unorder_categories = []
all_categories = {}

# 合并有对手未出单品线
for item in unsold_has_comp.get('byCategory', []):
    all_categories[item['category']] = {'hasComp': item, 'noComp': None}

# 合并无对手未出单品线
for item in unsold_no_comp.get('byCategory', []):
    if item['category'] in all_categories:
        all_categories[item['category']]['noComp'] = item
    else:
        all_categories[item['category']] = {'hasComp': None, 'noComp': item}

for category, data_pair in all_categories.items():
    has_comp = data_pair['hasComp']
    no_comp = data_pair['noComp']
    unorder_categories.append({
        "name": category,
        "a_jz": has_comp['competitiveWeak'] if has_comp else 0,
        "a_ws": has_comp['noMarket'] if has_comp else 0,
        "a_total": has_comp['total'] if has_comp else 0,
        "b_ws": no_comp['noMarket'] if no_comp else 0,
        "b_jz": no_comp['competitiveWeak'] if no_comp else 0,
        "b_total": no_comp['total'] if no_comp else 0,
        "total": (has_comp['total'] if has_comp else 0) + (no_comp['total'] if no_comp else 0)
    })

unorder_cat_str = json.dumps(unorder_categories, ensure_ascii=False, indent=2)
pattern = r'const unorderCatData = \[.*?\];'
replacement = f'const unorderCatData = {unorder_cat_str};'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 5. 更新PLP分析人维度数据
plp_analysts = data.get('plpAnalysts', [])
plp_analysts_str = json.dumps(plp_analysts, ensure_ascii=False, indent=2)
pattern = r'const plpAnalysts = \[.*?\];'
replacement = f'const plpAnalysts = {plp_analysts_str};'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 6. 更新PLP总计数据
plp_total = data.get('plpTotal', {})
plp_total_pattern = r'const plpTotal = \{.*?\};'
plp_total_replacement = f'''const plpTotal = {{
  campaignCount: {plp_total.get('campaignCount', 0)},
  linkCount: {plp_total.get('linkCount', 0)},
  impression: {plp_total.get('impression', 0)},
  click: {plp_total.get('click', 0)},
  sold: {plp_total.get('sold', 0)},
  cost: {plp_total.get('cost', 0)},
  revenue: {plp_total.get('revenue', 0)},
  roas: "{plp_total.get('roas', '')}",
  cvr: "{plp_total.get('cvr', '')}",
  ctr: "{plp_total.get('ctr', '')}",
  cpc: "{plp_total.get('cpc', '')}",
  cpa: "{plp_total.get('cpa', '')}",
  acos: "{plp_total.get('acos', '')}",
  acoas: "{plp_total.get('acoas', '')}"
}};'''
content = re.sub(plp_total_pattern, plp_total_replacement, content, flags=re.DOTALL)

# 保存更新后的文件
with open(r'c:\Users\Hardy\ai-projects\三部周报v1\New project 2\src\modules\newProductStatus\NewProductStatusPage.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("NewProductStatusPage.tsx 已更新")
print(f"- 四三累计数据: {len(data['cum43Data'])} 条")
print(f"- 低占比新品: {len(data['lowShareData'])} 条")
print(f"- 有对手未出单: {unsold_has_comp.get('total', 0)} 个")
print(f"- 无对手未出单: {unsold_no_comp.get('total', 0)} 个")
print(f"- PLP分析人数: {len(plp_analysts)} 个")
print(f"- PLP总ACOAS: {plp_total.get('acoas', '')}")
