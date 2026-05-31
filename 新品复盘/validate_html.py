import re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
print(f'Found {len(scripts)} script blocks')
for i, js in enumerate(scripts):
    lines = js.strip().split('\n')
    print(f'  Block {i+1}: {len(lines)} lines')
    # Check bracket balance
    op = js.count('(') - js.count(')')
    ob = js.count('{') - js.count('}')
    obr = js.count('[') - js.count(']')
    print(f'  Brackets: ()={op}, {{}}={ob}, []= {obr}')

for var in ['cum43Data', 'cum43Stats', 'prevWeekKpi', 'plpTotal', 'plgStats', 'categoryRevenueData', 'analystRevenueData']:
    ok = "OK" if var in html else "MISSING"
    print(f'  Variable {var}: {ok}')

for tab_id in ['tab1', 'tab2', 'tab3', 'tab4', 'tab5']:
    ok = "OK" if ('id="' + tab_id + '"') in html else "MISSING"
    print(f'  Tab {tab_id}: {ok}')

if 'chart.js@4' in html.lower():
    print('  Chart.js CDN: OK')

# Check for specific features
features = [
    ('4段甜甜圈', 'noRivalSold'),
    ('市占比环比', 'marketShareChange'),
    ('PLG ACOS', 'plgStats'),
    ('PLG花费', 'totalSpend'),
    ('新品总市占比', 'totalMarketShare'),
    ('品线市占比图表', 'chart-cat-share'),
    ('分析人市占比图表', 'chart-an-share'),
]
for name, keyword in features:
    ok = "OK" if keyword in html else "MISSING"
    print(f'  Feature [{name}]: {ok}')

print(f'\nFile size: {len(html)} chars')
print('Validation complete!')
