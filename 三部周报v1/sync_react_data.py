"""
从共享 JSON 生成 React 项目需要的 corrected_data.json
每次更新周期时运行此脚本
"""
import json, os, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_JSON = os.path.join(THIS_DIR, '..', 'shared', 'output', 'latest.json')
TARGET = os.path.join(THIS_DIR, 'New project 2-新品板块已放入', 'src', 'modules', 'newProductStatus', 'corrected_data.json')

with open(SHARED_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

kpi = data['kpi']
timeliness = data['timeliness']
dims = data['dimensions']
cum43 = data['cum43Data']

# 构建 React 格式
corrected = {
    'cum43Data': cum43,
    'cum43Stats': kpi,
    'lowShareData': data['lowShareData'],
    'expandTypeData': [
        {'expandType': k,
         'curSku': v.get('sku', 0),
         'curSalesQty': v.get('salesCurr', 0),
         'curRevenue': v.get('revenueCurr', 0),
         'soldRate': str(v.get('soldRate', 0))}
        for k, v in dims.get('expandTypes', {}).items()
    ],
    'timelinessData': {
        'analysts': [],
        'total': {
            'analyst': '合计',
            'curSku': timeliness['total'],
            'timelyCount': timeliness['timelyCount'],
            'noAnalysis8dCount': timeliness['noAnalysis8d'],
            'noAnalysis7dCount': timeliness['over7d'],
            'timelyRate': str(timeliness['timelyRate']) + '%',
        }
    },
    'categoryRevenueData': [
        {'category': k,
         'curSku': sum(1 for r in cum43 if r.get('category') == k),
         'curSalesQty': v.get('salesCurr', 0),
         'prevSalesQty': v.get('salesPrev', 0),
         'curRevenue': v.get('revenueCurr', 0),
         'prevRevenue': v.get('revenuePrev', 0),
         'salesQtyChange': '-',
         'revenueChange': '-'}
        for k, v in dims.get('categories', {}).items()
    ],
    'analystRevenueData': [
        {'analyst': k,
         'curSku': sum(1 for r in cum43 if r.get('analyst') == k),
         'curSalesQty': v.get('salesCurr', 0),
         'prevSalesQty': v.get('salesPrev', 0),
         'curRevenue': v.get('revenueCurr', 0),
         'prevRevenue': v.get('revenuePrev', 0),
         'salesQtyChange': '-',
         'revenueChange': '-'}
        for k, v in dims.get('analysts', {}).items()
    ],
    'prevWeekKpi': {
        'totalSales': kpi['totalSalesPrev'],
        'totalRevenue': kpi['totalRevenuePrev'],
        'hasCompetitorSku': kpi['hasRivalSku'],
    },
    'plgRecords': [],
    'plpTotal': {},
    'plpPrevTotal': {},
    'plpCategories': [],
    'plpExpandTypes': [],
    'plpAnalysts': [],
    'hasCompetitorUnsold': {},
    'unsoldNoCompetitor': {},
    'plgStats': {},
    'prevWeekAnalysts': {},
    'plpSummaryData': [],
    'plpDetailData': [],
}

with open(TARGET, 'w', encoding='utf-8') as f:
    json.dump(corrected, f, ensure_ascii=False, indent=2)

print('✅ corrected_data.json 已更新到 5.14-5.20')
print(f'   写入: {TARGET}')
print(f'   SKU: {len(cum43)}, 低占比: {len(data["lowShareData"])}')
print(f'   销量: {kpi["totalSales"]}, 销售额: ${kpi["totalRevenue"]:,.2f}')
print(f'   出单率: {kpi["soldRate"]}%')
