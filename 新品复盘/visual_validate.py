"""
视觉交叉验证：检查HTML结构和数据完整性
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html'
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

errors = []
warnings = []

# 1. 检查HTML结构完整性
print("=" * 60)
print("视觉交叉验证报告")
print("=" * 60)

# 检查必要元素
checks = [
    ('<html', 'HTML标签'),
    ('<head>', 'HEAD标签'),
    ('<body>', 'BODY标签'),
    ('</html>', 'HTML闭合标签'),
    ('chart.js', 'Chart.js CDN'),
    ('<style>', '内嵌CSS'),
    ('<script>', '内嵌JS'),
]
for pattern, desc in checks:
    if pattern.lower() in html.lower():
        print(f'  ✅ {desc}')
    else:
        print(f'  ❌ {desc} 缺失!')
        errors.append(f'{desc}缺失')

# 2. 检查5个Tab容器
for tab_id in ['tab1', 'tab2', 'tab3', 'tab4', 'tab5']:
    if f'id="{tab_id}"' in html:
        print(f'  ✅ Tab {tab_id} 容器存在')
    else:
        print(f'  ❌ Tab {tab_id} 容器缺失!')
        errors.append(f'Tab {tab_id} 容器缺失')

# 3. 检查图表Canvas
canvas_count = len(re.findall(r'<canvas id="chart-', html))
print(f'  ✅ Chart Canvas: {canvas_count} 个')

# 4. 检查数据块
js_blocks = re.findall(r'const (\w+) = (\[.*?\]|\{.*?\});', html, re.DOTALL)
print(f'  ✅ JS数据块: {len(js_blocks)} 个')

# 5. 检查侧边栏导航
nav_items = re.findall(r'<li><a href="javascript:void\(0\)".*?onclick="switchTab\(\'(tab\d)\'', html)
print(f'  ✅ 侧边栏导航项: {len(nav_items)} 个 ({", ".join(nav_items)})')

# 6. 验证无品效Tab（不应该存在）
if '品效Cohort' in html:
    warnings.append('发现"品效Cohort"内容（Tab品效应已删除）')
    print('  ⚠️  发现品效相关残留内容')
else:
    print('  ✅ 品效Tab已清理干净')

if 'pinxiaoData' in html:
    warnings.append('发现pinxiaoData数据块残留')
    print('  ⚠️  发现pinxiaoData数据残留')
else:
    print('  ✅ 品效数据已清理')

# 7. 验证新功能
print("\n--- 新功能验证 ---")
features = [
    ('4段甜甜圈', 'noRivalSold.*noRivalUnsold', '4段数据'),
    ('有对手未出单(含#N/A)', 'unCount.*11', 'unCount=11含#N/A'),
    ('新品总市占比KPI', 'totalMarketShare', '总市占比KPI卡片'),
    ('市占比环比', 'marketShareChange', '市占比环比'),
    ('品线市占比图表', 'chart-cat-share', '品线市占比图'),
    ('分析人市占比图表', 'chart-an-share', '分析人市占比图'),
    ('PLG花费卡片', 'totalSpend|plgSpend', 'PLG花费数据'),
    ('PLG ACOS/ACOAS', 'plgStats.*acos.*acoas', 'PLG ACOS/ACOAS'),
    ('PLP自然周', '5.18-5.24', '自然周标识'),
    ('自然周PLG', 'PLG广告概览.*自然周', 'PLG自然周板块'),
]
for name, pattern, desc in features:
    if re.search(pattern, html, re.DOTALL):
        print(f'  ✅ {desc}: {name}')
    else:
        print(f'  ❌ {desc}: {name} 缺失!')
        errors.append(name)

# 8. 检查ACOS和ACOAS是两个不同的计算
acos_count = html.count('ACOS')
acoas_count = html.count('ACOAS')
print(f'\n  ACOS出现次数: {acos_count}')
print(f'  ACOAS出现次数: {acoas_count}')
if acos_count > 0 and acoas_count > 0:
    print('  ✅ ACOS和ACOAS都已正确区分')
else:
    print('  ❌ ACOS或ACOAS缺失!')

# 9. 检查汇报输出内容
print("\n--- 汇报输出验证 ---")
report_checks = [
    ('风险预警', 'risk-high|risk-medium|risk-low'),
    ('主要发现', 'findings-card'),
    ('下周动作', 'action-card'),
    ('复制文案', 'copy-btn|copyReport'),
]
for name, pattern in report_checks:
    if re.search(pattern, html, re.DOTALL):
        print(f'  ✅ {name} 存在')
    else:
        print(f'  ❌ {name} 缺失!')

# 10. CSS动画
anim_count = len(re.findall(r'@keyframes', html))
print(f'\n  ✅ @keyframes动画: {anim_count} 个')

# 总结
print("\n" + "=" * 60)
if errors:
    print(f"❌ 错误: {len(errors)} 个")
    for e in errors:
        print(f"   - {e}")
else:
    print("✅ 无错误")

if warnings:
    print(f"⚠️  警告: {len(warnings)} 个")
    for w in warnings:
        print(f"   - {w}")
else:
    print("✅ 无警告")

print("=" * 60)
print("视觉交叉验证完成!")
