with open('新品月报_2026年3月_增强版.html', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('ALL_DATA', 'var ALL_DATA = '),
    ('LOW_SHARE_DATA', 'var LOW_SHARE_DATA = '),
    ('分析人频次字段freq_1', 'freq_1'),
    ('销售额字段amt_1', 'amt_1'),
    ('均价字段price_1', 'price_1'),
    ('上架日期onshelf', 'onshelf'),
    ('首次出单first_order', 'first_order'),
    ('三月市场状态status3', 'status3'),
    ('品线三月销售额amt_3', 'amt_3'),
    ('多选下拉过滤器detail-cat', 'detail-cat'),
    ('分析人过滤器detail-analyst', 'detail-analyst'),
    ('三月未出单对比UNORDER_DIST', 'UNORDER_DIST'),
]
for name, pattern in checks:
    found = pattern in html
    print(f'{"OK" if found else "MISSING"}: {name}')

import json
start = html.find('var ALL_DATA = ') + len('var ALL_DATA = ')
end = html.find(';\nvar CAT_DATA', start)
all_data = json.loads(html[start:end])
print(f'全量明细: {len(all_data)} 条')

start2 = html.find('var LOW_SHARE_DATA = ') + len('var LOW_SHARE_DATA = ')
end2 = html.find(';\nvar CAT_DATA', start2)
ls_data = json.loads(html[start2:end2])
print(f'低占比数据: {len(ls_data)} 条')

# 验证分析人数据包含freq字段
start3 = html.find('var ANALYST_DATA = ') + len('var ANALYST_DATA = ')
end3 = html.find(';\nvar EXPAND_DATA', start3)
an_data = json.loads(html[start3:end3])
first_analyst = list(an_data.values())[0]
print(f'分析人数据字段: {list(first_analyst.keys())}')
