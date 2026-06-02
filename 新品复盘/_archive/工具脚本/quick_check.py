"""快速JS诊断"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html', 'r', encoding='utf-8') as f:
    html = f.read()
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not script_match:
    print('ERROR: No script block found!')
    sys.exit(1)
js = script_match.group(1)
lines = js.split('\n')
print(f'JS total lines: {len(lines)}')

# Bracket balance
op = js.count('(') - js.count(')')
ob = js.count('{') - js.count('}')
obr = js.count('[') - js.count(']')
print(f'Brackets: ()={op}, {{}}={ob}, []= {obr}')

# Check critical functions
for fn in ['switchTab', 'initCharts1', 'initCharts2', 'copyReport', 'renderT5Table', 'renderLowShareTable']:
    found = f'function {fn}' in js or f'window.{fn}' in js
    print(f'  fn {fn}: {"OK" if found else "MISSING!"}')

# Check variables
for var in ['cum43Data', 'cum43Stats', 'prevWeekKpi', 'plpTotal', 'plgStats', 'priceOverview', 'mktDistOverall', 'shareTierOverview', 'categoryRevenueData', 'analystRevenueData']:
    found = var in js
    print(f'  var {var}: {"OK" if found else "MISSING!"}')

# Look for syntax error patterns
for i, line in enumerate(lines, 1):
    s = line.strip()
    if ',,' in s:
        print(f'  DOUBLE COMMA line {i}: {s[:80]}')
    if s.count('function(') > 1:
        print(f'  MULTI FUNCTION line {i}: {s[:80]}')

# Check for the specific restructure errors: does Tab2 JS correctly render to t2-kpi
if "getElementById('t2-kpi')" in js:
    t2_count = js.count("getElementById('t2-kpi')")
    print(f'  t2-kpi renders: {t2_count}x')
if "getElementById('t3-kpi')" in js:
    t3_count = js.count("getElementById('t3-kpi')")
    print(f'  t3-kpi renders: {t3_count}x')

# Check that initCharts2 is called on tab2 switch
if "tabId === 'tab2' && !window._charts2Init" in js:
    print('  Tab2 lazy init: OK')

# Verify HTML body has all 6 tabs
for ti in range(1, 7):
    tid = f'tab{ti}'
    if f'id="{tid}"' in html:
        print(f'  Tab container {tid}: OK')
    else:
        print(f'  Tab container {tid}: MISSING!')

print('\nDone.')
