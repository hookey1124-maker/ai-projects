"""最终检查JS渲染目标ID和HTML容器ID的一致性"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all JS getElementById targets
js_targets = set()
for m in re.finditer(r"getElementById\('([^']+)'\)", html):
    js_targets.add(m.group(1))

# Extract all HTML element IDs
html_ids = set()
for m in re.finditer(r'id="([^"]+)"', html):
    html_ids.add(m.group(1))

# Check consistency
print("=" * 60)
print("JS → HTML ID一致性检查")
print("=" * 60)

errors = []
for target in sorted(js_targets):
    if target.startswith('t') or target.startswith('chart-') or target.startswith('ls-'):
        if target in html_ids:
            print(f"  ✅ {target}")
        else:
            print(f"  ❌ {target} — JS渲染目标 但HTML中不存在!")
            errors.append(target)

# Extra: check all tab content IDs
for tab_id in ['tab1', 'tab2', 'tab3', 'tab4', 'tab5', 'tab6']:
    if f'id="{tab_id}"' in html:
        print(f"  ✅ Tab容器 {tab_id} 存在")
    else:
        print(f"  ❌ Tab容器 {tab_id} 缺失!")
        errors.append(tab_id)

print(f"\n共 {len(js_targets)} 个JS渲染目标")
print(f"错误: {len(errors)} 个")
if errors:
    for e in errors:
        print(f"  - {e}")
else:
    print("全部通过！")
